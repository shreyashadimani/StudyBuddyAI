import os
from openai import OpenAI

# Initialize OpenAI client
# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def summarize_text(text, summary_length="Medium"):
    """
    Summarize text using OpenAI GPT-4o
    
    Args:
        text (str): The text to summarize
        summary_length (str): The desired length of the summary
    
    Returns:
        str: The summarized text
    """
    # Map summary length to a descriptor and approximate word count
    length_map = {
        "Very Short": "extremely concise (around 100 words)",
        "Short": "brief (around 200 words)", 
        "Medium": "moderately detailed (around 350 words)",
        "Detailed": "comprehensive but still summarized (around 500 words)"
    }
    
    prompt = f"""
    Summarize the following text in a {length_map[summary_length]} summary.
    Focus on the key concepts, main ideas, and important details.
    Use clear, straightforward language suitable for a student.
    
    TEXT TO SUMMARIZE:
    {text}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error generating summary: {str(e)}")

def generate_quiz(text, num_questions=5, question_type="Mixed"):
    """
    Generate quiz questions from text using OpenAI GPT-4o
    
    Args:
        text (str): The text to generate questions from
        num_questions (int): Number of questions to generate
        question_type (str): Type of questions to generate
    
    Returns:
        list: List of question dictionaries
    """
    # Map question types to descriptions
    type_map = {
        "Multiple Choice": "multiple-choice questions with 4 options each",
        "True/False": "true/false questions",
        "Fill in the Blank": "fill-in-the-blank questions",
        "Mixed": "a mix of multiple-choice, true/false, and fill-in-the-blank questions"
    }
    
    prompt = f"""
    Create {num_questions} educational {type_map[question_type]} based on the following text.
    Make sure the questions test understanding of key concepts rather than trivial details.
    For each question, provide the correct answer and a brief explanation.
    
    Response should be in valid JSON format with this structure:
    [
        {{
            "question": "Question text",
            "type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option A",
            "explanation": "Brief explanation of why this is correct"
        }},
        {{
            "question": "True/False question text",
            "type": "true_false",
            "answer": "True",
            "explanation": "Brief explanation of why this is correct"
        }},
        {{
            "question": "Fill in the blank: _____ is a key concept.",
            "type": "fill_blank",
            "answer": "Answer",
            "explanation": "Brief explanation of why this is correct"
        }}
    ]
    
    Note: The structure for each question should match its type, and only include relevant fields.
    
    TEXT FOR QUIZ:
    {text}
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"},
            max_tokens=2000
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        # Ensure it's a list
        if not isinstance(result, list):
            if "questions" in result:
                # Sometimes the model might nest the questions
                return result["questions"]
            else:
                # Or create a new list with appropriate structure
                raise ValueError("Invalid response format from API")
        
        return result
    except Exception as e:
        raise Exception(f"Error generating quiz: {str(e)}")

def generate_study_tips(study_profile):
    """
    Generate personalized study tips based on user profile using OpenAI GPT-4o
    
    Args:
        study_profile (dict): User's study preferences and challenges
    
    Returns:
        list: Categorized study tips
    """
    prompt = f"""
    Generate personalized study tips and strategies for a student with the following profile:
    
    Subject: {study_profile['subject']}
    Learning Style: {study_profile['learning_style']}
    Challenges: {', '.join(study_profile['challenges'])}
    Study Time Available: {study_profile['study_time']}
    Study Environment: {study_profile['study_environment']}
    Additional Information: {study_profile['additional_info']}
    
    Provide tips in the following categories:
    1. Study Environment Optimization
    2. Learning Techniques specific to their subject and learning style
    3. Memory and Retention Strategies
    4. Focus and Motivation Tips
    5. Time Management Strategies
    
    Response should be in valid JSON format with this structure:
    [
        {{
            "title": "Category Name",
            "tips": ["Specific tip 1", "Specific tip 2", "Specific tip 3"]
        }},
        {{
            "title": "Another Category",
            "tips": ["Specific tip 1", "Specific tip 2", "Specific tip 3"]
        }}
    ]
    
    Make sure all tips are practical, specific, and tailored to this student's profile.
    Each category should have 3-5 actionable tips.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"},
            max_tokens=2000
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        # Ensure it's a list
        if not isinstance(result, list):
            if "categories" in result:
                # Sometimes the model might nest the categories
                return result["categories"]
            else:
                # Or create a new list with appropriate structure
                raise ValueError("Invalid response format from API")
        
        return result
    except Exception as e:
        raise Exception(f"Error generating study tips: {str(e)}")
