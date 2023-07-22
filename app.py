"""Flask app for User Feedback"""

from flask import Flask, redirect, render_template, session
from models import db, connect_db, User, Feedback
from forms import RegistrationForm, LoginForm, FeedbackForm
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

with app.app_context():
    db.create_all()

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
            return redirect(f"/users/{user.username}")

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

        return redirect(f"/users/{new_user.username}")

    return render_template("register.html", form=form)


@app.route("/users/<string:username>")
def profile(username):
    """User profile page that displays details of the user"""

    if "username" in session and username == session["username"]:
        user = User.query.get_or_404(username)
        feedbacks = Feedback.query.filter_by(username=username).all()

        return render_template("profile.html", user=user, feedbacks=feedbacks)

    return redirect("/login")


@app.route("/logout")
def logout():
    """Logout current user and redirect to home page"""

    session.pop("username")

    return redirect("/")


@app.route("/users/<string:username>/feedback/add")
def feedback_form(username):
    """Display a form to add feedback"""

    if "username" in session:
        form = FeedbackForm()

        return render_template("add_feedback.html", form=form, username=username)

    return redirect("/login")


@app.route("/users/<string:username>/feedback/add", methods=["POST"])
def add_feedback(username):
    """Add a new piece of feedback to the database and redirect to users profile page"""

    if "username" in session and username == session["username"]:
        form = FeedbackForm()

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            new_feedback = Feedback(title=title, content=content, username=username)

            db.session.add(new_feedback)
            db.session.commit()

            return redirect(f"/users/{username}")

    return redirect("/login")


@app.route("/feedbacks/<int:feedback_id>/update")
def edit_feedback_form(feedback_id):
    """Display a form to edit feedback"""

    if "username" in session:
        feedback = Feedback.query.get_or_404(feedback_id)

        if feedback.username == session["username"]:
            form = FeedbackForm(obj=feedback)

            return render_template(
                "edit_feedback.html", form=form, feedback_id=feedback_id
            )

    return redirect("/login")


@app.route("/feedbacks/<int:feedback_id>/update", methods=["POST"])
def update_feedback(feedback_id):
    """Update a specific feedback and redirect to users profile page"""

    if "username" in session:
        feedback = Feedback.query.get_or_404(feedback_id)

        if feedback.username == session["username"]:
            form = FeedbackForm()

            if form.validate_on_submit():
                feedback.title = form.title.data
                feedback.content = form.content.data

                db.session.commit()

                return redirect(f"/users/{feedback.username}")
            else:
                return render_template(
                    "edit_feedback.html", form=form, feedback_id=feedback_id
                )

    return redirect("/login")
