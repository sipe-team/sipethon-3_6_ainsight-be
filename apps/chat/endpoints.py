from ninja import Router, Schema
from django.http import StreamingHttpResponse
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

router = Router(tags=["Chat"])
load_dotenv()
client = OpenAI(api_key=os.getenv('GPT_OPENAI_API_KEY'))

# 요청 스키마 정의
class MessageSchema(Schema):
    message: str

@router.post("/chat/stream")
def chat_stream(request, message_data: MessageSchema):
    def event_stream():
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": message_data.message}],
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    data = {"content": chunk.choices[0].delta.content}
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                    
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream; charset=utf-8'
    )
