from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, Email
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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



# Delete DB records

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



# Create DB model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name


class UserForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    email = StringField(label="Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite-color")
    submit = SubmitField(label="Submit")


# Update Datebase Record
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated Successfully")
            name_to_update.name = ''
            name_to_update.email = ''
            name_to_update.favorite_color = ''
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
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        flash("User added successfully")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_users=our_users,
                           )


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


if __name__ == "__main__":
    app.run(debug=True)
