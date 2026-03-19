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
def generate_pdf_report(processed_data: List[Dict[str, Any]], metadata: Dict[str, Any], output_path: str):
    '''Generates a professional PDF report containing the contract metadata and clause analysis.'''
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=18)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=HexColor('#000000'),
        spaceAfter=20
    )
    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=18,
        spaceAfter=12,
        spaceBefore=16
    )
    metadata_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        spaceAfter=6
    )
    clause_title_style = ParagraphStyle(
        'ClauseTitle',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6
    )
    clause_text_style = ParagraphStyle(
        'ClauseText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=HexColor('#333333'),
        spaceAfter=10
    )
    risk_high_style = ParagraphStyle(
        'RiskHigh',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=HexColor('#FF3B30'),
        spaceAfter=6
    )
    risk_low_style = ParagraphStyle(
        'RiskLow',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=HexColor('#34C759'),
        spaceAfter=6
    )
    story = []
    story.append(Paragraph("Contract Risk Audit Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", metadata_style))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#CCCCCC'), spaceBefore=10, spaceAfter=20))
    story.append(Paragraph("Contract DNA (Metadata)", h2_style))
    for key, val in metadata.items():
        if isinstance(val, list):
            display_val = ", ".join(val) if val else "NOT_FOUND"
        else:
            display_val = val if val else "NOT_FOUND"
        story.append(Paragraph(f"<b>{key}:</b> {display_val}", metadata_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Detailed Clause Analysis", h2_style))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#CCCCCC'), spaceBefore=5, spaceAfter=15))
    for i, item in enumerate(processed_data):
        story.append(Paragraph(f"Clause C-{i+1:03}", clause_title_style))
        if item['is_risky']:
            story.append(Paragraph(f"Status: HIGH RISK (Confidence: {item['confidence']:.2%})", risk_high_style))
        else:
            story.append(Paragraph(f"Status: LOW RISK (Confidence: {item['confidence']:.2%})", risk_low_style))
        story.append(Paragraph(item['clause'], clause_text_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#EEEEEE'), spaceBefore=5, spaceAfter=10))
    doc.build(story)
if __name__ == '__main__':
    sample_data = [{'clause': 'The company shall not be liable.', 'is_risky': True, 'confidence': 0.95}]
    sample_meta = {'Party A': 'Acme Corp', 'Party B': 'Globex'}
    print(generate_json_report(sample_data, sample_meta))
    generate_pdf_report(sample_data, sample_meta, 'sample_report.pdf')
    print("PDF built.")
