const Turl = "/teacher"
const Student_url = "/student"


async function login() {
    const username =  document.getElementById('username').value
    const password = document.getElementById('password').value

    try {
        const response = await fetch('login/' + username, password)
    }
    catch(error) {
        alert(error.message)
        console.log(error)
    }
}

async function student_courses_table() {
    try {
        const response = await fetch(Student_url);
    }
    catch (error) {
        console.log(error)
    }
}




async function teacher_courses_table(){
    try{
        const response = await fetch(Turl)

    }
    catch(error){
        alert(error.message);
        
    }
}