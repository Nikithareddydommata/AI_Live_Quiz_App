from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import random
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "Frontend"))
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "ML", "performance_model.pkl"))
ENCODER_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "ML", "label_encoder.pkl"))

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

users = {}
quizzes = {}
leaderboard = []


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/signup.html")
def signup_page():
    return send_from_directory(FRONTEND_DIR, "signup.html")


@app.route("/quiz.html")
def quiz_page():
    return send_from_directory(FRONTEND_DIR, "quiz.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)


@app.route("/api/status")
def status():
    return jsonify({"message": "AI Quiz App Running Successfully"})


@app.route("/signup", methods=["POST"])
def signup():
    data = request.json

    name = data["name"]
    email = data["email"]
    password = data["password"]

    if email in users:
        return jsonify({"error": "User already exists"})

    users[email] = {
        "name": name,
        "email": email,
        "password": password
    }

    return jsonify({"message": "Signup successful", "name": name, "email": email})


@app.route("/login", methods=["POST"])
def login():
    data = request.json

    email = data["email"]
    password = data["password"]

    if email not in users:
        return jsonify({"error": "User not found"})

    if users[email]["password"] != password:
        return jsonify({"error": "Wrong password"})

    return jsonify({
        "message": "Login successful",
        "name": users[email]["name"],
        "email": email
    })


@app.route("/generate_quiz", methods=["POST"])
def generate_quiz():
    data = request.json

    category = data["category"]
    quiz_code = data["quiz_code"]

    questions = generate_ai_questions(category)

    quizzes[quiz_code] = {
        "category": category,
        "questions": questions
    }

    return jsonify({
        "message": "AI quiz generated successfully",
        "quiz_code": quiz_code,
        "category": category,
        "questions": questions
    })


@app.route("/join_quiz/<quiz_code>", methods=["GET"])
def join_quiz(quiz_code):
    if quiz_code not in quizzes:
        return jsonify({"error": "Quiz not found"})

    return jsonify({
        "quiz_code": quiz_code,
        "category": quizzes[quiz_code]["category"],
        "questions": quizzes[quiz_code]["questions"]
    })


@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    data = request.json

    name = data.get("name", "Guest")
    quiz_code = data["quiz_code"]
    answers = data["answers"]
    response_time = data["response_time"]

    if quiz_code not in quizzes:
        return jsonify({"error": "Invalid quiz code"})

    questions = quizzes[quiz_code]["questions"]

    score = 0
    explanations = []

    for i, question in enumerate(questions):
        correct_answer = question["answer"]
        user_answer = answers.get(str(i), "Not Attempted")

        if user_answer == correct_answer:
            score += 1

        explanations.append({
            "question": question["question"],
            "your_answer": user_answer,
            "correct_answer": correct_answer,
            "explanation": question["explanation"]
        })

    total = len(questions)
    accuracy = round((score / total) * 100, 2)
    attempted = len(answers)

    prediction_input = [[score, accuracy, response_time, attempted]]
    prediction_encoded = model.predict(prediction_input)
    prediction = encoder.inverse_transform(prediction_encoded)[0]

    feedback = generate_ai_feedback(name, score, total, accuracy, response_time, prediction)

    leaderboard.append({
        "name": name,
        "score": score,
        "accuracy": accuracy,
        "performance": prediction
    })

    sorted_leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)

    return jsonify({
        "score": score,
        "total": total,
        "accuracy": accuracy,
        "performance_prediction": prediction,
        "feedback": feedback,
        "explanations": explanations,
        "leaderboard": sorted_leaderboard
    })


def generate_ai_questions(category):
    question_bank = {
        "Python": [
            {
                "question": "Which keyword is used to define a function in Python?",
                "options": ["function", "def", "func", "define"],
                "answer": "def",
                "explanation": "In Python, the def keyword is used to create a function."
            },
            {
                "question": "Which data type is used to store multiple values in Python?",
                "options": ["int", "float", "list", "char"],
                "answer": "list",
                "explanation": "A list stores multiple values in one variable."
            },
            {
                "question": "Which symbol is used for comments in Python?",
                "options": ["//", "#", "/* */", "--"],
                "answer": "#",
                "explanation": "Python uses # for single-line comments."
            },
            {
                "question": "Which function is used to print output?",
                "options": ["display()", "echo()", "print()", "show()"],
                "answer": "print()",
                "explanation": "print() displays output on the screen."
            },
            {
                "question": "Python is which type of language?",
                "options": ["Compiled", "Interpreted", "Assembly", "Machine"],
                "answer": "Interpreted",
                "explanation": "Python is an interpreted high-level language."
            }
        ],
        "AI": [
            {
                "question": "What does AI stand for?",
                "options": ["Artificial Intelligence", "Automatic Internet", "Advanced Input", "Applied Information"],
                "answer": "Artificial Intelligence",
                "explanation": "AI means Artificial Intelligence."
            },
            {
                "question": "Machine Learning is a subset of?",
                "options": ["Database", "AI", "Networking", "Web Design"],
                "answer": "AI",
                "explanation": "Machine Learning is a branch of Artificial Intelligence."
            },
            {
                "question": "Which algorithm is used in this project?",
                "options": ["Linear Regression", "Logistic Regression", "K-Means", "Apriori"],
                "answer": "Logistic Regression",
                "explanation": "Logistic Regression is used for classification."
            },
            {
                "question": "Which library is used for ML in Python?",
                "options": ["React", "Scikit-learn", "HTML", "Bootstrap"],
                "answer": "Scikit-learn",
                "explanation": "Scikit-learn is a popular Python ML library."
            },
            {
                "question": "Generative AI is used to generate?",
                "options": ["Feedback", "Electricity", "Hardware", "Network cables"],
                "answer": "Feedback",
                "explanation": "Generative AI can create feedback and explanations."
            }
        ],
        "Data Science": [
            {
                "question": "Which library is used for data analysis?",
                "options": ["Pandas", "Flask", "HTML", "CSS"],
                "answer": "Pandas",
                "explanation": "Pandas is used for data analysis."
            },
            {
                "question": "Which chart is used to show trends?",
                "options": ["Line Chart", "Pie Chart", "Bar Chart", "Table"],
                "answer": "Line Chart",
                "explanation": "Line charts show trends over time."
            },
            {
                "question": "CSV stands for?",
                "options": ["Comma Separated Values", "Computer System Value", "Common Server Variable", "Code Save Version"],
                "answer": "Comma Separated Values",
                "explanation": "CSV means Comma Separated Values."
            },
            {
                "question": "Which language is mostly used in Data Science?",
                "options": ["Python", "HTML", "CSS", "PHP"],
                "answer": "Python",
                "explanation": "Python is widely used in Data Science."
            },
            {
                "question": "Accuracy is used to measure?",
                "options": ["Model performance", "File size", "Screen size", "Internet speed"],
                "answer": "Model performance",
                "explanation": "Accuracy measures correct predictions."
            }
        ],
        "Web Development": [
            {
                "question": "HTML is used for?",
                "options": ["Structure", "Styling", "Database", "Machine Learning"],
                "answer": "Structure",
                "explanation": "HTML creates webpage structure."
            },
            {
                "question": "CSS is used for?",
                "options": ["Styling", "Database", "Server", "AI"],
                "answer": "Styling",
                "explanation": "CSS styles webpages."
            },
            {
                "question": "JavaScript is used for?",
                "options": ["Interactivity", "Database only", "Image editing", "Operating System"],
                "answer": "Interactivity",
                "explanation": "JavaScript adds webpage interactivity."
            },
            {
                "question": "Flask is a framework of which language?",
                "options": ["Python", "Java", "C", "PHP"],
                "answer": "Python",
                "explanation": "Flask is a Python web framework."
            },
            {
                "question": "Frontend runs mainly in?",
                "options": ["Browser", "Database", "Server room", "Compiler"],
                "answer": "Browser",
                "explanation": "Frontend code runs in the browser."
            }
        ]
    }

    questions = question_bank.get(category, question_bank["Python"])
    return random.sample(questions, len(questions))


def generate_ai_feedback(name, score, total, accuracy, response_time, prediction):
    return f"""
Hello {name},

You answered {score} out of {total} questions correctly.

Your accuracy is {accuracy}% and your response time is {response_time} seconds.

AI Performance Analysis:
Your predicted performance category is {prediction}.

Feedback:
You completed the quiz successfully. Your result shows your current understanding of the selected topic.

Suggestions:
If your score is high, continue practicing advanced questions.
If your score is average, revise basic concepts and practice more.
If your score is low, focus on fundamentals and review explanations carefully.

Improvement Tip:
Try to improve both accuracy and time management.

Overall Result:
{prediction}
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)