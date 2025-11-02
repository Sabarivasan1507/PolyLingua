from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import requests
import json
import random
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your-secret-key-here'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ====== DATABASE MODELS ======
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(50))
    title = db.Column(db.String(150))
    content = db.Column(db.Text)
    audio_link = db.Column(db.String(200))

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer)
    question = db.Column(db.Text)
    options = db.Column(db.Text)
    correct_answer = db.Column(db.String(150))

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    lesson_id = db.Column(db.Integer)
    completed = db.Column(db.Boolean, default=False)
    quiz_score = db.Column(db.Integer, default=0)

class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    source_lang = db.Column(db.String(50))
    target_lang = db.Column(db.String(50))
    input_text = db.Column(db.Text)
    translated_text = db.Column(db.Text)

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mother_language = db.Column(db.String(50))
    learning_language = db.Column(db.String(50))
    question_text = db.Column(db.Text)
    options = db.Column(db.Text)
    correct_answer = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=db.func.now())

# ====== SIMPLE AGENT SYSTEM ======
class SimpleAgent:
    def __init__(self, user_id):
        self.user_id = user_id
    
    def chat(self, message):
        """Simple chat response without database dependencies"""
        responses = [
            "Hello! I'm your language learning assistant. How can I help you today?",
            "Great question! I recommend starting with basic vocabulary lessons.",
            "Practice makes perfect! Try taking a quiz to test your knowledge.",
            "I'm here to help you learn languages. What would you like to practice?",
            "Remember to review previous lessons to reinforce your learning!",
            "Language learning is a journey. Take it one step at a time!",
            "Try using the translation feature to practice sentence construction.",
            "Don't forget to practice speaking aloud for better pronunciation!"
        ]
        return random.choice(responses)
    
    def get_analytics(self):
        """Simple analytics without database queries"""
        return {
            'completed_lessons': random.randint(0, 10),
            'streak_days': random.randint(0, 30),
            'average_score': random.randint(50, 95)
        }

# ====== LOGIN MANAGER ======
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ====== GEMINI AI INTEGRATION ======
def generate_quiz_questions(mother_language, learning_language, num_questions=10):
    """Generate quiz questions using Gemini AI"""
    
    prompt = f"""
    Create {num_questions} basic language learning quiz questions for someone learning {learning_language} with {mother_language} as their native language.
    
    Requirements:
    - Questions should be in {mother_language}
    - Multiple choice options should be in {learning_language}
    - Questions should cover basic vocabulary, common phrases, and simple grammar
    - Make questions appropriate for beginners
    - Provide exactly 4 options for each question
    - Format your response as a JSON array where each object has:
      - "question": the question in {mother_language}
      - "options": array of 4 options in {learning_language}
      - "correct_answer": the correct option in {learning_language}
    
    Example for mother_language=English, learning_language=Spanish:
    {{
      "question": "How do you say 'Hello' in Spanish?",
      "options": ["Hola", "Adiós", "Gracias", "Por favor"],
      "correct_answer": "Hola"
    }}
    
    Return ONLY the JSON array, no other text.
    """
    
    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            headers={
                'Content-Type': 'application/json',
                'X-goog-api-key': 'AIzaSyBACmRnjoJB-Ycq9-kEDenpokt7jRRHkAs'
            },
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            text_response = result['candidates'][0]['content']['parts'][0]['text']
            # Clean the response (remove markdown code blocks if present)
            text_response = text_response.replace('```json', '').replace('```', '').strip()
            questions = json.loads(text_response)
            return questions
        else:
            print(f"Gemini API error: {response.status_code}")
            return generate_fallback_questions(mother_language, learning_language, num_questions)
            
    except Exception as e:
        print(f"Error generating questions: {e}")
        return generate_fallback_questions(mother_language, learning_language, num_questions)

def generate_fallback_questions(mother_language, learning_language, num_questions):
    """Fallback questions if Gemini API fails"""
    fallback_data = {
        'english': {
            'spanish': [
                {
                    "question": "How do you say 'Hello' in Spanish?",
                    "options": ["Hola", "Adiós", "Gracias", "Por favor"],
                    "correct_answer": "Hola"
                },
                {
                    "question": "How do you say 'Thank you' in Spanish?",
                    "options": ["Hola", "Adiós", "Gracias", "Por favor"],
                    "correct_answer": "Gracias"
                },
                {
                    "question": "How do you say 'Goodbye' in Spanish?",
                    "options": ["Hola", "Adiós", "Gracias", "Por favor"],
                    "correct_answer": "Adiós"
                },
                {
                    "question": "How do you say 'Please' in Spanish?",
                    "options": ["Hola", "Adiós", "Gracias", "Por favor"],
                    "correct_answer": "Por favor"
                }
            ],
            'french': [
                {
                    "question": "How do you say 'Hello' in French?",
                    "options": ["Bonjour", "Au revoir", "Merci", "S'il vous plaît"],
                    "correct_answer": "Bonjour"
                },
                {
                    "question": "How do you say 'Thank you' in French?",
                    "options": ["Bonjour", "Au revoir", "Merci", "S'il vous plaît"],
                    "correct_answer": "Merci"
                }
            ],
            'tamil': [
                {
                    "question": "How do you say 'Hello' in Tamil?",
                    "options": ["வணக்கம்", "போ", "நன்றி", "தயவு செய்து"],
                    "correct_answer": "வணக்கம்"
                },
                {
                    "question": "How do you say 'Thank you' in Tamil?",
                    "options": ["வணக்கம்", "போ", "நன்றி", "தயவு செய்து"],
                    "correct_answer": "நன்றி"
                }
            ]
        },
        'tamil': {
            'english': [
                {
                    "question": "ஆங்கிலத்தில் 'வணக்கம்' எப்படி சொல்வது?",
                    "options": ["Hello", "Goodbye", "Thank you", "Please"],
                    "correct_answer": "Hello"
                },
                {
                    "question": "ஆங்கிலத்தில் 'நன்றி' எப்படி சொல்வது?",
                    "options": ["Hello", "Goodbye", "Thank you", "Please"],
                    "correct_answer": "Thank you"
                }
            ]
        }
    }
    
    return fallback_data.get(mother_language.lower(), {}).get(learning_language.lower(), [])[:num_questions]

# ====== ROUTES ======
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Login now.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    languages = ["English", "Tamil", "Mandarin", "Hindi", "Spanish", "French", "Arabic", "Bengali", "Portuguese", "Russian", "Urdu", "Indonesian"]
    
    # Create agent for analytics
    agent = SimpleAgent(current_user.id)
    analytics = agent.get_analytics()
    
    return render_template('dashboard.html', 
                         username=current_user.username, 
                         languages=languages,
                         analytics=analytics)

# ====== AGENT CHAT ROUTES (MISSING ROUTES) ======
@app.route('/agent_chat')
@login_required
def agent_chat():
    """Chat with AI agent"""
    agent = SimpleAgent(current_user.id)
    analytics = agent.get_analytics()
    return render_template('agent_chat.html', analytics=analytics)

@app.route('/agent/send_message', methods=['POST'])
@login_required
def send_agent_message():
    """Send message to AI agent"""
    try:
        user_message = request.json.get('message', '')
        agent = SimpleAgent(current_user.id)
        response = agent.chat(user_message)
        
        return jsonify({
            'success': True,
            'response': response
        })
    except Exception as e:
        print(f"Error in agent chat: {e}")
        return jsonify({
            'success': False,
            'response': 'Sorry, I encountered an error. Please try again.'
        })

@app.route('/learn/<language>')
@login_required
def learn_language(language):
    lessons = Lesson.query.filter_by(language=language).all()
    return render_template('learn_language.html', lessons=lessons, language=language)

@app.route('/translate', methods=['GET','POST'])
@login_required
def translate():
    translated_text = ""
    if request.method == 'POST':
        source_lang = request.form['source_lang']
        target_lang = request.form['target_lang']
        input_text = request.form['input_text']

        url = f"https://api.mymemory.translated.net/get?q={input_text}&langpair={source_lang}|{target_lang}"
        response = requests.get(url).json()
        translated_text = response['responseData']['translatedText']

        new_trans = Translation(user_id=current_user.id, source_lang=source_lang,
                                target_lang=target_lang, input_text=input_text,
                                translated_text=translated_text)
        db.session.add(new_trans)
        db.session.commit()

    return render_template('translate.html', translated_text=translated_text)

@app.route('/progress')
@login_required
def progress():
    progress_data = db.session.query(UserProgress, Lesson).join(Lesson, UserProgress.lesson_id == Lesson.id).filter(UserProgress.user_id == current_user.id).all()
    return render_template('progress.html', progress_data=progress_data)

@app.route('/delete_progress/<int:progress_id>', methods=['POST'])
@login_required
def delete_progress(progress_id):
    progress = UserProgress.query.get_or_404(progress_id)
    if progress.user_id != current_user.id:
        flash("Unauthorized")
        return redirect(url_for('progress'))
    db.session.delete(progress)
    db.session.commit()
    flash("Progress record deleted")
    return redirect(url_for('progress'))

@app.route('/quiz_setup')
@login_required
def quiz_setup():
    languages = ["Tamil", "English", "Telugu", "French", "German", "Spanish", "Hindi", "Mandarin"]
    return render_template('quiz_setup.html', languages=languages)

@app.route('/start_quiz', methods=['POST'])
@login_required
def start_quiz():
    mother_language = request.form['mother_language']
    learning_language = request.form['learning_language']
    
    questions = generate_quiz_questions(mother_language, learning_language)
    
    if not questions:
        flash("Failed to generate quiz questions. Please try again.")
        return redirect(url_for('quiz_setup'))
    
    session['quiz_questions'] = questions
    session['current_question'] = 0
    session['user_answers'] = []
    session['mother_language'] = mother_language
    session['learning_language'] = learning_language
    session['score'] = 0
    
    return redirect(url_for('take_quiz'))

@app.route('/take_quiz')
@login_required
def take_quiz():
    questions = session.get('quiz_questions', [])
    current_index = session.get('current_question', 0)
    
    if current_index >= len(questions):
        return redirect(url_for('quiz_result'))
    
    question = questions[current_index]
    return render_template('take_quiz.html', 
                         question=question,
                         question_number=current_index + 1,
                         total_questions=len(questions),
                         mother_language=session.get('mother_language'),
                         learning_language=session.get('learning_language'))

@app.route('/submit_answer', methods=['POST'])
@login_required
def submit_answer():
    user_answer = request.form['answer']
    current_index = session.get('current_question', 0)
    questions = session.get('quiz_questions', [])
    
    if current_index < len(questions):
        current_question = questions[current_index]
        
        if user_answer == current_question['correct_answer']:
            session['score'] = session.get('score', 0) + 1
        
        user_answers = session.get('user_answers', [])
        user_answers.append({
            'question': current_question['question'],
            'user_answer': user_answer,
            'correct_answer': current_question['correct_answer'],
            'is_correct': user_answer == current_question['correct_answer']
        })
        session['user_answers'] = user_answers
        
        session['current_question'] = current_index + 1
    
    return redirect(url_for('take_quiz'))

@app.route('/quiz_result')
@login_required
def quiz_result():
    score = session.get('score', 0)
    total_questions = len(session.get('quiz_questions', []))
    user_answers = session.get('user_answers', [])
    mother_language = session.get('mother_language')
    learning_language = session.get('learning_language')
    
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    
    if total_questions > 0:
        lesson = Lesson.query.filter_by(
            language=learning_language,
            title=f"{learning_language} Quiz"
        ).first()
        
        if not lesson:
            lesson = Lesson(
                language=learning_language,
                title=f"{learning_language} Quiz",
                content=f"Quiz for {learning_language} learners",
                audio_link=""
            )
            db.session.add(lesson)
            db.session.commit()
        
        progress = UserProgress(
            user_id=current_user.id,
            lesson_id=lesson.id,
            completed=True,
            quiz_score=percentage
        )
        db.session.add(progress)
        db.session.commit()
    
    session.pop('quiz_questions', None)
    session.pop('current_question', None)
    session.pop('user_answers', None)
    
    return render_template('quiz_result.html',
                         score=score,
                         total_questions=total_questions,
                         percentage=percentage,
                         user_answers=user_answers,
                         mother_language=mother_language,
                         learning_language=learning_language)

@app.route('/generate_lesson_content', methods=['POST'])
@login_required
def generate_lesson_content():
    data = request.get_json()
    language = data.get('language')
    lesson_number = data.get('lesson_number', 1)
    
    prompt = f"""
    Create a language learning lesson for someone learning {language}. 
    The user is a beginner and this is lesson {lesson_number}.
    
    Provide a JSON response with this exact structure:
    {{
        "native_sentence": "A useful, practical sentence in English for beginners",
        "learning_sentence": "The translation of the native sentence in {language}",
        "native_vocabulary": ["list", "of", "5", "key", "words"],
        "learning_vocabulary": ["translated", "words", "in", "target", "language"]
    }}
    
    Make the sentence practical for daily conversation. Include 5 key vocabulary words from the sentence.
    Return ONLY the JSON, no other text.
    """
    
    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            headers={
                'Content-Type': 'application/json',
                'X-goog-api-key': 'AIzaSyBACmRnjoJB-Ycq9-kEDenpokt7jRRHkAs'
            },
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            text_response = result['candidates'][0]['content']['parts'][0]['text']
            text_response = text_response.replace('```json', '').replace('```', '').strip()
            content = json.loads(text_response)
            
            return jsonify({
                'success': True,
                'content': content
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate content'
            })
            
    except Exception as e:
        print(f"Error generating lesson content: {e}")
        fallback_content = {
            "native_sentence": "Hello, how are you today?",
            "learning_sentence": get_fallback_translation("Hello, how are you today?", language),
            "native_vocabulary": ["Hello", "How", "Are", "You", "Today"],
            "learning_vocabulary": get_fallback_vocabulary(language)
        }
        return jsonify({
            'success': True,
            'content': fallback_content
        })

def get_fallback_translation(text, language):
    translations = {
        'Spanish': '¡Hola! ¿Cómo estás hoy?',
        'French': 'Bonjour ! Comment allez-vous aujourd\'hui ?',
        'German': 'Hallo! Wie geht es dir heute?',
        'Tamil': 'வணக்கம்! இன்று நீங்கள் எப்படி இருக்கிறீர்கள்?',
        'Hindi': 'नमस्ते! आप आज कैसे हैं?',
        'Mandarin': '你好！你今天好吗？'
    }
    return translations.get(language, 'Hello! How are you today?')

def get_fallback_vocabulary(language):
    vocabularies = {
        'Spanish': ['Hola', 'Cómo', 'Estás', 'Hoy', 'Bien'],
        'French': ['Bonjour', 'Comment', 'Allez-vous', 'Aujourd\'hui', 'Bien'],
        'German': ['Hallo', 'Wie', 'Geht', 'Heute', 'Gut'],
        'Tamil': ['வணக்கம்', 'எப்படி', 'இன்று', 'நீங்கள்', 'நன்றாக'],
        'Hindi': ['नमस्ते', 'कैसे', 'आज', 'आप', 'अच्छा'],
        'Mandarin': ['你好', '怎么', '今天', '你', '好']
    }
    return vocabularies.get(language, ['Hello', 'How', 'Today', 'You', 'Good'])

# ====== RUN ======
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)