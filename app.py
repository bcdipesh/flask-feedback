"""Flask app for User Feedback"""

from flask import Flask, redirect, render_template, session
from models import db, connect_db, User
from forms import RegistrationForm, LoginForm
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

app.config["SECRET_KEY"] = "Flask_Feedback"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://postgres:{os.environ.get('DB_PASSWORD')}@localhost/flask_feedback"
app.config["SQLALCHEMY_ECHO"] = True

connect_db(app)

# API routes


@app.route("/")
def home():
    """Home route"""

    return redirect("/register")


@app.route("/login")
def login():
    """User login page"""

    form = LoginForm()

    return render_template("login.html", form=form)


@app.route("/login", methods=["POST"])
def authenticate():
    """Authenticate user"""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username
            return redirect("/secret")

    return render_template("login.html", form=form)


@app.route("/register")
def register():
    """Register new user"""
    form = RegistrationForm()

    return render_template("register.html", form=form)


@app.route("/register", methods=["POST"])
def save_user():
    """Register and save user to a database"""
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        with app.app_context():
            db.session.add(new_user)
            db.session.commit()
            session["username"] = new_user.username

        return redirect("/secret")

    return render_template("register.html", form=form)


@app.route("/secret")
def secret_page():
    """A secret page only authenticated users can see"""

    if "username" in session:
        return render_template("secret.html")

    return redirect("/login")


@app.route("/logout")
def logout():
    """Logout current user and redirect to home page"""

    session.pop("username")

    return redirect("/")
