from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import random

app = Flask(__name__)
CORS(app)

model = joblib.load("../ML/performance_model.pkl")
encoder = joblib.load("../ML/label_encoder.pkl")

users = {}
quizzes = {}
leaderboard = []


@app.route("/")
def home():
    return jsonify({"message": "AI Quiz Backend Running"})


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

    return jsonify({
        "message": "Signup successful",
        "name": name,
        "email": email
    })


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

    feedback = generate_ai_feedback(
        name,
        score,
        total,
        accuracy,
        response_time,
        prediction
    )

    leaderboard.append({
        "name": name,
        "score": score,
        "accuracy": accuracy,
        "performance": prediction
    })

    sorted_leaderboard = sorted(
        leaderboard,
        key=lambda x: x["score"],
        reverse=True
    )

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
                "explanation": "A list stores multiple values in a single variable."
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
                "explanation": "Python is an interpreted high-level programming language."
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
                "explanation": "Logistic Regression is used for classification prediction."
            },
            {
                "question": "Which library is used for ML in Python?",
                "options": ["React", "Scikit-learn", "HTML", "Bootstrap"],
                "answer": "Scikit-learn",
                "explanation": "Scikit-learn is a popular ML library in Python."
            },
            {
                "question": "Generative AI is used to generate?",
                "options": ["Feedback", "Electricity", "Hardware", "Network cables"],
                "answer": "Feedback",
                "explanation": "Generative AI can create text, feedback, explanations, and content."
            }
        ],

        "Data Science": [
            {
                "question": "Which library is used for data analysis?",
                "options": ["Pandas", "Flask", "HTML", "CSS"],
                "answer": "Pandas",
                "explanation": "Pandas is used for data analysis and manipulation."
            },
            {
                "question": "Which chart is used to show trends?",
                "options": ["Line Chart", "Pie Chart", "Bar Chart", "Table"],
                "answer": "Line Chart",
                "explanation": "Line charts are commonly used to show trends over time."
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
                "explanation": "Accuracy measures how many predictions are correct."
            }
        ],

        "Web Development": [
            {
                "question": "HTML is used for?",
                "options": ["Structure", "Styling", "Database", "Machine Learning"],
                "answer": "Structure",
                "explanation": "HTML creates the structure of a webpage."
            },
            {
                "question": "CSS is used for?",
                "options": ["Styling", "Database", "Server", "AI"],
                "answer": "Styling",
                "explanation": "CSS is used to style webpages."
            },
            {
                "question": "JavaScript is used for?",
                "options": ["Interactivity", "Database only", "Image editing", "Operating System"],
                "answer": "Interactivity",
                "explanation": "JavaScript adds interactivity to webpages."
            },
            {
                "question": "Flask is a framework of which language?",
                "options": ["Python", "Java", "C", "PHP"],
                "answer": "Python",
                "explanation": "Flask is a lightweight Python web framework."
            },
            {
                "question": "Frontend runs mainly in?",
                "options": ["Browser", "Database", "Server room", "Compiler"],
                "answer": "Browser",
                "explanation": "Frontend code runs in the user's browser."
            }
        ]
    }

    questions = question_bank.get(category, question_bank["Python"])
    return random.sample(questions, len(questions))


def generate_ai_feedback(name, score, total, accuracy, response_time, prediction):
    feedback = f"""
Hello {name},

You answered {score} out of {total} questions correctly.

Your accuracy is {accuracy}% and your response time is {response_time} seconds.

AI Performance Analysis:
Your predicted performance category is {prediction}.

Feedback:
You have completed the quiz successfully. Your result shows your current understanding of the selected topic.

Suggestions:
If your score is high, continue practicing advanced-level questions.
If your score is average, revise the basic concepts and practice more.
If your score is low, focus on fundamentals and review explanations carefully.

Improvement Tip:
Try to improve both accuracy and time management in the next quiz.

Overall Result:
{prediction}
"""
    return feedback


if __name__ == "__main__":
    app.run(debug=True)