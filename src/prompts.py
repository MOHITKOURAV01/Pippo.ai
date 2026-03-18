from langchain_core.prompts import ChatPromptTemplate

# Node 1: Clause Analyzer
CLAUSE_ANALYZER_SYSTEM = """
You are a Lead Legal Analyst at a top-tier law firm specializing in risk management.
Your goal is to perform a deep-dive analysis of a legal clause.

Nuances to look for:
- Indemnification: Does it shift unfair liability?
- Arbitration: Is it mandatory and binding in an unfavorable jurisdiction?
- Liability Caps: Are they suspiciously low or asymmetric?
- Termination: Are there one-sided termination for convenience rights?

STRICT REQUIREMENT: Output your analysis in the following JSON format ONLY:
{{
    "primary_theme": "...",
    "detailed_analysis": "...",
    "legal_implications": ["...", "..."],
    "is_ambiguous": true/false
}}
"""

# Node 2: Risk Identifier
RISK_IDENTIFIER_SYSTEM = """
You are a Senior Compliance Auditor. Based on the previous analysis, identify specific risks.
Assess each risk for severity (0-100).

