import os
import json
from ai.gemini import Gemini_flash_2_5
from rag.shakespeare_rag import shakespeare_rag
import pandas as pd
import time

#load file
def load_data(filename):

    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print('Error! File not found')
        return None

#load system prompt
def load_system_prompt(filename):
    try:
        with open(filename,'r') as f:
            return f.read()
    except FileNotFoundError:
        return None


def run_test_rag_only(file,main_ai,eval_ai,retriever_ai,rag,k = 5,rerank = False,rk = 5,term_based = False, tk = 5):
    i = 0
    df = pd.DataFrame(columns=['id','Question Type','Question','Answer','Correct id found','RAG AI Answer', 'AI Answer Evaluation'])

    for row in file:
        if i == 1000:
            break
        i +=1

        print(f'\nQuestion #{i}:\n')
        playname = row['play_name']
        cor_id = row['id']
        
        question = json.loads(row["Question"])
        qtype = question["Qtype"]
        q = question["Question"]
        ans = question["Answer"]
        print('Play Name:',playname)
        print('Play id:', cor_id,'\n')
        print(f'Question Type: {qtype}\n')
        print(f'Question: {q}\n')
        print(f'Answer: {ans}\n')

        #---Retrieve embeddings based
        chunks = rag.retrieve_embedded_data(q,k)

        #---Term Based search
        if term_based == True:
            retrieval_query = rag.keyword_query_expansion_prompt(q,retriever_ai)
            print(f'retrieval_query: {retrieval_query}')

            for q_temp in retrieval_query:
                chunk = rag.retrieve_term_based_search(q_temp, k = tk)
                print(len(chunk))
                chunks += chunk

        #---Rerank if set to True
        print(f'Initial Chunk Len: {len(chunks)}')
        if rerank == True:
            reranked_scores, chunks_only = rag.reranking(q,chunks,rk)
            chunks = chunks_only

        #---Check if correct chuch retrieved
        id_found = False
        for chunk in chunks:
            
            if chunk.id ==cor_id:
                id_found = True

        if id_found:
            print('Correct id found')
        else:
            print('ID Not queried')

        #---Check if AI response answers question properly
        full_query = rag.generate_query_context(q,chunks)
        response = main_ai.chat(full_query)
        evaluate = f'-----Question----\n {q}\n -----Actual Answer-----\n {ans}\n-----RAG AI Response-----\n {response}'
        evaluation = eval_ai.chat(evaluate)

        print(f'\nQuestion #{i}:\n')
        print(f'\nAI response to Question: {response}\n Actual Answer: {ans} \n AI evaluation of Answer: {evaluation}\n Correct chunk found: {id_found}')


        df.loc[i-1] ={'id':cor_id,'Question Type':qtype,'Question':q,'Answer':ans,'Correct id found': id_found,'RAG AI Answer':response, 'AI Answer Evaluation':evaluation}
        time.sleep(10)
    return df




if __name__ == '__main__':
    '''
    1. Retrieval: Did the rag retrieve the correct chunk in final chunks. Simple id check (0-1)
        a. Quote based retrieval avg = sum of qbr scores/300, percent retrieval accuracy avg*100
        b. Conceptual based retrieval avg = sum of cbr scores/300, percent retrieval accuracy avg*100
        c. play/act specific question avg = sum of pasq scores/300, percent retrieval accuracy avg*100
        d. total avg = sum of all scores/300, percent retrieval accuracy avg*100
    2. Generation: Was the answer wrong/semi correct/ correct. LLM judge (0/.5/1)
        a. Quote based retrieval avg = sum of qbr scores/300, percent retrieval accuracy avg*100
        b. Conceptual based retrieval avg = sum of cbr scores/300, percent retrieval accuracy avg*100
        c. play/act specific question avg = sum of pasq scores/300, percent retrieval accuracy avg*100
        d. total avg = sum of all scores/300, percent retrieval accuracy avg*100
    
    '''
    
    filepath = 'postgres/rag_test_set1.json'
    file = load_data(filepath)
    GEMINI_API_KEY = os.getenv("gemini_api_key")
    rag = shakespeare_rag()
    System_prompt = load_system_prompt('prompts/system_prompt.md')
    retrieval_prompt = load_system_prompt("prompts/keyword_retriever_prompt.md")
    print(retrieval_prompt)
    Evaluation_prompt = 'You are a Shakespear RAG LLM Judge. Your job is to evaluate the response made by the RAG AI and compare it to the actual answer. ' \
    'Finally return back ONLY one of the following float values and nothing else' \
    '0: return if the RAG AI answer is completely wrong with no correct elements' \
    '0.5: Return if the RAG AI is almost correct or demonstrates a decent understanding of the question but does not quite give the correct answer' \
    '1: Return if the RAG AI returns an answer that is the correct answer or reasonably similar enough'
    main_ai = Gemini_flash_2_5(GEMINI_API_KEY,system_prompt=System_prompt)
    retriever_ai = Gemini_flash_2_5(GEMINI_API_KEY,retrieval_prompt)
    eval_ai = Gemini_flash_2_5(GEMINI_API_KEY,system_prompt=Evaluation_prompt)
    
    results_df = run_test_rag_only(file,main_ai,eval_ai,retriever_ai,rag,k = 80,rerank= True, rk = 10,term_based = True, tk = 5)
    print(results_df[['id','Question Type','Correct id found','AI Answer Evaluation']])
    eval_filename = f'postgres/eval_results/reranker_hybrid_query_expansion_rag_fixed_prompt_k_80_15_rk_10_evaluation.csv'
    results_df.to_csv(eval_filename,index = False)