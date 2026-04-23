from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import sys
from typing import List, Dict

# Add backend directory to path so we can import our logic
sys.path.append(os.getcwd())

from backend.logic.extract import extract_text_from_pdf, extract_legal_metadata
from backend.logic.clause_splitter import split_into_clauses
from backend.logic.predict import predict_risk
# from backend.logic.agent_logic import analyze_risk_with_agent # Optional for now

app = FastAPI()

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Pippo AI Backend is active"}

@app.post("/api/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = tmp.name

        # 1. Extract Text
        full_text = extract_text_from_pdf(temp_path)
        
        if not full_text or len(full_text.strip()) < 5:
            raise HTTPException(
                status_code=400, 
                detail="Failed to extract readable text from the PDF. The file might be empty, password-protected, or a scanned image that requires OCR."
            )

        # 2. Extract Metadata
        metadata = extract_legal_metadata(full_text)
        
        # 3. Split into clauses
        clause_list = split_into_clauses(full_text)
        
        # 4. Predict Risk for each clause
        processed_data = []
        for clause in clause_list:
            if not clause.strip():
                continue
            prediction = predict_risk(clause)[0]
            processed_data.append({
                "clause": clause,
                "is_risky": bool(prediction['is_risky']),
                "confidence": float(prediction['risk_probability'])
            })
            
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        risky_count = sum(1 for x in processed_data if x['is_risky'])
        integrity = int((sum(1 for x in processed_data if not x['is_risky']) / len(processed_data) * 100)) if processed_data else 0

        # 5. Persistence (Functional Persistence)
        from backend.logic.database import save_audit
        try:
            save_audit(
                filename=file.filename,
                total_clauses=len(processed_data),
                risky_clauses=risky_count,
                safe_ratio=float(integrity),
                findings=processed_data
            )
        except Exception as e:
            print(f"Database persistence failed: {e}")

        return {
            "filename": file.filename,
            "metadata": metadata,
            "analysis": processed_data,
            "summary": {
                "total_clauses": len(processed_data),
                "risky_clauses": risky_count,
                "safe_ratio": integrity
            }
        }
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
