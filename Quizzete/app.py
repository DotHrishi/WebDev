from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
import json

app = Flask(__name__)

# MySQL Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "hrishi123",
    "database": "quiz_db"
}

# Simulated AI question generation
import google.generativeai as genai

# Set up Gemini API key
genai.configure(api_key="AIzaSyD3mB_u050F1GAhW48OAWLuY5NGzNpybbM")

# Generate questions using Gemini API
def generate_questions(topic, num_questions, difficulty):
    prompt = f"Generate {num_questions} multiple-choice questions on the topic '{topic}' with a difficulty level of '{difficulty}'. " \
             "Each question should have 4 options and one correct answer. Format the response as JSON: " \
             "[{'question': '...', 'options': ['A', 'B', 'C', 'D'], 'answer': 'A'}]"
    
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        print("Raw Response:", response.text)  # Debugging step

        questions = json.loads(response.text)  # Convert to JSON
        if not isinstance(questions, list):
            raise ValueError("Invalid response format")

        return [(f"{topic[:3].lower()}{i+1}", q["question"], q["options"][0], q["options"][1], q["options"][2], q["options"][3], q["answer"], topic, difficulty) for i, q in enumerate(questions)]
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []



# Append questions to MySQL database
def append_to_database(topic, num_questions, difficulty):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    questions = generate_questions(topic, num_questions, difficulty)
    if not questions:
        print("No questions generated!")
        return []

    insert_query = """
        INSERT INTO questions (id, question, option1, option2, option3, option4, answer, topic, difficulty)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            question=VALUES(question),
            option1=VALUES(option1),
            option2=VALUES(option2),
            option3=VALUES(option3),
            option4=VALUES(option4),
            answer=VALUES(answer),
            topic=VALUES(topic),
            difficulty=VALUES(difficulty)
    """
    
    try:
        cursor.executemany(insert_query, questions)
        conn.commit()
        print(f"Appended {len(questions)} questions to database.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

    return [{"id": q[0], "question": q[1], "options": [q[2], q[3], q[4], q[5]], "answer": q[6]} for q in questions]


# Load quiz data from database
def load_quiz_data(topic=None):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = "SELECT id, question, option1, option2, option3, option4, answer FROM questions"
    params = ()
    if topic:
        query += " WHERE topic = %s"
        params = (topic,)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    if not rows:
        print("No quiz data found!")

    quiz_data = [
        {
            "id": q[0],
            "question": q[1],
            "options": [q[2], q[3], q[4], q[5]],
            "answer": q[6]
        } for q in rows
    ]
    
    cursor.close()
    conn.close()
    return quiz_data


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/configurequiz", methods=["GET", "POST"])
def configure_quiz():
    if request.method == "POST":
        topic = request.form.get("topic")
        num_questions = int(request.form.get("num_questions", 5))
        difficulty = request.form.get("difficulty", "easy")
        
        quiz_data = append_to_database(topic, num_questions, difficulty)
        return render_template("test.html", quiz_data=quiz_data)
    
    return render_template("configurequiz.html")

@app.route("/test")
def test():
    # Redirect to configurequiz instead of loading directly
    return redirect(url_for("configure_quiz"))

@app.route("/results", methods=["POST"])
def results():
    user_answers = request.form.to_dict()
    quiz_data = load_quiz_data()
    correct_answers = {q["id"]: q["answer"] for q in quiz_data}
    
    correct_count = 0
    wrong_count = 0
    attempted = len(user_answers)
    total_questions = len(quiz_data)
    unattempted = total_questions - attempted

    questions = []
    for q in quiz_data:
        q_dict = {
            "question": q["question"],
            "options": q["options"],
            "correct_answer": q["answer"],
            "user_answer": user_answers.get(q["id"], "Not attempted")
        }
        if q["id"] in user_answers:
            if user_answers[q["id"]] == q["answer"]:
                correct_count += 1
            else:
                wrong_count += 1
        questions.append(q_dict)

    percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    if os.path.exists("static/images"):
        import matplotlib.pyplot as plt
        labels = ["Correct", "Wrong", "Unattempted"]
        sizes = [correct_count, wrong_count, unattempted]
        colors = ["#00FF00", "#FF0000", "#808080"]
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        plt.axis("equal")
        chart_path = "static/images/results.png"
        plt.savefig(chart_path)
        plt.close()
    else:
        chart_path = None

    emoji = "🗿" if percentage >= 95 else "😎" if percentage >= 85 else "😁" if percentage >= 75 else "😀" if percentage > 50 else "🥲"

    return render_template("results.html",
                          score=correct_count,
                          wrong_count=wrong_count,
                          attempted=attempted,
                          unattempted=unattempted,
                          total=total_questions,
                          percentage=round(percentage, 2),
                          emoji=emoji,
                          result=chart_path,
                          questions=questions)

@app.route("/createquiz", methods=["GET", "POST"])
def create_quiz():
    if request.method == "POST":
        topic = request.form.get("topic")
        num_questions = int(request.form.get("num_questions", 5))
        difficulty = request.form.get("difficulty", "easy")
        
        quiz_data = append_to_database(topic, num_questions, difficulty)
        return render_template("test.html", quiz_data=quiz_data)
    
    return render_template("createquiz.html")

if __name__ == "__main__":
    app.run(debug=True)