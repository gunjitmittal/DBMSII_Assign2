from flask_wtf import FlaskForm,Form
from wtforms import StringField, SubmitField,TextField, PasswordField, SelectField, HiddenField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField

class CreatePostForm(FlaskForm):
    title = StringField("Post title", validators=[DataRequired()])
    newtag = StringField("Tags",id= 'tag_autocomplete' ,validators=[DataRequired()],render_kw={"placeholder": "Add tags"})
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("SUBMIT POST")

class RegistrationForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    submit = SubmitField("REGISTER")

class LoginForm(FlaskForm):
    id = StringField("ID", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("LOGIN")

class CommentForm(FlaskForm):
    body = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("SUBMIT COMMENT")
    
class SearchForm(FlaskForm):
    autocomp = TextField("",id='autocomplete',render_kw={"placeholder": "Search by name"})
    tag_autocomp = TextField("",id= 'tag_autocomplete',render_kw={"placeholder": "Search by tag", "style": "min-width: 200px;"})
    newtag = TextField("",id= 'newtag',render_kw={"placeholder": "Search by tags"})
    sortby = SelectField('Sort by', choices=[('none',"Sort By"), ('Time','Time'), ('Upvotes','Upvotes')])
    submit = SubmitField("SEARCH")

class AnswerForm(FlaskForm):
    body1 = CKEditorField("Answer", validators=[DataRequired()])
    submit = SubmitField("SUBMIT ANSWER")

class AnswerCommentForm(FlaskForm):
    body2 = CKEditorField("Comment" ,validators=[DataRequired()])
    post_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField("SUBMIT COMMENT")

class EditUserForm(FlaskForm):
    display_name = TextField("New username",render_kw={"placeholder":"Enter new username"})
    profile_picture = TextField("New image URL",render_kw={"placeholder":"Enter valid url"})
    submit = SubmitField("Submit")