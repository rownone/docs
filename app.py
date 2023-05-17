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

construct_index("/home/ubuntu/docs/data/")


def has_question_mark(string):
    if string[-1] == '?':
        return True
    else:
        return False

#ask_ai();

index = GPTSimpleVectorIndex.load_from_disk('index.json')

Q1 = "What do you like to do in your free time?"

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

@app.route('/', methods=['GET'])
def answer():
    #args = request.args
    #q = args.get("q") 
    print('hello')
    return jsonify({'message': 'Please post question'})


@app.route('/ask', methods=['POST'])
def ask():
   
    question = request.form.get('q');
    prev = request.form.get('prev');
    if question:
        question = question.replace('"', '\\"')
        if prev:
            convo = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly. \n\nAI: "+prev+"\nHuman: "
        else:
            convo = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly. \n\nAI: "+Q1+"\nHuman: "
        question = convo+question+"\nAI: "
        print('Convo: '+question)
        
        #return jsonify({'message': question})

        #if has_question_mark(question):
            #print('A question')
            #question = 'The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly. '+
        #else:
            #print('An answer')
        
        response = index.query(question)
        
        print('Answer: '+response.response)
        
        #print(has_question_mark(response.response))
        
        if has_question_mark(response.response):
            return jsonify({'message': response.response,'question':''})
        else:
            # newq = index.query("Make a question about this conversation '"+response.response+"'")
            newq = index.query("Ask question about this conversation '"+response.response+"'")
            print('New Question: '+newq.response);
            
            # subject = index.query("What is the subject of this '"+response.response+"'")
            
            # print('Subject: '+subject.response)
            
            # newquestion = index.query("Create a short question base on this conversation '"+subject.response+"'")
            
            # print('New Question: '+newquestion.response)
             
            return jsonify({'message': response.response+" "+newq.response,'question':newq.response})
        
        
    else:
        return jsonify({'message': 'What do you want to ask?'})
    
if __name__ == '__main__':
    #app.run(debug=True)
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)