from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any
from app.utils.chatbot import chat
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []  # optional conversation history


class ChatResponse(BaseModel):
    reply: str
    raw: Dict[str, Any] | None = None


@router.post("/ai/chat", response_model=ChatResponse)
async def ai_chat(req: ChatRequest):
    """Simple chat endpoint that forwards messages to OpenAI and returns the assistant reply."""
    messages = []
    if req.history:
        messages.extend(req.history)
    messages.append({"role": "user", "content": req.message})

    try:
        resp = await chat(messages)
        return {"reply": resp.get("text", ""), "raw": resp.get("raw")}
    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
