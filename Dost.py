import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os
import google.generativeai as genai
from datetime import datetime
import json

genai_api_key = "AIzaSyCsMnbjIqxwaSOW4MvFQK9gIGHJEawHklU"
if not genai_api_key:
    st.error("Please set up your GEMINI_API_KEY in the .env file")
    st.stop()

genai.configure(api_key=genai_api_key)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def load_sample_inventory():
    """Load sample book inventory for demonstration"""
    return {
        "fiction": ["The Great Gatsby", "1984", "Pride and Prejudice"],
        "non_fiction": ["Sapiens", "Atomic Habits", "Think and Grow Rich"],
        "textbooks": ["Introduction to Python", "Data Science Basics", "Web Development 101"]
    }

def validate_date(date_str):
    """Validate date format"""
    try:
        return bool(datetime.strptime(date_str, "%Y-%m-%d"))
    except ValueError:
        return False

def generate_response(prompt, max_retries=3):
    """Generate response with retry mechanism"""
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt == max_retries - 1:
                return f"Error: Unable to generate response after {max_retries} attempts. {str(e)}"
            continue

def create_study_schedule(syllabus, exam_dates, free_time):
    """Create a structured study schedule"""
    try:
        free_time = float(free_time)
        if not syllabus or not exam_dates or free_time <= 0:
            return "Please provide all required information with valid values."
        
        if not validate_date(exam_dates):
            return "Please enter a valid exam date in YYYY-MM-DD format."

        prompt = f"""
        Create a detailed study schedule with the following parameters:
        - Syllabus topics: {syllabus}
        - Exam date: {exam_dates}
        - Available study time: {free_time} hours per day
        
        Please include:
        1. Daily breakdown of topics
        2. Recommended study intervals
        3. Short breaks and revision periods
        4. Progress tracking milestones
        """
        return generate_response(prompt)
    except ValueError:
        return "Please enter a valid number for free study hours."

def analyze_pdf_content(pdf_text):
    """Analyze PDF content and generate revision tips"""
    prompt = f"""
    Analyze the following text and provide:
    1. Key concepts and important points
    2. Suggested revision strategy
    3. Practice questions
    4. Memory techniques for important terms
    
    Text: {pdf_text[:1000]}...
    """
    return generate_response(prompt)

def process_bookstore_query(query, inventory):
    """Process bookstore related queries"""
    prompt = f"""
    Answer the following query about the bookstore:
    Query: {query}
    
    Available inventory categories:
    {json.dumps(inventory, indent=2)}
    
    Please provide a helpful, detailed response including:
    - Book availability if asked
    - Relevant recommendations
    - Any additional useful information
    """
    return generate_response(prompt)

# Main UI
st.set_page_config(page_title="AI Mentor & Bookstore Assistant", layout="wide")
st.title("📚 AI Mentor and Bookstore Assistant")

# Sidebar configuration
st.sidebar.header("Settings")
options = ["Time-Saving Study Planner", "Bookstore Inventory Manager"]
choice = st.sidebar.selectbox("Choose Chatbot Mode", options)

# Main application logic
if choice == "Time-Saving Study Planner":
    st.header("📆 Study Schedule Assistant")
    
    col1, col2 = st.columns(2)
    
    with col1:
        syllabus = st.text_area("Enter the syllabus topics:", 
                               help="List your topics separated by commas or new lines")
        exam_dates = st.text_input("Enter exam date:", 
                                 placeholder="YYYY-MM-DD",
                                 help="Enter the date in YYYY-MM-DD format")
    
    with col2:
        free_time = st.text_input("Available study hours per day:",
                                placeholder="e.g., 4.5",
                                help="Enter the number of hours you can study each day")
        
        if st.button("Generate Study Schedule", type="primary"):
            with st.spinner("Creating your personalized study schedule..."):
                schedule = create_study_schedule(syllabus, exam_dates, free_time)
                st.success("Schedule generated successfully!")
                st.markdown(schedule)

else:  # Bookstore Inventory Manager
    st.header("🏪 Bookstore Inventory Management Assistant")
    
    # Load sample inventory
    inventory = load_sample_inventory()
    
    # Display available categories
    st.subheader("Available Book Categories")
    for category, books in inventory.items():
        st.write(f"**{category.title()}:** {', '.join(books)}")
    
    query = st.text_input("Ask about books, recommendations, or store information:",
                         placeholder="e.g., Do you have any Python programming books?")
    
    if st.button("Get Response", type="primary"):
        with st.spinner("Processing your query..."):
            response = process_bookstore_query(query, inventory)
            st.markdown(response)
    
    # PDF Analysis Section
    st.subheader("📑 Book Content Analysis")
    uploaded_file = st.file_uploader(
        "Upload a PDF for analysis (revision tips or study guide)",
        type="pdf",
        help="Upload a PDF to get personalized revision tips and study guidance"
    )
    
    if uploaded_file:
        try:
            with st.spinner("Analyzing PDF content..."):
                pdf_reader = PdfReader(uploaded_file)
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
                
                revision_tips = analyze_pdf_content(text_content)
                st.success("Analysis complete!")
                st.markdown(revision_tips)
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")

# Display chat history
if st.session_state.chat_history:
    st.subheader("Recent Interactions")
    for chat in st.session_state.chat_history[-5:]:  # Show last 5 interactions
        st.text(chat)
