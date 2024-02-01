from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from decouple import config
import google.generativeai as genai
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pdfplumber
import shutil

API_KEY = config("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-pro')

@api_view(['POST'])
def pdf_chat(request):
    if request.method == 'POST':
        session_id = request.data.get('session_id')
        pdf = request.data.get('pdf')
        prompt = request.data.get('prompt')

        text = ""

        # Parsing PDF and saving text
        with pdfplumber.open(pdf) as pd:
            for page_number in range(len(pd.pages)):
                page = pd.pages[page_number]
                text += page.extract_text()

        # Splitting the text extracted from text got from PDF
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        text_chunks = text_splitter.split_text(text)

        # Create Vector Embedding of text
        embeddings = GoogleGenerativeAIEmbeddings(google_api_key=API_KEY, model="models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)

        # Store embeddings locally
        os.makedirs('pdf_chat/embeddings/', exist_ok=True)
        vector_store.save_local(f'pdf_chat/embeddings/{session_id}_index')

        # Load saved embeddings
        user_embeddings = FAISS.load_local(f'pdf_chat/embeddings/{session_id}_index', embeddings)

        # Perform similarity search between user prompt and pdf uploaded
        docs = user_embeddings.similarity_search(prompt)

        # Prompt template to ask questions to PDF
        prompt_template = '''
                          Answer question as detailed as possible from the provided context, make sure to provide all the details.
                          If the answer is not in provided context, just say "your question's answer is not available in the PDF provided", do not provide the wrong answer\n\n
                          Context: \n{context}?\n
                          Question: \n{question}\n

                          Answer:
                          '''
        
        # Langchain model declaration
        model = ChatGoogleGenerativeAI(model='gemini-pro', temperature=0.5, google_api_key=API_KEY)
        prompting = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff", prompt=prompting)
        
        # Delete embeddings after QA
        shutil.rmtree(f'pdf_chat/embeddings/{session_id}_index')

        # Storing model answer
        response = chain({"input_documents": docs, "question": prompt}, return_only_outputs=True)

        return Response({"generated_text": response['output_text']})
