'''Postgres Database basic info'''

#imports
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector

load_dotenv()

db_url = os.getenv("DATABASE_URL")

class Base(DeclarativeBase):
    pass

engine = create_engine(db_url)
session = sessionmaker(bind=engine)

class Shakespearechunks(Base):
    __tablename__ = 'shakespeare_embeddings'

    id = Column(Integer, primary_key= True)
    play_name = Column(String(255))
    content = Column(String)
    meta_data = Column(JSONB, default = {})
    embedding = Column(Vector(384))


with engine.connect() as conn:
    result = conn.execute(text("select 1"))
    print('--- SQL Engine Connected---')