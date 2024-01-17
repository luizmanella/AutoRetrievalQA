import os
import json
import secrets
from datetime import datetime
import torch

import fitz  # PyMuPDF
import tiktoken
import openai

# from sentence_transformers import SentenceTransformer


from dotenv import find_dotenv, load_dotenv
from os import environ as env

from pytz import timezone

TZ = timezone('US/Eastern')

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
openai.api_key = env.get('OPEN_AI_KEY')

users_top_level_directory = env.get('ARQA_USERS')
presets_top_level_directory = env.get('ARQA_PRESETS')
MAX_TOKENS = int(env.get('MAX_TOKENS'))


# ----------------------------------------------------------------------------------------------
#         PRESETS RELATED
# ----------------------------------------------------------------------------------------------
def grab_presets_metadata():
    target_path = os.path.join(presets_top_level_directory, 'presets_metadata.json')
    with open(target_path, 'r') as f:
        return json.load(f)
    

def grab_preset_questions(p_name):
    target_path = os.path.join(presets_top_level_directory, f'{p_name}.json')
    with open(target_path, 'r') as f:
        return json.load(f)
    

def grab_specific_preset(p_name):
    presets_metadata = grab_presets_metadata()
    for preset in presets_metadata:
        if preset['questionnaire_name'] == p_name:
            _target = preset
            break
    questions = grab_preset_questions( p_name)
    return _target['questionnaire_name'], _target['tag_color'], _target['description'], questions



# ----------------------------------------------------------------------------------------------
#         QUESTIONNAIRE RELATED
# ----------------------------------------------------------------------------------------------
def grab_questionnaire_metadata(user):
    target_path = os.path.join(users_top_level_directory, user, 'questionnaires', 'questionnaire_metadata.json')
    with open(target_path, 'r') as f:
        questionnaires = json.load(f)
    return questionnaires        


def save_questionnaire_metadata(user, questionnaire_metadata):
    target_path = os.path.join(users_top_level_directory, user, 'questionnaires', 'questionnaire_metadata.json')
    with open(target_path, 'w') as f:
        json.dump(questionnaire_metadata, f)


def save_new_questionnaire(user, qid, questions):
    counter = list(range(len(questions)))
    q = [{'#': index, 'question': questions[index]} for index in counter]
    target_path = os.path.join(users_top_level_directory, user, 'questionnaires', f'{qid}.json')
    with open(target_path, 'w') as f:
        json.dump(q, f)


def create_new_questionnaire(user, questionnaire_name, tag_color, description, questions):
    qid = secrets.token_hex(32)
    id_exists = False
    questionnaire_metadata = grab_questionnaire_metadata(user)
    for qm in questionnaire_metadata:
        if qm['questionnaire_name'] == questionnaire_name:
            return {'internal_status': 1, 'message': 'A questionnaire with this name already exists.'}
        if qm['qid'] == qid:
            id_exists = True
    while id_exists:
        qid = secrets.token_hex(32)
        id_exists = False
        for qm in questionnaire_metadata:
            if qm['qid'] == qid:
                id_exists = True
    q_obj = {
        'qid': qid,
        'questionnaire_name': questionnaire_name,
        'tag_color': tag_color,
        'description': description
    }
    questionnaire_metadata.append(q_obj)
    save_questionnaire_metadata(user, questionnaire_metadata)
    save_new_questionnaire(user, qid, questions)
    return {'internal_status': 0}


def update_questionnaire(user, qid, questionnaire_name, tag_color, description, questions):
    questionnaire_metadata = grab_questionnaire_metadata(user)
    for index, row in enumerate(questionnaire_metadata):
        if row['qid'] == qid:
            target_index = index
            break
    questionnaire_metadata[target_index]['questionnaire_name'] = questionnaire_name
    questionnaire_metadata[target_index]['tag_color'] = tag_color
    questionnaire_metadata[target_index]['description'] = description
    save_questionnaire_metadata(user, questionnaire_metadata)
    save_new_questionnaire(user, qid, questions)
    return {'internal_status': 0}
    

def delete_questionnaire(user, qids):
    indexes_to_delete = []
    questionnaire_metadata = grab_questionnaire_metadata(user)
    for index, row in enumerate(questionnaire_metadata):
        for qid in qids:
            if row['qid'] == qid:
                target_path = os.path.join(users_top_level_directory, user, 'questionnaires', f'{row["qid"]}.json')
                os.remove(target_path)
                indexes_to_delete.append(index)
    for idx in indexes_to_delete[::-1]:
            questionnaire_metadata.pop(idx)
    save_questionnaire_metadata(user, questionnaire_metadata)
    return {'internal_status': 0}
            

def grab_questionnaire_questions(user, qid):
    target_path = os.path.join(users_top_level_directory, user, 'questionnaires', f'{qid}.json')
    with open(target_path, 'r') as f:
        return json.load(f)


def grab_specific_questionnaire(user, qid, source):
    if source == 'preset':
        return grab_specific_preset(qid)
    else:
        questionnaire_metadata = grab_questionnaire_metadata(user)
        for row in questionnaire_metadata:
            if row['qid'] == qid:
                target_row = row
                break
        questionnaire_questions = grab_questionnaire_questions(user, qid)
        return target_row['questionnaire_name'], target_row['tag_color'], target_row['description'], questionnaire_questions


# ----------------------------------------------------------------------------------------------
#         DIRECTORIES RELATED
# ----------------------------------------------------------------------------------------------
def grab_client_file_metadata(user):
    target_path = os.path.join(users_top_level_directory, user, 'client_files_metadata.json')
    with open(target_path,'r') as f:
        file = json.load(f)
    return file


def save_metadata_file(user, metadata):
    target_path = os.path.join(users_top_level_directory, user, 'client_files_metadata.json')
    with open(target_path, 'w') as f:
        json.dump(metadata, f)


def grab_starred(user):
    metadata = grab_client_file_metadata(user)
    starred_folders = []
    starred_files = []
    for row in metadata:
        # Grab starred content
        if row['starred']:
            if row['type'] == 'folder':
                starred_folders.append({'filename': row['filename'], 'id': row['id'], 'type': row['type']})
            elif row['type'] == 'file':
                starred_files.append({'filename': row['filename'], 'id': row['id'], 'type': row['type']}) 
    starred_folders += starred_files
    return starred_folders


def star_unstar(user, id):
    status = None
    metadata = grab_client_file_metadata(user)
    for index, row in enumerate(metadata):
        if row['id'] == id:
            target_row = row
            if target_row['starred'] == 0:
                target_row['starred'] = 1
            else:
                target_row['starred'] = 0
            metadata[index] = target_row
            save_metadata_file(user, metadata=metadata)
            status = {'internal_status': 0}
            break
    if status is None:
        return {'internal_status': 1, 'message': 'No file found with that name.'}
    return status
    

def grab_path_by_id(user, id):
    metadata = grab_client_file_metadata(user)
    file_info = None
    for row in metadata:
        if row['id'] == id:
            file_info = row
            break
    return file_info['path']


def check_if_file_exists(metadata, parent_id, name):
    if len(metadata) == 0:
        return False
    for row in metadata:
        if row['parent_id'] == parent_id and row['filename'] == name:
            return True
    return False


def create_new_folder(user, parent_id, name):
    status = {'internal_status': 0}
    metadata = grab_client_file_metadata(user)
    try:
        file_exist = check_if_file_exists(metadata, parent_id, name)
        if not file_exist:
            if parent_id == 'root':
                # create path
                store_path = os.path.join(users_top_level_directory, user, 'root', name)
                # build directory
                os.mkdir(store_path)
                # build obj for metadata
                folder_json_obj = {
                    'id': secrets.token_hex(32),
                    'parent_id': 'root',
                    'filename': name,
                    'path': store_path,
                    'last_modified': datetime.now(TZ).strftime("%m/%d/%Y, %H:%M:%S"),
                    'number_of_children': 0,
                    'file_size': '-',
                    'tags': [],
                    'starred': 0,
                    'type': 'folder'
                }
            else:
                for index, row in enumerate(metadata):
                    if row['id'] == parent_id:
                        parent_row = row
                        metadata[index]['number_of_children'] += 1
                        break
                
                # create path        
                store_path = os.path.join(parent_row['path'], name)
                # build directory
                os.mkdir(store_path)
                # build obj for metadata
                folder_json_obj = {
                    'id': secrets.token_hex(32),
                    'parent_id': parent_row['id'],
                    'filename': name,
                    'path': store_path,
                    'last_modified': datetime.now(TZ).strftime("%m/%d/%Y, %H:%M:%S"),
                    'number_of_children': 0,
                    'file_size': '-',
                    'tags': [],
                    'starred': 0,
                    'type': 'folder'
                }
            # Double checking if the id exists and changing until non-duplicate found
            id_exists = False
            for row in metadata:
                if row['id'] == folder_json_obj['id']:
                    id_exists = True
                    break
            while id_exists:
                folder_json_obj['id'] = secrets.token_hex(32)
                id_exists = False
                for row in metadata:
                    if row['id'] == folder_json_obj['id']:
                        id_exists = True
                        break
            metadata.append(folder_json_obj)
            save_metadata_file(user, metadata)
        else:
            status = {'internal_status': 1, 'message': 'File already exists.'}
    except:
        status = {'internal_status': 1, 'message': 'Failed to create folder. Please try again.'}
    return status


def grab_specific_content(user, id):
    starred_folders = []
    starred_files = []
    target_folders = []
    target_files = []
    metadata = grab_client_file_metadata(user)
    for row in metadata:
        # Grab starred content
        if row['starred']:
            if row['type'] == 'folder':
                starred_folders.append({'filename': row['filename'], 'id': row['id'], 'type': row['type']})
            elif row['type'] == 'file':
                starred_files.append({'filename': row['filename'], 'id': row['id'], 'type': row['type']})
        
        # Grab target rows
        if row['parent_id'] == id:
            if row['type'] == 'folder':
                target_folders.append(row)
            else:
                target_files.append(row)
    target_objects = target_folders + target_files

    # Building the path object
    display_path_objects = []
    p_id = id
    while p_id != 'root':
        for row in metadata:
            if row['id'] == p_id:
                if len(display_path_objects) == 0:
                    last = True
                else:
                    last = False
                display_path_objects.insert(0, {'filename': row['filename'], 'url': '/files/'+row['id'], 'last': last})
                p_id = row['parent_id']
    display_path_objects.insert(0, {'filename': 'Root', 'url':'/files/root', 'last': False})
    starred_folders += starred_files

    return display_path_objects, starred_folders, target_objects


def delete_folder(user, ids):
    metadata = grab_client_file_metadata(user)
    failed_to_delete = 0
    indexes_to_delete = []
    parent_ids = []
    for index, row in enumerate(metadata):
        for id in ids:
            if row['id'] == id:
                if row['number_of_children'] == 0:
                    parent_ids.append(row['parent_id'])
                    try:
                        indexes_to_delete.append(index)
                        if row['type'] == 'folder':
                            os.rmdir(row['path'])
                        else:
                            # delete file
                            os.remove(row['path'])
                            # delete vectorized version
                            vectorized_path = os.path.join(users_top_level_directory, user, 'vectorized', f'{row["id"]}.json')
                            os.remove(vectorized_path)
                            chat_directory_path = os.path.join(users_top_level_directory, user, 'chat_history', f'{row["id"]}.json')
                            os.remove(chat_directory_path)
                        
                    except:
                        continue
                else:
                    failed_to_delete += 1
    if len(indexes_to_delete) != 0:
        for idx in indexes_to_delete[::-1]:
            metadata.pop(idx)
        for id in parent_ids:
            for index, row in enumerate(metadata):
                if row['id'] == id:
                    metadata[index]['number_of_children'] -= 1
        save_metadata_file(user, metadata)
    if failed_to_delete > 0:
        if len(indexes_to_delete) > 0:
            # Failed on some but not all
            return {'message': 'Some of the selected folders are not empty. Please empty them before deletion.', 'internal_status': 1} 
        # Failed on all
        return {'message': "The selected folders are not empty. Please empty them before deletion.", 'internal_status': 2}
    # Failed on None
    return {'internal_status': 0}


def create_new_file(user, metadata, parent_id, file, tag):
    if parent_id == 'root':
        store_path = os.path.join(users_top_level_directory, user, 'root', file.filename)
    else:
        for index, row in enumerate(metadata):
            if row['id'] == parent_id:
                parent_row = row
                metadata[index]['number_of_children'] += 1
                break
        store_path = os.path.join(parent_row['path'], file.filename)
    
    # Create metadata json obj
    file_json_obj = {
        'id': secrets.token_hex(32),
        'parent_id': parent_id,
        'filename': file.filename,
        'path': store_path,
        'last_modified': datetime.now(TZ).strftime("%m/%d/%Y, %H:%M:%S"),
        'number_of_children': 0,
        'tag': tag,
        'starred': 0,
        'type': 'file'
    }
    id_exists = False
    for row in metadata:
        if row['id'] == file_json_obj['id']:
            id_exists = True
            break
    while id_exists:
        file_json_obj['id'] = secrets.token_hex(32)
        id_exists = False
        for row in metadata:
            if row['id'] == file_json_obj['id']:
                id_exists = True
                break
    metadata.append(file_json_obj)
    save_metadata_file(user, metadata)

    # Save file
    try:
        file.save(store_path)
        return {'internal_status':0 ,'file_json_obj': file_json_obj}
    except:
        delete_folder([file_json_obj['id']])
        return {'internal_status': 1}


def upload_file(user, parent_id, file, questionnaire_choice, source, k_similar, prompt, hallucination_prompt):
    try:
        metadata = grab_client_file_metadata(user)
        file_exists = check_if_file_exists(metadata, parent_id, file.filename)
        if file_exists:
            # file exists
            return {'internal_status': 1, 'message': 'File already exists.'}
        else:
            if questionnaire_choice != 'no_questionnaire':
                _q_choice = grab_specific_questionnaire(user, questionnaire_choice, source)[0]
                file_json_obj = create_new_file(user, metadata, parent_id, file, _q_choice) 
            else:
                file_json_obj = create_new_file(user, metadata, parent_id, file, questionnaire_choice)
    except Exception as e:
        print(e)
        return {'internal_status': 1, 'message': 'Upload failed! Please try again.'}
    
    try:
        if file_json_obj['internal_status'] == 0:
            file_json_obj = file_json_obj['file_json_obj']
            batched_document = pdf2batches(file_json_obj['path'])
            if batched_document['internal_status'] == 0:
                batched_document = batched_document['batches']
                vectorized = vectorize_batches(batched_document)
                if vectorized['internal_status'] == 0:
                    vectorized = vectorized['vectors']
                    save_batch_vector_path = os.path.join(users_top_level_directory, user, 'vectorized', f'{file_json_obj["id"]}.json')
                    save_batch_vector_pair(save_batch_vector_path, batched_document, vectorized)
                    if questionnaire_choice == 'no_questionnaire':
                        save_chat_history(user, file_json_obj['id'], [])
                        return {'message': 'Upload successful!' ,'internal_status': 0}            
                    else:
                        try:
                            if source == 'preset':
                                questions = grab_preset_questions(questionnaire_choice)
                            else:
                                # custom quest...
                                questions = grab_questionnaire_questions(user, questionnaire_choice)
                            date_today = datetime.now(TZ).strftime("%m/%d/%Y, %H:%M:%S")
                            qa = []
                            for question in questions:
                                answer = custom_rag(user, question['question'], k_similar, prompt, file_json_obj['id'], hallucination_prompt, True)
                                qa.append({
                                    "timestamp": date_today,
                                    "question": question['question'],
                                    "answer": answer
                                })
                            save_chat_history(user, file_json_obj['id'], qa)
                            return {'message': 'Upload successful!' ,'internal_status': 0}            
                        except:
                            # backtrack and delete
                            delete_folder(user, [file_json_obj['id']])
                            return {'internal_status': 1, 'message': 'Upload failed! Please try again.'}
        delete_folder(user, [file_json_obj['id']])
        return {'internal_status': 1, 'message': 'Upload failed! Please try again.'}
    except:
        delete_folder(user, [file_json_obj['id']])
        return {'internal_status': 1, 'message': 'Upload failed! Please try again.'}


# ----------------------------------------------------------------------------------------------
#         RAG RELATED
# ----------------------------------------------------------------------------------------------
def pdf2batches(path):
    def remove_new_lines(text):
        text = text.replace('\n', ' ')
        text = text.replace('\\n', ' ')
        text = text.replace('  ', ' ')
        text = text.replace('  ', ' ')
        return text

    try:
        tokenizer = tiktoken.get_encoding('cl100k_base')
        pdf_document = fitz.open(path)
        pdf_text = ''

        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            text = page.get_text("text")
            text = remove_new_lines(text)
            pdf_text += text
        pdf_document.close()
        pdf_text = pdf_text.split('. ')
        

        batches = []
        chunk = ''
        chunk_tokens = 0
        max_tokens = 500
        token_lengths = []
        for line in pdf_text:
            line_tokens = len(tokenizer.encode(line))
            if chunk_tokens + line_tokens >= max_tokens:
                if chunk_tokens + line_tokens >= 1.75*max_tokens:
                    token_lengths += [chunk_tokens, line_tokens]
                    # Hit the token limit
                    batches.append(chunk)
                    batches.append(line+'.')
                    chunk = ''
                    chunk_tokens = 0
                else:
                    token_lengths.append(chunk_tokens + line_tokens)
                    # Hit the token limit
                    chunk += f'. {line}.'
                    batches.append(chunk)
                    chunk = ''
                    chunk_tokens = 0
            else:
                if len(chunk) == 0:
                    chunk += line
                else:
                    chunk += f'. {line}'
                chunk_tokens += line_tokens + 1
        if chunk_tokens != 0:
            chunk += '.'
            batches.append(chunk)
        
        empty_batch = []
        for index, batch in enumerate(batches):
            if len(batch) == 0:
                empty_batch.append(index)
        if empty_batch:
            for i in empty_batch[::-1]:
                batches.pop(i)

        return {'internal_status': 0, 'batches': batches}
    except:
        return {'internal_status': 1}
    

def vectorize_batches(batches):
    try:
        vectors = openai.Embedding.create(input=batches, engine='text-embedding-ada-002')
        # embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        # vectors = embed_model.encode(batches).tolist()
        vectors = [v['embedding'] for v in vectors['data']]
        return {'internal_status':0, 'vectors': vectors}
    except Exception as e:
        print(e)
        return {'internal_status':1}


def save_batch_vector_pair(path, batches, vectors):
    json_obj = {'batches': batches, 'vectors': vectors}
    with open(path, 'w') as f:
        json.dump(json_obj, f)


def grab_batch_vector_pair(user, id):
    target_path = os.path.join(users_top_level_directory, user, 'vectorized', f'{id}.json')
    with open(target_path, 'r') as f:
        data = json.load(f)
    return data


def custom_rag(user, question, k_similar, prompt, document_id, hallucination_prompt, from_upload=False):

    def store_qa(user, document_id, question, answer):
        date_today = datetime.now(TZ).strftime("%m/%d/%Y, %H:%M:%S")
        obj = {'timestamp': date_today, 'question': question, 'answer': answer}
        chat_history = load_chat_history(user, document_id)
        chat_history.append(obj)
        save_chat_history(user, document_id, chat_history)


    def load_vectorized_pdf(user, document_id) -> torch.tensor:
        pdf_vectorized = grab_batch_vector_pair(user, document_id)
        pdf_vectorized['vectors'] = torch.tensor(pdf_vectorized['vectors'])
        return pdf_vectorized

    def batch_cosine_similarity(question, context) -> torch.Tensor:
        return (context @ question).view(1, context.shape[0]).squeeze() / (torch.norm(context, dim=1) * torch.norm(question))

    def top_k_similar(k_similar: int, similarity_scores: torch.tensor) -> list:
        _, top_indices = torch.topk(similarity_scores, k_similar)
        return top_indices.tolist()

    def embed_question(question) -> torch.tensor:
        embedded_q = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']
        # embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        # embedded_q = embed_model.encode(question).tolist()
        
        return torch.tensor(embedded_q)
    
    def prompt_llm(prompt, question, hallucation_context, hallucination_prompt):
        messages = [
            {
                'role': 'system',
                'content': prompt
            },
            {
                'role': 'user',
                'content': question
            }
        ]
        try:
            response = openai.Completion.create(
                prompt=prompt,
                temperature=0,
                max_tokens=MAX_TOKENS,
                model='gpt-3.5-turbo-instruct'
            )
            llm_response = response['choices'][0]['text'].strip()
            hallucination_prompt = hallucination_prompt.format(context=hallucation_context,response=llm_response)
            hallucation_response = openai.Completion.create(
                prompt=hallucination_prompt,
                temperature=0,
                max_tokens=MAX_TOKENS,
                model='gpt-3.5-turbo-instruct'
            )
            hallucation_response = hallucation_response['choices'][0]['text'].strip()
            if hallucation_response.lower() == "yes":
                return "My apologies! I could not find any information in the document that was relevant to your question. Please rephrase your question or ask another one."
            return llm_response
        except Exception as e:
            print(e)
            return "There was an error processing your question. Please wait 60 seconds before asking your next question."
    try:
        question_embedding = embed_question(question)
        context = load_vectorized_pdf(user, document_id)
        similarity_scores = batch_cosine_similarity(question_embedding, context['vectors'])
        if len(similarity_scores) < k_similar:
            k_similar = len(similarity_scores)
        most_similar_idxs = top_k_similar(k_similar, similarity_scores)
        context_text = [context['batches'][i] for i in most_similar_idxs]
        context_text = " ".join(context_text)
        prompt = prompt.format(context=context_text, question=question)
        llm_response = prompt_llm(prompt, question, context_text, hallucination_prompt)
        if not from_upload:
            store_qa(user, document_id, question, llm_response)
        return llm_response
    except:
        return "There was an error processing your question. Please try again."


# ----------------------------------------------------------------------------------------------
#         CHAT HISTORY RELATED
# ----------------------------------------------------------------------------------------------
def doc_chat_load_content(user, id):
    metadata = grab_client_file_metadata(user)
    starred_folders = []
    starred_files = []
    target_name = ''
    for row in metadata:
        # Grab starred content
        if row['id'] == id:
            target_name = row['filename']
        if row['starred']:
            if row['type'] == 'folder':
                starred_folders.append({'filename': row['filename'], 'id': row['id'], 'type': row['type']})
            elif row['type'] == 'file':
                starred_files.append({'filename': row['filename'], 'id': row['id'], 'type': row['type']}) 
    starred_folders += starred_files
    chat_history = load_chat_history(user, id)
    return target_name, starred_folders, chat_history


def grab_target_info_for_view_chat_history(user, id):
    metadata = grab_client_file_metadata(user)
    for row in metadata:
        if row['id'] == id:
            return row
        

def load_chat_history(user, id):
    target_path = os.path.join(users_top_level_directory, user, 'chat_history', f'{id}.json')
    with open(target_path, 'r') as f:
        data = json.load(f)
    return data


def save_chat_history(user, id, chat):
    target_path = os.path.join(users_top_level_directory, user, 'chat_history', f'{id}.json')
    with open(target_path, 'w') as f:
        json.dump(chat, f)
