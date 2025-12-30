#Main Fast API application

#imports
import os
import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, Depends, routing
from fastapi.middleware.cors import CORSMiddleware
from .api.chat import chatrouter
from contextlib import asynccontextmanager
from .ai.gemini import Gemini_flash_2_5
from .rag.shakespeare_rag import shakespeare_rag

#---Misc Functions---
#load system prompt
def load_system_prompt(filename):
    try:
        with open(filename,'r') as f:
            return f.read()
    except FileNotFoundError:
        return None


# --- Rag model loading for server state ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading RAG Engine...")
    try:
        # --- Load AI platform ---
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set")
        
        system_prompt = load_system_prompt("src/prompts/system_prompt.md")
        retrieval_prompt = load_system_prompt("src/prompts/keyword_retriever_prompt.md")
        
        ai_platform = Gemini_flash_2_5(gemini_api_key,system_prompt)
        retriever_ai = Gemini_flash_2_5(gemini_api_key,retrieval_prompt)


        app.state.rag_engine = shakespeare_rag(retriever=retriever_ai, main_ai=ai_platform)
        print("Loaded Successfully.")
    except Exception as e:
        print(f'Failed to load engine: {e}')
        app.state.rag_engine = None

    yield

# --- App Init ---
app = FastAPI(title = "Shakespeare RAG API", version = '1.0.0',lifespan=lifespan)
app.include_router(chatrouter)

#Front end permissions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Set up APP ---
@app.get('/')
async def root():
    return {'Message': 'Shakespeare RAG is running'}

# TO RUN command: uvicorn src.main:app --reload --port 8000

'''
if __name__ == "__main__":
    uvicorn.run("main:app",host = '0.0.0.0', port = 8000, reload = True)
'''

