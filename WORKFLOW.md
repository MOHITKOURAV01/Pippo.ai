# Project Workflow & Architecture

This document describes the flow of information and processing steps in the Intelligent Contract Risk Analysis system using Mermaid diagrams.

## 1. High-Level System Architecture
This diagram shows how the user interacts with the system and how the background processes handle the data.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#1f2937', 'primaryTextColor': '#fff', 'primaryBorderColor': '#3b82f6', 'lineColor': '#60a5fa', 'secondaryColor': '#111827', 'tertiaryColor': '#1f2937'}}}%%
graph TD
    User([User/Legal Professional]) -->|Uploads PDF| UI[Streamlit Interface]
    UI -->|Sends PDF| Extractor[PDF Text Extractor]
    Extractor -->|Raw Text| Splitter[Clause Splitter]
    Splitter -->|Individual Clauses| Preprocessor[Text Preprocessor]
    Preprocessor -->|Cleaned Text| Classifier[Risk Classifier Model]
    Classifier -->|Predicted Risk Levels| UI
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

## 3. Milestone 2: Agentic Assistant Flow (Upcoming)
This shows how LangGraph and LLMs will interact for deeper legal reasoning.

```mermaid
stateDiagram-v2
    [*] --> InputReceived
    InputReceived --> ExtractingTerms
    ExtractingTerms --> ClassifyingRisk
    ClassifyingRisk --> RiskDetected: High/Medium Risk
    ClassifyingRisk --> LowRisk: Safe
    RiskDetected --> LLM_Analysis: Ask LLM for Explanation
    LLM_Analysis --> SuggestingMitigation: How to fix the clause?
    SuggestingMitigation --> FinalReport
    LowRisk --> FinalReport
    FinalReport --> [*]
```

## 4. Team Responsibilities & Work Division
This map outlines the specialized roles for Phase 1 and Phase 2.

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#FF6B00',
    'textColor': '#000000',
    'mainBkg': '#FFFFFF',
    'nodeTextColor': '#000000',
    'cScale0': '#FFFFFF',
    'cScale1': '#FFFFFF',
    'cScale2': '#FFFFFF',
    'cScale3': '#FFFFFF',
    'cScaleLabel0': '#000000',
    'cScaleLabel1': '#000000',
    'cScaleLabel2': '#000000',
    'cScaleLabel3': '#000000'
  }
}}%%
mindmap
  root((fa:fa-project-diagram AI-ML))
    ::icon(fa fa-users)
    Kumar Gautam
      ::icon(fa fa-desktop)
      Data Engineering & OCR
      Legal Metadata Extraction
      Streamlit HUD-Logic & Dashboard
      Automated Audit Integration
    Mohit Kourav
      ::icon(fa fa-brain)
      Intelligence Logic Microservices
      Graph-based Reasoning Architecture
      Statistical Risk Variance Mapping
      Validation Verification Framework
    Karan Thakur
      ::icon(fa fa-file-export)
      Multiformat Report Generation Engine
      Relational Persistence Layers (SQLite)
      Frontend-Backend State Middleware
      High-Concurrency Batch Orchestration
```

## 5. System Themes & Styling
*All diagrams use the 'Base' modern theme with customized node coloring for readability.*
