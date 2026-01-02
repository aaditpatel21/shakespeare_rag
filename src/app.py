'''
Shakespeare bot app

'''

#imports
import os
import json
from ai.gemini import Gemini_flash_2_5
from rag.shakespeare_rag import shakespeare_rag


'''
#Still To do
1.
. Perform Eval on results (LLM-as-a-judge,golden dataset) DONE
. reranking DONE
. hybrid search system DONE
. Push to Githup
. Build a Read me
2. Create Fast API wrapper
3. Add way to store chat history with another table in postgres
4. Create way to track simple user and session id
5. Build small react front end
6. dockerize
7. Host on AWS
8. Perform Caching with redis
8. Add More data to vector DB such as summaries, Shakespeare history, etc
'''

#user input (temporary)
#user_prompt = input("Input Question: ")
#user_prompt = "Between whom does a “merry war” of words go on in Shakespeare’s Much Ado About Nothing?"
user_prompt = 'Which of these plays by Shakespeare uses a statue to reveal a most dramatic secret?'
#user_prompt = 'What is the name of the penniless Venetian who asks his friend for a loan in The Merchant of Venice?'
#user_prompt = 'Which of Shakespeare’s title roles has the fewest lines?'




#load system prompt
def load_system_prompt(filename):
    try:
        with open(filename,'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

system_prompt = load_system_prompt("src/prompts/system_prompt.md")
retrieval_prompt = load_system_prompt("src/prompts/keyword_retriever_prompt.md")

# --- Load AI platform ---
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not set")

ai_platform = Gemini_flash_2_5(gemini_api_key,system_prompt)
retriever_ai = Gemini_flash_2_5(gemini_api_key,retrieval_prompt)

# --- Run RAG ---
rag = shakespeare_rag()

#embedding based retrieval
chunks1 = rag.retrieve_embedded_data(user_prompt,k =80)

#term based retrieval
retrieval_query = rag.keyword_query_expansion_prompt(user_prompt,retriever_ai)

for q in retrieval_query:
    chunk = rag.retrieve_term_based_search(q, k = 5)
    #print(len(chunk))
    chunks1 += chunk

#merge chunkss
#chunks = chunks1 + chunks2

#print(type(chunks1),len(chunks1))
#print(len(chunks1))
reranked_scores, chunks_only = rag.reranking(user_prompt,chunks1,10)
full_prompt = rag.generate_query_context(user_prompt,chunks_only)


#print("\nFull Prompt:\n",full_prompt)

response_text = ai_platform.chat(full_prompt)

print(f"\n---Gemini Response---:\n{response_text}")
print(retrieval_query)

#print(f'\n\nReranker Results: {reranked_scores}\nChunks {chunks_only}')