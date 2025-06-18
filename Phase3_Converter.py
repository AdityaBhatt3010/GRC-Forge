import os
from dotenv import load_dotenv, find_dotenv
import requests


# Load Environment Variables
load_dotenv(find_dotenv())

COHERE_API_KEY = os.environ.get("COHERE_API_KEY")

def generate_clause_data():
    url = "https://api.cohere.ai/generate"
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Load contents from file
    with open("Compliance_Framework_Report.txt", "r", encoding="utf-8") as file:
        report_content = file.read()

    # Strict no-hallucination, compact-label prompt
    prompt = f"""
You are a strict compliance auditor. Based ONLY on the text below (no assumptions), extract framework-wise compliant and non-compliant clauses.

Format: Return only Python-compatible output like below:
- Include **only the article number or section ID** in parentheses if available. Do NOT include full descriptions.
- If no official clause/article ID is available, use one of the following abbreviations:

    # Clause Short Form Mapping Key
    KEY_MAPPING = {{
    "Incident Response": "IR",
    "Data Protection Officer": "DPO",
    "Consent": "CNSNT",
    "Audit Logs": "LOG",
    "Background Checks": "BGCHK",
    "Physical Security": "PHYSEC",
    "Encryption": "ENC",
    "Access Control": "AC",
    "Network Security": "NETSEC",
    "Surveillance": "SRV",
    "Role-Based Access Control": "RBAC",
    "Training": "TRN",
    "Risk Management": "RM",
    "Documented Info": "DOCINF",
    "Media Handling": "MEDH"
    }}

Use the key if a clause is mentioned without an official reference.

Strictly use only the actual clause names and IDs found in the report. Do not hallucinate.

Return in this format:

compliant_clauses = {{
    "ISO 27001": ["(4.2.2.2)", "(10.6.2)", "(8.2.2)", ...],
    "HIPAA": ["(164.312)"],
    "GDPR": ["(Art. 32)", "(Art. 24)"],
    "PCI DSS": ["(Req 3)", "(Req 1)", "RBAC", "(10.6)", "requirement 1.1 (Control 1.2)", "Control 1.2], 
    "NIST 800-53": ["(SI-3)", "(AU-3)", "(AC-3)"],
    "SOC2": ["CC6.5", "NETSEC", "RBAC"... ], 
    "SOX": ["Section 404, Clause 404.2", ...]
}}

non_compliant_clauses = {{
    "ISO 27001": ["(4.2.2.2)", "(10.6.2)", "(8.2.2)", ...],
    "HIPAA": ["(164.312)"],
    "GDPR": ["(Art. 32)", "(Art. 24)"],
    "PCI DSS": ["(Req 3)", "(Req 1)", "RBAC", "(10.6)", "requirement 1.1 (Control 1.2)", "Control 1.2], 
    "NIST 800-53": ["(SI-3)", "(AU-3)", "(AC-3)"],
    "SOC2": ["CC6.5", "NETSEC", "RBAC"... ], 
    "SOX": ["Section 404, Clause 404.2", ...]
}}


=== Report Begins ===
{report_content}
=== Report Ends ===
"""


    body = {
        "model": "command-r-08-2024",
        "prompt": prompt,
        "max_tokens": 20000,
        "temperature": 0.1,
        "k": 0,
        "p": 1.0,
        "frequency_penalty": 0.3,
        "presence_penalty": 0.3,
        "stop_sequences": []
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        result = response.json()
        output_text = result.get("text", "[No text returned]").strip()

        # Save to file
        with open("Clauses_Clean.py", "w", encoding="utf-8") as out_file:
            out_file.write(output_text)

        print("✅ Output saved to 'Clauses_Clean.py'")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

# Run it
generate_clause_data()