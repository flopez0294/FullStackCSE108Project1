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
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)

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
        choices=[('student', 'Student'), ('teacher', 'Teacher'), ('admin', 'Admin')],
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

class StudentView(ModelView):
    form = UserForm
    # form.role = SelectField('Role', choices=[('student', 'Student')], validators=[DataRequired()])
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
    # form.role = SelectField('Role', choices=[('teacher', 'Teacher')], validators=[DataRequired()])
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
    return render_template('index.html')

@app.route("/student")
def student_view():
    return render_template('student.html')

@app.route("/teacher")
def teacher_view():
    return render_template('teacher.html')

if __name__ == "__main__":
    app.run(debug=True)

