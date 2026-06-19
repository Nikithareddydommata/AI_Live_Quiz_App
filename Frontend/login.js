function login(){

    const email =
    document.getElementById("loginEmail").value;

    const password =
    document.getElementById("loginPassword").value;

    fetch(
        "http://127.0.0.1:5000/login",
        {
            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                email,
                password
            })
        }
    )

    .then(res=>res.json())

    .then(data=>{

        if(data.error){

            alert(data.error);

            return;
        }

        localStorage.setItem(
            "username",
            data.name
        );

        window.location =
        "quiz.html";

    });

}