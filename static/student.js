// const Turl = "/teacher_courses"


const cleanString = (str) => {
    str = str.replace(/</g, "&lt;");
    str = str.replace(/>/g, "&gt;");
    str = str.replace(/\"/g, "&quot;");
    str = str.replace(/\'/g, "&apos;");
    str = str.trim();
    console.log(str.substring(0,100))
    return str.substring(0, 100);
}

function cleanInt(num) {
    const pars = parseFloat(num);
    if (isNaN(pars)) {
        return "N/A";
    }
    return String(pars);
}

function student_courses_table() {
    fetch('/student_table')
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('#student_table tbody');
            document.getElementById('student_table').style.display = 'block'
            tbody.innerHTML = '';

            data.forEach(course => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${course.name}</td>
                    <td>${course.teacher}</td>
                    <td>${course.time}</td>
                    <td>${course.grade}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching courses:', error));
}

function load_available_courses() {
    fetch('/available_courses')
    .then(response => response.json())
    .then(data => {
        

        const tbody = document.querySelector('#student_table tbody');
        tbody.innerHTML = '';

        data.forEach(course => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${course.name}</td>
                <td>${course.teacher}</td>
                <td>${course.time}</td>
                <td>${course.enrolled}</td>
                <td>${course.is_enrolled === true ?
                        `<button onclick="unenroll_course(${course.id})">Unenroll</p>`:
                        `<button onclick="join_course(${course.id})">Enroll</button>`
                }
            `;
            tbody.appendChild(row);
        });
    })
    .catch(error => console.error('Error fetching available courses:', error));
}

function join_course(courseId) {
    fetch(`/join_course/${courseId}`, 
        { 
        method: 'POST' 
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Successfully joined the course!');
                load_available_courses();
            } else {
                alert('Failed to join the course. It might be full or an error occurred.');
            }
        })
        .catch(error => console.error('Error joining the course:', error));
}


function teacher_courses_table() {
    fetch('/teacher_courses')
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('#teacher_table tbody');
            document.getElementById('teacher_table').style.display = 'block'; 
            tbody.innerHTML = ''; 

            data.forEach(course => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${course.name}</td>
                    <td>${course.time}</td>
                    <td>${course.enrolled}</td>
                    <td><button><a href="/teacher/${course.id}">view students</a></button></td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching teacher courses:', error));
}



function viewCourseDetails(courseId) {
    fetch(`/course_details/${courseId}`)
        .then(response => response.json())
        .then(data => {
            // Display course details in a modal or section on the page
            console.log(data); // Replace with your UI logic
        })
        .catch(error => console.error('Error fetching course details:', error));
}

function loadTeacherName() {
    console.log("Fetching username...");
    const h1 = document.getElementById("teacher_displayname");
    
    fetch('/currusername')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Response data:", data);
            h1.textContent += data.name; // Update the H1 content
        })
        .catch(error => console.error("Error fetching name details:", error));
    teacher_courses_table()
}


function toggleEdit(id){
    var toggle = document.getElementById('edit_student_' + id); // Target the edit div for the specific student
    const upd = document.getElementById('update_grade_' + id); // Button for the specific student
    const new_grade = document.getElementById('new_grade_' + id); // Input for the specific student

    if (toggle.style.display === 'block') {
        toggle.style.display = 'none';
        new_grade.value = "";
        upd.style.display = "inline";
    } else {
        toggle.style.display = 'block';
        new_grade.value = "";
        upd.style.display = "none";
    }
}

function loadCourseName() {
    const path = window.location.pathname;
    const list = path.split('/');
    const id = list[2];
    const uri = '/course/' + id;
    const h1 = document.getElementById("coursename");
    fetch(uri)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            h1.textContent += data.coursename;
            const tbody = document.querySelector('#students_table tbody');
            tbody.innerHTML = ''; 

            data.students.forEach(student => {
                const row = document.createElement('tr');
                if (student.grade == null){
                    student.grade = 'N/A'
                }

                row.innerHTML = `
                    <td id="student_id">${student.id}</td>
                    <td class="student">${student.name}</td>
                    <td>${student.grade}</td>
                    <td>
                        <button id="update_grade_${student.id}" onclick="toggleEdit(${student.id})">Update Grade</button>
                        <div id="edit_student_${student.id}" hidden>
                            <input id="new_grade_${student.id}" type="text" placeholder="Enter New Grade As Float:"></input>
                            <button id="edit_stud_${student.id}" onclick="editGrade(${student.id}, ${id})">Submit</button>
                            <button id="edit_cancel_${student.id}" onclick="toggleEdit(${student.id})">Cancel</button>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
            })
        })
        .catch(error => console.error("Error fetching details:", error));
}

async function editGrade(student_id, course_id) {
    var new_grade = document.getElementById('new_grade_' + student_id).value;
    console.log(new_grade)
    console.log(course_id)
    console.log(student_id)
    try{
        const response = await fetch('/editgrade/' + course_id, {method: 'PUT',
            headers:{'Content-type': 'application/json'},
            body: JSON.stringify({grade: new_grade, id: student_id})
        })

        if(!response.ok){
            throw new Error(`Response Status: ${response.status}` );
        }
        else{
            alert(`Grade was updated successfully!`)
            new_grade.value = '';
            loadCourseName()
        }

    }

    catch(error){
        alert(error.message);
       }
}



function loadStudentName(){
    const h1 = document.getElementById("student_displayname");
    
    fetch('/currusername')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Response data:", data);
            h1.textContent += data.name; // Update the H1 content
        })
        .catch(error => console.error("Error fetching name details:", error));
        student_courses_table()
}
