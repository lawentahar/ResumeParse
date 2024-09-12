# resume_parser.py
import re
import spacy
import docx
import pdfplumber
import os
from collections import defaultdict

nlp = spacy.load('en_core_web_sm')

# list of skills
SKILLS = ['Python', 'Java', 'C++', 'Machine Learning', 'Deep Learning', 'NLP', 'Data Analysis', 'SQL', 'Excel']

# extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        raise ValueError(f"Failed to read PDF file: {pdf_path}. Error: {str(e)}")

# extract text from DOCX
def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        raise ValueError(f"Failed to read DOCX file: {docx_path}. Error: {str(e)}")

# extract contact details
def extract_contact_details(text):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'
    
    email = re.findall(email_pattern, text)
    phone = re.findall(phone_pattern, text)
    
    return {
        'email': email[0] if email else None,
        'phone': phone[0][1] if phone else None
    }

# name and organizations using Spacy NLP
def extract_name_and_organizations(text):
    doc = nlp(text)
    name = None
    organizations = []
    
    for ent in doc.ents:
        if ent.label_ == "PERSON" and not name:
            name = ent.text
        elif ent.label_ == "ORG":
            organizations.append(ent.text)
    
    return name, organizations

# extract skills based on predefined list
def extract_skills(text):
    skills_found = []
    for skill in SKILLS:
        if re.search(fr'\b{skill}\b', text, re.IGNORECASE):
            skills_found.append(skill)
    return skills_found

# extract education section
def extract_education(text):
    education_keywords = ['university', 'college', 'bachelor', 'master', 'phd', 'diploma']
    education_info = []
    for line in text.split("\n"):
        if any(keyword in line.lower() for keyword in education_keywords):
            education_info.append(line.strip())
    return education_info

# extract work experience section
def extract_work_experience(text):
    work_experience = []
    work_keywords = ['experience', 'worked', 'employment', 'responsibilities']
    for line in text.split("\n"):
        if any(keyword in line.lower() for keyword in work_keywords):
            work_experience.append(line.strip())
    return work_experience

# parse a resume with error handling
def parse_resume(file_path):
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Check for unsupported file types
    if file_ext == '.pdf':
        try:
            text = extract_text_from_pdf(file_path)
        except ValueError as e:
            return {'error': str(e)}
    elif file_ext == '.docx':
        try:
            text = extract_text_from_docx(file_path)
        except ValueError as e:
            return {'error': str(e)}
    else:
        return {'error': f"Unsupported file type: {file_ext}. Only PDF and DOCX files are supported."}
    
    # Extract key details from text
    try:
        contact_details = extract_contact_details(text)
        name, organizations = extract_name_and_organizations(text)
        skills = extract_skills(text)
        education = extract_education(text)
        work_experience = extract_work_experience(text)
    
        # Store extracted data in a dictionary
        parsed_data = {
            'name': name,
            'email': contact_details['email'],
            'phone': contact_details['phone'],
            'organizations': organizations,
            'skills': skills,
            'education': education,
            'work_experience': work_experience
        }
        return parsed_data
    except Exception as e:
        return {'error': f"Failed to parse resume content: {str(e)}"}

# multiple resumes with error logging
def batch_parse_resumes(resume_folder):
    # Check if directory exists
    if not os.path.exists(resume_folder):
        raise FileNotFoundError(f"Directory '{resume_folder}' does not exist.")
    
    results = defaultdict(list)
    for filename in os.listdir(resume_folder):
        if filename.endswith(('.pdf', '.docx')):
            file_path = os.path.join(resume_folder, filename)
            parsed_resume = parse_resume(file_path)
            results[filename].append(parsed_resume)
    return results

# Example usage
if __name__ == '__main__':
    # Use absolute path to the resume folder
    resume_folder = "/Users/lawentaher/Documents/resumes/"
    
    # Create the directory if it does not exist
    if not os.path.exists(resume_folder):
        os.makedirs(resume_folder)
    
    parsed_resumes = batch_parse_resumes(resume_folder)
    for file, data in parsed_resumes.items():
        print(f"Results for {file}:")
        print(data)
        print("-" * 40)