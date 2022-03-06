""" Flask app for Flask Feedback """

from flask import Flask, redirect, render_template, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret" 
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

debug = DebugToolbarExtension(app)

connect_db(app)

@app.route('/')
def home_page():
    """ Render Home page """

    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """ Register a new user """

    form = RegisterForm()

    if 'username' in session:
        return redirect(f"/users/{session['username']}")

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)

        try:
            db.session.commit()
            session['username'] = new_user.username
        except:
            form.username.errors.append('Username taken.  Please pick another.')
            form.password.errors.append('Please enter a stronger password.')
            form.email.errors.append('Invalid email. Try again.')
            return render_template('/users/register.html', form=form)

        return redirect(f"/users/{new_user.username}")
        
    return render_template('/users/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """ Show and handle login form for user """

    form = LoginForm()

    if "username" in session:
        return redirect(f"/users/{session['username']}")

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)

        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['username'] = username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('/users/login.html', form=form)


@app.route('/logout')
def logout_user():
    """ Logout Route """

    session.pop("username")
    return redirect('/login')


@app.route('/users/<username>')
def user_page(username):
    """ Home page for logged-in users """

    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')

    user = User.query.get_or_404(username)
    form = DeleteForm()

    return render_template('/users/show.html', user=user, form=form)


@app.route("/users/<username>/delete", methods=["POST"])
def remove_user(username):
    """Remove user nad redirect to login."""

    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')

    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("username")

    return redirect("/login")


@app.route("/users/<username>/feedback/new", methods=["GET", "POST"])
def new_feedback(username):
    """ Show and handle add feedback form """

    form = FeedbackForm()

    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    else:
        return render_template("feedback/new.html", form=form)


@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Show update-feedback form and process it."""

    feedback = Feedback.query.get(feedback_id)

    form = FeedbackForm(obj=feedback)

    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template("/feedback/edit.html", form=form, feedback=feedback)


@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""

    feedback = Feedback.query.get(feedback_id)
    form = DeleteForm()

    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")

