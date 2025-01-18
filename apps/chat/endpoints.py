# endpoints.py
from ninja import Router, Schema
from django.http import StreamingHttpResponse
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from itertools import zip_longest

router = Router(tags=["Chat"])
load_dotenv()
client = OpenAI(api_key=os.getenv('GPT_OPENAI_API_KEY'))


class MessageSchema(Schema):
    message: str
    models: list[str] = ['gpt-4o']


@router.post("/chat/stream")
def chat_stream(request, message_data: MessageSchema):
    def event_stream():
        # 모든 모델의 응답을 동시에 시작
        responses = {
            model: client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": message_data.message}],
                stream=True
            ) for model in message_data.models
        }
        
        # 각 모델의 시작을 알림
        for model in message_data.models:
            yield f"data: {json.dumps({'type': 'start', 'model': model}, ensure_ascii=False)}\n\n"

        # 모든 응답의 청크를 번갈아가며 처리
        active_responses = {model: True for model in message_data.models}
        
        while any(active_responses.values()):
            for model in message_data.models:
                if not active_responses[model]:
                    continue
                    
                try:
                    chunk = next(responses[model])
                    if chunk.choices[0].delta.content:
                        data = {
                            "type": "content",
                            "model": model,
                            "content": chunk.choices[0].delta.content
                        }
                        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                except StopIteration:
                    active_responses[model] = False
                    yield f"data: {json.dumps({'type': 'end', 'model': model}, ensure_ascii=False)}\n\n"
                except Exception as e:
                    active_responses[model] = False
                    yield f"data: {json.dumps({'type': 'error', 'model': model, 'error': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream; charset=utf-8'
    )
