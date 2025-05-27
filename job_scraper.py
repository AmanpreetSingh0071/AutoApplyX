import streamlit as st
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util

# Load the model once
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

GREENHOUSE_COMPANIES = {
    "cohere": "Cohere",
    "runwayml": "Runway",
    "scaleai": "Scale AI",
    "samsara": "Samsara",
    "anduril": "Anduril",
    "notion": "Notion",
    "asana": "Asana",
    "roboflow": "Roboflow",
    "adept": "Adept AI",
    "perplexity": "Perplexity AI"
}

def fetch_jobs(keyword="AI Engineer"):
    model = load_model()
    query_embedding = model.encode(keyword, convert_to_tensor=True)
    results = []

    required_word = keyword.lower().split()[0]

    for slug, company_name in GREENHOUSE_COMPANIES.items():
        url = f"https://boards.greenhouse.io/embed/job_board?for={slug}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            jobs = soup.select("div.opening")

            for job in jobs:
                title_elem = job.select_one("a")
                location_elem = job.select_one(".location")
                if not title_elem:
                    continue

                title = title_elem.text.strip()
                href = title_elem["href"]
                link = href if href.startswith("http") else "https://boards.greenhouse.io" + href
                location = location_elem.text.strip() if location_elem else "N/A"

                # Semantic scoring
                full_text = f"{title} {location} {company_name}"
                job_embedding = model.encode(full_text, convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(query_embedding, job_embedding).item()

                # Combo filter
                passes_keyword = required_word in title.lower()
                passes_similarity = similarity >= 0.7

                if passes_keyword or passes_similarity:
                    results.append({
                        "position": title,
                        "company": company_name,
                        "location": location,
                        "url": link,
                        "score": round(similarity, 3)
                    })

        except Exception as e:
            print(f"Error scraping {company_name}: {e}")
            continue

    results.sort(key=lambda x: x["score"], reverse=True)
    return results