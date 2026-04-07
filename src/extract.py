import fitz  # PyMuPDF
import os
import re
from typing import Any
import pytesseract
from PIL import Image
import io

def extract_text_via_ocr(page):
    """Fallback OCR extraction using pytesseract for scanned pages."""
    pix = page.get_pixmap()
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))
    return pytesseract.image_to_string(img)

def extract_text_from_pdf(pdf_path, start=0, end=None):
    """ Grabs text from PDF. end=None reads till the end. """
    try:
        doc = fitz.open(pdf_path)
        content = []
        
        last_page = end if end and end <= len(doc) else len(doc)
        print(f"--- Processing: {pdf_path} (Pages {start+1} to {last_page}) ---")
        
        for i in range(start, last_page):
            page = doc.load_page(i)
            page_text = page.get_text("text").strip()
            
            # Smart Fallback: If no text but page is not empty (images or scanned)
            if not page_text:
                print(f"--- [!] No text on Page {i+1}. Attempting OCR Scan... ---")
                page_text = extract_text_via_ocr(page)
                if page_text:
                    print(f"--- [✓] OCR Success on Page {i+1} ---")
                else:
                    print(f"--- [X] OCR Failed on Page {i+1} ---")
            
            content.append(page_text)
            
        doc.close()
        return "\n".join(content)
    except Exception as err:
        print(f"PDF Error: {err}")
        return None

def extract_legal_metadata(text):
    """
    Data Engineering: Extract key identifiers from raw text.
    Improved version with better regex and more fields.
    """
    metadata: dict[str, Any] = {
        "Parties": [],
        "Effective Date": "N/A",
        "Governing Law": "N/A",
        "Jurisdiction": "N/A",
        "Termination Notice": "N/A"
    }
    
    # regex patterns for legal terms - improved for variety
    patterns = {
        "Parties": r'(?:between|among|BY AND BETWEEN)\s+([A-Z0-9][\w\s&,.\-\(\)]+?)(?:\s*(?:LLC|Inc|Corp|Ltd|and|a [a-z ]+ corporation|a [a-z ]+ limited liability company))',
        "Effective Date": r'(?:Effective\s+Date|dated|this\s+day\s+of|Date:)\s+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+[A-Z][a-z]+\s+\d{4})',
        "Governing Law": r'(?:governed\s+by|laws\s+of)\s+the\s+(?:laws|state)\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        "Jurisdiction": r'(?:exclusive\s+)?jurisdiction\s+(?:of|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        "Termination Notice": r'(\d+\s+(?:day|month)s?)\s+prior\s+written\s+notice'
    }
    
    for key, pattern in patterns.items():
        try:
            matches = list(re.findall(pattern, text, re.IGNORECASE))
            if matches:
                if key == "Parties":
                    # Clean up and deduplicate
                    unique_parties = []
                    for m in matches:
                        p = str(m).strip().strip(',').strip()
                        if p and p not in unique_parties and len(p) > 2:
                            unique_parties.append(p)
                    metadata[key] = unique_parties[:2]
                else:
                    metadata[key] = str(matches[0]).strip()
        except Exception:
            pass
                
    return metadata

def save_text(text, target_path):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved to: {target_path}")

if __name__ == "__main__":
    pass
