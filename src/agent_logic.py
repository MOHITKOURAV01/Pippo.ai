import os
from typing import Annotated, TypedDict, List, Dict, Any, Literal
import logging
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from src.prompts import (
    CLAUSE_ANALYZER_SYSTEM,
    RISK_IDENTIFIER_SYSTEM,
    SELF_CORRECTION_SYSTEM,
    FINAL_VERDICT_SYSTEM
)
from src.ml_model import LegalMLModel
from src.utils import (
    parse_json_with_retry,
    calculate_hybrid_score,
    map_score_to_level,
    logger
)

load_dotenv()

# --- State Definition ---
class AgentState(TypedDict):
    clause: str
    ml_result: Dict[str, Any]
    analysis: Dict[str, Any]
    risks: Dict[str, Any]
    review: Dict[str, Any]
    final_output: Dict[str, Any]
    iterations: int
    max_iterations: int
