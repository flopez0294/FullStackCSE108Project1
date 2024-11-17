const Turl = "/teacher"

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
        tbody.innerHTML = '';  // Clear existing rows

        data.forEach(course => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${course.name}</td>
                <td>${course.teacher}</td>
                <td>${course.time}</td>
                <td>${course.enrolled ?
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


async function teacher_courses_table() {
    const Turl = "/teacher"; // Replace with your actual API endpoint for teacher courses

    try {
        const response = await fetch(Turl); // Fetch data from server
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json(); // Parse JSON response

        const tbody = document.querySelector('#student_table tbody');
        tbody.innerHTML = ''; // Clear existing rows

        // Populate table rows with data
        data.forEach(course => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><a href="/teacher_course/${course.id}" class="course-link">${course.name}</a></td>
                <td>${course.teacher}</td>
                <td>${course.time}</td>
                <td>${course.enrolled}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching teacher courses:', error);
        alert('Failed to load courses. Please check your backend.');
    }
}

// Call the function to populate the table



function viewCourseDetails(courseId) {
    fetch(`/course_details/${courseId}`)
        .then(response => response.json())
        .then(data => {
            // Display course details in a modal or section on the page
            console.log(data); // Replace with your UI logic
        })
        .catch(error => console.error('Error fetching course details:', error));
}
