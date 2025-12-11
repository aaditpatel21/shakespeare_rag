from fastapi import Depends, APIRouter
from .models import ChatRequest, ChatResponse


router = APIRouter(prefix = "/chat", tags = ["chat"])

@router.post("/chat")
def chat(request: ChatRequest ):
    pass