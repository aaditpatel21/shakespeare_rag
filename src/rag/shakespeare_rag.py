import os
import re
import json
from sentence_transformers import SentenceTransformer, CrossEncoder
from src.postgres.database import session, Shakespearechunks, getdb
from dotenv import load_dotenv
from sqlalchemy import text
from src.postgres.database import session


class shakespeare_rag:

    def __init__(self, retriever = None, main_ai = None, history_ai = None):
        print("Loading Embedding Model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Model loaded")

        print("Loading Reranker Model...")
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        print("Reranker Loaded")

        print("Loading Gemini Term Based Retriever Model...")
        self.retriever_ai = retriever

        print("Loading History Context Gemini Model...")
        self.history_ai = history_ai

        print("Loading Main Gemini Model...")
        self.main_ai = main_ai

    
    def retrieve_embedded_data(self,query, k =5):
        print("Retrieving Embedding data...")
        sql_session = session()
        #sql_session.execute(text(f"SET hnsw.ef_search = {k}"))

        #1. Embed query
        vectorized_query = self.model.encode(query).tolist()

        #retrieve k data
        results = sql_session.query(Shakespearechunks).order_by(Shakespearechunks.embedding.cosine_distance(vectorized_query)).limit(k).all()

        print("Data Retrieved!")


        sql_session.close()
        return results
    
    def reranking(self,query,results,k = 5):
        pairs = [[query,result.content] for result in results]
        scores = self.reranker.predict(pairs)
        scores_topk = sorted(scores, reverse=True)
        scores_topk = scores_topk[:k]

        
        chunks_with_score = []
        for i,score in enumerate(scores):
            chunks_with_score.append([results[i],score])
        
        chunks_with_score.sort(key = lambda x:x[1],reverse= True)
        topk_chunks_with_score = chunks_with_score[:k]
        chunks_only = []
        for chunk in topk_chunks_with_score:
            chunks_only.append(chunk[0])

        return  topk_chunks_with_score,chunks_only


    def generate_query_context(self,query,chunks,history = ''):

        query_context = ""
        i = 0
        for chunk in chunks:
            i+=1
            metadata = chunk.meta_data
            playname = chunk.play_name
            query_context += f"\n-Chunk {i}-\nPlay Name: {playname}\n Chunk MetaData: {metadata} \nText: {chunk.content}\n"

        #full_prompt = f"---System Instructions---\n {system_instructions} \n\n ---Context---\n {query_context}\n\n  ---User Question---\n {query}"
        #full_prompt = f"---History---\n {history}\n\n---New Context---\n {query_context}\n\n ---New User Question---\n {query}"
        full_prompt = f"---New Context---\n {query_context}\n\n---Chat History---\n {history}\n\n ---New User Question---\n {query}"


        return full_prompt
    
    def retrieve_term_based_search(self,query, k =5):
        load_dotenv()
        print("Retrieving term based data...")
        sql_session = session()

        chunks = sql_session.query(Shakespearechunks).filter(text("text_search @@ websearch_to_tsquery('english', :q)")).params(q=query).limit(k).all()
        for chunk in chunks:
            #print(f'Term Based search chunks:\n {chunk.play_name}')
            pass
        return chunks

    def merge_chunks(self):
        pass

    
    def keyword_query_expansion_prompt(self,query,ai):
        prompt = f"""
        USER QUESTION: "{query}"
        JSON OUTPUT:
        """

        text = ai.chat(prompt)

        text = text.replace("```json", "").replace("```", "")
        text.strip()
        try:
            prompts = json.loads(text)
            return prompts
        except json.JSONDecodeError:
            return []
    
    def history_context_query_rewritten(self,query):
        rewritten_query = self.history_ai.chat(query)
        return rewritten_query

    def run_full_rag(self,query,history,kv = 50, kt = 5, kr = 5 ):
        #Automatically runs rag pipeline, used by fast api
        
        #rewrite query to take history context
        query = self.history_context_query_rewritten(query)
        print(query)

        #embedding based retrieval
        chunks1 = self.retrieve_embedded_data(query,k =kv)
        #term based retrieval
        retrieval_query = self.keyword_query_expansion_prompt(query,self.retriever_ai)
        
        for q in retrieval_query:
            chunk = self.retrieve_term_based_search(q, k = kt)
            #print(len(chunk))
            chunks1 += chunk

        reranked_scores, chunks_only = self.reranking(query,chunks1,kr)
        full_prompt = self.generate_query_context(query,chunks_only,history)

        return full_prompt
    
    def generate_answer(self,prompt):
        response_text = self.main_ai.chat(prompt)
        return response_text
