import os
import dotenv
import json
from datetime import date, datetime
import smtplib
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, Query
from sqlalchemy import func
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
    name = request.args.get('autocomp',"",type=str).split(':')[0]
    tags = request.args.get('tag_autocomp',"")
    sortby = request.args.get('sortby','none',type=str)
    args=dict(request.args)
    posts = Posts.query.filter_by(post_type_id=1)
    if name != "":
        posts = Posts.query.filter_by(post_type_id=1).filter_by(owner_display_name=name)
    if name == "" and tags!= "":
        tags = tags.split(',')
        tags = [tag.split(':')[0] for tag in tags]
        q=[]
        for i in range(len(tags)):
            q.append(db.session.query(Posts).filter(Posts.tags.like('%<' + str(tags[i]) + '>%')))
        query=q[0]
        for i in range(len(tags)-1):
            query = query.intersect(q[i+1])
        posts = query
    if sortby=='Time':
        posts = posts.order_by(Posts.creation_date.desc())
    elif sortby=='Upvotes' or sortby=='none':
        posts = posts.order_by(Posts.score.desc())
    posts = posts.paginate(page)
    return render_template("index.html", all_posts=posts, form=form, args=args)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if request.method == "GET":
        return render_template("register.html", form=form)
    elif request.method == "POST":
        if form.validate_on_submit():
            new_user = Users(
                display_name=form.data['name'],
                creation_date = datetime.now(),
                last_access_date = datetime.now(),
                reputation=0,
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
    form = CommentForm()
    requested_post = Posts.query.get(post_id)
    if form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comments(
                post_id=post_id,
                user_id=current_user.id,
                score = 0,
                content_license = 'cc',
                user_display_name = current_user.display_name,
                text=form.data['body'],
                creation_date = datetime.now()
            )
            db.session.add(new_comment)
            db.session.commit()
        else:
            flash("You need to login or register first.")
            return redirect(url_for('login'))
    comments = Comments.query.filter_by(post_id=post_id).all()[:5]
    answer_posts = Posts.query.filter_by(parent_id=post_id).filter_by(post_type_id=2).all()
    answer_comments = {answer.id:Comments.query.filter_by(post_id=answer.id).all()[:5] for answer in answer_posts}
    for answer in answer_comments:
        print(len(answer_comments[answer]))
    # print(len(answer_posts))
    return render_template("post.html", post=requested_post, form=form, comments=comments, answer_posts=answer_posts, answer_comments=answer_comments)
 

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
    posts = Posts.query.filter_by(owner_user_id=current_user.id).filter_by(post_type_id=1).paginate(page)
    print(posts.items)
    return render_template("profile.html", all_posts=posts)



@app.route('/profile')
def profile():
    page = request.args.get('page', 1, type=int)
    posts = Posts.query.filter_by(owner_user_id=current_user.id).filter_by(post_type_id=1).paginate(page)
    print(posts.items)
    return render_template("profile.html", all_posts=posts)


@authenticated
@app.route("/new-post", methods=['GET', 'POST'])
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        max_id = db.session.query(func.max(Posts.id)).first()
        new_post = Posts(
            id=max_id+1,
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
            tags = '<'+form.tags.data.replace(',','><')+'>',
            content_license='cc',
            favorite_count=0,
            creation_date=datetime.now(),
            last_edit_date=datetime.now(),
            last_activity_date=datetime.now()
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@authenticated
@app.route("/edit-post/<int:post_id>")
def edit_post(post_id):
    post = Posts.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        tags=post.tags.replace('<','').replace('>',',')[:-1],
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title=edit_form.title.data
        post.body=edit_form.body.data
        post.last_editor_user_id=current_user.id
        post.last_editor_display_name=current_user.display_name
        post.tags = '<'+edit_form.tags.data.replace(',','><')+'>'
        post.last_edit_date=datetime.now()
        post.last_activity_date=datetime.now()
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form)


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

@app.route('/tagsearch')
def tagcomplete():
    curr_search = request.args.get('q')
    print(curr_search)
    query_tags = db.session.query(Tags.tag_name,Tags.id).filter(Tags.tag_name.like('%' + str(curr_search) + '%')).distinct().all()
    results_tag = [mv.tag_name+':'+str(mv.id) for mv in query_tags]
    results = results_tag
    return jsonify(matching_results=results)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
