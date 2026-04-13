# Project Workflow & Architecture

This document describes the flow of information and processing steps in the Intelligent Contract Risk Analysis system using Mermaid diagrams.

## 1. High-Level System Architecture
This diagram shows how the user interacts with the system and how the background processes handle the data.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#1f2937', 'primaryTextColor': '#fff', 'primaryBorderColor': '#3b82f6', 'lineColor': '#60a5fa'}}}%%
flowchart LR
    User([User/Legal Professional]) -->|Uploads PDF| UI[Streamlit Interface]
    UI -->|Sends PDF| Extractor[PDF Text Extractor]
    Extractor -->|Raw Text| Splitter[Clause Splitter]
    Splitter -->|Clauses| Preprocessor[Text Preprocessor]
    Preprocessor -->|Clean Data| Classifier[ML Classifier]
    Classifier -->|Risk Levels| UI
    UI -->|Displays Results| User
```

## 2. Milestone 1: Detailed Data Pipeline
This flow represents the work completed for the initial ML-based classification.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#1f2937', 'primaryTextColor': '#fff', 'primaryBorderColor': '#10b981', 'lineColor': '#34d399'}}}%%
flowchart LR
    A[Contract PDF] --> B(PyMuPDF Extraction)
    B --> C{Text Available?}
    C -->|Yes| D[Regex Clause Splitting]
    C -->|No| E[Error Handling]
    D --> F[NLTK Preprocessing]
    F --> G[TF-IDF Vectorization]
    G --> H[ML Model Prediction]
    H --> I[Risk Category Output]
```

## 3. Milestone 2: Agentic Assistant & Deep Audit Flow
This flow represents the advanced, agentic legal reasoning using LangGraph and hybrid analysis.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#1f2937', 'primaryTextColor': '#fff', 'primaryBorderColor': '#ec4899', 'lineColor': '#f472b6'}}}%%
flowchart LR
    A[Legal PDF] --> B(OCR & Term Extraction)
    B --> C(Clause Segmentation)
    C --> D[ML Risk Prediction]
    D --> E{High Risk?}
    E -->|Yes| F[LangGraph Agentic Reasoning]
    E -->|No| G[Final Status: Nominal]
    F --> H[Hybrid Risk Scoring]
    H --> I[SQLite Persistence]
    I --> J[JSON/PDF Report Export]
    G --> I
```

## 4. Team Responsibilities & Work Division
This map outlines the specialized roles for Phase 1 and Phase 2.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#1f2937', 'primaryTextColor': '#fff', 'primaryBorderColor': '#f59e0b', 'lineColor': '#fbbf24'}}}%%
flowchart LR
    subgraph Team[Project Contributors]
    KG[Kumar Gautam]
    MK[Mohit Kourav]
    KT[Karan Thakur]
    end

    KG --- KG1[Data Engineering & OCR]
    KG --- KG2[Metadata Extraction]
    KG --- KG3[HUD UX & Dashboard]

    MK --- MK1[Agentic Microservices]
    MK --- MK2[Graph Reasoning]
    MK --- MK3[Statistical Mapping]

    KT --- KT1[Report Generation]
    KT --- KT2[SQLite Persistence]
    KT --- KT3[State Middleware]
```

## 5. System Themes & Styling
*All diagrams use the 'Base' modern theme with customized node coloring for readability.*
