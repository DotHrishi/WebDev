from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import os
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"  # Change this if you have a different user
app.config["MYSQL_PASSWORD"] = "hrishi123"  # Add your MySQL password
app.config["MYSQL_DB"] = "quiz_db"

mysql = MySQL(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/test")
def test():
    # Fetch questions from MySQL
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM questions")
    questions = cur.fetchall()
    cur.close()

    print(questions)
    
    # Format questions for rendering
    quiz_data = []
    for q in questions:
        quiz_data.append({
            "id": q[0],
            "question": q[1],
            "options": [q[2], q[3], q[4], q[5]],
            "answer": q[6]
        })
    
    return render_template("test.html", quiz_data=quiz_data)

@app.route("/results", methods=["POST"])
def results():
    user_answers = request.form.to_dict()

    # Fetch correct answers and questions from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, question, option1, option2, option3, option4, answer FROM questions")
    questions = cur.fetchall()
    cur.close()

    correct_answers = {str(q[0]): q[6] for q in questions}  # {id: answer}

    correct_count = 0
    wrong_count = 0
    attempted = len(user_answers)
    total_questions = len(correct_answers)
    unattempted = total_questions - attempted

    # Calculate correct and wrong answers
    for qid, user_answer in user_answers.items():
        if qid in correct_answers:
            if user_answer == correct_answers[qid]:
                correct_count += 1
            else:
                wrong_count += 1

    percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    # Generate pie chart
    labels = ["Correct", "Wrong", "Unattempted"]
    sizes = [correct_count, wrong_count, unattempted]
    colors = ["green", "red", "grey"]

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    plt.axis("equal")

    chart_path = os.path.join("static", "images", "results.png")
    plt.savefig(chart_path)
    plt.close()

    emoji = ''
    if percentage >= 95:
        emoji = '🗿'
    elif percentage >= 85:
        emoji = '😎'
    elif percentage >= 75:
        emoji = '😁'
    elif percentage > 50:
        emoji = '😀'
    else:
        emoji = '🥲'

    # Prepare data to display questions and correct answers
    formatted_questions = []
    for q in questions:
        formatted_questions.append({
            "id": q[0],
            "question": q[1],
            "options": [q[2], q[3], q[4], q[5]],
            "correct_answer": q[6],
            "user_answer": user_answers.get(str(q[0]), "Unattempted")
        })

    return render_template("results.html",
                           score=correct_count,
                           wrong_count=wrong_count,
                           attempted=attempted,
                           unattempted=unattempted,
                           total=total_questions,
                           percentage=round(percentage, 2),
                           emoji=emoji,
                           result=chart_path,
                           questions=formatted_questions)  # Pass questions with answers


if __name__ == "__main__":
    app.run(debug=True)
