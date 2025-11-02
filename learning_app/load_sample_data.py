import json
from app import app, db, Lesson, Quiz

with app.app_context():
    # Load Lessons
    with open('sample_data/lessons.json', 'r', encoding='utf-8') as f:
        lessons = json.load(f)
        for l in lessons:
            lesson = Lesson(
                id=l['id'],
                language=l['language'],
                title=l['title'],
                content=l['content'],
                audio_link=l.get('audio_link', '')
            )
            db.session.merge(lesson)
    db.session.commit()
    print("Lessons loaded successfully!")

    # Load Quizzes
    with open('sample_data/quizzes.json', 'r', encoding='utf-8') as f:
        quizzes = json.load(f)
        for q in quizzes:
            quiz = Quiz(
                id=q['id'],
                lesson_id=q['lesson_id'],
                question=q['question'],
                options=q['options'],
                correct_answer=q['correct_answer']
            )
            db.session.merge(quiz)
    db.session.commit()
    print("Quizzes loaded successfully!")