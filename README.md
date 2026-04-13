# Pippo AI: Intelligent Legal Partner

**Bharat's Precision. Global Ambition. Intelligent World.**

Pippo AI is a next-generation, agentic intelligence engine designed to navigate the complexities of modern legal landscapes. Engineered for deep-nuance analysis, Pippo AI identifies, classifies, and audits risky clauses in contractual documents with high-fidelity precision using a hybrid ML and LLM Reasoning approach.

![Pippo AI Banner](https://raw.githubusercontent.com/Gautam-Bharadwaj/Pippo.ai/main/assets/PippoBanner.png) 
*(Note: Replace with actual asset link if available)*

---

## Core Intelligence Architecture

Pippo AI is built on a "Deep Audit" philosophy, moving beyond simple keyword matching to understanding the fundamental intent of legal prose.

- **Agentic Reasoning Engine:** Powered by `LangGraph` and `GPT-4o`, the system performs multi-step semantic verification, identifies hidden liabilities, and suggests mitigation strategies.
- **Machine Learning Layer:** A robust `RandomForest` classifier provides a probabilistic baseline for risk, trained on thousands of curated legal clauses.
- **Hybrid Scoring:** Combines data-driven ML models with logic-driven LLM agents to produce a unified "Contract DNA" risk profile.

## Features and Capabilities

### HUD-Inspired Interface
Experience a premium, high-contrast dark theme designed for focus. Featuring glassmorphism, dynamic bento-cards, and real-time scanning feedback.

### Multidimensional Extraction
- **Legal Metadata:** Automatic detection of Parties, Effective Dates, Jurisdiction, and Governing Laws.
- **Smart OCR:** Intelligent fallback to `Tesseract OCR` for scanned documents and image-heavy PDFs.
- **Clause Segmentation:** Proprietary regex-based splitting that preserves legal context.

### Risk Analytics and Export
- **Bento Dashboard:** Visual representations of risk ratios using `Plotly`.
- **Professional Reports:** Export findings into branded, ready-to-share PDF or JSON audits.
- **Audit Logs:** local persistence using `SQLite` for tracking historical document analysis.

---

## Quick Start

### 1. Local Setup
Ensure you have Python 3.9+ installed and run the following in your terminal:

```bash
# Clone the repository
git clone https://github.com/Gautam-Bharadwaj/Pippo.ai.git
cd Pippo.ai

# Install dependencies
python3 -m pip install -r requirements.txt

# Setup Environment
echo "OPENAI_API_KEY=your_key_here" > .env

# Launch the engine
streamlit run app.py
```

### 2. Hosting
- **Streamlit Cloud (Recommended):** Connect your GitHub repo and deploy. Ensure `packages.txt` is present for Tesseract support.
- **Vercel:** Possible via the provided `vercel.json` runtime configuration.

---

## Built With

- **Backend:** Python 3.9, OpenAI, LangChain, LangGraph
- **Frontend:** Streamlit, CSS3 (Glassmorphism), Plotly
- **Data/ML:** Scikit-learn, Pandas, NLTK, PyMuPDF
- **Reporting:** ReportLab, Joblib

---

## The Team

Pippo AI is the result of focused engineering and design by:

- **Kumar Gautam:** System Architecture, OCR, and UX Design
- **Mohit Kourav:** Risk ML Model & Reasoning Orchestration
- **Karan Thakur:** Database Persistence & Reporting Systems

---

<p align="center">
  <img src="https://img.shields.io/badge/Status-Nominal-58A6FF?style=for-the-badge&logo=statuspage" alt="Status">
  <img src="https://img.shields.io/badge/Security-Encrypted-E91E63?style=for-the-badge&logo=security" alt="Security">
</p>

© 2026 Gautam Bharadwaj Systems // Pippo AI Intelligence.
