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
        
os.environ["OPENAI_API_KEY"] = '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'

construct_index("/home/ubuntu/docs/data")


        

#ask_ai();

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def answer():
    args = request.args
    q = args.get("q")
    
    if q:
        index = GPTSimpleVectorIndex.load_from_disk('index.json')
        response = index.query(q)
        #print(response)
            
        return jsonify({'message': response.response})
    else:
        return jsonify({'message': 'Pls enter question'})



if __name__ == '__main__':
    #app.run(debug=True)
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)