import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import string

# Simple version without NLTK
class SimpleResumeScorer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    def preprocess_text(self, text):
        """Basic text preprocessing"""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'\d+', '', text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text
    
    def calculate_match(self, resume_text, job_text):
        """Calculate match score"""
        processed_resume = self.preprocess_text(resume_text)
        processed_job = self.preprocess_text(job_text)
        
        if not processed_resume or not processed_job:
            return 0
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform([processed_resume, processed_job])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return round(similarity[0][0] * 100, 2)
        except:
            return 0

def main():
    st.set_page_config(page_title="Resume Matcher", layout="wide")
    st.title("📊 Simple Resume-Job Matcher")
    
    scorer = SimpleResumeScorer()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Resume")
        resume_text = st.text_area("Paste your resume:", height=200)
    
    with col2:
        st.subheader("💼 Job Description")
        job_text = st.text_area("Paste job description:", height=200)
    
    if st.button("Calculate Match Score") and resume_text and job_text:
        score = scorer.calculate_match(resume_text, job_text)
        
        st.markdown("---")
        st.subheader("Results")
        
        # Display score
        st.metric("Match Score", f"{score}%")
        
        # Progress bar
        st.progress(score/100)
        
        # Simple recommendations
        if score < 40:
            st.error("Low match - Consider tailoring your resume to the job description")
        elif score < 70:
            st.warning("Moderate match - Some improvements needed")
        else:
            st.success("Good match! Your resume aligns well with the job")

if __name__ == "__main__":
    main()