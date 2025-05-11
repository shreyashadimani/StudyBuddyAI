import streamlit as st
import os
from utils import summarize_text, generate_quiz, generate_study_tips

# Page configuration
st.set_page_config(
    page_title="Study Buddy: AI-Powered Learning Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom logo SVG
def display_logo():
    with open("assets/logo.svg", "r") as f:
        logo_svg = f.read()
    st.markdown(f"""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        {logo_svg}
    </div>
    """, unsafe_allow_html=True)

# App header
st.title("Study Buddy: AI-Powered Learning Assistant")
st.subheader("Your personal AI assistant for better studying")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "home"
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "tips" not in st.session_state:
    st.session_state.tips = []

# Sidebar navigation
st.sidebar.title("Navigation")

# Navigation buttons
if st.sidebar.button("Home", use_container_width=True):
    st.session_state.page = "home"
if st.sidebar.button("Text Summarizer", use_container_width=True):
    st.session_state.page = "summarizer"
if st.sidebar.button("Quiz Generator", use_container_width=True):
    st.session_state.page = "quiz"
if st.sidebar.button("Study Tips", use_container_width=True):
    st.session_state.page = "tips"

# About section in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("About Study Buddy")
st.sidebar.info(
    "Study Buddy uses AI to help you study more effectively. "
    "Summarize your notes, generate practice quizzes, and get "
    "personalized study tips."
)

# Check for API key
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    st.error(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
    )
    st.stop()

# Home page
if st.session_state.page == "home":
    st.markdown("""
    ## Welcome to Study Buddy! 👋
    
    This AI-powered learning assistant is designed to help you study more effectively.
    
    ### Features:
    - **Text Summarizer**: Condense your notes or textbook content into concise summaries
    - **Quiz Generator**: Create practice questions from your study material
    - **Study Tips**: Get personalized study recommendations based on your preferences
    
    Use the navigation menu on the left to get started!
    """)
    
    st.markdown("---")
    
    # Display feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📝 Text Summarizer")
        st.markdown("Paste your notes or textbook content to get a concise summary.")
        if st.button("Try Summarizer", key="try_summarizer"):
            st.session_state.page = "summarizer"
            st.rerun()
    
    with col2:
        st.markdown("### 🧠 Quiz Generator")
        st.markdown("Generate practice questions from your study material.")
        if st.button("Try Quiz Generator", key="try_quiz"):
            st.session_state.page = "quiz"
            st.rerun()
    
    with col3:
        st.markdown("### 💡 Study Tips")
        st.markdown("Get personalized study recommendations based on your preferences.")
        if st.button("Try Study Tips", key="try_tips"):
            st.session_state.page = "tips"
            st.rerun()

# Text Summarizer page
elif st.session_state.page == "summarizer":
    st.header("Text Summarizer")
    st.markdown("Paste your notes or textbook content to get a concise summary.")
    
    # Input text area
    text_input = st.text_area(
        "Enter the text you want to summarize:",
        height=200,
        placeholder="Paste your notes or textbook content here..."
    )
    
    # Summary length options
    summary_length = st.select_slider(
        "Summary Length",
        options=["Very Short", "Short", "Medium", "Detailed"],
        value="Medium"
    )
    
    # Process text when button is clicked
    if st.button("Generate Summary"):
        if text_input:
            with st.spinner("Generating summary..."):
                try:
                    summary = summarize_text(text_input, summary_length)
                    st.session_state.summary = summary
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter some text to summarize.")
    
    # Display summary if available
    if st.session_state.summary:
        st.subheader("Summary:")
        st.write(st.session_state.summary)
        
        # Download button for summary
        st.download_button(
            label="Download Summary",
            data=st.session_state.summary,
            file_name="summary.txt",
            mime="text/plain"
        )
        
        # Option to generate quiz from summary
        if st.button("Generate Quiz from Summary"):
            st.session_state.page = "quiz"
            st.rerun()

# Quiz Generator page
elif st.session_state.page == "quiz":
    st.header("Quiz Generator")
    st.markdown("Generate practice questions from your study material.")
    
    # Input text area (with option to use summary if available)
    if st.session_state.summary and st.checkbox("Use my previous summary"):
        text_input = st.session_state.summary
        st.success("Using your previous summary as input.")
    else:
        text_input = st.text_area(
            "Enter the text to generate questions from:",
            height=200,
            placeholder="Paste your notes or textbook content here..."
        )
    
    # Quiz options
    col1, col2 = st.columns(2)
    with col1:
        num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=5)
    with col2:
        question_type = st.selectbox(
            "Question Type",
            options=["Multiple Choice", "True/False", "Fill in the Blank", "Mixed"]
        )
    
    # Generate quiz button
    if st.button("Generate Quiz"):
        if text_input:
            with st.spinner("Generating quiz questions..."):
                try:
                    quiz = generate_quiz(text_input, num_questions, question_type)
                    st.session_state.quiz = quiz
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter some text to generate questions from.")
    
    # Display quiz if available
    if st.session_state.quiz:
        st.subheader("Practice Quiz:")
        
        # Count for correct answers
        if "correct_answers" not in st.session_state:
            st.session_state.correct_answers = 0
            st.session_state.submitted = False
            st.session_state.answers = {}
        
        # Display each question
        for idx, q in enumerate(st.session_state.quiz):
            st.markdown(f"**Question {idx+1}**: {q['question']}")
            
            # Different display based on question type
            if q['type'] == 'multiple_choice':
                answer = st.radio(
                    f"Select answer for question {idx+1}:",
                    options=q['options'],
                    key=f"q{idx}"
                )
                if f"q{idx}" not in st.session_state.answers:
                    st.session_state.answers[f"q{idx}"] = None
            
            elif q['type'] == 'true_false':
                answer = st.radio(
                    f"Select answer for question {idx+1}:",
                    options=["True", "False"],
                    key=f"q{idx}"
                )
                if f"q{idx}" not in st.session_state.answers:
                    st.session_state.answers[f"q{idx}"] = None
            
            elif q['type'] == 'fill_blank':
                answer = st.text_input(
                    f"Your answer for question {idx+1}:",
                    key=f"q{idx}"
                )
                if f"q{idx}" not in st.session_state.answers:
                    st.session_state.answers[f"q{idx}"] = None
            
            st.markdown("---")
        
        # Submit button for quiz
        if st.button("Submit Quiz"):
            st.session_state.submitted = True
            st.session_state.correct_answers = 0
            
            # Check answers
            for idx, q in enumerate(st.session_state.quiz):
                user_answer = st.session_state[f"q{idx}"]
                st.session_state.answers[f"q{idx}"] = user_answer
                
                if q['type'] == 'multiple_choice':
                    if user_answer == q['answer']:
                        st.session_state.correct_answers += 1
                
                elif q['type'] == 'true_false':
                    if user_answer.lower() == q['answer'].lower():
                        st.session_state.correct_answers += 1
                
                elif q['type'] == 'fill_blank':
                    if user_answer.lower() == q['answer'].lower():
                        st.session_state.correct_answers += 1
            
            st.rerun()
        
        # Display results if submitted
        if st.session_state.submitted:
            st.subheader("Quiz Results:")
            st.success(f"You got {st.session_state.correct_answers} out of {len(st.session_state.quiz)} correct!")
            
            for idx, q in enumerate(st.session_state.quiz):
                st.markdown(f"**Question {idx+1}**: {q['question']}")
                st.markdown(f"Your answer: {st.session_state.answers[f'q{idx}']}")
                st.markdown(f"Correct answer: {q['answer']}")
                
                if q.get('explanation'):
                    st.markdown(f"Explanation: {q['explanation']}")
                
                st.markdown("---")
            
            # Reset button
            if st.button("Take Another Quiz"):
                st.session_state.submitted = False
                st.session_state.answers = {}
                st.session_state.quiz = []
                st.rerun()

# Study Tips page
elif st.session_state.page == "tips":
    st.header("Personalized Study Tips")
    st.markdown("Get customized study recommendations based on your preferences and needs.")
    
    # Study preferences form
    with st.form("study_preferences_form"):
        st.subheader("Tell us about your study habits")
        
        # Subject and learning style
        col1, col2 = st.columns(2)
        with col1:
            subject = st.selectbox(
                "What subject are you studying?",
                ["Math", "Science", "History", "Literature", "Languages", "Computer Science", "Other"]
            )
        
        with col2:
            learning_style = st.selectbox(
                "What's your preferred learning style?",
                ["Visual", "Auditory", "Reading/Writing", "Kinesthetic", "I'm not sure"]
            )
        
        # Study challenges
        challenges = st.multiselect(
            "What challenges do you face when studying?",
            [
                "Staying focused", 
                "Remembering information",
                "Understanding complex concepts",
                "Finding motivation",
                "Managing study time",
                "Test anxiety",
                "Information overload"
            ]
        )
        
        # Study schedule
        col1, col2 = st.columns(2)
        with col1:
            study_time = st.select_slider(
                "How much time do you typically spend studying per day?",
                options=["Less than 1 hour", "1-2 hours", "2-3 hours", "3-4 hours", "4+ hours"]
            )
        
        with col2:
            study_environment = st.selectbox(
                "Where do you usually study?",
                ["At home", "Library", "Coffee shop", "School/Campus", "Different places"]
            )
        
        # Additional notes
        additional_info = st.text_area(
            "Anything else you'd like to share about your study habits or goals?",
            placeholder="e.g., I'm preparing for a big exam in 2 weeks..."
        )
        
        # Submit form
        submitted = st.form_submit_button("Get Personalized Study Tips")
    
    # Process form submission
    if submitted:
        with st.spinner("Generating your personalized study tips..."):
            try:
                # Compile study profile
                study_profile = {
                    "subject": subject,
                    "learning_style": learning_style,
                    "challenges": challenges,
                    "study_time": study_time,
                    "study_environment": study_environment,
                    "additional_info": additional_info
                }
                
                # Generate personalized tips
                tips = generate_study_tips(study_profile)
                st.session_state.tips = tips
            except Exception as e:
                st.error(f"An error occurred: {e}")
    
    # Display tips if available
    if st.session_state.tips:
        st.subheader("Your Personalized Study Tips:")
        
        # Display each category of tips
        for category in st.session_state.tips:
            with st.expander(f"{category['title']}", expanded=True):
                for tip in category['tips']:
                    st.markdown(f"- {tip}")
        
        # Option to download tips
        tips_text = ""
        for category in st.session_state.tips:
            tips_text += f"# {category['title']}\n\n"
            for tip in category['tips']:
                tips_text += f"- {tip}\n"
            tips_text += "\n"
        
        st.download_button(
            label="Download Your Study Tips",
            data=tips_text,
            file_name="study_tips.txt",
            mime="text/plain"
        )
