# AI-Driven Legal Document Analysis System

Design and implement an AI-driven legal document analysis system that identifies and classifies risky clauses in contracts.

##  Getting Started

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Project Roadmap

### Milestone 1: Automated ML Classification Pipeline
- [x] **Core Extraction Engine** (Kumar Gautam)
    - Directory & Environment Architecture
    - PDF Stream Parsers & Text Normalization
    - Regex-based Clause Segmentation Logic
- [x] **Risk Assessment Model** (Mohit Kourav)
    - TF-IDF Feature Engineering
    - RandomForest Model Serialization
    - Global Risk Prediction Scopes
- [x] **Initial Telemetry Dashboard** (Karan Thakur)
    - Base Streamlit Interface Logic
    - Visual Probability Matrix Display

### Milestone 2: Intelligent HUD & Deep Audit Interface
- [x] **Data Intelligence Layer** (Kumar Gautam)
    - Legal Metadata Extraction (Parties, Jurisdiction, Dates)
    - OCR-Detection & Image-PDF Support Infrastructure
- [x] **Premium User Experience (UX)** (Kumar Gautam)
    - HUD-Inspired Dark Theme (Succesship Aesthetics)
    - Real-time Scanning & Processing Simulation HUD
    - Dynamic Intelligence Bento-Cards for Metrics
- [ ] **Advanced Reasoning Engine** (Mohit Kourav) [In Development]
    - Graph-based Reasoning Orchestrator
    - Multistep Logic Verification Chains
- [ ] **Functional Persistence** (Karan Thakur) [In Development]
    - Secure SQLite Audit Log Storage
    - Multi-Format (PDF/JSON) Intelligence Report Export

## How to Run (Workflow)
1. **Install what's needed:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Setup the Dataset:**
   Run this to clean your raw data and get it ready for training:
   ```bash
   python3 src/prepare_dataset.py
   ```
   *This will create: `data/processed/cleaned_legal_clauses.csv`*

3. **Launch the App:**
   ```bash
   streamlit run app.py
   ```
