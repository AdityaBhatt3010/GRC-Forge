import re
from collections import defaultdict
import json

with open("Compliance_Framework_Report.txt", "r", encoding="utf-8") as f:
    data = f.read()

KEY_MAPPING = {
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
}

CLAUSE_PATTERNS = [
    r"Art\.?\s*\d+(\.\d+)*",
    r"Article\s+\d+(\.\d+)*",
    r"\d{3}\.\d+",
    r"A\.\d+",
    r"CC\d\.\d",
    r"\d+\.\d+\.\d+",
    r"Req\s?\d+(\.\d+)?",
    r"Requirement\s+\d+(\.\d+)?",
    r"Section\s+\d+,\s*Clause\s+\d+\.\d+"
]
CLAUSE_REGEX = re.compile(r"\(?(" + "|".join(CLAUSE_PATTERNS) + r")\)?", flags=re.IGNORECASE)

def normalize_refs(text):
    text = re.sub(r"(Article|Art\.?)\s+(\d+(\.\d+)*)", r"Art. \2", text, flags=re.IGNORECASE)
    text = re.sub(r"Requirement\s+(\d+(\.\d+)*)", r"Req \1", text, flags=re.IGNORECASE)
    text = re.sub(r"Section\s+(\d+),\s*Clause\s+(\d+\.\d+)", r"Section \1, Clause \2", text, flags=re.IGNORECASE)
    return text

def extract_keywords(text):
    found = set()
    for phrase, short in KEY_MAPPING.items():
        if phrase.lower() in text.lower():
            found.add(short)
    return found

def extract_clauses(text):
    return set(m.group(1).strip() for m in CLAUSE_REGEX.finditer(text))

def ensure_not_empty(clauses, block, prefix):
    return clauses or {prefix + "_" + str(abs(hash(block)) % 10000)}

def parse_section(framework, block):
    block = normalize_refs(block)
    compliant_text = block.split("Non-compliant")[0]
    noncompliant_text = block.split("Non-compliant")[-1] if "Non-compliant" in block else ""
    compliant = extract_clauses(compliant_text) | extract_keywords(compliant_text)
    noncompliant = extract_clauses(noncompliant_text) | extract_keywords(noncompliant_text)
    compliant = ensure_not_empty(compliant, compliant_text, "COMP")
    noncompliant = ensure_not_empty(noncompliant, noncompliant_text, "NONCOMP")
    compliant -= noncompliant
    return sorted(compliant), sorted(noncompliant)

sections = re.split(r"===\s+(.*?)\s+COMPLIANCE\s+===", data)
framework_blocks = dict(zip(sections[1::2], sections[2::2]))
compliant_clauses = defaultdict(list)
non_compliant_clauses = defaultdict(list)

for fw, block in framework_blocks.items():
    fw_key = fw.strip().replace(" ", "_").replace("-", "_")
    comp, noncomp = parse_section(fw, block)
    compliant_clauses[fw_key] = comp
    non_compliant_clauses[fw_key] = noncomp

with open("New.py", "w", encoding="utf-8") as f:
    f.write("compliant_clauses = ")
    json.dump(compliant_clauses, f, indent=4)
    f.write("\n\nnon_compliant_clauses = ")
    json.dump(non_compliant_clauses, f, indent=4)