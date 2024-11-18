// const Turl = "/teacher_courses"

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
                    <td>${course.enrolled}</td>
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
                        '<p >Already Enrolled</p>':
                        `<button onclick="join_course(${course.id})">Join</button>`
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
                load_available_courses();  // Reload the available courses list
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
                    <td>${course.studentsEnrolled}</td>
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
