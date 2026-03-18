import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.predict import predict_risk
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM lazily
def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return ChatOpenAI(model="gpt-4o", temperature=0)

ANALYSIS_PROMPT = ChatPromptTemplate.from_template("""
You are a senior legal compliance officer. 
Analyzed Clause: {clause}
Risk Probability: {risk_prob:.2f}

Your task:
1. Explain WHY this clause was flagged as High-Risk by our ML model.
2. Suggest a specific MITIGATION strategy (e.g., specific wording to add/remove).
3. Provide a 'Draft Correction' for this clause.

Tone: Professional, concise, and technical.
""")

def analyze_risk_with_agent(clause_text):
    """
    Orchestrates the flow: ML Prediction -> LLM Reasoning (if needed).
    """
    # Step 1: ML Prediction
    prediction = predict_risk(clause_text)[0]
    
    # Step 2: Conditional Agentic Reasoning
    if prediction['is_risky'] and prediction['risk_probability'] > 0.65:
        # Check LLM
        llm = get_llm()
        if not llm:
            return {
                "status": "DANGER",
                "ml_risk": prediction['risk_probability'],
                "explanation": "AGENT_ERROR: OpenAI API Key is missing. Please set OPENAI_API_KEY in your .env file.",
                "can_mitigate": False
            }
            
        # Request LLM Analysis
        response = llm.invoke(ANALYSIS_PROMPT.format(
            clause=clause_text,
            risk_prob=prediction['risk_probability']
        ))
        
        return {
            "status": "DANGER",
            "ml_risk": prediction['risk_probability'],
            "explanation": response.content,
            "can_mitigate": True
        }
    
    return {
        "status": "NOMINAL",
        "ml_risk": prediction['risk_probability'],
        "explanation": "Safe clause. No intervention required.",
        "can_mitigate": False
    }

if __name__ == "__main__":
    # Test sample
    test_clause = "The company shall not make any investments without prior approval and the user accepts all liability for loss."
    print("Analyzing Sample Clause...")
    result = analyze_risk_with_agent(test_clause)
    print(result)
