import json
import os
import time
from dotenv import load_dotenv
from ai.gemini import Gemini_flash_2_5


def load_data(filename):

    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print('Error! File not found')
        return None


def create_quiz(test_set,ai,k = 2):
    
    answers = []
    for i, chunk in enumerate(test_set):
        play_name = chunk.get('play_name')
        content = chunk.get('content')
        meta_data = chunk.get('meta_data')
        id = chunk['id']
        prompt = f'---Chunk---\n{content}'
        if i < k:
            answer = ai.chat(prompt)
            print('\n30 seconds sleep...\n')
            time.sleep(30)
            clean_text = answer.strip()
            #print(f'Prompt:\n{prompt}\n---\n')
            #print(f'Answer {i}:\n{clean_text}\n---\n')
            for q in clean_text.splitlines():
                print(f'line split: \n{q}\n')
                answers.append({"play_name": play_name,"id": id, "meta_data": meta_data, "prompt": prompt, "Question": q})
    return answers
if __name__ == '__main__':
    
    #JSON filename
    test_filename ='postgres/100_chunk_rag_test_set.json'
    output_filename = 'postgres/rag_test_set1.json'
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        
    test_set = load_data(test_filename)
    instructions = 'You are a Teacher for a ShakeSpeare Rag. Youre job is to make a question out of each chunk given to you. ' \
    'Output a clean machine readable file with these values(No extra markdowns, machine friendly ex. Do not add "```" or "json" in beginning). The type of question being asked as "Qtype". The Question you created as "Question", and the correct answer as "Answer"' \
    'You will output 3 questions of the following type:' \
    '1. Quote based question: To test if the rag can find a specific phrase.' \
    '2. Conceptual question: To test if the rag is able to understand the context being talked about.' \
    '3. Play/act specific question: Ask about the play title or specific scene without direction saying in Play "playname". Simple as for example "what is the key plot point in Hamlet"'
    gemini_ai = Gemini_flash_2_5(GEMINI_API_KEY,instructions)
    answers = create_quiz(test_set,gemini_ai,100)
    with open(output_filename, 'w') as f:
        json.dump(answers, f, indent=4)
        print('Test Set File Created!')