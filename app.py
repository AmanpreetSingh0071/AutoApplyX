import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from job_scraper import fetch_jobs
from tools import extract_text_from_pdf_file, score_resume

st.set_page_config(page_title="AutoApplyX - AI Job Agent", layout="centered")
st.title("🤖 AutoApplyX — Your Personal AI Job Agent")

# 🔒 Hide GitHub icon, menu, and footer
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "job_results" not in st.session_state:
    st.session_state.job_results = []

if "applied_jobs" not in st.session_state:
    st.session_state.applied_jobs = []

# Upload Resume and Cover Letter
resume = st.file_uploader("📄 Upload Your Resume (PDF)", type=["pdf"])
cover_letter = st.file_uploader("📝 Upload Your Cover Letter (TXT or PDF)", type=["txt", "pdf"])

# Keyword search input
job_keywords = st.text_input("🔍 Enter job keywords (e.g. 'AI Engineer', 'LLM', 'NLP')", value="AI Engineer")

# Job search
if resume and cover_letter and job_keywords:
    st.success("✅ Resume and Cover Letter uploaded. Ready to search jobs.")

    if st.button("🔎 Find Jobs"):
        st.session_state.job_results = fetch_jobs(job_keywords)

# Display jobs if available
if st.session_state.job_results:
    jobs = st.session_state.job_results
    st.write(f"📌 Found {len(jobs)} jobs for **{job_keywords}**")

    for i, job in enumerate(jobs):
        with st.expander(f"{job['position']} at {job['company']}"):
            st.markdown(f"**Location:** {job.get('location', 'N/A')}")
            st.markdown(f"**Link:** [{job['url']}]({job['url']})")
            st.markdown(f"**Match Score:** {job.get('score', 'N/A')}")

            # Resume scoring
            if st.button(f"📊 Score My Resume for {job['position']}", key=f"score_{i}"):
                if resume:
                    resume_text = extract_text_from_pdf_file(resume)
                    job_text = job["position"] + " " + job["company"]
                    score = score_resume(resume_text, job_text)
                    st.success(f"Resume Match Score: {score}")
                else:
                    st.warning("Please upload your resume first.")

            # Apply to job
            if st.button(f"✅ Applied to {job['company']}? Mark the button below to save in below CSV log", key=f"apply_{i}"):
                st.session_state.applied_jobs.append({
                    "Company": job["company"],
                    "Job Title": job["position"],
                    "Location": job.get("location", "N/A"),
                    "Applied On": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Link": job["url"]
                })
                st.success(f"Applied to {job['company']} successfully!")

# Download Application Log
if st.session_state.applied_jobs:
    df = pd.DataFrame(st.session_state.applied_jobs)
    csv = df.to_csv(index=False).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="applied_jobs.csv">📥 Download Application Log</a>'
    st.markdown(href, unsafe_allow_html=True)