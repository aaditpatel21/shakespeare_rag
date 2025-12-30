from fastapi import Depends, APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from .models import ChatRequest, ChatResponse
from .users import get_user_identifier
from .throttling import apply_rate_limit


chatrouter = APIRouter(prefix = "/chat", tags = ["chat"])

@chatrouter.post("/", response_model= ChatResponse)
async def chat_endpoint(request: Request , chatrequest: ChatRequest, user_id: str = Depends(get_user_identifier)):
    #Rate limit check
    print(user_id)
    await apply_rate_limit(user_id)
    
    #point to rag model
    rag_engine = request.app.state.rag_engine
    if not rag_engine:
        raise HTTPException(status_code=503, detail= "RAG Engine error")
    
    #Run Full Rag
    rag_final_output = await run_in_threadpool(
        rag_engine.run_full_rag,
        query = chatrequest.prompt,
        kv = 80,
        kt = 5,
        kr = 10 
    )
    
    ai_response = await run_in_threadpool(
        rag_engine.generate_answer,
        prompt = rag_final_output
    )

    return ChatResponse(response = ai_response)

