from sentence_transformers import SentenceTransformer, util
import fitz  # PyMuPDF

# Load once
model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf_file(uploaded_pdf_file) -> str:
    """Extracts and returns plain text from a PDF file uploaded via Streamlit."""
    text = ""
    try:
        with fitz.open(stream=uploaded_pdf_file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        return f"Failed to extract text: {e}"
    return text.strip()

def score_resume(resume_text: str, job_text: str) -> str:
    """Returns a similarity score between resume text and a job description/title (0 to 1)."""
    try:
        resume_embedding = model.encode(resume_text, convert_to_tensor=True)
        job_embedding = model.encode(job_text, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(resume_embedding, job_embedding).item()
        return str(round(similarity, 3))
    except Exception as e:
        return f"Scoring error: {e}"