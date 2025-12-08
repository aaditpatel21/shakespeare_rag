'''
Load shakespear plays and save them as chuncks of vector embeddings in postgres server
'''

#imports
import os
import glob
import re
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from postgres.database import session,Shakespearechunks


# --- Helper Functions ---

#Get all sonnets
def get_sonnets(html_folder_path,folder):
    files_to_embed = []
    search_path = os.path.join(html_folder_path + r'\\'+folder, "**/*.html")
    files = glob.glob(search_path, recursive=True)
    for file in files:
        filename = os.path.basename(file)
        match = 'sonnet.' in filename.lower()
        if match:
            files_to_embed.append(file)

    print(files_to_embed)
    return files_to_embed
    

# Get only scenes html pages from book folder
def get_scene(html_folder_path, folder):
    files_to_embed = []
    search_path = os.path.join(html_folder_path + r'\\'+folder, "**/*.html") 
    files = glob.glob(search_path, recursive=True)
    
    for file in files:
        filename = os.path.basename(file)
        match = re.match(r'^(.+)\.(\d+)\.(\d+)\.html$', filename)

        if match:
            files_to_embed.append(file)

    #print(files_to_embed)
    return files_to_embed

#Get act, scene, scene_title meta data from HTML
def get_metadata(soup):
    scene_title = soup.find('title').get_text(separator=' ', strip=True)
    nav = soup.find('td',class_ = 'nav').get_text(separator=' ', strip=True)
    match = re.search(r'Act\s+(\d+),\s+Scene\s+(\d+)', nav, re.IGNORECASE)
    if match:
        act = match.group(1)
        scene = match.group(2)
        #print(act, scene)
    elif "Induction" in nav:
            act = "0"
            scene = "0"
    elif "Prologue" in nav:
            act = "0"
            scene = "0"

    #print(scene_title)
    return act, scene, scene_title

# Parse scene script and convert into easily readable string
def parse_scene(soup):

    speaker = ''
    converted_text = []


    for element in soup.find_all(['a','i']):
        if element.name == 'a':
            name = element.get('name','')
            if name and name.startswith('speech'):
                speaker = element.get_text(strip = True)
                converted_text.append(f"\n{speaker}:")
            elif name:
                text = element.get_text(separator=' ', strip=True)
                converted_text.append(text)
            else:
                pass
        else:
            converted_text.append(f'\nStage Instructions: {element.get_text(strip = True)}\n')
    return "\n".join(converted_text)

# Split long scenes into chunks for embedding
def chunk_text(title,metadata,text, chunk_size = 1000, overlap = 100):
    chunks =[]
    start = 0
    segment_prefix = f'Title: {title}, Metadata: {metadata}\n'
    while start < len(text):
        end = start + chunk_size
        raw_segment = text[start:end]
        segment = segment_prefix+raw_segment
        chunks.append(segment)
        start += chunk_size - overlap
    return chunks


# --- Main Functions --- 

def run_book(path,folder,book_title,model,session):
    files_to_embed = get_scene(path,folder)

    for file in files_to_embed:
        with open(file,'r',encoding = 'utf-8') as f:
            soup = BeautifulSoup(f,'html.parser')
        act, scene, scene_title = get_metadata(soup)
        print(f'\nWorking on act {act}, scene {scene}: {scene_title}\n')
        converted_text = parse_scene(soup)
        #print(converted_text)
        metadata = {
                    "act":act,
                    "scene":scene,
                    "scene_title": scene_title,
                }
        chunked_text = chunk_text(book_title,metadata,converted_text,chunk_size=1000,overlap= 100)
        print(f'Total chunks to add: {len(chunked_text)}\n')
        new_docs = []
        for i,chunk in enumerate(chunked_text):
            vector = model.encode(chunk).tolist()
            doc = Shakespearechunks(
                play_name =book_title,
                content = chunk,
                embedding = vector,
                meta_data = {
                    "act":act,
                    "scene":scene,
                    "scene_title": scene_title,
                    "chunk_num_in_scene": i
                }

            )
            new_docs.append(doc)

        #Add data to postgres server
        session.add_all(new_docs)
        session.commit()
        print(f'Chunks added: {len(new_docs)}\n')

#run sonnets
def run_sonnet(sonnet_files,model,session):

    for file in sonnet_files:
        print(file)
        match = re.search(r'sonnet\.([a-zA-Z]+)\.html', file, re.IGNORECASE)
        roman_num = match.group(1).upper()
        name = f'Sonnet {roman_num}'
        print(f'\nWorking on Sonnet {roman_num}\n')
        with open(file,'r',encoding = 'utf-8') as f:
            soup = BeautifulSoup(f,'html.parser')
            text = ''
            for element in soup.find_all(['BLOCKQUOTE'.lower()]):
                text = element.get_text(separator=' ', strip=True)
                
            #print(text)
            metadata = {
                        "act": 'Sonnet',
                        "sonnet_vol": roman_num}
            chunked_text = chunk_text(name,metadata,text,chunk_size=1000,overlap= 100)
            print(f'Total chunks to add: {len(chunked_text)}\n')
            new_docs = []
            for i,chunk in enumerate(chunked_text):
                vector = model.encode(chunk).tolist()
                doc = Shakespearechunks(
                    play_name =name,
                    content = chunk,
                    embedding = vector,
                    meta_data = {
                        "act": 'Sonnet',
                        "sonnet_vol": roman_num,
                        "chunk_num_in_scene": i
                    }

                )
                new_docs.append(doc)

            #Add data to postgres server
            session.add_all(new_docs)
            session.commit()
            print(f'Chunks added: {len(new_docs)}\n')
    
if __name__ == "__main__":
    #shakespeare files
    html_folder_path = "shakespeare-master"
    #books to downlowad
    folders = ['1henryiv','1henryvi']
    titles =  {'1henryiv': 'Henry IV, part 1',
               '1henryvi': 'Henry VI, part 1',
               '2henryiv': 'Henry IV, part 2',
               '2henryvi': 'Henry VI, part 2',
               '3henryvi': 'Henry VI, part 3',
               'allswell':"All's Well That Ends Well",
               'asyoulikeit': 'As You Like It',
               'cleopatra': 'Antony and Cleopatra',
               'comedy_errors': 'Comedy of Errors',
               'coriolanus':'Coriolanus',
               'cymbeline':'Cymbeline',
               'hamlet':'Hamlet',
               'henryv':'Henry V',
               'henryviii':'Henry VIII',
               'john':'King John',
               'julius_caesar':'Julius Caesar',
               'lear':'King Lear',
               'lll': "Love's Labour's Lost",
               'macbeth':"Macbeth",
               'measure': 'Measure for Measure',
               'merchant': 'Merchant of Venice',
               'merry_wives': 'Merry Wives of Windsor',
               'midsummer': "Midsummer Night's Dream",
               'much_ado': "Much Ado About Nothing",
               'othello':'Othello',
               'pericles':'Pericles',
               'richardii':'Richard II',
               'richardiii':'Richard III',
               'romeo_juliet':'Romeo and Juliet',
               'taming_shrew':'Taming of the Shrew',
               'tempest':'The Tempest',
               'timon':'Timon of Athens',
               'titus':'Titus Andronicus',
               'troilus_cressida': 'Troiles and Cressida',
               'twelfth_night':'Twelfth Night',
               'two_gentlemen':'Two Gentlemen of Verona',
               'winters_tale':"Winter's Tale"
               }

    #embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    sql_session = session()

    #run data gathering, chunking, and embedding
    sonnets_complete = True
    plays_complete = True
    
    if plays_complete == False:
        for folder in titles:
            print(f"\nAdding all scenes from {folder} with title {titles[folder]}\n")
            run_book(html_folder_path,folder,titles[folder],model,sql_session)
            print(f"\nAdded all scenes from {folder} with title {titles[folder]}\n")
    
    if sonnets_complete == False:
        sonnet_files = get_sonnets(html_folder_path,'Poetry')
        run_sonnet(sonnet_files,model,sql_session)