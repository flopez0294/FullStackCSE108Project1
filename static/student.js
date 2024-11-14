const Turl = "/teacher"
const Student_url = "/student"



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