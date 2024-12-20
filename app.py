from datetime import time
from flask import Flask, jsonify, render_template, make_response, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import login_required, UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import PasswordField, StringField, SelectField, IntegerField, TimeField, SelectMultipleField
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import DataRequired, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import ListWidget, CheckboxInput

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.secret_key = 'Freak Bob'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class StudentCourse(db.Model):
    __tablename__ = 'student_course'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column('student_id', db.Integer, db.ForeignKey('students.id'))
    course_id = db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))
    grade = db.Column(db.Float, nullable=True)
    
class TeacherCourse(db.Model):
    __tablename__ = 'teacher_course'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id'))
    course_id = db.Column('course_id', db.Integer, db.ForeignKey('courses.id'))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)


    def __repr__(self):
        return f"<User {self.fullname}>"
    
    def get_id(self):
        return str(self.id)

class Teacher(User):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    courses = db.relationship('Course', secondary='teacher_course', back_populates="teachers")
    def __repr__(self):
        return f"<User {self.fullname}>"

class Student(User):
    __tablename__ = 'students'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    courses = db.relationship('Course', secondary='student_course', back_populates="students")

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    currsize = db.Column(db.Integer, nullable=False, default=0)
    maxsize = db.Column(db.Integer, nullable=False)
    days = db.Column(db.String(100), nullable=False) 
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    # Foreign key to User (Teacher)
    teachers = db.relationship('Teacher', secondary='teacher_course', back_populates='courses')
    
    # Many-to-many relationship with students
    students = db.relationship('Student', secondary='student_course', back_populates="courses")

    def __repr__(self):
        return f"<Course {self.name}>"
# Admin Views



class UserForm(FlaskForm):
    fullname = StringField("Fullname", validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField(
        'Role',
        choices=[('student', 'Student'), ('teacher', 'Teacher')],
        validators=[DataRequired()]
    )
    

class CourseForm(FlaskForm):
    name = StringField('Course Name', validators=[DataRequired()])
    currsize = IntegerField('Current Size', validators=[Optional()], default=0)
    maxsize = IntegerField('Max Size', validators=[DataRequired()])
    days =  StringField("Days using comma to separate", validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    teachers = QuerySelectMultipleField(
        'Teachers',
        query_factory=lambda: Teacher.query.all(),
        get_label="fullname"
    )
    

class AllUserView(ModelView):
    form = UserForm
    can_create = False
    can_delete = True
    can_edit = True
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
    
    def on_model_change(self, form, model, is_created):
        model.password = generate_password_hash(model.password)
        super().on_model_change(form, model, is_created)    

class StudentView(ModelView):
    form = UserForm
    can_create = True
    can_delete = True
    can_edit = True
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
    
    def on_model_change(self, form, model, is_created):
        model.password = generate_password_hash(model.password)
        super().on_model_change(form, model, is_created)

class TeacherView(ModelView):
    form = UserForm
    can_create = True
    can_delete = True
    can_edit = True
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
    
    def on_model_change(self, form, model, is_created):
        model.password = generate_password_hash(model.password)
        super().on_model_change(form, model, is_created)
    
class CourseView(ModelView):
    form = CourseForm
    can_create = True
    can_delete = True
    can_edit = True
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
    
    def _get_currsize(view, context, model, name):
        return len(model.students)
    
    column_formatters = {
        'currsize': _get_currsize
    }
    
    def on_model_change(self, form, model, is_created):
        model.teachers = []
        
        # Add the selected teachers to the course
        for teacher in form.teachers.data:
            model.teachers.append(teacher)
        
        super().on_model_change(form, model, is_created)
        

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

admin = Admin(app, name='Admin', index_view=MyAdminIndexView(), template_mode='bootstrap3')  
admin.add_view(AllUserView(User, db.session))       
admin.add_view(StudentView(Student, db.session))
admin.add_view(TeacherView(Teacher, db.session))
admin.add_view(CourseView(Course, db.session))


# Ensure tables are created
# with app.app_context():
#     db.create_all()



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been Logged Out", 'info')
    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == "student":
            return redirect('/student')
        if current_user.role == "teacher":
            return redirect("/teacher")
        if current_user.role == "admin":
               return redirect("/admin") 
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user:
            if check_password_hash(user.password, request.form.get('password')):
                login_user(user)
                if user.role == "student":
                    return redirect('/student')
                if user.role == "teacher":
                    return redirect("/teacher")
                if user.role == "admin":
                    return redirect("/admin") 
            flash("Incorrect password. Please try again.", "error")
            return redirect(url_for('login'))
        flash("Incorrect password or Username. Please try again.", "error")
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route("/")
@login_required
def index():
    return redirect(url_for('login'))

@app.route("/student")
def student_view():
    return render_template('student.html')
    
@app.route("/student_table", methods=["GET"])
def course_table():
    student = Student.query.filter_by(id=current_user.id).first()
    if not student:
            return jsonify({"error": "Student not found"}), 404

    student_courses = student.courses
    print("getting course data")
    courses_data = [
        {
            "name": course.name,
            "teacher": ", ".join([teacher.fullname for teacher in course.teachers]),
            "time": f"{course.days} {course.start_time.strftime('%H:%M')} - {course.end_time.strftime('%H:%M')}",
            "grade": StudentCourse.query.filter_by(student_id=student.id, course_id=course.id).first().grade or "N/A"
        } for course in student_courses
    ]
    
    return jsonify(courses_data)

@app.route("/available_courses", methods=["GET"])
@login_required
def available_courses():
    student = Student.query.filter_by(id=current_user.id).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404


    all_courses = Course.query.all()
    
    courses_data = [
        {
            "id": course.id,
            "name": course.name,
            "teacher": ", ".join([teacher.fullname for teacher in course.teachers]),
            "time": f"{course.days} {course.start_time.strftime('%H:%M')} - {course.end_time.strftime('%H:%M')}",
            "enrolled": f"{len(course.students)}/{course.maxsize}",
            "is_enrolled": student in course.students
        }
        for course in all_courses
    ]
    
    return jsonify(courses_data)

@app.route("/join_course/<int:course_id>", methods=["POST"])
@login_required
def join_course(course_id):
    student = Student.query.filter_by(id=current_user.id).first()
    course = Course.query.get(course_id)

    if not student or not course:
        return jsonify({"error": "Student or course not found"}), 404
    
    if len(course.students) >= course.maxsize:
        return jsonify({"success": False}), 400

    course.students.append(student)
    student.courses.append(course)
    db.session.commit()

    return jsonify({"success": True})
    
@app.route("/unenroll_course/<int:course_id>", methods=["DELETE"])
@login_required
def unenroll_course(course_id):
    student = Student.query.filter_by(id=current_user.id).first()
    course = Course.query.get(course_id)
    # print(student.courses)
    # print(course.students)
    # for i in student.courses:
    #     print (i)

    if not student or not course:
        return jsonify({"error": "Student or Course not found"}), 404
    print("student in course and found in db")

    if course in student.courses:
        print("trying to delete student from db")
        # course.students.remove(student)
        student.courses.remove(course)
        db.session.commit()
        db.session.refresh(student)
        return jsonify({"success": True})

    return make_response("Student is not enrolled in the course", 400)

@app.route("/teacher")
def teacher_view():
    return render_template('teacher.html')

@app.route('/currusername')
def currUserName():
    print("Current user fullname:", current_user.fullname)
    return jsonify({'name': current_user.fullname})

@app.route("/teacher_courses", methods=['GET'])
@login_required
def teacher_courses():
    teacher = Teacher.query.filter_by(id=current_user.id).first()

    if not teacher:
        flash("You must be a teacher to access this page.", "error")
        return redirect(url_for("index"))

    courses_data = [
        {
            "id": course.id,
            "name": course.name,
            "time": f"{course.days} {course.start_time.strftime('%H:%M')} - {course.end_time.strftime('%H:%M')}",
            "enrolled": f"{len(course.students)}/{course.maxsize}"
        }
        for course in teacher.courses
    ]

    return jsonify(courses_data)

@app.route("/editgrade/<int:course_id>", methods=["PUT"])
def editGrade(course_id):
    new_grade = request.get_json()
    print(new_grade)

    

    if new_grade['grade'] is None:
        flash("there was no grade", 'error')
        return make_response("No grade", 400)
    
    stud = StudentCourse.query.filter_by(course_id=course_id, student_id=new_grade['id']).first()
    if stud is None:
        flash("No Student exist", 'error')
        return make_response("No Student exist", 400)
    stud.grade = new_grade['grade']
    db.session.commit()
    return make_response("Update Successfully", 200)


@app.route("/teacher/<int:id>", methods=["GET"])
@login_required
def teacherCourseId(id):
    return render_template('teacher_students.html')

@app.route('/course/<int:id>', methods=["GET"])
def courseReturn(id):
    course = Course.query.filter_by(id=id).first()
    if course == None:
        flash("Course is not avaliable", "error")
        return redirect(url_for("teacher.view"))
    students_data = []
    for student in course.students:
        student_course = StudentCourse.query.filter_by(student_id=student.id, course_id=id).first()
        grade = student_course.grade if student_course else 'N/A'
        students_data.append({
            'name': student.fullname,
            'id': student.id,
            'grade': grade
        })
    
    # Prepare the response as a dictionary
    course_info = {
        'coursename': course.name,
        'students': students_data
    }
    
    return jsonify(course_info)


if __name__ == "__main__":
    app.run(debug=True)

