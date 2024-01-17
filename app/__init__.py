from flask import Flask, render_template, redirect, request, jsonify, abort, url_for, session, send_from_directory
from flask import send_file
# Autho0 Imports
from os import environ as env
import json
from . import file_database_methods

import os
import io
# from sentence_transformers import SentenceTransformer
# from transformers import AutoModelForCausalLM, AutoTokenizer
import functools

# Autho0 Imports
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv

import re
from datetime import datetime
from pytz import timezone

TZ = timezone('US/Eastern')

PROMPT = """
Your task: You are tasked with answering questions given to you based only on the context provided and no knowledge you may already have.
Rules you must follow: 
1) All answers must come from the context itself. 
2) You have no prior knowledge other than understanding text and the context that is provided to you below.
Rule regarding your response: You may reply if you have found an answer based on the context. If you have not found the answer, kindly apologize for not finding an answer.
Additional Rules:
1) Give back as much information as possible.
2) Try to be specific with your answers.
3) Do no be redundant.
4) Avoid using too many similar words or using the same words too many times.
5) Include as many quantitative details as you can find in the context that supports the answer.

Context: {context}

Question: {question}

Answer:
"""

HALLUCATION_PROMPT = """
Your task: Given two pieces of text, called context and response respectively, your job is to determine if the response was answered based on the context or if there is information in the response that could not have come from the context.
Instruction on how to reply: If and only if you are completely certain the response could NOT have come from the context, reply with "yes", otherwise reply with "no".

Context: {context}

Response: {response}

Answer:
"""

app = Flask(__name__, instance_relative_config=True)
# app = Flask(__name__)

# ----------------------------------------------------------------------------------------------
#       AUTH0 CODE
# ----------------------------------------------------------------------------------------------
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

K_SIMILAR = int(env.get("K_SIMILAR"))
app.secret_key = env.get("APP_SECRET_KEY")
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# ------------------------------
#       SIGN UP
# ------------------------------
@app.route("/sign_up")
def sign_up():
    user_agent = request.headers.get('User-Agent')
    mobile_regex = r"(iphone|ipad|android|mobile|blackberry|iemobile|opera mini|webos)"
    if re.search(mobile_regex, user_agent, re.IGNORECASE):
        return render_template('mobile_not_allowed.html')
    else:
        return oauth.auth0.authorize_redirect(screen_hint='signup', redirect_uri=url_for('callback', _external=True))


# ------------------------------
#       LOGIN
# ------------------------------
@app.route("/login")
def login():
    user_agent = request.headers.get('User-Agent')
    mobile_regex = r"(iphone|ipad|android|mobile|blackberry|iemobile|opera mini|webos)"
    if re.search(mobile_regex, user_agent, re.IGNORECASE):
        return render_template('mobile_not_allowed.html')
    else:
        return oauth.auth0.authorize_redirect(redirect_uri=url_for('callback', _external=True))


# ------------------------------
#       LOG OUT
# ------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("landing_page", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# ------------------------------
#       AUTH0 CALLBACK
# ------------------------------
@app.route('/callback', methods=['GET', 'POST'])
def callback():
    try:
        token = oauth.auth0.authorize_access_token()
        session['user_id'] = token
        return redirect('/files/root')

    except Exception as e:
        print(e)
        return abort(400)


# ----------------------------------------------------------------------------------------------
#         DECORATORS
# ----------------------------------------------------------------------------------------------
# ------------------------------
#     LOGED-IN CHECK
# ------------------------------
def login_required(view):
    def create_user_directory(user):
        user_top_level_path = os.path.join(env.get("ARQA_USERS"), user)
        os.makedirs(user_top_level_path)
        
        chat_history_path = os.path.join(user_top_level_path, 'chat_history')
        os.makedirs(chat_history_path)

        root_path = os.path.join(user_top_level_path, 'root')
        os.makedirs(root_path)

        vectorized_path = os.path.join(user_top_level_path, 'vectorized')
        os.makedirs(vectorized_path)

        questionnaires_path = os.path.join(user_top_level_path, 'questionnaires')
        os.makedirs(questionnaires_path)
        q_metadata_path = os.path.join(questionnaires_path, 'questionnaire_metadata.json')
        with open(q_metadata_path, 'w') as f:
            json.dump([], f)

        client_files_metadata_path = os.path.join(user_top_level_path, 'client_files_metadata.json')
        with open(client_files_metadata_path, 'w') as f:
            json.dump([], f)

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user_id = session.get('user_id')
        if user_id is None:
            return redirect(url_for('landing_page'))
        directory_path = os.path.join(env.get("ARQA_USERS"), user_id['userinfo']['email'])
        if not os.path.exists(directory_path):
            create_user_directory(user_id['userinfo']['email'])
        return view(**kwargs)
    return wrapped_view


# ----------------------------------------------------------------------------------------------
#         LANDING PAGE
# ----------------------------------------------------------------------------------------------
@app.route('/')
def landing_page():
    return render_template('landing_page.html')



# ----------------------------------------------------------------------------------------------
#         DIRECTORIES
# ----------------------------------------------------------------------------------------------
@app.route("/files/<id>")
@login_required
def files(id):
    user = session.get('user_id')['userinfo']['email']
    display_path, starred, targets = file_database_methods.grab_specific_content(user, id)
    presets_metadata = file_database_methods.grab_presets_metadata()
    questionnaires = file_database_methods.grab_questionnaire_metadata(user)
    return render_template('directories.html', display_path=display_path, starred=starred, targets=targets, questionnaires=questionnaires, presets_metadata=presets_metadata)

@app.route('/create_folder', methods=['POST', 'GET'])
@login_required
def create_folder():
    user = session.get('user_id')['userinfo']['email']
    if request.method == 'POST':
        id = request.json['id']
        name = request.json['name']
        status = file_database_methods.create_new_folder(user, id, name)
        return jsonify(status)

@app.route('/delete_folders', methods=['POST', 'GET'])
@login_required
def delete_content():
    user = session.get('user_id')['userinfo']['email']
    ids = request.json['ids']
    status = file_database_methods.delete_folder(user, ids)
    return jsonify(status)


@app.route('/upload_file', methods=['POST', 'GET'])
@login_required
def upload():
    start_time = datetime.now(TZ)
    user = session.get('user_id')['userinfo']['email']

    client_json = request.form['json']
    client_json = json.loads(client_json) 
    parent_id = client_json['parent_id']
    questionnaire_choice = client_json['questionnaire']
    source = client_json['source']
    uploaded_file = request.files['file']
    if not uploaded_file:
        return jsonify({'message': 'No file part', 'internal_status': 1})
    if uploaded_file.filename == '':
        return jsonify({'message': 'No selected file', 'internal_status': 1})
    if uploaded_file.mimetype != 'application/pdf':
        return jsonify({'message': 'Only PDF files are allowed.', 'internal_status': 1})
    
    status = file_database_methods.upload_file(user, parent_id, uploaded_file, questionnaire_choice, source, K_SIMILAR, PROMPT, HALLUCATION_PROMPT)
    return jsonify(status)


@app.route('/document_chat/<id>')
@login_required
def document_chat(id):
    user = session.get('user_id')['userinfo']['email']
    filename, starred, chat_history = file_database_methods.doc_chat_load_content(user, id)
    return render_template('document_chat.html', id=id, filename=filename, starred=starred, chat_history=chat_history)


# -------------------------------------------
# -------------------------------------------
# -------------------------------------------
# -------------------------------------------
@app.route('/grab_pdf/<id>')
@login_required
def grab_pdf(id):
    user = session.get('user_id')['userinfo']['email']
    pdf_path_txt = file_database_methods.grab_path_by_id(user, id)
    pdf_path = os.path.dirname(pdf_path_txt).replace("\\", "/")
    file_name = os.path.basename(pdf_path_txt)
    return send_from_directory(pdf_path, file_name)
    # return send_file(pdf_path_txt, as_attachment=True)


@app.route('/star_file', methods=['POST','GET'])
@login_required
def star_file():
    user = session.get('user_id')['userinfo']['email']
    id = request.json['ids']
    status = file_database_methods.star_unstar(user, id)
    return jsonify(status)

@app.route('/ask_question', methods=['POST', 'GET'])
@login_required
def ask_question():
    user = session.get('user_id')['userinfo']['email']
    document_id = request.json['document_id']
    question = request.json['question']
    question = question.lstrip().rstrip()
    if (question[-1] != '?'):
        question += '?'
    answer = file_database_methods.custom_rag(
        user,
        question,
        K_SIMILAR, 
        PROMPT,
        document_id,
        HALLUCATION_PROMPT)
    return jsonify(answer)


@app.route('/view_chat_history/<id>')
@login_required
def view_chat_history(id):
    user = session.get('user_id')['userinfo']['email']
    chat_history = file_database_methods.load_chat_history(user, id)
    target_info = file_database_methods.grab_target_info_for_view_chat_history(user, id)
    return render_template('view_chat_history.html', chat_history=chat_history, target_info=target_info)

# ----------------------------------------------------------------------------------------------
#         QUESTIONNAIRE RELATED
# ----------------------------------------------------------------------------------------------
@app.route("/questionnaire")
@login_required
def questionnaire():
    user = session.get('user_id')['userinfo']['email']
    starred = file_database_methods.grab_starred(user)
    questionnaires = file_database_methods.grab_questionnaire_metadata(user)
    presets = file_database_methods.grab_presets_metadata()
    return render_template('questionnaire.html', starred=starred, questionnaires=questionnaires, presets=presets)


@app.route('/create_questionnaire', methods=['POST', 'GET'])
@login_required
def create_questionnaire():
    user = session.get('user_id')['userinfo']['email']
    if request.method == 'POST':
        questionnaire_name = request.json['questionnaire_name']
        tag_color = request.json['tag_color']
        description = request.json['description'] 
        questions = request.json['questions']
        edited_questions=[]
        for q in questions:
            q = q.lstrip().rstrip()
            if q[-1] != '?':
                q += '?'
            edited_questions.append(q)
        questions = edited_questions
        status = file_database_methods.create_new_questionnaire(user, questionnaire_name, tag_color, description, questions)
        return jsonify(status)
    else:
        starred = file_database_methods.grab_starred(user)
        presets = file_database_methods.grab_presets_metadata()
        return render_template('create_questionnaire.html', starred=starred, presets=presets)
    

@app.route("/edit_questionnaire/<qid>", methods=['POST', 'GET'])
@login_required
def edit_questionnaire(qid):
    user = session.get('user_id')['userinfo']['email']
    # return the data to load the page
    questionnaire_name, tag_color, description, questions = file_database_methods.grab_specific_questionnaire(user, qid, 'custom')
    return render_template('edit_questionnaire.html', questionnaire_name=questionnaire_name, tag_color=tag_color, description=description, questions=questions)
    

@app.route("/save_edited_questionnaire", methods=['POST', 'GET'])
@login_required
def save_edited_questionnaire():
    user = session.get('user_id')['userinfo']['email']
    if request.method == 'POST':
        qid = request.json['qid']
        questionnaire_name = request.json['questionnaire_name']
        tag_color = request.json['tag_color']
        description = request.json['description'] 
        questions = request.json['questions']
        edited_questions=[]
        for q in questions:
            q = q.lstrip().rstrip()
            if q[-1] != '?':
                q += '?'
            edited_questions.append(q)
        questions = edited_questions
        status = file_database_methods.update_questionnaire(user, qid, questionnaire_name, tag_color, description, questions)
        return jsonify(status)
    else:
        starred = file_database_methods.grab_starred()
        questionnaires = file_database_methods.grab_questionnaire_metadata(user)
        return render_template('questionnaire.html', starred=starred, questionnaires=questionnaires)

    
@app.route('/delete_questionnaire', methods=['POST', 'GET'])
@login_required
def delete_questionnaire():
    user = session.get('user_id')['userinfo']['email']

    qids = request.json['qids']
    file_database_methods.delete_questionnaire(user, qids)
    status = {'internal_status': 0}
    return jsonify(status)


@app.route('/view_questionnaire/<qid>')
@login_required
def view_questionnaire(qid):
    user = session.get('user_id')['userinfo']['email']
    questionnaire_name, tag_color, description, questions = file_database_methods.grab_specific_questionnaire(user, qid, 'custom')
    return render_template('view_questionnaire.html', questionnaire_name=questionnaire_name, tag_color=tag_color, description=description, questions=questions)


# ----------------------------------------------------------------------------------------------
#         PRESETS RELATED
# ----------------------------------------------------------------------------------------------
@app.route('/view_preset/<pid>')
@login_required
def view_preset(pid):
    questionnaire_name, tag_color, description, questions = file_database_methods.grab_specific_preset(pid)
    return render_template('view_questionnaire.html', questionnaire_name=questionnaire_name, tag_color=tag_color, description=description, questions=questions)


@app.route('/load_specific_preset/<pid>')
@login_required
def load_specific_preset(pid):
    questions = file_database_methods.grab_preset_questions(pid)
    return jsonify(questions)

