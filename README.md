# GRC-Forge 🛡️  
**AI-Powered Multi-Framework Compliance Automation Toolkit**  
Built as part of an internship at Ernst & Young (EY)

---

## 📌 Overview

**GRC-Forge** is a modular, offline-first pipeline designed to automate the compliance audit process across multiple security frameworks including SOC 2, ISO 27001, HIPAA, NIST 800-53, SOX, GDPR, and PCI DSS. It leverages local LLMs, vector embeddings, and prompt-engineered pipelines to extract, compare, classify, and visualize the compliance posture of an organization.

> This project was developed as a core deliverable during a cybersecurity internship at EY, focused on transforming static compliance reviews into scalable, AI-assisted audit workflows.

---

## Visual Pipeline

```mermaid
graph TD

%% === Phase 1: Extract Compliance Text from PDF ===
subgraph Phase_1_Compliance_Text_Extraction
    A1[SOC2 Report in data/ directory]
    A2[Load and split PDFs into chunks]
    A3[Generate embeddings with allMiniLM]
    A4[Store chunks with FAISS in vectorstore/ diectory]
    A5[Define compliance audit information extraction prompt]
    A6[Run RetrievalQA chain using finetuned Mistral via Ollama]
    A7[Extracted compliance text saved as Given_Compliance.txt]

    A1 --> A2
    A2 --> A3
    A3 --> A4
    A4 --> A6
    A5 --> A6
    A6 --> A7
end

%% === Phase 2: Framework-wise Compliance Check ===
subgraph Phase_2_Compliance_Evaluation
    B1[Load Given_Compliance.txt]
    B2[Load GDPR, HIPAA, ISO 27001, NIST 800-53, PCII DSS, SOC2 and SOX framework rules in JSON format in dataset/ directory]
    B3[Split into chunks and embed each framework via allMiniLM]
    B4[Store vectorstores via FAISS per framework in vectorstore2/ directory]
    B5[Prompt template for clause comparison]
    B6[Run RetrievalQA using finetuned Mistral via Ollama]
    B7[Write output to Compliance_Framework_Report.txt]

    B1 --> B6
    B2 --> B3
    B3 --> B4
    B4 --> B6
    B5 --> B6
    B6 --> B7
end

%% === Phase 4: Suggestive Measures for Non-Compliance (Final Fix Summary Generation) ===
subgraph Phase_4_Suggestive_Measures_FixSummary
    D1[Load Compliance_Framework_Report.txt]
    D2[Split compliance report by frameworks]
    D3[Prompt to create summary on compliant and non-compliant clauses along with suggesting measures to fix non-compliant clauses]
    D4[Run LLMChain using DeepSeek-R1 via Ollama]
    D5[Remove hallucinated <think> tags from output]
    D6[Write cleaned output to Final_Compliance_Summary.txt]
    D7[Log unfiltered raw model output to Debug_Framework_Logs.txt]

    D1 --> D2
    D2 --> D4
    D3 --> D4
    D4 --> D5
    D5 --> D6
    D4 --> D7
end

%% === Phase 3: Clause Classification and Graph ===
subgraph Phase_3_Clause_Mapping_and_Visualization
    C1[Load Compliance_Framework_Report.txt]
    C2[Strict clause mapping prompt using Cohere API]
    C3[Generate compliant and non-compliant clause dictionaries]
    C4[Save the variables in Clauses_Clean.py]
    C5[Plot radar charts using matplotlib and numpy]
    C6[Save radar chart as Compliance_Radar_Charts.png]

    C1 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> C5
    C5 --> C6
end



A7 --> B1
B7 --> C1
B7 --> D1
```

---

## ⚙️ Key Features

- Extracts security-specific clauses from long audit documents (e.g., SOC 2 PDFs)
- Benchmarks against 7+ frameworks using LangChain, FAISS, and HuggingFace embeddings
- Automatically maps compliant and non-compliant clauses
- Generates professional summaries and remediation recommendations using LLMs
- Produces radar charts for clause-level visualization
- Fully offline, containerized, and enterprise-ready

---

## 🧠 Tech Stack

- **Python 3.11**
- **LangChain**, **FAISS**, **HuggingFace** embeddings
- **Ollama + Mistral**, **DeepSeek-R1** (local LLMs)
- **Cohere API** (for clause parsing)
- **Matplotlib**, **NumPy** (visualization)
- **PowerShell (`set.ps1`)** for setup automation
- **Docker** for reproducible environments

---

## 🗂️ Directory Structure

```

GRC-Forge/
├── data/                           # Input PDFs (SOC2 reports)
├── dataset/                        # JSON rules for frameworks
├── vectorstore/, vectorstore2/     # FAISS embeddings
├── Clauses_Clean.py                # Structured compliance data
├── Compliance_Framework_Report.txt
├── Compliance_Radar_Charts.png
├── Final_Compliance_Summary.txt
├── Dockerfile                      # Containerized execution pipeline
├── set.ps1                         # PowerShell setup & automation script
├── Phase1.py → Phase4.py           # Modular pipeline scripts

````

---

## 🚀 Setup & Execution

### Option 1: Run via Docker (Recommended)

```bash
docker build -t grc-forge-auto .
docker run -it --rm -v "$PWD:/app" --network=host grc-forge-auto
````

### Option 2: Automated Setup via PowerShell (Windows)

```powershell
.\set.ps1
```

This script installs dependencies, pulls Ollama models (`mistral:instruct`, `deepseek:latest`), creates required directories, and runs all pipeline phases in order.

---

## 🔄 Pipeline Phases

| Phase       | Description                                                        |
| ----------- | ------------------------------------------------------------------ |
| **Phase 1** | Extracts compliance clauses from PDFs using RetrievalQA (Mistral)  |
| **Phase 2** | Compares extracted clauses against frameworks (FAISS + JSONLoader) |
| **Phase 3** | Maps clauses to framework identifiers and generates radar charts   |
| **Phase 4** | Produces human-readable remediation summaries using DeepSeek-R1    |

---

## 📸 Results & Screenshots

| Phase                 | Output                                                  |
| --------------------- | ------------------------------------------------------- |
| Phase 1               | ![Phase1 Output](Screenshots/Phase1_Output.png)         |
| Phase 2               | ![Phase2 Output](Screenshots/Phase2_Output.png)         |
| Phase 3 - Clauses     | ![Clauses](Screenshots/Phase3_Clauses.png)              |
| Phase 3 - Radar Graph | ![Radar](Screenshots/Phase3_GraphOutput.png)            |
| Phase 4 - Summary     | ![Fix Summary](Screenshots/Phase4_ComplianceOutput.png) |
| Phase 4 - Debug       | ![Debug](Screenshots/Phase4_DebugOutput.png)            |
| Docker Execution      | ![Docker](Screenshots/Docker.png)                       |

---

## 📈 Future Scope

* Extend support to ISO 27002, FedRAMP, CSA STAR
* Add clause confidence scoring and risk-weighted prioritization
* Secure secrets management via Docker + Vault
* Flask/FastAPI-based GUI for non-technical users
* Export summaries in SOC2 Bridge Letter or audit-ready templates
* Real-time GRC monitoring via streaming LLM APIs

---

## 👨‍💻 Author

**Aditya Bhatt**
BTech CSE | Cybersecurity | EY Intern

---
