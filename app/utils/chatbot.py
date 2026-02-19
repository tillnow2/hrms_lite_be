import os
import asyncio
from typing import List, Dict, Optional
from google import genai
from app.config.settings import settings

GEMINI_API_KEY = getattr(settings, 'GEMINI_API_KEY', '')
GEMINI_MODEL = getattr(settings, 'GEMINI_MODEL', 'gemini-flash-lite-latest')
print(GEMINI_MODEL)

client = genai.Client(api_key=GEMINI_API_KEY)
print(f"Initialized Gemini client with model: {GEMINI_MODEL}")
async def chat(messages: List[Dict[str, str]], model: Optional[str] = None, max_tokens: int = 512) -> Dict:
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "Hello")
            break
    
    def _call():
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_message,
        )
        return response

    try:
        resp = await asyncio.to_thread(_call)

        usage = resp.usage_metadata if hasattr(resp, 'usage_metadata') else None
        if usage:
            prompt_tokens = usage.prompt_token_count
            response_tokens = usage.candidates_token_count
            total_tokens = usage.total_token_count
            billable_tokens = prompt_tokens + response_tokens  # What you actually pay for

        text = resp.text if hasattr(resp, 'text') and resp.text else ""
        raw_data = {
            "text": text,
            "model": GEMINI_MODEL,
            "status": "success",
            "usage": {
                "prompt_tokens": prompt_tokens if usage else 0,
                "response_tokens": response_tokens if usage else 0,
                "total_tokens": total_tokens if usage else 0,
                "billable_tokens": billable_tokens if usage else 0

            },
        }
        return {"text": text, "raw": raw_data}
    except Exception as e:
        if "quota" in str(e).lower() or "429" in str(e):
            return {"text": "I'm currently unavailable due to API quota limits. Please contact your administrator or try again later.", "error": "quota_exceeded"}
        raise e
