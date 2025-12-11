from pydantic import BaseModel

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str

class Rag(BaseModel):
    prompt: str
    keywords: list
    vector_search_chunks: list
    ts_chunks: list
    reranked_chunks: list
    output_full_prompt: str