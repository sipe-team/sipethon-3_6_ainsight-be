from ninja import Router, Schema
from django.http import StreamingHttpResponse
from openai import OpenAI
import anthropic
import google.generativeai as genai
import json
import os
import re
from dotenv import load_dotenv
from itertools import zip_longest

from apps.answer.models import UserAnswer, ModelAnswer

router = Router(tags=["Chat"])
load_dotenv()

# AI 서비스의 클라이언트 초기화
openai_client = OpenAI(api_key=os.getenv('GPT_OPENAI_API_KEY'))
claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# 공통 컨텍스트 정의
CODE_CONTEXT = """
You are a text-only assistant. You must follow these rules:
1. Never use code blocks or backticks
2. Never use markdown formatting
3. Show code as plain text with proper indentation using spaces
"""

def remove_markdown(content):
    """마크다운 및 코드 블록 제거"""
    if content:
        # 코드 블록 제거 (3개의 백틱으로 감싸진 부분)
        content = re.sub(r'```[\s\S]*?```', '', content)
        # 인라인 코드 제거 (1개의 백틱으로 감싸진 부분)
        content = re.sub(r'`[^`]*`', '', content)
        # 헤더 제거 (Markdown 헤더, #으로 시작하는 부분)
        content = re.sub(r'#{1,6}\s', '', content)
        # 리스트 항목 제거 (목록의 아이템들, * - + 등으로 시작하는 부분)
        content = re.sub(r'^[\*\+-]\s', '', content, flags=re.MULTILINE)
        # 링크 제거 (Markdown 링크 형식)
        content = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', content)
        # HTML 태그 제거
        content = re.sub(r'<.*?>', '', content)
        # \`로 감싸진 코드 블록 제거 (escape된 백틱 처리)
        content = re.sub(r'\\`[^`]*\\`', '', content)  # \`로 감싸진 코드 블록 제거
        # 마크다운 형식의 백틱 부분 제거 (기타 백틱 포함 부분 처리)
        content = re.sub(r'`+', '', content)  # 하나 이상의 연속된 백틱 제거
    return content


# API 엔드포인트와 스키마 정의
class MessageSchema(Schema):
    message: str
    models: list[str] = ['gpt-4o']


@router.post("/chat/stream")
def chat_stream(request, message_data: MessageSchema):
    def event_stream():
        responses = {}
        # 모델별 응답 생성
        for model in message_data.models:
            # GPT 모델 처리
            if model.startswith('gpt'):
                responses[model] = openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": CODE_CONTEXT},
                        {"role": "user", "content": message_data.message}
                    ],
                    stream=True
                )
            # Claude 모델 처리
            elif model.startswith('claude'):
                responses[model] = claude_client.messages.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": CODE_CONTEXT + "\n\n" + message_data.message
                        }
                    ],
                    stream=True,
                    max_tokens=1024,
                )
            # Gemini 모델 처리
            elif model.startswith('gemini'):
                gen_model = genai.GenerativeModel(model_name=model)
                response = gen_model.generate_content(
                    contents=CODE_CONTEXT + "\n\n" + message_data.message,
                    generation_config={"temperature": 0.7},
                    stream=True
                )
                responses[model] = iter(response)
        
        for model in message_data.models:
            yield f"data: {json.dumps({'type': 'start', 'model': model}, ensure_ascii=False)}\n\n"

        active_responses = {model: True for model in message_data.models}
        text = {model: '' for model in message_data.models}

        # 스트리밍 응답 처리
        while any(active_responses.values()):
            for model in message_data.models:
                if not active_responses[model]:
                    continue
                    
                try:
                    chunk = next(responses[model])
                    content = None
                    
                    # 각 모델별로 다른 응답 형식 처리
                    if model.startswith('gpt'):
                        content = chunk.choices[0].delta.content
                    elif model.startswith('claude'):
                        # Claude 응답 처리
                        if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                            content = chunk.delta.text  # 'text'가 있다면 이 값을 사용
                        elif hasattr(chunk, 'completion'):
                            content = chunk.completion  # 'completion'을 사용
                    elif model.startswith('gemini'):
                        # Gemini 응답 처리
                        if hasattr(chunk, 'text'):
                            content = chunk.text
                        
                    if content:
                        # 마크다운 제거 적용
                        content = remove_markdown(content)
                        text[model] = content
                        data = {
                            "type": "content",
                            "model": model,
                            "content": content
                        }
                        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                except StopIteration:
                    active_responses[model] = False
                    yield f"data: {json.dumps({'type': 'end', 'model': model}, ensure_ascii=False)}\n\n"
                except Exception as e:
                    active_responses[model] = False
                    yield f"data: {json.dumps({'type': 'error', 'model': model, 'error': str(e)}, ensure_ascii=False)}\n\n"

        if text.keys():
            answer = UserAnswer(question=message_data.message)
            answer.save()
            model_answers = []
            for model_id in text.keys():
                model_answers.append(ModelAnswer(model_id=model_id, answer=text[model_id], user_answer=answer))
            ModelAnswer.objects.bulk_create(model_answers)

    return StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream; charset=utf-8'
    )