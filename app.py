from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_login import login_required, UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import PasswordField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.secret_key = 'Freak Bob'
db = SQLAlchemy(app)
admin = Admin(app, name='Admin', template_mode='bootstrap3')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    
    
    
    
class UserView(ModelView):
    form_base_class = SecureForm
    can_create = True
    can_delete = True
    can_edit = True
    
    form_choices = {}


admin.add_view(UserView(User, db.session))


# Ensure tables are created
with app.app_context():
    db.create_all()


@app.route("/admin")

@app.route("/login", methods=['GET'])
def member():
    return render_template('login.html')

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
