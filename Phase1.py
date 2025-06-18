# Imports and Environment Setup
import os
from dotenv import load_dotenv, find_dotenv
from pyfiglet import figlet_format
from termcolor import colored

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# Load Environment Variables
load_dotenv(find_dotenv())

# Constants
DB_FAISS_PATH = "vectorstore/db_faiss"
DATA_PATH = "data/"
HF_TOKEN = os.environ.get("HF_TOKEN")

# Heading Banner
def stylish_heading():
    title = figlet_format("HackerBot", font="starwars", width=1000)
    print(colored(title, "green"))

# Load local Ollama model
def load_local_llm():
    return OllamaLLM(model="mistral", temperature=0.1)

# Compliance Prompt (for plain text)
CUSTOM_PROMPT_TEMPLATE = """
You are a SOC 2 compliance auditor.

Your job is to extract all sections or lines related to:
- Security controls
- Risk management
- Access control
- Data protection
- Audit logs
- Incident response
- Employee vetting and training
- Vendor/third-party management
- Physical security

Only extract the relevant statements and policies exactly as described. 
DO NOT summarize. DO NOT add commentary. 
Output must be plaintext only.

Context: {context}
"""

# Set Prompt Template
prompt_template = PromptTemplate(
    template=CUSTOM_PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

# Load PDFs
def load_pdf_files(data):
    loader = DirectoryLoader(data, glob='*.pdf', loader_cls=PyPDFLoader)
    return loader.load()

documents = load_pdf_files(DATA_PATH)

# Chunking PDF Text
def create_chunks(extracted_data):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(extracted_data)

text_chunks = create_chunks(documents)

# Embedding Model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Vector Store
db = FAISS.from_documents(text_chunks, embedding_model)
db.save_local(DB_FAISS_PATH)

# Load Vector Store
db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)

# Embedding Model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load FAISS Vector Store
db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)

# QA Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=load_local_llm(),
    chain_type="stuff",
    retriever=db.as_retriever(search_kwargs={'k': 10}),
    return_source_documents=True,
    chain_type_kwargs={'prompt': prompt_template},
    input_key="question"
)

stylish_heading()

# Query
query = "Extract all compliance and security-related information in text"

# Run Chain
try:
    response = qa_chain.invoke({'question': query})
    result_text = response['result']
    print(f"\nExtracted Info:\n{result_text}\n")

    # Save as .txt
    output_path = "Given_Compliance.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result_text.strip())

    print(f"Data saved to '{output_path}'")

except Exception as e:
    print("Error while processing:", e)
