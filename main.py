from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json

app = Flask(__name__)
CORS(app)

# ⚠️ আপনার Gemini API key এখানে দিন
GEMINI_API_KEY = 'AIzaSyD6BQNkAWwDFRu3NQGVPY9u6A9XqYQjXAc'

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Language configurations
LANGUAGE_NAMES = {
    'en': 'English',
    'bn': 'Bengali (বাংলা)',
    'hi': 'Hindi (हिंदी)',
    'ta': 'Tamil (தமிழ்)',
    'te': 'Telugu (తెలుగు)',
    'mr': 'Marathi (मराठी)',
    'gu': 'Gujarati (ગુજરાતી)',
    'kn': 'Kannada (ಕನ್ನಡ)',
    'ml': 'Malayalam (മലയാളം)',
    'pa': 'Punjabi (ਪੰਜਾਬੀ)'
}

def generate_quiz(category, level, count, language):
    """Generate quiz questions using Gemini AI in specified language"""
    
    lang_instruction = {
        'en': 'in English language',
        'bn': 'in Bengali language (বাংলা)',
        'hi': 'in Hindi language (हिंदी)',
        'ta': 'in Tamil language (தமிழ்)',
        'te': 'in Telugu language (తెలుగు)',
        'mr': 'in Marathi language (मराठी)',
        'gu': 'in Gujarati language (ગુજરાતી)',
        'kn': 'in Kannada language (ಕನ್ನಡ)',
        'ml': 'in Malayalam language (മലയാളം)',
        'pa': 'in Punjabi language (ਪੰਜਾਬੀ)'
    }
    
    prompt = f"""Generate {count} multiple choice quiz questions {lang_instruction.get(language, 'in English')}.
    
Category: {category}
Difficulty Level: {level}
Language: {LANGUAGE_NAMES.get(language, 'English')}

Requirements:
- ALL questions, options, and explanations must be in {LANGUAGE_NAMES.get(language, 'English')}
- Each question should have 4 options (A, B, C, D)
- Provide the correct answer
- Questions should be {level} difficulty level
- For "Country Quiz": questions about specific countries (geography, capital, culture, flag, currency, famous landmarks, leaders, etc.)
- For "World Quiz": questions about world facts, international events, global geography, famous personalities, world history, etc.

Return ONLY a valid JSON array in this exact format:
[
  {{
    "question": "Question text in {LANGUAGE_NAMES.get(language, 'English')}?",
    "options": {{
      "A": "Option 1 in {LANGUAGE_NAMES.get(language, 'English')}",
      "B": "Option 2 in {LANGUAGE_NAMES.get(language, 'English')}",
      "C": "Option 3 in {LANGUAGE_NAMES.get(language, 'English')}",
      "D": "Option 4 in {LANGUAGE_NAMES.get(language, 'English')}"
    }},
    "correct_answer": "A",
    "explanation": "Explanation in {LANGUAGE_NAMES.get(language, 'English')}"
  }}
]

IMPORTANT: 
- Do not include any markdown formatting, backticks, or extra text
- Return only the JSON array
- All text must be in {LANGUAGE_NAMES.get(language, 'English')}
- Make questions interesting and diverse"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Remove markdown formatting if present
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        text = text.strip()
        
        questions = json.loads(text)
        return questions
    except Exception as e:
        print(f"Error generating quiz: {e}")
        # Fallback questions based on language
        fallback_questions = {
            'en': [{
                "question": "What is the capital of India?",
                "options": {"A": "Mumbai", "B": "Delhi", "C": "Kolkata", "D": "Chennai"},
                "correct_answer": "B",
                "explanation": "New Delhi is the capital of India."
            }],
            'bn': [{
                "question": "ভারতের রাজধানী কোথায়?",
                "options": {"A": "মুম্বাই", "B": "দিল্লি", "C": "কলকাতা", "D": "চেন্নাই"},
                "correct_answer": "B",
                "explanation": "নতুন দিল্লি ভারতের রাজধানী।"
            }],
            'hi': [{
                "question": "भारत की राजधानी कहाँ है?",
                "options": {"A": "मुंबई", "B": "दिल्ली", "C": "कोलकाता", "D": "चेन्नई"},
                "correct_answer": "B",
                "explanation": "नई दिल्ली भारत की राजधानी है।"
            }],
            'ta': [{
                "question": "இந்தியாவின் தலைநகரம் எது?",
                "options": {"A": "மும்பை", "B": "டெல்லி", "C": "கொல்கத்தா", "D": "சென்னை"},
                "correct_answer": "B",
                "explanation": "புது டெல்லி இந்தியாவின் தலைநகரம்."
            }],
            'te': [{
                "question": "భారతదేశ రాజధాని ఏది?",
                "options": {"A": "ముంబై", "B": "ఢిల్లీ", "C": "కోల్‌కతా", "D": "చెన్నై"},
                "correct_answer": "B",
                "explanation": "న్యూఢిల్లీ భారతదేశ రాజధాని."
            }]
        }
        return fallback_questions.get(language, fallback_questions['en'])

@app.route('/api/generate-quiz', methods=['POST'])
def create_quiz():
    """API endpoint to generate quiz questions"""
    try:
        data = request.get_json()
        
        category = data.get('category', 'World Quiz')
        level = data.get('level', 'Normal')
        count = data.get('count', 5)
        language = data.get('language', 'en')
        
        # Validate inputs
        if category not in ['Country Quiz', 'World Quiz']:
            return jsonify({'error': 'Invalid category'}), 400
        
        if level not in ['Easy', 'Normal', 'Hard']:
            return jsonify({'error': 'Invalid level'}), 400
        
        if count < 1 or count > 20:
            return jsonify({'error': 'Count must be between 1 and 20'}), 400
        
        if language not in LANGUAGE_NAMES:
            return jsonify({'error': 'Invalid language'}), 400
        
        questions = generate_quiz(category, level, count, language)
        
        return jsonify({
            'success': True,
            'questions': questions,
            'category': category,
            'level': level,
            'language': language
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get available languages"""
    return jsonify({
        'success': True,
        'languages': LANGUAGE_NAMES
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Quiz API is running',
        'supported_languages': list(LANGUAGE_NAMES.keys())
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Quiz API Backend - Multi-Language Support',
        'endpoints': {
            '/api/generate-quiz': 'POST - Generate quiz questions',
            '/api/languages': 'GET - Get available languages',
            '/api/health': 'GET - Health check'
        },
        'supported_languages': LANGUAGE_NAMES
    })

@app.route('/', methods=['GET'])
def home():
    """Serve the frontend HTML"""
    return render_template('index.html')
    
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
