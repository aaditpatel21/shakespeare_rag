#Main Fast API application

#imports
import os
#from .ai.gemini import Gemini_flash_2_5
from fastapi import FastAPI, Depends
from pydantic import BaseModel

# --- App Init ---
app = FastAPI()

