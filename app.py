import streamlit as st
import os
import pdfplumber
import re
import google.generativeai as genai
import argparse
from utils import *
import base64

# Parse command-line arguments for API key
parser = argparse.ArgumentParser(description="Resume Evaluator App")
parser.add_argument("--api_key", type=str, required=True, help="Google Gemini API Key")
args = parser.parse_args()

# Configure Gemini API
genai.configure(api_key=args.api_key)

# Custom Styling
st.markdown("""
    <style>
        
        /* Title Styling */
        h1 {
            text-align: center;
            font-size: 3rem;
            font-weight: bold;
            color: #4388f7;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
        }
        
        /* Sidebar Styling */
        .css-1d391kg {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
        }

        /* Buttons */
        div.stButton > button {
            width: 100%;
            background-color: #FF5733;
            color: white;
            font-size: 18px;
            padding: 12px;
            border-radius: 10px;
            transition: 0.3s;
        }
        
        div.stButton > button:hover {
            background-color: #C70039;
        }

        /* Textbox Styling */
        textarea {
            border: 2px solid #FF5733;
            border-radius: 8px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Main Function
def main():
    # Add a GIF for header
    st.image("assets/header.png", use_column_width=True)

    # Upload PDF/DOCX File
    uploaded_file = st.file_uploader("📄 Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

    # Job Description Input
    job_description = st.text_area("📝 Paste Job Description Here", height=150)

    # Sidebar for Branding
    with st.sidebar:
        st.image("assets/logo.png", width=200)
        st.markdown("### 🤖 AI-Powered by Gemini")
        st.markdown("👨‍💻 Built for Job Seekers & Recruiters")
        st.markdown("🔍 Get Instant Resume Feedback!")

    # Evaluate Button
    if uploaded_file and job_description:
        if st.button("🔎 Evaluate Resume"):
            with st.spinner("🤖 AI is analyzing... Please wait!"):
                # Save uploaded file temporarily
                file_ext = uploaded_file.name.split(".")[-1].lower()
                temp_path = f"temp_resume.{file_ext}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())

                # Extract Resume Sections
                resume_data = extract_resume_sections(temp_path)

                # Evaluate Resume
                result = evaluate_resume(resume_data, job_description)

                # Display Results
                st.markdown("## ✅ Evaluation Results")
                st.markdown(f"### 🔥 **Relevance Score:** `{result['Relevance Percentage']}%`")
                st.markdown("### 📌 **Resume Review**")
                st.write(result["Resume Review"])

                # Cleanup temporary file
                os.remove(temp_path)

if __name__ == "__main__":
    main()
