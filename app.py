import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.scoring import ResumeJobScorer
import docx
import PyPDF2
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Resume-Job Match Scorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .recommendation-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

def read_pdf(file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def read_docx(file):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return ""

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Resume-Job Match Scorer</h1>', unsafe_allow_html=True)
    
    # Initialize scorer
    if 'scorer' not in st.session_state:
        st.session_state.scorer = ResumeJobScorer()
    
    # Sidebar
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose Mode", 
                                   ["Single Analysis", "Batch Analysis", "About"])
    
    if app_mode == "Single Analysis":
        single_analysis()
    elif app_mode == "Batch Analysis":
        batch_analysis()
    else:
        about_page()

def single_analysis():
    """Single resume-job analysis mode"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Resume Input")
        resume_option = st.radio("Choose resume input method:", 
                               ["Text Input", "File Upload"])
        
        resume_text = ""
        if resume_option == "Text Input":
            resume_text = st.text_area("Paste your resume text here:", 
                                     height=200,
                                     placeholder="Paste your resume content here...")
        else:
            uploaded_file = st.file_uploader("Upload Resume", 
                                           type=['txt', 'pdf', 'docx'],
                                           help="Supported formats: TXT, PDF, DOCX")
            if uploaded_file:
                if uploaded_file.type == "text/plain":
                    resume_text = str(uploaded_file.read(), "utf-8")
                elif uploaded_file.type == "application/pdf":
                    resume_text = read_pdf(uploaded_file)
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    resume_text = read_docx(uploaded_file)
    
    with col2:
        st.subheader("💼 Job Description")
        job_description = st.text_area("Paste job description here:",
                                     height=200,
                                     placeholder="Paste the job description here...")
    
    # Analysis button
    if st.button("🔍 Analyze Match", type="primary"):
        if resume_text and job_description:
            with st.spinner("Analyzing your resume and job description..."):
                results = st.session_state.scorer.analyze_match(resume_text, job_description)
                display_results(results)
        else:
            st.warning("Please provide both resume and job description.")

def display_results(results):
    """Display analysis results"""
    st.markdown("---")
    st.subheader("📈 Analysis Results")
    
    # Score cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="score-card">
            <h3>Overall Match Score</h3>
            <h2 style="color: #1f77b4; text-align: center;">{results['overall_score']}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="score-card">
            <h3>Skill Match Score</h3>
            <h2 style="color: #1f77b4; text-align: center;">{results['skill_match_score']}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        matched_count = len(results['matched_skills'])
        total_job_skills = len(results['job_skills'])
        st.markdown(f"""
        <div class="score-card">
            <h3>Skills Matched</h3>
            <h2 style="color: #1f77b4; text-align: center;">{matched_count}/{total_job_skills}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Visualization
    col1, col2 = st.columns(2)
    
    with col1:
        # Score comparison chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=['Overall Match', 'Skill Match'],
            x=[results['overall_score'], results['skill_match_score']],
            orientation='h',
            marker_color=['#1f77b4', '#ff7f0e']
        ))
        fig.update_layout(
            title="Match Scores Comparison",
            xaxis_title="Score (%)",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Skills radar chart
        if results['job_skills']:
            skills_data = {
                'Category': ['Matched Skills', 'Missing Skills'],
                'Count': [len(results['matched_skills']), len(results['missing_skills'])]
            }
            fig = px.pie(skills_data, values='Count', names='Category',
                        title="Skills Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    # Skills analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Matched Skills")
        if results['matched_skills']:
            for skill in results['matched_skills']:
                st.success(f"• {skill}")
        else:
            st.info("No skills matched")
    
    with col2:
        st.subheader("❌ Missing Skills")
        if results['missing_skills']:
            for skill in results['missing_skills']:
                st.error(f"• {skill}")
        else:
            st.success("All required skills are present!")
    
    # Recommendations
    st.subheader("💡 Recommendations")
    for recommendation in results['recommendations']:
        st.markdown(f"""
        <div class="recommendation-box">
            📌 {recommendation}
        </div>
        """, unsafe_allow_html=True)

def batch_analysis():
    """Batch analysis mode for multiple resumes"""
    st.subheader("📊 Batch Analysis")
    
    st.info("""
    Upload multiple resumes and a job description to analyze them in batch.
    This feature is useful for recruiters or when comparing multiple candidates.
    """)
    
    # Job description input
    job_description = st.text_area("Job Description for Batch Analysis:",
                                 height=150,
                                 placeholder="Paste the job description here...")
    
    # Multiple resume upload
    uploaded_files = st.file_uploader("Upload Multiple Resumes", 
                                    type=['txt', 'pdf', 'docx'],
                                    accept_multiple_files=True,
                                    help="Select multiple files to analyze")
    
    if st.button("Analyze Batch", type="primary") and job_description and uploaded_files:
        results = []
        
        with st.spinner("Analyzing multiple resumes..."):
            for uploaded_file in uploaded_files:
                # Extract text based on file type
                resume_text = ""
                try:
                    if uploaded_file.type == "text/plain":
                        resume_text = str(uploaded_file.read(), "utf-8")
                    elif uploaded_file.type == "application/pdf":
                        resume_text = read_pdf(uploaded_file)
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        resume_text = read_docx(uploaded_file)
                    
                    # Analyze
                    analysis = st.session_state.scorer.analyze_match(resume_text, job_description)
                    results.append({
                        'filename': uploaded_file.name,
                        'overall_score': analysis['overall_score'],
                        'skill_match_score': analysis['skill_match_score'],
                        'matched_skills_count': len(analysis['matched_skills']),
                        'missing_skills_count': len(analysis['missing_skills'])
                    })
                    
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {e}")
        
        # Display batch results
        if results:
            df = pd.DataFrame(results)
            st.subheader("Batch Analysis Results")
            
            # Sort by overall score
            df = df.sort_values('overall_score', ascending=False)
            
            # Display table
            st.dataframe(df, use_container_width=True)
            
            # Visualization
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(df, x='filename', y='overall_score',
                           title="Overall Match Scores by Resume",
                           color='overall_score',
                           color_continuous_scale='Viridis')
                fig.update_layout(xaxis_title="Resume", yaxis_title="Score (%)")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(df, x='overall_score', y='skill_match_score',
                               size='matched_skills_count', color='filename',
                               title="Overall Score vs Skill Match Score",
                               hover_data=['filename'])
                st.plotly_chart(fig, use_container_width=True)

def about_page():
    """About page with project information"""
    st.subheader("About Resume-Job Match Scorer")
    
    st.markdown("""
    ## 🤔 What is this?
    
    The **Resume-Job Match Scorer** is an intelligent application that helps job seekers and recruiters:
    
    - 📊 **Analyze compatibility** between resumes and job descriptions
    - 🔍 **Identify matching skills** and missing requirements
    - 💡 **Provide recommendations** for improvement
    - 📈 **Compare multiple candidates** for the same position
    
    ## 🛠️ How it works
    
    1. **Text Processing**: Cleans and preprocesses resume and job description text
    2. **TF-IDF Vectorization**: Converts text into numerical vectors
    3. **Cosine Similarity**: Calculates semantic similarity between documents
    4. **Skill Extraction**: Identifies and matches technical skills
    5. **Comprehensive Scoring**: Provides overall and skill-based match scores
    
    ## 🎯 Features
    
    - ✅ Single resume analysis
    - ✅ Batch analysis for multiple resumes
    - ✅ Support for multiple file formats (TXT, PDF, DOCX)
    - ✅ Interactive visualizations
    - ✅ Detailed skill matching
    - ✅ Actionable recommendations
    
    ## 🔧 Technology Stack
    
    - **Streamlit** - Web application framework
    - **Scikit-learn** - Machine learning and text processing
    - **NLTK** - Natural language processing
    - **Plotly** - Interactive visualizations
    - **Pandas** - Data manipulation
    
    ## 📝 Usage Tips
    
    - Provide complete and accurate resume text
    - Use detailed job descriptions for better analysis
    - Review both overall scores and specific skill matches
    - Consider the recommendations for resume improvement
    """)

if __name__ == "__main__":
    main()