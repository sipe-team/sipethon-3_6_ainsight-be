from ninja import Router, Schema
from django.http import StreamingHttpResponse
from openai import OpenAI
import anthropic
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from itertools import zip_longest

from apps.answer.models import UserAnswer, ModelAnswer

router = Router(tags=["Chat"])
load_dotenv()

# AI 서비스의 클라이언트 초기화
openai_client = OpenAI(api_key=os.getenv('GPT_OPENAI_API_KEY'))
claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# API 엔드포인트와 스키마 정의
class MessageSchema(Schema):
    message: str
    models: list[str] = ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo']

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
                    messages=[{"role": "user", "content": message_data.message}],
                    stream=True
                )
            # Claude 모델 처리
            elif model.startswith('claude'):
                responses[model] = claude_client.messages.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": message_data.message
                        }
                    ],
                    stream=True,
                    max_tokens=1024,
                )
            # Gemini 모델 처리
            elif model.startswith('gemini'):
                response = genai.GenerativeModel(model_name=model).generate_content(
                message_data.message,
                stream=True
                )
                responses[model] = iter(response)  # iter() 함수를 사용하여 이터레이터로 변환
        
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

                    text[model] += content

                    if content:
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