from flask_wtf import FlaskForm,Form
from wtforms import StringField, SubmitField,TextField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField

# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    tags = StringField("Tags",id= 'tag_autocomplete' ,validators=[DataRequired()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegistrationForm(FlaskForm):
    name = StringField("Display Name", validators=[DataRequired()])
    submit = SubmitField("SIGN ME UP!")

class LoginForm(FlaskForm):
    id = StringField("ID", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("LET ME IN!")


class CommentForm(FlaskForm):
    body = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("SUBMIT COMMENT")
    
class SearchForm(FlaskForm):
    autocomp = TextField("",id='autocomplete',render_kw={"placeholder": "Search by name"})
    tag_autocomp = TextField("",id= 'tag_autocomplete',render_kw={"placeholder": "Search by tag"})
    sortby = SelectField('Sort by', choices=[('none',"Sort By"), ('Time','Time'), ('Upvotes','Upvotes')])
    submit = SubmitField("search")