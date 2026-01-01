import os
from typing import Optional
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt
import uuid


'''
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error= False)

async def get_user_identifier(token: Optional[str] = Depends(oauth2_scheme)):
    if token is None:
        return "global_unauthenticated_user"
    payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
    username: str = payload.get("sub")
    return username

'''


async def get_user_identifier(x_user_id: str = Header(None)) -> str:
    if not x_user_id:
        x_user_id = f"temp_{uuid.uuid4()}"
    
    return x_user_id
