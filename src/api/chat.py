from fastapi import Depends, APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from .models import ChatRequest, ChatResponse
from .users import get_user_identifier
from .throttling import apply_rate_limit
from sqlalchemy.orm import session
from src.postgres.database import getdb, chathistory


chatrouter = APIRouter(prefix = "/chat", tags = ["chat"])

@chatrouter.post("/", response_model= ChatResponse)
async def chat_endpoint(request: Request , chatrequest: ChatRequest, user_id: str = Depends(get_user_identifier), db: session = Depends(getdb)):
    #Rate limit check
    print(user_id)
    await apply_rate_limit(user_id)
    
    #point to rag model
    rag_engine = request.app.state.rag_engine
    if not rag_engine:
        raise HTTPException(status_code=503, detail= "RAG Engine error")
    
    history = db.query(chathistory).filter(chathistory.user_id == user_id).order_by(chathistory.time.desc()).limit(5).all()
    chat_history = [{"role": h.role, "content": h.content} for h in reversed(history)]

    #Run Full Rag
    rag_final_output = await run_in_threadpool(
        rag_engine.run_full_rag,
        query = chatrequest.prompt,
        history = chat_history,
        kv = 80,
        kt = 5,
        kr = 10 
    )
    
    print(rag_final_output)

    #Get AI response
    ai_response = await run_in_threadpool(
        rag_engine.generate_answer,
        prompt = rag_final_output
    )

    user_entry = chathistory(user_id = user_id, role = 'user', content = chatrequest.prompt)
    ai_entry = chathistory(user_id = user_id, role = 'gemini 2.5 flash', content = ai_response)

    db.add(user_entry)
    db.add(ai_entry)
    db.commit()


    return ChatResponse(response = ai_response)

