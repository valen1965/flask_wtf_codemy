from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, logout_user, login_required, LoginManager, current_user

# Create Flask Instance
app = Flask(__name__)
# Add database (sqlite)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# Add database (MySQL DB)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localdb
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/users'
# Secret key for WTF forms
app.config["SECRET_KEY"] = "my super secret key"
# initialize The database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# create login form
class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# create login page
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successful!")
                return redirect(url_for('dashboard', form=form))
            else:
                flash("Wrong password. Try again")
        else:
            flash("That User Doesn't exist. Try Again ...")
            form.username.data = ''
            form.password.data = ''
    return render_template('login.html', form=form)


# Create logout function
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You Have Benn logged out. Thanks for stopping by ")
    return redirect(url_for('login'))

# create dashboard page
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form = UserForm()
    return render_template('dashboard.html', form=form)


# Create Blog POst Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(120))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))


# Create Post Form

class PostForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    content = StringField(label="Content", validators=[DataRequired()], widget=TextArea())
    author = StringField(label="Author", validators=[DataRequired()])
    slug = StringField(label="Slug", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


@app.route("/posts/delete/<int:id>")
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Blog Post was deleted successfully")
        all_posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", all_posts=all_posts)

    except:

        flash("Whoops, something went wrong. Try again")
        all_posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html",
                               all_posts=all_posts)


@app.route("/posts")
def posts():
    # Grab all the posts from database
    all_posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", all_posts=all_posts)


# Individual POst Page
@app.route("/posts/<int:id>")
def post(id):
    single_post = Posts.query.get_or_404(id)
    return render_template("post.html", post=single_post)


@app.route("/posts/edit/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update database
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated")
        return redirect(url_for('post', id=post.id))
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template("edit_post.html", form=form)


# Add Post Page
@app.route("/add-post", methods=["GET", "POST"])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(
            title=form.title.data,
            content=form.content.data,
            author=form.author.data,
            slug=form.slug.data
        )
        # Add to database
        db.session.add(post)
        db.session.commit()

        # Clear the form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        flash("Post added successfully")
    our_posts = Posts.query.order_by(Posts.date_posted)
    return render_template("add_post.html",
                           form=form,
                           our_posts=our_posts)


# JSON return
@app.route("/date")
def get_current_date():
    favorite_pizza = {
        "John": "peperoni",
        "Mary": "cheese",
        "Alex": "mushroom"
    }
    return favorite_pizza
    # return {"Date": date.today()}


# Create DB model


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    #  Create password
    password_hash = db.Column(db.String(120))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name


class UserForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    username = StringField(label="username", validators=[])
    email = StringField(label="Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite-color")
    password_hash = PasswordField('Password',
                                  validators=[
                                      DataRequired(),
                                      EqualTo('password_hash2',
                                              message='Passwords Must Match')
                                  ])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField(label="Submit")


# Update Database Record
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User Updated Successfully")
            name_to_update.name = ''
            name_to_update.email = ''
            name_to_update.favorite_color = ''
            name_to_update.username = ''
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)

        except:
            flash("Error! Looks like there was an error...")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)
    else:
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        return render_template("update.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)


# Create password Form
class PasswordForm(FlaskForm):
    email = StringField(label="What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField(label="What's Your Password", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


# Create form class
class NamerForm(FlaskForm):
    name = StringField(label="What's Your Name", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


# FILTERS !!!!!!

# safe
# capitalize
# lower
# upper
# title
# trim
# striptags
# '''


# Create a route decorator
@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, method='pbkdf2:sha256')
            user = Users(name=form.name.data,
                         username=form.username.data,
                         email=form.email.data,
                         favorite_color=form.favorite_color.data,
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash("User added successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_users=our_users,
                           )


@app.route("/delete/<int:id>")
def delete(id):
    form = UserForm()
    name = None
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully")

        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               our_users=our_users)
    except:
        flash("Whoops, there was a problem deleting user, try again.")
        our_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               our_users=our_users)


@app.route("/")
def index():
    first_name = "John"
    stuff = "This is <strong>Bold</strong> Text"

    favorite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 41]

    return render_template("index.html",
                           first_name=first_name,
                           stuff=stuff,
                           favorite_pizza=favorite_pizza)


@app.route("/user/<name>")
def user(name):
    return render_template("/user.html", user_name=name)


# Create Name Page
@app.route("/name", methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()
    # Validate entry
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash(message="Form submitted successfully")
    return render_template("name.html",
                           name=name,
                           form=form
                           )


# Create Custom Error Pages

# Invalid URL

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


# Internal Server Error thing

@app.errorhandler(500)
def page_not_found(error):
    render_template("500.html"), 500


# Create Password Test Page
@app.route("/test_pw", methods=["GET", "POST"])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    # Validate entry
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        # Lookup user by email address
        pw_to_check = Users.query.filter_by(email=email).first()
        #     Check hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template("test_pw.html",
                           email=email,
                           password=password,
                           form=form,
                           pw_to_check=pw_to_check,
                           passed=passed
                           )


if __name__ == "__main__":
    app.run(debug=True)
