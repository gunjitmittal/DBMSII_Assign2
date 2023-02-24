import os
import select
import dotenv
import json
from datetime import date, datetime
from urllib.request import urlopen
import smtplib
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, Query
from sqlalchemy import func, update

from flask import Flask, render_template, redirect, url_for, flash, abort, request, Response, jsonify
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar

from forms import *
from db import *

files = dotenv.load_dotenv(".env")
my_email = os.getenv("MY_EMAIL")
password = os.getenv("PASSWORD")
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ckeditor = CKEditor(app)
Bootstrap(app)

# Connect to the database
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@localhost:5432/cqadb"
db = SQLAlchemy(app)
# migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

def authenticated(f):
    def innerfunction(*args, **kwargs):
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        return abort(403)
    return innerfunction

def is_url_image(image_url):
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    site = urlopen(image_url)
    meta = site.info()
    if meta["content-type"] in image_formats:
        return True
    return False

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

@login_manager.user_loader
def load_user(id):
    return Users.query.filter_by(id=id).first()


@app.route('/', methods=['GET'])
def get_all_posts():
    page = request.args.get('page', 1, type=int)
    form = SearchForm()
    name = request.args.get('autocomp', '', type=str).split(':')[0]
    tags1 = request.args.get('newtag', '')
    sortby = request.args.get('sortby', 'none', type=str)
    args=dict(request.args)
    posts = Posts.query.filter_by(post_type_id=1)
    if name != "":
        posts = Posts.query.filter_by(post_type_id=1).filter_by(owner_display_name=name)
    if name == "" and tags1 != "":
        tags1 = [tag['value'] for tag in json.loads(tags1)]
        print(tags1)
        tags1 = [tag.split(':')[0] for tag in tags1]
        q=[]
        for i in range(len(tags1)):
            q.append(db.session.query(Posts).filter(Posts.tags.like('%<' + str(tags1[i]) + '>%')))
        query=q[0]
        for i in range(len(tags1)-1):
            query = query.intersect(q[i+1])
        posts = query
    if sortby == 'Time':
        posts = posts.order_by(Posts.creation_date.desc())
    elif sortby == 'Upvotes' or sortby == 'none':
        posts = posts.order_by(Posts.score.desc())
    posts = posts.paginate(page)
    all_tags = db.session.query(Tags.tag_name,Tags.id).all()
    all_tags = [tag.tag_name+':'+str(tag.id) for tag in all_tags]
    return render_template("index.html", all_posts=posts, form=form, args=args, all_tags=all_tags)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if request.method == "GET":
        return render_template("register.html", form=form)
    elif request.method == "POST":
        if form.validate_on_submit():
            max_index = db.session.query(func.max(Users.id)).first()
            new_user = Users(
                id = max_index[0] + 1,
                display_name = form.data['name'],
                creation_date = datetime.now(),
                last_access_date = datetime.now(),
                reputation = 0,
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = Users.query.filter_by(id=form.data['id']).first()
        if user is None:
            flash("Not registered")
        else:
            if form.data['password']==form.data['id']:
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash('Wrong password')
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=['POST', 'GET'])
def show_post(post_id):
    comment_form = CommentForm()
    answer_form = AnswerForm()
    requested_post = Posts.query.get(post_id)
    answer_comment_form = AnswerCommentForm()
    comments = Comments.query.filter_by(post_id=post_id).all()[:5]
    answer_posts = Posts.query.filter_by(parent_id=post_id).filter_by(post_type_id=2).all()
    answer_comments = {answer.id:Comments.query.filter_by(post_id=answer.id).all()[:5] for answer in answer_posts}

    if request.method == "POST":
        print(answer_comment_form.data)
        print(comment_form.data)
        print(answer_form.data)
        if answer_form.validate_on_submit():
            if current_user.is_authenticated:
                max_index = db.session.query(func.max(Posts.id)).first()
                new_answer = Posts(
                    id = max_index[0] + 1,
                    owner_user_id = current_user.id,
                    last_editor_user_id = current_user.id,
                    post_type_id = 2,
                    score = 0,
                    parent_id = post_id,
                    view_count = 0,
                    answer_count = 0,
                    comment_count = 0,
                    owner_display_name = current_user.display_name,
                    last_editor_display_name = current_user.display_name,
                    content_license = 'CC',
                    body = answer_form.data['body1'],
                    creation_date = datetime.now(),
                    last_edit_date = datetime.now(),
                    last_activity_date = datetime.now()
                )
                db.session.add(new_answer)
                db.session.commit()
                requested_post.answer_count += 1
                db.session.commit()

            else:
                flash("You need to login or register first.")
                return redirect(url_for('login'))

        elif comment_form.validate_on_submit():
            if current_user.is_authenticated:
                max_index = db.session.query(func.max(Comments.id)).first()
                new_comment = Comments(
                    id = max_index[0] + 1,
                    post_id = post_id,
                    user_id = current_user.id,
                    score = 0,
                    content_license = 'CC',
                    user_display_name = current_user.display_name,
                    text = comment_form.data['body'],
                    creation_date = datetime.now()
                )
                db.session.add(new_comment)
                db.session.commit()
                requested_post.comment_count += 1
                db.session.commit()

            else:
                flash("You need to login or register first.")
                return redirect(url_for('login'))

        elif answer_comment_form.validate_on_submit():
            print('just added')
            already_query = Comments.query.filter_by(user_id=current_user.id).filter_by(text=answer_comment_form.data['body2']).filter(str(Comments.creation_date)[:19] == str(datetime.now())[:19])
            if already_query.count() == 0 and current_user.is_authenticated:
                max_index = db.session.query(func.max(Comments.id)).first()
                new_answer_comment = Comments(
                    id = max_index[0] + 1,
                    post_id = answer_comment_form.data['post_id'],
                    user_id = current_user.id,
                    score = 0,
                    content_license = 'CC',
                    user_display_name = current_user.display_name,
                    text = answer_comment_form.data['body2'],
                    creation_date = datetime.now()
                )
                db.session.add(new_answer_comment)
                db.session.commit()
            elif already_query.count() == 0:
                flash("You need to login or register first.")
                return redirect(url_for('login'))
        return render_template("post.html", post=requested_post, comment_form=comment_form, comments=comments, answer_form=answer_form, answer_posts=answer_posts, answer_comments=answer_comments, answer_comment_form=answer_comment_form)
    
    
    return render_template("post.html", post=requested_post, comment_form=comment_form, comments=comments, answer_form=answer_form, answer_posts=answer_posts, answer_comments=answer_comments, answer_comment_form=answer_comment_form)
 

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=['POST', "GET"])
def contact():
    if request.method == "GET":
        return render_template("contact.html", submitted=False)
    elif request.method == "POST":
        connection = smtplib.SMTP("smtp.gmail.com", 587)
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email, to_addrs="ai21btech11004@iith.ac.in",
                            msg=f"Subject: Blog-contact-form\n\n Name: {request.form['name']} \n Email:"
                                f" {request.form['email']} \n Phone: {request.form['phone']} \n Message: {request.form['message']} ")
        connection.close()
        return render_template("contact.html", submitted=True)


@app.route('/profile')
def profile():
    page = request.args.get('page', 1, type=int)
    id = request.args.get('id',type=int)
    user = Users.query.get(id)
    posts = Posts.query.filter_by(owner_user_id=id).filter_by(post_type_id=1)
    posts = posts.order_by(Posts.creation_date.desc())
    posts=posts.paginate(page)
    return render_template("profile.html", all_posts=posts, user=user)


@authenticated
@app.route('/editprofile', methods=['POST', 'GET'])
def editprofile():
    id = request.args.get('id',type=int)
    user = Users.query.get(id)
    form = EditUserForm(display_name=user.display_name, profile_picture=user.profile_image_url )

    if request.method == "GET":
        return render_template("editprofile.html", form=form, user=user,check=0)
    elif request.method == "POST":
        if form.validate_on_submit():
            print(form.data)
            user.display_name = form.display_name.data
            if form.data['profile_picture'] !='':
                if is_url_image(form.data['profile_picture'])== True:
                    user.profile_image_url=form.data['profile_picture']
                else:
                    return render_template("editprofile.html", form=form, user=user,check=1)
            db.session.commit()
            return redirect(url_for('profile', id=id))


@authenticated
@app.route("/new-post", methods=['GET', 'POST'])
def add_new_post():
    form = CreatePostForm()
    all_tags = db.session.query(Tags.tag_name,Tags.id).all()
    all_tags = [tag.tag_name+':'+str(tag.id) for tag in all_tags]
    if form.validate_on_submit():
        max_index = db.session.query(func.max(Posts.id)).first()
        new_post = Posts(
            id = max_index[0] + 1,
            title=form.title.data,
            body=form.body.data,
            owner_user_id=current_user.id,
            last_editor_user_id=current_user.id,
            post_type_id=1,
            score=0,
            view_count=0,
            answer_count=0,
            comment_count=0,
            owner_display_name=current_user.display_name,
            last_editor_display_name=current_user.display_name,
            tags = '<'+form.newtag.data.replace(',','><')+'>',
            content_license='CC',
            favorite_count=0,
            creation_date=datetime.now(),
            last_edit_date=datetime.now(),
            last_activity_date=datetime.now()
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, all_tags=all_tags)


@authenticated
@app.route("/edit-post/<int:post_id>", methods=['GET', 'POST'])
def edit_post(post_id):
    post = Posts.query.get(post_id)
    all_tags = db.session.query(Tags.tag_name,Tags.id).all()
    all_tags = [tag.tag_name+':'+str(tag.id) for tag in all_tags]
    post_tags = post.tags.replace('<','').replace('>',',')[:-1]
    edit_form = CreatePostForm(
        title=post.title,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title=edit_form.title.data
        post.body=edit_form.body.data
        post.last_editor_user_id=current_user.id
        post.last_editor_display_name=current_user.display_name
        post.tags = '<'+edit_form.newtag.data.replace(',','><')+'>'
        post.last_edit_date=datetime.now()
        post.last_activity_date=datetime.now()
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, all_tags=all_tags, post_tags=post_tags)


@authenticated
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = Posts.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route('/search')
def autocomplete(): 
    curr_search = request.args.get('q')
    query_names = db.session.query(Users.display_name,Users.id).filter(Users.display_name.like('%' + str(curr_search) + '%')).order_by(Users.display_name).distinct().all()
    results_name = [mv.display_name+':'+str(mv.id) for mv in query_names]
    results = results_name[:200]
    return jsonify(matching_results=results) 


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
