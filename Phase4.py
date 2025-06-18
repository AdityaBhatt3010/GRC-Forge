# compliance_fix_frameworkwise.py
import os
import re
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from pyfiglet import figlet_format
from termcolor import colored

from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# === Load Environment ===
load_dotenv(find_dotenv())

# === Constants ===
COMPLIANCE_REPORT = "Compliance_Framework_Report.txt"
OUTPUT_FILE = "Final_Compliance_Summary.txt"
DEBUG_LOG = "Debug_Framework_Logs.txt"

# === Banner ===
def stylish_heading():
    title = figlet_format("FixSummary", font="slant", width=100)
    print(colored(title, "cyan"))

# === LLM Setup ===
def load_local_llm():
    return OllamaLLM(model="deepseek-r1:latest", temperature=0.1)

# === Read Report File ===
def load_compliance_report():
    with open(COMPLIANCE_REPORT, 'r', encoding='utf-8') as f:
        return f.read()

# === Split by === FRAMEWORK COMPLIANCE ===
def split_by_frameworks(raw_text):
    sections = re.split(r"===\s*(.*?)\s*COMPLIANCE\s*===", raw_text, flags=re.IGNORECASE)
    frameworks = {}
    for i in range(1, len(sections), 2):
        fw = sections[i].strip().upper()
        content = sections[i+1].strip()
        frameworks[fw] = content
    return frameworks

# === Clean Any <think> Tags ===
def remove_think_tags(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

# === Prompt Template for Each Framework ===
FRAMEWORK_PROMPT = """
You are a compliance analyst. Rewrite and format the following compliance findings professionally.

Instructions:
- Keep all compliant and non-compliant points.
- For each non-compliant issue, add a clear fix based ONLY on the provided text.
- Do not hallucinate or add any new points.
- Start directly with the formatted framework output. No thoughts or reasoning.

Use the format:

===
## [Framework Name] Compliance Summary

**Compliant Areas:**
- ...

**Non-Compliant Areas & Fixes:**
- [Issue]  
  💡 Fix: [Fix based only on the input]

===

Compliance Report:
{framework_chunk}
"""

def get_framework_prompt():
    return PromptTemplate(template=FRAMEWORK_PROMPT, input_variables=["framework_chunk"])

# === Main Framework-wise Execution ===
def generate_frameworkwise_summary():
    llm = load_local_llm()
    prompt = get_framework_prompt()
    chain = LLMChain(llm=llm, prompt=prompt)

    raw_text = load_compliance_report()
    frameworks = split_by_frameworks(raw_text)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as fout, open(DEBUG_LOG, "w", encoding="utf-8") as flog:
        fout.write(f"Compliance Summary Report - Generated on {datetime.now()}\n\n")
        flog.write(f"DEBUG LOG - {datetime.now()}\n{'='*60}\n\n")

        for fw_name, fw_content in frameworks.items():
            print(f"⏳ Processing: {fw_name}")
            input_text = f"=== {fw_name} COMPLIANCE ===\n{fw_content}"
            result = chain.run({"framework_chunk": input_text})

            result_clean = remove_think_tags(result)

            # Debug log full uncut output
            flog.write(f"\n=== {fw_name} ===\n{result_clean}\n{'-'*60}\n")

            # Append cleaned output to final report
            fout.write(result_clean + "\n\n")
            print(f"✅ Done: {fw_name}")

    print("\n📄 Final full report saved to:", OUTPUT_FILE)
    print("🪵 Debug log with raw DeepSeek output saved to:", DEBUG_LOG)
    
stylish_heading()
generate_frameworkwise_summary()