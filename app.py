from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin, login_user, logout_user, login_required, LoginManager, current_user
from webforms import LoginForm, PostForm, PasswordForm, UserForm, NamerForm, SearchForm
import os
from dotenv import load_dotenv
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import psycopg2




load_dotenv(f"{os.getcwd()}/{'.env'}")
# WTF_SECRET_KEY = os.environ.get("WTF_SECRET_KEY")
DATABASE_URL=os.environ.get("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

WTF_SECRET_KEY="it is super secret key of mine"
# DATABASE_URI = 'mysql+pymysql://root:password123@localhost/users'
# Create Flask Instance
app = Flask(__name__)
ckeditor = CKEditor(app)
# Add database (sqlite)
# Heroku database URL
# ===============================
# DATABASE_URI="postgres://ojwpjrfqoololg:4345d913d361ba22034a637001c529a18901cc6aa06d130e19d1648cccbd73c8@ec2-54-144-112-84.compute-1.amazonaws.com:5432/df7iss8edfnedn"
# ======================================================================

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# Add database (MySQL DB)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localdb
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/users'
# Secret key for WTF forms
app.config["SECRET_KEY"] = WTF_SECRET_KEY
# initialize The database

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Create Admin Page
@app.route("/admin")
@login_required
def admin():
    id = current_user.id
    if id == 36:
        return render_template("admin.html")
    else:
        flash("Sorry! You must have admin privilege to access this page!")
        return redirect(url_for('dashboard'))


# Pass form to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


#  Create Search Function
@app.route('/search', methods=["GET", "POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # Get data from submitted form
        post_searched = form.searched.data
        # Query the database
        posts = posts.filter(Posts.content.like('%' + post_searched + '%'))
        posts_found = posts.order_by(Posts.title).all()
        return render_template("search.html",
                               form=form,
                               searched=post_searched,
                               posts=posts_found)


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
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']

        #  Check for profile pic
        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']
            # Grab image name
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            # Set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # Save That Image
            saver = request.files['profile_pic']
            # Change it to a string to save to db
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(UPLOAD_FOLDER, pic_name))
                flash("User Updated Successfully")
                return render_template("dashboard.html",
                                       form=form,
                                       name_to_update=name_to_update,
                                       id=id)

            except:
                flash("Error! Looks like there was an error...")
                return render_template("dashboard.html",
                                       form=form,
                                       name_to_update=name_to_update,
                                       id=id)

        else:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)

    else:
        return render_template("dashboard.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)


@app.route("/posts/delete/<int:id>")
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == current_user.id or id == 36:
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
    else:
        flash("You Are Not Authorized To Delete That Post")
        all_posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", all_posts=all_posts)


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
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        poster_id = poster
        # Update database
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated")
        return redirect(url_for('post', id=post.id))
    if current_user.id == post.poster_id or current_user.id == 36:
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template("edit_post.html", form=form)
    else:
        flash("You Aren't Authorizes To Edit This Post")
        all_posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", all_posts=all_posts)


# Add Post Page
@app.route("/add_post", methods=["GET", "POST"])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(
            title=form.title.data,
            content=form.content.data,
            slug=form.slug.data,
            poster_id=poster
        )
        # Add to database
        db.session.add(post)
        db.session.commit()

        # Clear the form
        form.title.data = ''
        form.content.data = ''
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


# Update Database Record
@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']

        try:
            db.session.commit()
            flash("User Updated Successfully")
            name_to_update.name = ''
            name_to_update.email = ''
            name_to_update.favorite_color = ''
            name_to_update.username = ''
            name_to_update.about_author = ''
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
        form.about_author.data = ''
        return render_template("update.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)


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
                         about_author=form.about_author.data,
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.about_author.data = ''
        form.password_hash.data = ''
        flash("User added successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_users=our_users,
                           )


@app.route("/delete/<int:id>")
@login_required
def delete(id):
    if id == current_user.id:
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
    else:
        flash("Sorry, you can't delete that user")
        return redirect(url_for('dashboard'))


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


# databases
# //////////////////////////////////////////////
# Create Blog POst Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(120))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    #     Create Foreign Key to Link Users(refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# Create DB model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(120), nullable=True)
    #  Create password
    password_hash = db.Column(db.String(120))
    #  User can have many posts
    posts = db.relationship('Posts', backref='poster')

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


if __name__ == "__main__":
    app.run(debug=True)


