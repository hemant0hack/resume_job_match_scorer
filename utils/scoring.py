import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import string

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

class ResumeJobScorer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and short tokens, then lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def calculate_similarity(self, resume_text, job_description):
        """Calculate cosine similarity between resume and job description"""
        # Preprocess texts
        processed_resume = self.preprocess_text(resume_text)
        processed_job = self.preprocess_text(job_description)
        
        if not processed_resume or not processed_job:
            return 0.0
        
        # Create TF-IDF vectors
        try:
            tfidf_matrix = self.vectorizer.fit_transform([processed_resume, processed_job])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return min(similarity[0][0] * 100, 100)  # Cap at 100%
        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return 0.0
    
    def extract_skills(self, text):
        """Extract potential skills from text"""
        common_skills = [
            'python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'angular',
            'node', 'express', 'django', 'flask', 'mongodb', 'mysql', 'postgresql',
            'aws', 'azure', 'docker', 'kubernetes', 'git', 'jenkins', 'linux', 'unix',
            'machine learning', 'data analysis', 'statistics', 'tableau', 'power bi',
            'excel', 'word', 'powerpoint', 'project management', 'agile', 'scrum',
            'communication', 'leadership', 'teamwork', 'problem solving', 'analytical',
            'c++', 'c#', 'php', 'ruby', 'go', 'swift', 'kotlin', 'typescript',
            'vue', 'angularjs', 'jquery', 'bootstrap', 'sass', 'less',
            'rest', 'api', 'graphql', 'microservices', 'ci/cd', 'devops',
            'tensorflow', 'pytorch', 'keras', 'pandas', 'numpy', 'scikit',
            'big data', 'hadoop', 'spark', 'kafka', 'elasticsearch',
            'ui/ux', 'photoshop', 'figma', 'adobe', 'illustrator'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))  # Remove duplicates
    
    def analyze_match(self, resume_text, job_description):
        """Comprehensive analysis of resume-job match"""
        similarity_score = self.calculate_similarity(resume_text, job_description)
        
        resume_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_description)
        
        # Calculate skill match
        if job_skills:
            matched_skills = set(resume_skills) & set(job_skills)
            skill_match_percentage = (len(matched_skills) / len(job_skills)) * 100
        else:
            skill_match_percentage = 0
            matched_skills = set()
        
        # Missing skills
        missing_skills = set(job_skills) - set(resume_skills)
        
        # Overall score (weighted average)
        overall_score = (similarity_score * 0.6) + (skill_match_percentage * 0.4)
        
        return {
            'overall_score': round(overall_score, 2),
            'similarity_score': round(similarity_score, 2),
            'skill_match_score': round(skill_match_percentage, 2),
            'resume_skills': resume_skills,
            'job_skills': job_skills,
            'matched_skills': list(matched_skills),
            'missing_skills': list(missing_skills),
            'recommendations': self.generate_recommendations(missing_skills, overall_score)
        }
    
    def generate_recommendations(self, missing_skills, score):
        """Generate improvement recommendations"""
        recommendations = []
        
        if score < 40:
            recommendations.append("❌ Low match: Consider significantly tailoring your resume to better match the job requirements")
        elif score < 60:
            recommendations.append("⚠️ Moderate match: Your resume needs improvements to better align with the job description")
        elif score < 80:
            recommendations.append("✅ Good match: Your resume aligns well, but there's room for improvement")
        else:
            recommendations.append("🎉 Excellent match! Your resume strongly aligns with the job requirements")
        
        if missing_skills:
            skills_list = ', '.join(missing_skills[:5])  # Show max 5 skills
            recommendations.append(f"📚 Consider highlighting these skills: {skills_list}")
        
        if score < 70:
            recommendations.append("💡 Use more keywords from the job description in your resume")
            recommendations.append("🎯 Focus on quantifying your achievements with numbers and metrics")
        
        return recommendations