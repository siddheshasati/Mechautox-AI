import base64
import json
import mimetypes
import os
import re
import zipfile
import xml.etree.ElementTree as ET
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple

from dotenv import dotenv_values
from langchain_core.documents import Document

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from .RAGSystem import LocalRAGSystem
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logger.warning("RAGSystem not available. Using legacy mode.")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "Data")
ENV_PATH = os.path.join(BASE_DIR, ".env")
UPLOAD_CONTEXT_PATH = os.path.join(DATA_DIR, "UploadedContext.json")
os.makedirs(DATA_DIR, exist_ok=True)

env_vars = dotenv_values(ENV_PATH)
GroqAPIKey = env_vars.get("GroqAPIKey", "")
Assistantname = env_vars.get("Assistantname", "Assistant")
client = Groq(api_key=GroqAPIKey) if Groq and GroqAPIKey else None

VISION_MODEL = env_vars.get("GroqVisionModel", "meta-llama/llama-4-scout-17b-16e-instruct")
TEXT_MODEL = env_vars.get("GroqTextModel", "llama-3.3-70b-versatile")

rag_system = None
if RAG_AVAILABLE:
    try:
        rag_system = LocalRAGSystem(groq_api_key=GroqAPIKey)
        logger.info("RAG system initialized in UploadProcessor")
    except Exception as e:
        logger.warning(f"RAG initialization failed: {e}")

def save_upload_context(context):
    """Save upload context and index to FAISS if RAG available"""
    with open(UPLOAD_CONTEXT_PATH, "w", encoding="utf-8") as file:
        json.dump(context, file, indent=4)

    if rag_system and context.get("text"):
        try:
            doc = Document(
                page_content=context["text"],
                metadata={
                    "source": context.get("filename", "uploaded_file"),
                    "kind": context.get("kind", "document"),
                    "uploaded_at": datetime.now().isoformat() if 'datetime' in dir() else ""
                }
            )
            result = rag_system.add_documents([doc], context.get("filename", "uploaded_file"))
            logger.info(f"Indexed to FAISS: {result}")
        except Exception as e:
            logger.warning(f"Failed to index to FAISS: {e}")


def load_upload_context():
    try:
        with open(UPLOAD_CONTEXT_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, ValueError):
        return {}


def has_upload_context():
    context = load_upload_context()
    return bool(context.get("text") or context.get("summary"))


def clean_text(text):
    text = re.sub(r"\r", "\n", text or "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def extract_docx_text(path):
    """Extract text from DOCX file"""
    paragraphs = []
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    try:
        with zipfile.ZipFile(path) as docx:
            with docx.open("word/document.xml") as document:
                tree = ET.parse(document)
        for paragraph in tree.findall(".//w:p", namespace):
            parts = [node.text for node in paragraph.findall(".//w:t", namespace) if node.text]
            if parts:
                paragraphs.append("".join(parts))
        logger.info(f"Extracted text from DOCX: {len(paragraphs)} paragraphs")
        return clean_text("\n".join(paragraphs))
    except Exception as e:
        logger.error(f"Error extracting DOCX: {e}")
        return ""


def extract_pdf_text(path):
    """Extract text from PDF file with multiple library fallbacks"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        text = clean_text("\n".join(page.extract_text() or "" for page in reader.pages))
        logger.info(f"Extracted text from PDF: {len(reader.pages)} pages")
        return text
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"pypdf error: {e}")
    
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(path)
        text = clean_text("\n".join(page.extract_text() or "" for page in reader.pages))
        logger.info(f"Extracted text from PDF (PyPDF2): {len(reader.pages)} pages")
        return text
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"PyPDF2 error: {e}")
    
    logger.error("No PDF library available")
    return ""


def image_metadata(path):
    """Extract image metadata"""
    if Image is None:
        return "Image uploaded, but Pillow is not installed for local image metadata."
    try:
        with Image.open(path) as image:
            width, height = image.size
            return f"Image file: {os.path.basename(path)}\nFormat: {image.format}\nSize: {width} x {height}px"
    except Exception as e:
        logger.warning(f"Image metadata error: {e}")
        return f"Image file: {os.path.basename(path)}"


def ask_llm(system_prompt, user_prompt, max_tokens=900):
    """Query LLM for analysis"""
    if client is None:
        return "AI analysis is not ready because the Groq package or API key is missing."
    try:
        completion = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.4,
            top_p=1,
        )
        return clean_text(completion.choices[0].message.content)
    except Exception as exc:
        logger.error(f"LLM error: {exc}")
        return f"I could not analyze this with AI right now: {exc}"


def analyze_image(path):
    """Analyze image using vision model"""
    metadata = image_metadata(path)
    if client is None:
        return metadata + "\n\nI can store this image, but visual understanding needs the Groq package and API key."

    mime_type = mimetypes.guess_type(path)[0] or "image/png"
    try:
        with open(path, "rb") as file:
            image_data = base64.b64encode(file.read()).decode("utf-8")
        completion = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Understand this image. If there is text, a question, a problem, or a form in it, answer it directly. Otherwise describe the image clearly and mention important details.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{image_data}"},
                        },
                    ],
                }
            ],
            max_tokens=900,
            temperature=0.3,
        )
        result = clean_text(completion.choices[0].message.content)
        logger.info(f"Image analyzed: {len(result)} chars")
        return result
    except Exception as exc:
        logger.error(f"Image analysis error: {exc}")
        return metadata + f"\n\nI could not visually analyze the image right now: {exc}"


def looks_like_resume(text, path):
    """Check if document looks like a resume"""
    name = os.path.basename(path).lower()
    keywords = [
        "resume", "cv", "experience", "education", "skills", "projects",
        "certifications", "summary", "objective", "linkedin", "github"
    ]
    hits = sum(1 for keyword in keywords if keyword in text.lower() or keyword in name)
    return hits >= 3


def analyze_resume(text):
    """Analyze resume quality"""
    prompt = f"""
Evaluate this resume for ATS quality.

Return:
1. ATS score out of 100
2. Strong points
3. Missing or weak areas
4. Keyword and formatting suggestions
5. Concrete improved bullet examples if useful

Resume text:
{text[:12000]}
"""
    return ask_llm(
        "You are an ATS resume reviewer. Be practical, structured, and direct.",
        prompt,
        max_tokens=1200,
    )


def summarize_document(text, filename):
    """Summarize uploaded document"""
    prompt = f"""
The user uploaded a document named {filename}.
Summarize the document, identify important points, and tell the user they can ask questions about it.

Document text:
{text[:12000]}
"""
    return ask_llm(
        "You analyze uploaded documents. Be clear, structured, and not too long.",
        prompt,
        max_tokens=900,
    )


def process_uploaded_file(path):
    """
    Process uploaded file: extract text, summarize, and index to FAISS.
    Args:
        path: Path to uploaded file
    Returns:
        Summary message and status
    """
    if not path or not os.path.exists(path):
        return "I could not find the uploaded file. Please upload it again."

    extension = os.path.splitext(path)[1].lower()
    filename = os.path.basename(path)
    context = {
        "path": path,
        "filename": filename,
        "extension": extension,
        "text": "",
        "summary": "",
        "kind": "unknown",
    }

    logger.info(f"Processing uploaded file: {filename}")

    # Handle images
    if extension in [".png", ".jpg", ".jpeg", ".webp", ".bmp"]:
        context["kind"] = "image"
        analysis = analyze_image(path)
        context["summary"] = analysis
        save_upload_context(context)
        result = f"Uploaded image: {filename}\n\n{analysis}"
        logger.info(f"Image processed: {filename}")
        return result

    if extension == ".docx":
        text = extract_docx_text(path)
    elif extension == ".pdf":
        text = extract_pdf_text(path)
        if not text:
            return "I uploaded the PDF, but I could not extract readable text. Install `pypdf` or upload a text-based PDF instead of a scanned image PDF."
    else:
        return "Unsupported file type. Please upload an image, PDF, or DOCX file."

    context["kind"] = "document"
    context["text"] = text


    if looks_like_resume(text, path):
        context["summary"] = analyze_resume(text)
        context["kind"] = "resume"
    else:
        context["summary"] = summarize_document(text, filename)

    save_upload_context(context)
    
    rag_status = "Indexed to FAISS" if rag_system else ""
    result = f"Uploaded file: {filename}\n{rag_status}\n\n{context['summary']}"
    logger.info(f"Document processed: {filename}")
    return result


def answer_question_about_upload(question):
    """
    Answer questions about uploaded documents.
    First tries RAG system, then falls back to legacy method.
    """

    if rag_system and has_upload_context():
        try:
            logger.info(f"🔍 Querying RAG for: {question}")
            rag_response = rag_system.query(question)
            if rag_response.sources:
                logger.info(f"RAG found {len(rag_response.sources)} sources")
                return rag_response.answer
        except Exception as e:
            logger.warning(f"RAG query failed, using fallback: {e}")


    context = load_upload_context()
    if not context:
        return ""

    source_text = context.get("text") or context.get("summary", "")
    if not source_text:
        return "I have the uploaded file reference, but no readable text or visual summary was extracted."

    prompt = f"""
Uploaded file: {context.get('filename', 'uploaded file')}
File type: {context.get('kind', 'unknown')}

Uploaded content/context:
{source_text[:14000]}

User question:
{question}
"""
    result = ask_llm(
        "Answer questions using the uploaded file context. If the answer is not in the file, say that clearly and then help with the best available reasoning.",
        prompt,
        max_tokens=1000,
    )
    logger.info(f"Legacy Q&A processed")
    return result


def get_indexed_documents():
    """Get list of indexed documents in FAISS"""
    if rag_system:
        stats = rag_system.get_db_stats()
        if stats["status"] == "active":
            return stats.get("indexed_documents", [])
    return []


def clear_indexed_documents():
    """Clear FAISS index (use with caution)"""
    if rag_system:
        return rag_system.clear_database()
    return {"status": "error", "message": "RAG system not available"}


