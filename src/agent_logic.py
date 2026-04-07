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

# --- Node Implementation ---

class LegalReasoningAgent:
    def __init__(self, model_name: str = "gpt-4o"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.ml_engine = LegalMLModel()
        self.workflow = self._build_graph()

    def _call_llm_json(self, system_prompt: str, user_input: str) -> Dict[str, Any]:
        """ Helper to call LLM and ensure JSON output. """
        messages = [
            ("system", system_prompt),
            ("user", user_input)
        ]
        response = self.llm.invoke(messages)
        parsed = parse_json_with_retry(response.content)
        
        if parsed is None:
            # Simple fallback if JSON fails again
            logger.warning("JSON parsing failed, returning empty dict.")
            return {}
        return parsed

    def analyze_node(self, state: AgentState) -> AgentState:
        logger.info(f"Node: Analyze [Iteration {state['iterations'] + 1}]")
        prompt = f"Target Clause:\n{state['clause']}"
        if state.get('review'):
            prompt += f"\n\nPrevious Review Feedback:\n{state['review'].get('correction_instructions', '')}"
            
        result = self._call_llm_json(CLAUSE_ANALYZER_SYSTEM, prompt)
        state['analysis'] = result
        state['iterations'] += 1
        return state

    def risk_id_node(self, state: AgentState) -> AgentState:
        logger.info("Node: Risk Identification")
        user_input = f"Clause Content:\n{state['clause']}\n\nTechnical Analysis:\n{state['analysis']}"
        result = self._call_llm_json(RISK_IDENTIFIER_SYSTEM, user_input)
        state['risks'] = result
        return state

    def validate_node(self, state: AgentState) -> AgentState:
        logger.info("Node: Validation/Self-Correction")
        user_input = (
            f"Original Clause: {state['clause']}\n"
            f"Analysis: {state['analysis']}\n"
            f"Identified Risks: {state['risks']}"
        )
        result = self._call_llm_json(SELF_CORRECTION_SYSTEM, user_input)
        state['review'] = result
        return state

    def verdict_node(self, state: AgentState) -> AgentState:
        logger.info("Node: Final Verdict Generator")
        
        # Calculate Hybrid Score
        llm_score = state['risks'].get('llm_risk_score', 0)
        ml_score_raw = state['ml_result'].get('risk_probability', 0) * 100
        
        final_score = calculate_hybrid_score(llm_score, ml_score_raw)
        
        user_input = (
            f"Hybrid Evaluation Data:\n"
            f"- LLM Component Score: {llm_score}\n"
            f"- ML Component Score: {ml_score_raw:.2f}\n"
            f"- Final Computed Score: {final_score}\n"
            f"- Detailed Analysis: {state['analysis']}\n"
            f"- Identified Risks: {state['risks']}"
        )
        
        verdict = self._call_llm_json(FINAL_VERDICT_SYSTEM, user_input)
        
        # Combine everything into final structured response
        state['final_output'] = {
            "clause": state['clause'],
            "risk_type": verdict.get("risk_type", "Unknown"),
            "risk_level": map_score_to_level(final_score),
            "llm_score": llm_score,
            "ml_score": round(ml_score_raw, 2),
            "final_score": final_score,
            "confidence": state['risks'].get('confidence_level', 0.5),
            "issues_detected": verdict.get("issues_detected", []),
            "suggestion": verdict.get("suggestion", "N/A"),
            "final_verdict": verdict.get("final_verdict", "N/A")
        }
        return state

    def _should_continue(self, state: AgentState) -> Literal["continue", "end"]:
        """ Conditional edge logic for self-correction loop. """
        review = state.get('review', {})
        if review.get('needs_correction', False) and state['iterations'] < state['max_iterations']:
            logger.warning(f"Self-Correction Triggered: {review.get('correction_instructions')}")
            return "continue"
        return "end"

    def _build_graph(self):
        builder = StateGraph(AgentState)
        
        # Add Nodes
        builder.add_node("analyze", self.analyze_node)
        builder.add_node("identify_risks", self.risk_id_node)
        builder.add_node("validate", self.validate_node)
        builder.add_node("finalize", self.verdict_node)
        
        # Add Edges
        builder.set_entry_point("analyze")
        builder.add_edge("analyze", "identify_risks")
        builder.add_edge("identify_risks", "validate")
        
        # Conditional Edge (Loop)
        builder.add_conditional_edges(
            "validate",
            self._should_continue,
            {
                "continue": "analyze",
                "end": "finalize"
            }
        )
        
        builder.add_edge("finalize", END)
        
        return builder.compile()

    def run_analysis(self, clause_text: str) -> Dict[str, Any]:
        """ Public interface to run the full pipeline. """
        logger.info(f"Starting analysis for clause: {clause_text[:50]}...")
        
        # Initial ML Prediction
        ml_res = self.ml_engine.get_risk_score(clause_text)
        
        initial_state: AgentState = {
            "clause": clause_text,
            "ml_result": ml_res,
            "analysis": {},
            "risks": {},
            "review": {},
            "final_output": {},
            "iterations": 0,
            "max_iterations": 3 # Cap loop
        }
        
        final_state = self.workflow.invoke(initial_state)
        return final_state['final_output']

def get_mock_response(clause_text: str) -> Dict[str, Any]:
    """Fallback simulated response for demos when API is unavailable or limits reached."""
    return {
        "clause": clause_text,
        "risk_type": "Simulated Risk Analysis",
        "risk_level": "High (Review Required)",
        "llm_score": 85,
        "ml_score": 82.5,
        "final_score": 84,
        "confidence": 0.88,
        "issues_detected": [
            "Potential unlimited liability trigger found in phrasing.",
            "Non-standard termination notice period detected.",
            "Ambiguous indemnity scope lacks clear boundaries."
        ],
        "suggestion": "Suggest adding a liability cap or clarifying the notice period.",
        "final_verdict": "[DEMO MODE] This clause contains high-risk triggers. Manual legal oversight is strongly recommended."
    }

# Compatibility Wrapper
def analyze_risk_with_agent(clause_text: str) -> Dict[str, Any]:
    """
    Public API for the UI. Always returns a dict with at minimum:
      - explanation (str)
      - risk_level (str)
      - issues_detected (list)
      - suggestion (str)
    """
    try:
        agent = LegalReasoningAgent()
        result = agent.run_analysis(clause_text)
    except Exception as e:
        logger.error(f"Critical Agent Failure: {e}")
        if "insufficient_quota" in str(e).lower() or "limit" in str(e).lower():
            result = get_mock_response(clause_text)
        else:
            result = {
                "clause": clause_text,
                "error": str(e),
                "final_verdict": f"Agent execution encountered an error: {str(e)[:100]}..."
            }

    # Build a unified 'explanation' from whichever fields are present
    parts = []
    if result.get("final_verdict"):
        parts.append(f"**Verdict:** {result['final_verdict']}")
    if result.get("risk_type"):
        parts.append(f"**Risk Type:** {result['risk_type']}")
    if result.get("risk_level"):
        parts.append(f"**Risk Level:** {result['risk_level']}")
    if result.get("issues_detected"):
        issues = result["issues_detected"]
        if isinstance(issues, list):
            parts.append("**Issues Detected:**\n" + "\n".join(f"• {i}" for i in issues))
    if result.get("suggestion"):
        parts.append(f"**Suggestion:** {result['suggestion']}")
    if result.get("error"):
        parts.append(f"⚠️ **Error:** {result['error']}")

    result["explanation"] = "\n\n".join(parts) if parts else "Analysis completed but no detailed explanation was generated."
    return result

if __name__ == "__main__":
    # Test example
    sample = "The company shall not be liable for any indirect damages under any circumstances."
    print("Iniatizing Deep Audit...")
    try:
        res = analyze_risk_with_agent(sample)
        import json
        print(json.dumps(res, indent=2))
    except Exception as e:
        print(f"Error: {e}")
