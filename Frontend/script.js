let currentQuizCode = "";
let questions = [];
let startTime;
let loggedInUser = null;
let timerInterval;


/* SIGNUP */
function signup() {
    const name = document.getElementById("signupName").value;
    const email = document.getElementById("signupEmail").value;
    const password = document.getElementById("signupPassword").value;

    if (!name || !email || !password) {
        alert("Please fill all signup fields");
        return;
    }

    fetch("http://127.0.0.1:5000/signup", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name,
            email,
            password
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert("Signup successful. Now login.");
        }
    });
}


/* LOGIN */
function login() {
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    if (!email || !password) {
        alert("Please enter email and password");
        return;
    }

    fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            email,
            password
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            loggedInUser = data;

            document.getElementById("welcomeUser").innerText =
                "Welcome, " + data.name;

            document.getElementById("authSection").style.display = "none";

            alert("Login successful");
        }
    });
}


/* GENERATE AI QUIZ */
function generateQuiz() {
    const quizCode = document.getElementById("quizCode").value;
    const category = document.getElementById("quizCategory").value;

    if (!loggedInUser) {
        alert("Please login first");
        return;
    }

    if (!quizCode || !category) {
        alert("Please enter quiz code and select quiz type");
        return;
    }

    fetch("http://127.0.0.1:5000/generate_quiz", {
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
        alert(data.message);
    });
}


/* JOIN QUIZ */
function joinQuiz() {
    const quizCode = document.getElementById("joinCode").value;

    if (!loggedInUser) {
        alert("Please login first");
        return;
    }

    if (!quizCode) {
        alert("Please enter quiz code");
        return;
    }

    fetch(`http://127.0.0.1:5000/join_quiz/${quizCode}`)
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        currentQuizCode = quizCode;
        questions = data.questions;

        document.getElementById("quizTitle").innerText =
            data.category + " Quiz Questions";

        startTime = new Date();

        startTimer();

        displayQuestions();
    });
}


/* TIMER */
function startTimer() {
    clearInterval(timerInterval);

    timerInterval = setInterval(() => {
        const now = new Date();
        const seconds = Math.round((now - startTime) / 1000);

        document.getElementById("timer").innerText =
            "Time: " + seconds + " seconds";
    }, 1000);
}


/* DISPLAY QUESTIONS */
function displayQuestions() {
    document.getElementById("quizSection").classList.remove("hidden");

    let html = "";

    questions.forEach((q, index) => {
        html += `
        <div class="question-box">
            <h3>${index + 1}. ${q.question}</h3>
        `;

        q.options.forEach(option => {
            html += `
            <label class="option">
                <input type="radio" name="q${index}" value="${option}">
                ${option}
            </label>
            `;
        });

        html += `</div>`;
    });

    document.getElementById("questions").innerHTML = html;
}


/* SUBMIT QUIZ */
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

    fetch("http://127.0.0.1:5000/submit_quiz", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name: loggedInUser.name,
            quiz_code: currentQuizCode,
            answers: answers,
            response_time: responseTime
        })
    })
    .then(res => res.json())
    .then(data => {
        showResult(data);
    });
}


/* SHOW RESULT */
function showResult(data) {
    document.getElementById("resultSection").classList.remove("hidden");

    document.getElementById("score").innerText =
        `Score: ${data.score}/${data.total}`;

    document.getElementById("accuracy").innerText =
        `Accuracy: ${data.accuracy}%`;

    document.getElementById("prediction").innerText =
        `ML Performance Prediction: ${data.performance_prediction}`;

    document.getElementById("feedback").innerText = data.feedback;

    let reviewHTML = "";

    data.explanations.forEach(item => {
        reviewHTML += `
        <div class="question-box">
            <p><b>Question:</b> ${item.question}</p>
            <p><b>Your Answer:</b> ${item.your_answer}</p>
            <p><b>Correct Answer:</b> ${item.correct_answer}</p>
            <p><b>Explanation:</b> ${item.explanation}</p>
        </div>
        `;
    });

    document.getElementById("review").innerHTML = reviewHTML;

    let leaderboardHTML = "<ol>";

    data.leaderboard.forEach(player => {
        leaderboardHTML += `
        <li>
            ${player.name} - Score: ${player.score}, Accuracy: ${player.accuracy}%, ${player.performance}
        </li>
        `;
    });

    leaderboardHTML += "</ol>";

    document.getElementById("leaderboard").innerHTML = leaderboardHTML;
}