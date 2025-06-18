# Phase 2: Compliance Check against Frameworks
import os
from dotenv import load_dotenv, find_dotenv
from pyfiglet import figlet_format
from termcolor import colored

from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# === Environment Setup ===
load_dotenv(find_dotenv())

# === Constants ===
RULESET_PATH = "dataset/"
RULE_VSTORE_PATH = "vectorstore2"
INPUT_FILE = "Given_Compliance.txt"
HF_TOKEN = os.environ.get("HF_TOKEN")

# === Heading ===
def stylish_heading():
    title = figlet_format("ComplianceCheck", font="slant", width=100)
    print(colored(title, "cyan"))

# === Load LLM & Embeddings ===
def load_local_llm():
    return OllamaLLM(model="mistral", temperature=0.1)

def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

embedding_model = get_embedding_model()

# === Step 1: Create Vector DBs for Each Framework ===
def create_framework_vectors():
    for fname in os.listdir(RULESET_PATH):
        if fname.endswith(".json"):
            path = os.path.join(RULESET_PATH, fname)
            loader = JSONLoader(file_path=path, jq_schema=".", text_content=False)
            docs = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_documents(docs)
            vstore = FAISS.from_documents(chunks, embedding_model)
            framework_name = fname.replace(".json", "")
            vstore.save_local(os.path.join(RULE_VSTORE_PATH, framework_name))

# === Prompt Template for Comparison ===
COMPLIANCE_CHECK_PROMPT = """
You are a compliance analyst.
Compare the provided organizational compliance report with the selected security framework's rules.

Task:
- Identify which parts are compliant.
- Flag non-compliant or missing areas.
- Mention clause numbers (in brackets) when possible.
- Respond in plain English without bullet points or repetition.

Compliance Text:
{context}
"""

def set_comparison_prompt():
    return PromptTemplate(
        template=COMPLIANCE_CHECK_PROMPT,
        input_variables=["context"]  # ✅ must match "stuff" chain
    )

# === Step 2: Load Given Compliance Report ===
def load_given_compliance_txt():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        return f.read()

# === Step 3: Evaluate against all frameworks ===
def evaluate_compliance():
    base_text = load_given_compliance_txt()
    results = []

    for framework in os.listdir(RULE_VSTORE_PATH):
        path = os.path.join(RULE_VSTORE_PATH, framework)
        db = FAISS.load_local(path, embedding_model, allow_dangerous_deserialization=True)

        qa_chain = RetrievalQA.from_chain_type(
            llm=load_local_llm(),
            chain_type="stuff",
            retriever=db.as_retriever(search_kwargs={'k': 10}),
            return_source_documents=True,
            chain_type_kwargs={'prompt': set_comparison_prompt()},
            input_key="query"  # <- This is now aligned with .invoke({'query': ...})
        )

        try:
            response = qa_chain.invoke({'query': base_text})  # <- Fixed input key
            results.append(f"=== {framework.upper()} COMPLIANCE ===\n{response['result']}\n\n")
        except Exception as e:
            results.append(f"=== {framework.upper()} COMPLIANCE ===\nError: {e}\n\n")

    with open("Compliance_Framework_Report.txt", "w", encoding="utf-8") as f:
        f.writelines(results)

    print("\n✅ Compliance check completed. Output saved to 'Compliance_Framework_Report.txt'")

# === Execution Entry Point ===
stylish_heading()
# Uncomment only the first time
#os.makedirs(RULE_VSTORE_PATH, exist_ok=True)  # ✅ Ensure folder exists
#create_framework_vectors()
evaluate_compliance()