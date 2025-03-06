import pdfplumber
import re
import google.generativeai as genai

def extract_resume_sections(pdf_path):
    """Extracts and organizes resume text into structured sections."""
    
    sections = {
        "Name": None,
        "Contact": None,
        "Summary": None,
        "Skills": None,
        "Experience": None,
        "Education": None,
        "Certifications": None,
        "Projects": None
    }
    
    # Extract text from PDF
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text())
    
    text = "\n".join(text)
    
    # Extract Name (Assumes the first line is the candidate's name)
    lines = text.split("\n")
    sections["Name"] = lines[0].strip() if lines else None
    
    # Extract Contact Information (email & phone)
    email = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phone = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    sections["Contact"] = {"Email": email.group() if email else None, "Phone": phone.group() if phone else None}
    
    # Extract Sections based on keywords
    section_order = ["Summary", "Skills", "Experience", "Education", "Certifications", "Projects"]
    section_text = {key: "" for key in section_order}
    
    current_section = None
    for line in lines:
        line_lower = line.lower()
        
        # Identify section headers
        for sec in section_order:
            if re.search(rf"\b{sec.lower()}\b", line_lower):
                current_section = sec
                continue
        
        # Assign text to the current section
        if current_section and line.strip():
            section_text[current_section] += line.strip() + " "
    
    # Update structured sections
    for key in section_text:
        sections[key] = section_text[key].strip() if section_text[key] else None

    return sections

def evaluate_resume(resume_data, job_description):

    # Convert structured resume to formatted text
    resume_text = f"""
    Name: {resume_data.get("Name", "N/A")}
    Contact: {resume_data.get("Contact", "N/A")}
    
    Summary: {resume_data.get("Summary", "N/A")}
    
    Skills: {resume_data.get("Skills", "N/A")}
    
    Experience: {resume_data.get("Experience", "N/A")}
    
    Education: {resume_data.get("Education", "N/A")}
    
    Certifications: {resume_data.get("Certifications", "N/A")}
    
    Projects: {resume_data.get("Projects", "N/A")}
    """
    
    # Define LLM Prompt for Relevance Percentage
    relevance_prompt = f"""
    Given the following resume and job description, determine the relevance percentage (0-100%). 
    Base your evaluation on skill match, experience, and job fit.

    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Return only a number without any text.
    """
    
    # Define LLM Prompt for Resume Review
    review_prompt = f"""
    Review the following resume against the job description. Provide:
    1. Strengths
    2. Weaknesses
    3. Areas for improvement

    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Your response should be structured and clear.
    """
    
    # Generate responses
    model = genai.GenerativeModel("gemini-1.5-pro-002")
    
    relevance_response = model.generate_content(relevance_prompt).text.strip()
    review_response = model.generate_content(review_prompt).text.strip()
    
    # Convert relevance response to integer
    try:
        # Use regex to find the first number in the string.
        match = re.search(r'\d+', relevance_response)
        if match:
          relevance_percentage = int(match.group(0))
        else:
          relevance_percentage = None
    except ValueError:
        relevance_percentage = None  # Fallback in case of an unexpected response
    
    return {
        "Relevance Percentage": relevance_percentage,
        "Resume Review": review_response
    }