#Main Fast API application

#imports
import os
#from .ai.gemini import Gemini_flash_2_5
from fastapi import FastAPI, Depends, routing
from pydantic import BaseModel
import uvicorn

# --- App Init ---
app = FastAPI()



# --- Set up APP ---
@app.get('/')
async def root():
    return {'Message': 'API is running'}


items = []

@app.post('/items')
def add_items(item):
    items.append(item)
    return items

@app.get('/items')
def get_item(i:int):
    return items[i] 