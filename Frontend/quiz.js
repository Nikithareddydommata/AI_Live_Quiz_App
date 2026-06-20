let currentQuizCode = "";
let questions = [];
let startTime;
let timerInterval;

const username = localStorage.getItem("username");

if (!username) {
    alert("Please login first");
    window.location = "index.html";
}

document.getElementById("welcomeUser").innerHTML =
    "Welcome " + username;


function generateQuiz() {
    const quizCode = document.getElementById("quizCode").value;
    const category = document.getElementById("quizCategory").value;

    if (!quizCode || !category) {
        alert("Enter quiz code and select category");
        return;
    }

    fetch("/generate_quiz", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            quiz_code: quizCode,
            category: category
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        alert("Quiz Generated Successfully. Now click Join Quiz.");
    });
}


function joinQuiz() {
    const quizCode = document.getElementById("joinCode").value;

    if (!quizCode) {
        alert("Enter quiz code");
        return;
    }

    fetch("/join_quiz/" + quizCode)
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        currentQuizCode = quizCode;
        questions = data.questions;
        startTime = new Date();

        displayQuestions();
        startTimer();
    });
}


function displayQuestions() {
    let html = `
        <div class="card">
            <h2>Quiz Questions</h2>
            <p id="timer">Time: 0 seconds</p>
    `;

    questions.forEach((q, index) => {
        html += `
            <div class="question-box">
                <h3>${index + 1}. ${q.question}</h3>
        `;

        q.options.forEach(option => {
            html += `
                <div class="option">
                    <input type="radio" name="q${index}" value="${option}">
                    <label>${option}</label>
                </div>
            `;
        });

        html += `</div>`;
    });

    html += `
            <button onclick="submitQuiz()">Submit Quiz</button>
        </div>
    `;

    document.getElementById("quizSection").innerHTML = html;
}


function startTimer() {
    clearInterval(timerInterval);

    timerInterval = setInterval(() => {
        const now = new Date();
        const seconds = Math.round((now - startTime) / 1000);

        document.getElementById("timer").innerText =
            "Time: " + seconds + " seconds";
    }, 1000);
}


function submitQuiz() {
    let answers = {};

    questions.forEach((q, index) => {
        const selected = document.querySelector(
            `input[name="q${index}"]:checked`
        );

        if (selected) {
            answers[index] = selected.value;
        }
    });

    const endTime = new Date();
    const responseTime = Math.round((endTime - startTime) / 1000);

    clearInterval(timerInterval);

    fetch("/submit_quiz", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: username,
            quiz_code: currentQuizCode,
            answers: answers,
            response_time: responseTime
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        showResult(data);
    });
}


function showResult(data) {
    let html = `
        <div class="result-card">
            <h2>Quiz Result</h2>

            <p><b>Score:</b> ${data.score}/${data.total}</p>
            <p><b>Accuracy:</b> ${data.accuracy}%</p>
            <p><b>ML Prediction:</b> ${data.performance_prediction}</p>

            <h3>AI Feedback</h3>
            <pre>${data.feedback}</pre>

            <h3>Answer Review</h3>
    `;

    data.explanations.forEach(item => {
        html += `
            <div class="review-item">
                <p><b>Question:</b> ${item.question}</p>
                <p><b>Your Answer:</b> ${item.your_answer}</p>
                <p><b>Correct Answer:</b> ${item.correct_answer}</p>
                <p><b>Explanation:</b> ${item.explanation}</p>
            </div>
        `;
    });

    html += `
            <div class="leaderboard">
                <h3>Leaderboard</h3>
                <ol>
    `;

    data.leaderboard.forEach(player => {
        html += `
            <li>
                ${player.name} - Score: ${player.score}, Accuracy: ${player.accuracy}%
            </li>
        `;
    });

    html += `
                </ol>
            </div>
        </div>
    `;

    document.getElementById("resultSection").innerHTML = html;
}