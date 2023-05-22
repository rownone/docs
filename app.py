from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper, ServiceContext
from langchain import OpenAI
import sys
import os


from IPython.display import Markdown, display


def construct_index(directory_path):
    # set maximum input size
    max_input_size = 4096
    # set number of output tokens
    num_outputs = 2000
    # set maximum chunk overlap
    max_chunk_overlap = 20
    # set chunk size limit
    chunk_size_limit = 600 

    # define prompt helper
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)

    # define LLM
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name="text-davinci-003", max_tokens=num_outputs))
 
    documents = SimpleDirectoryReader(directory_path).load_data()
    
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)

    index.save_to_disk('index.json')

    return index

def ask_ai():
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    while True: 
        query = input("What do you want to ask? ")
        response = index.query(query)
        print(response)
        
os.environ["OPENAI_API_KEY"] = ''

construct_index("")


def has_question_mark(string):
    if string[-1] == '?':
        return True
    else:
        return False

#ask_ai();

index = GPTSimpleVectorIndex.load_from_disk('index.json')

Q1 = "What do you like to do in your free time?"

#AI: What do you like to do in your free time? \n
#Human: Play guitar
#AI:"

from flask import Flask, jsonify, request
from flask_cors import CORS

from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

CORS(app)

@app.route('/', methods=['GET'])
def answer():
    #args = request.args
    #q = args.get("q") 
    return jsonify({'message': 'Please post question'})

@app.route('/history', methods=['POST'])
def history():
    uid = request.form.get('uid');
    domain = 'contrib.com';
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT user_chat, ai_answer FROM contrib_ai_app WHERE userid = %s AND domain= %s ORDER BY id ASC", (uid,domain))
    messages = cursor.fetchall()
    
    return jsonify({'messages': messages,'intro':""})
    
@app.route('/ask', methods=['POST'])
def ask():
    uid = request.form.get('uid');
    question = request.form.get('q');
    prev = request.form.get('prev');
    domain = 'contrib.com';
    if question:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM contrib_ai_app WHERE userid = %s AND domain= %s", (uid,domain))
        messages = cursor.fetchall()
        
        chat_msg = ''
        if messages:
            for row in messages:
                user_chat = row['user_chat']
                ai_answer = row['ai_answer']
                chat_msg = chat_msg+"Human: "+user_chat+"\n"+"AI: "+ai_answer+"\n"
        
        question = question.replace('"', '\\"')
        raw_question = question;
        if prev:
            #prev = chat_msg
            convo = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly. \n\nAI: "+prev+"\nHuman: "
        else:
            convo = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly. \n\nAI: "+Q1+"\nHuman: "
        
        question = convo+question+"\nAI: "
        print('Convo: '+question)
                
        response = index.query(question)
        
        print('Answer: '+response.response)
        
        datetime_created = datetime.now()
        
        cursor.execute("INSERT INTO contrib_ai_app (datetime_created, domain, userid, user_chat, ai_answer) VALUES (%s, %s, %s, %s, %s)", (datetime_created, domain, uid, raw_question, response.response))
        mysql.connection.commit()
        mid = cursor.lastrowid
        cursor.close()
        #if has_question_mark(response.response):
        return jsonify({'message': response.response,'question':'','mid':mid})
        #else:
            # newq = index.query("Make a question about this conversation '"+response.response+"'")
            #newq = index.query("Ask question about this conversation '"+response.response+"'")
           
            # subject = index.query("What is the subject of this '"+response.response+"'")
            
            # newquestion = index.query("Create a short question base on this conversation '"+subject.response+"'")
            
            #return jsonify({'message': response.response+" "+newq.response,'question':newq.response})
        
        
    else:
        return jsonify({'message': 'What do you want to ask?'})
    
if __name__ == '__main__':
    #app.run(debug=True)
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)