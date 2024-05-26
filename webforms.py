from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditor, CKEditorField
from flask_wtf.file import FileField


# Create A Search Form
class SearchForm(FlaskForm):
    searched = StringField(label="Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")


# create login form
class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create Post Form
class PostForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    # content = StringField(label="Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content',validators=[DataRequired()])
    author = StringField(label="Author")
    slug = StringField(label="Slug", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


# Create User Form
class UserForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    username = StringField(label="username", validators=[])
    email = StringField(label="Email", validators=[DataRequired()])
    favorite_color = StringField(label="Favorite color")
    about_author = TextAreaField(label="About Author")
    password_hash = PasswordField('Password',
                                  validators=[
                                      DataRequired(),
                                      EqualTo('password_hash2',
                                              message='Passwords Must Match')
                                  ])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")
    submit = SubmitField(label="Submit")


# Create password Form
class PasswordForm(FlaskForm):
    email = StringField(label="What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField(label="What's Your Password", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


# Create form class
class NamerForm(FlaskForm):
    name = StringField(label="What's Your Name", validators=[DataRequired()])
    submit = SubmitField(label="Submit")
