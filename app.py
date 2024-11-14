from flask import Flask, jsonify, render_template, make_response, request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import login_required, UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.secret_key = 'Freak Bob'
db = SQLAlchemy(app)
admin = Admin(app, name='Admin', template_mode='bootstrap3')

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


enrollment = db.Table('enrollment',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<User {self.fullname}>"

class Teacher(User):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

class Student(User):
    __tablename__ = 'student'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    courses = db.relationship('Course', secondary=enrollment, back_populates="students")

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    currsize = db.Column(db.Integer, nullable=False, default=0)
    maxsize = db.Column(db.Integer, nullable=False)
    
    # Foreign key to User (Teacher)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    teacher = db.relationship('Teacher', backref=db.backref('courses', lazy=True))
    
    # Many-to-many relationship with students
    students = db.relationship('Student', secondary=enrollment, back_populates="courses")

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
    

class StudentView(ModelView):
    form = UserForm
    can_create = True
    can_delete = True
    can_edit = True

class TeacherView(ModelView):
    form = UserForm
    can_create = True
    can_delete = True
    can_edit = True

admin.add_view(StudentView(Student, db.session))
# admin.add_view(TeacherView(Teacher, db.session))


# Ensure tables are created
# with app.app_context():
#     db.create_all()


@app.route("/login", methods=['GET'])
def member():
    return render_template('login.html')

@app.route("/login_method", methods=['GET'])
def loging_in():
    username = request.form.get('username')
    password = request.form.get('password')

    username_search = User.query.filter_by(username = username).first()
    password_search = User.query.filter_by(password = password).first()
    
    if not username_search:
        return make_response("Student Not Found", 404)
    else:
        #if username found, query the role and then do if password_serach and role==student or
        if password_search:
            return make_response('Logged in')
            #if password matches, we query the role and send them to whichever role is
        else:
            return make_response("Password doesn't match")
        
@app.route("/")
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
