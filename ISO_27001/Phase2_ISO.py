# iso27001_compliance_check.py

import os
import json
import csv

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

# === ENVIRONMENT ===
load_dotenv(find_dotenv())

# Paths
RULESET_PATH = "dataset/ISO27001_Updated.json"
VECTORSTORE_PATH = "vector_ISO"
INPUT_FILE = "Given_Compliance.txt"
OUTPUT_CSV = "ISO_27001_Summary.csv"

HF_TOKEN = os.environ.get("HF_TOKEN")

# === Heading ===
def stylish_heading():
    title = figlet_format("ISO27001 Check", font="slant", width=120)
    print(colored(title, "cyan"))

# === Load LLM & Embeddings ===
def load_local_llm():
    return OllamaLLM(model="mistral", temperature=0.1)

def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

embedding_model = get_embedding_model()

# === Create Vector DB for ISO27001 JSON ===
def create_iso27001_vectors():
    loader = JSONLoader(
        file_path=RULESET_PATH,
        jq_schema=".",           # Load entire JSON tree
        text_content=False
    )
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    db = FAISS.from_documents(chunks, embedding_model)
    os.makedirs(VECTORSTORE_PATH, exist_ok=True)
    db.save_local(VECTORSTORE_PATH)
    print("✅ Vector store created and saved.")

# === Load vector store ===
def load_vector_store():
    return FAISS.load_local(VECTORSTORE_PATH, embedding_model, allow_dangerous_deserialization=True)

# === Load Given Compliance Text ===
def load_given_compliance_txt():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return f.read()

# === Load ISO27001 JSON into native objects ===
def load_iso27001_controls():
    with open(RULESET_PATH, "r", encoding="utf-8") as f:
        iso_data = json.load(f)

    controls_list = []
    for domain in iso_data["domains"]:
        for ctrl in domain["controls"]:
            controls_list.append({
                "ref": ctrl["ref"],
                "title": ctrl["title"],
                "summary": ctrl["summary"],
                "ToD": ctrl.get("ToD_ISO_27001", ""),
                "ToE": ctrl.get("ToE_ISO_27002", "")
            })

    return controls_list

# === Prompt Template for Compliance Status ===
COMPLIANCE_CHECK_PROMPT = """
You are an ISO27001 compliance analyst.

Given the following text extracted from a SOC 2 report:

SOC2_CONTEXT:
{context}

And the following ISO27001 control clause:

CONTROL_CLAUSE:
{question}

Determine if the SOC 2 context shows that the ISO27001 control clause is:

- Compliant
- Partially Compliant
- Non-Compliant

Respond with only one word: "Compliant", "Non-Compliant" or "Partially Compliant".
"""

def set_compliance_prompt():
    return PromptTemplate(
        template=COMPLIANCE_CHECK_PROMPT,
        input_variables=["context", "question"]
    )

# === Main Compliance Check ===
def evaluate_controls_against_soc2():
    # Load context text from SOC2
    soc2_text = load_given_compliance_txt()

    # Load controls
    controls = load_iso27001_controls()

    # Load vector DB
    db = load_vector_store()

    llm = load_local_llm()

    # Prepare QA Chain
    prompt_template = set_compliance_prompt()

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={'k': 3}),
        return_source_documents=False,
        chain_type_kwargs={'prompt': prompt_template},
        input_key="question"
    )

    rows = []

    for ctrl in controls:
        question_text = f"Clause {ctrl['ref']} - {ctrl['title']}. Description: {ctrl['summary']}. How compliant is this in the SOC2 context above?"
        
        try:
            result = qa_chain.invoke({
                "context": soc2_text,
                "question": question_text
            })

            compliance_status = result["result"].strip()

            # If LLM returns extra text, normalize to just the expected label
            compliance_status = compliance_status.lower()
            if "compliant" in compliance_status and "partial" in compliance_status:
                compliance_status = "Partially Compliant"
            elif "non" in compliance_status:
                compliance_status = "Non-Compliant"
            elif "partial" in compliance_status:
                compliance_status = "Partially Compliant"
            elif "compliant" in compliance_status:
                compliance_status = "Compliant"
            else:
                compliance_status = "Unknown"

        except Exception as e:
            print(f"❌ Error on control {ctrl['ref']} - {ctrl['title']}: {e}")
            compliance_status = "Error"

        rows.append({
            "Control_Name": f"{ctrl['ref']} - {ctrl['title']}",
            "Control_Description": ctrl["summary"],
            "Audit_Steps_ToD": ctrl["ToD"],
            "Evidence_ToE": ctrl["ToE"],
            "Compliance_Status": compliance_status
        })

    # Write CSV
    with open(OUTPUT_CSV, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = [
            "Control_Name",
            "Control_Description",
            "Audit_Steps_ToD",
            "Evidence_ToE",
            "Compliance_Status"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Compliance check complete. CSV saved as {OUTPUT_CSV}")

# === Entry Point ===
if __name__ == "__main__":
    stylish_heading()

    # Create the vector store only the first time
    if not os.path.exists(os.path.join(VECTORSTORE_PATH, "index.faiss")):
        create_iso27001_vectors()

    evaluate_controls_against_soc2()