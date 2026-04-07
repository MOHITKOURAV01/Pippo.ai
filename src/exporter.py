import json
import os
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
def generate_json_report(processed_data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> str:
    '''Generates a structured JSON report from the processed contract clauses and metadata.'''
    report = {
        "generated_at": datetime.now().isoformat(),
        "metadata": metadata,
        "findings": processed_data
    }
    return json.dumps(report, indent=4)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Image as RLImage

def generate_pdf_report(processed_data: List[Dict[str, Any]], metadata: Dict[str, Any], output_path: str):
    '''Generates a professional, branded PDF report for contract analysis.'''
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    # Custom Brand Colors
    PIPPO_PINK = HexColor('#E91E63')
    PIPPO_BLUE = HexColor('#58A6FF')
    DARK_TEXT = HexColor('#1F2328')
    GRAY_TEXT = HexColor('#484F58')
    LINE_COLOR = HexColor('#D0D7DE')

    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=26,
        textColor=PIPPO_PINK, spaceAfter=10, leading=32
    )
    subtitle_style = ParagraphStyle(
        'SubStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10,
        textColor=GRAY_TEXT, spaceAfter=20
    )
    h2_style = ParagraphStyle(
        'H2Style', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=16,
        textColor=DARK_TEXT, spaceBefore=20, spaceAfter=12, borderPadding=5
    )
    meta_label_style = ParagraphStyle(
        'MetaLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10,
        textColor=PIPPO_BLUE, spaceAfter=2
    )
    meta_val_style = ParagraphStyle(
        'MetaVal', parent=styles['Normal'], fontName='Helvetica', fontSize=11,
        textColor=DARK_TEXT, spaceAfter=10
    )
    clause_id_style = ParagraphStyle(
        'ClauseID', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9,
        textColor=GRAY_TEXT, spaceBefore=15
    )
    clause_text_style = ParagraphStyle(
        'ClauseText', parent=styles['Normal'], fontName='Helvetica', fontSize=10,
        textColor=DARK_TEXT, leading=14, spaceAfter=8
    )
    risk_high_style = ParagraphStyle(
        'RiskHigh', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10,
        textColor=HexColor('#FF3B30'), spaceAfter=5
    )
    risk_low_style = ParagraphStyle(
        'RiskLow', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10,
        textColor=HexColor('#34C759'), spaceAfter=5
    )
    footer_style = ParagraphStyle(
        'Footer', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8,
        textColor=PIPPO_PINK, alignment=1, spaceBefore=30
    )

    story = []
    
    # Header Section
    story.append(Paragraph("Pippo AI: Legal Audit Report", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PIPPO_PINK, spaceAfter=25))
    
    # Contract DNA
    story.append(Paragraph("Contract DNA & Context", h2_style))
    for key, val in metadata.items():
        if isinstance(val, list):
            display_val = ", ".join(val) if val else "NOT DETECTED"
        else:
            display_val = val if val else "NOT DETECTED"
        
        story.append(Paragraph(key.upper(), meta_label_style))
        story.append(Paragraph(str(display_val), meta_val_style))
    
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=LINE_COLOR, spaceAfter=20))
    
    # Audit Findings
    story.append(Paragraph("Detailed Risk Findings", h2_style))
    
    risky_clauses = [item for item in processed_data if item['is_risky']]
    if not risky_clauses:
        story.append(Paragraph("No high-risk clauses were detected in this document.", styles['Normal']))
    else:
        for i, item in enumerate(processed_data):
            story.append(Paragraph(f"CLAUSE IDENTIFIER: C-{i+1:03}", clause_id_style))
            
            if item['is_risky']:
                story.append(Paragraph(f"STATUS: HIGH RISK / ANOMALY DETECTED (Confidence: {item['confidence']:.0%})", risk_high_style))
            else:
                story.append(Paragraph(f"STATUS: NOMINAL / LOW RISK (Confidence: {item['confidence']:.0%})", risk_low_style))
            
            story.append(Paragraph(item['clause'], clause_text_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceBefore=10, spaceAfter=10))

    # Footer
    story.append(Spacer(1, 40))
    story.append(Paragraph("PIPPO AI // GAUTAM BHARADWAJ SYSTEMS // 2026 EDITION", footer_style))
    
    doc.build(story)
if __name__ == '__main__':
    sample_data = [{'clause': 'The company shall not be liable.', 'is_risky': True, 'confidence': 0.95}]
    sample_meta = {'Party A': 'Acme Corp', 'Party B': 'Globex'}
    print(generate_json_report(sample_data, sample_meta))
    generate_pdf_report(sample_data, sample_meta, 'sample_report.pdf')
    print("PDF built.")
