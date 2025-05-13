import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from job_scraper import fetch_jobs  # make sure this uses semantic scoring

st.set_page_config(page_title="AutoApplyX - AI Job Agent", layout="centered")

st.title("🤖 AutoApplyX — Your Personal AI Job Agent")

# Upload Resume
resume = st.file_uploader("📄 Upload Your Resume (PDF)", type=["pdf"])

# Upload Cover Letter
cover_letter = st.file_uploader("📝 Upload Your Cover Letter (TXT or PDF)", type=["txt", "pdf"])

# Keyword Input
job_keywords = st.text_input("🔍 Enter job keywords (e.g. 'AI Engineer', 'LLM', 'NLP')", value="AI Engineer")

applied_jobs = []

# Search and display jobs if everything is uploaded
if resume and cover_letter and job_keywords:
    st.success("✅ Resume and Cover Letter uploaded. Ready to search jobs.")
    
    if st.button("🔎 Find Jobs"):
        jobs = fetch_jobs(job_keywords)

        if not jobs:
            st.warning("No matching jobs found.")
        else:
            st.write(f"📌 Found {len(jobs)} jobs for **{job_keywords}**")
            for i, job in enumerate(jobs):
                with st.expander(f"{job['position']} at {job['company']}"):
                    st.markdown(f"**Location:** {job.get('location', 'N/A')}")
                    st.markdown(f"**Link:** [{job['url']}]({job['url']})")
                    st.markdown(f"**Match Score:** {job.get('score', 'N/A')}")  # Display match score

                    if st.button(f"✅ Apply to {job['company']}", key=f"apply_{i}"):
                        applied_jobs.append({
                            "Company": job["company"],
                            "Job Title": job["position"],
                            "Location": job.get("location", "N/A"),
                            "Applied On": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Link": job["url"]
                        })
                        st.success(f"Applied to {job['company']} successfully!")

# Download Application Log (CSV for user to download)
if applied_jobs:
    df = pd.DataFrame(applied_jobs)
    csv = df.to_csv(index=False).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="applied_jobs.csv">📥 Download Application Log</a>'
    st.markdown(href, unsafe_allow_html=True)