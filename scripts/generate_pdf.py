from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import os

def md_to_paragraphs(md_text):
    paragraphs = []
    blocks = md_text.split('\n\n')
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # Headers
        if block.startswith('**') or block.startswith('#'):
            # treat as heading
            paragraphs.append(('heading', block.strip('#').strip('* ').strip()))
        else:
            paragraphs.append(('body', block.replace('\n', ' ')))
    return paragraphs

def sanitize(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def build_pdf(md_path, out_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md = f.read()

    doc = SimpleDocTemplate(out_path, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['BodyText'], spaceAfter=6, fontSize=10)

    flow = []
    for kind, text in md_to_paragraphs(md):
        text = sanitize(text)
        if kind == 'heading':
            flow.append(Paragraph(text, heading_style))
        else:
            flow.append(Paragraph(text, body_style))
        flow.append(Spacer(1, 6))

    doc.build(flow)

if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md_path = os.path.join(root, 'TECHNICAL_SUMMARY.md')
    out_path = os.path.join(root, 'Technical_Summary.pdf')
    print(f"Reading: {md_path}")
    build_pdf(md_path, out_path)
    print(f"Wrote: {out_path}")
