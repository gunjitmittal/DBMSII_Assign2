from flask import Flask
import os
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ckeditor = CKEditor(app)
Bootstrap(app)

# #CONNECT TO DB
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL",  "sqlite:///blog.db")
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:notsoeasy@localhost:5432/stackdb"
db = SQLAlchemy(app)


# #CONFIGURE TABLES
# class BlogPost(db.Model):
#     __tablename__ = "blog_posts"
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(250), unique=True, nullable=False)
#     subtitle = db.Column(db.String(250), nullable=False)
#     date = db.Column(db.String(250), nullable=False)
#     body = db.Column(db.Text, nullable=False)
#     img_url = db.Column(db.String(250), nullable=False)
#     author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
#     author = relationship("User", back_populates="posts")
#     post_comments = relationship("Comment", back_populates="parent_post")


# class User(UserMixin, db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(250), nullable=False)
#     email = db.Column(db.String(250), nullable=False)
#     password = db.Column(db.String(250), nullable=False)
#     posts = relationship("BlogPost", back_populates="author")
#     comments = relationship("Comment", back_populates="comment_author")


# class Comment(db.Model):
#     __tablename__ = "comments"
#     id = db.Column(db.Integer, primary_key=True)
#     text = db.Column(db.String(250), nullable=False)
#     author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
#     comment_author = relationship("User", back_populates="comments")
#     post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
#     parent_post = relationship("BlogPost", back_populates="post_comments")
##
##
##
class Users(db.Model,UserMixin):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    account_id=db.Column(db.Integer)
    reputation=db.Column(db.Integer,nullable=False)
    views=db.Column(db.Integer,default=0)
    down_votes=db.Column(db.Integer,default=0)
    up_votes=db.Column(db.Integer,default=0)
    display_name=db.Column(db.String(255),nullable=False)
    location=db.Column(db.String(512))
    profile_image_url=db.Column(db.String(255))
    website_url=db.Column(db.String(255))
    about_me=db.Column(db.Unicode)
    creation_date=db.Column(db.TIMESTAMP,nullable=False)
    last_access_date=db.Column(db.TIMESTAMP,nullable=False)
    #
    post=relationship("Posts",back_populates='user')
    posth=relationship("PostHistory",back_populates='user')
    comment=relationship("Comments",back_populates='user')
    vote=relationship("Votes",back_populates='user')
    badge=relationship("Badges",back_populates='user')

class Posts(db.Model):
    __tablename__='posts'
    id=db.Column(db.Integer,primary_key=True)
    owner_user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    last_editor_user_id=db.Column(db.Integer)
    post_type_id=db.Column(db.Integer,nullable=False)
    accepted_answer_id=db.Column(db.Integer)
    score=db.Column(db.Integer,nullable=False)
    parent_id=db.Column(db.Integer)
    view_count=db.Column(db.Integer)
    answer_count=db.Column(db.Integer,default=0)
    comment_count=db.Column(db.Integer,default=0)
    owner_display_name=db.Column(db.String(64))
    last_editor_display_name=db.Column(db.String(64))
    title=db.Column(db.String(512))
    tags=db.Column(db.String(512))
    content_license=db.Column(db.String(64),nullable=False)
    body=db.Column(db.Unicode)
    favorite_count=db.Column(db.Integer)
    creation_date=db.Column(db.TIMESTAMP,nullable=False)
    community_owned_date=db.Column(db.TIMESTAMP)
    closed_date=db.Column(db.TIMESTAMP)
    last_edit_date=db.Column(db.TIMESTAMP)
    last_activity_date=db.Column(db.TIMESTAMP)
    #
    user=relationship("Users",back_populates='post')
    posth1=relationship("PostHistory",back_populates='post1')
    comm=relationship("Comments",back_populates='post')

class PostsLinks(db.Model):
    __tablename__='post_links'
    id=db.Column(db.Integer,primary_key=True)
    related_post_id=db.Column(db.Integer,nullable=False)
    post_id=db.Column(db.Integer,nullable=False)
    link_type_id=db.Column(db.Integer,nullable=False)
    creation_date=db.Column(db.TIMESTAMP,nullable=False)


class PostHistory(db.Model):
    __tablename__='post_history'
    id=db.Column(db.Integer,primary_key=True)
    post_id=db.Column(db.Integer,db.ForeignKey("posts.id"),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    post_history_type_id=db.Column(db.Integer,nullable=False)
    user_display_name=db.Column(db.String(64))
    content_license=db.Column(db.String(128))
    text=db.Column(db.Unicode)
    comment=db.Column(db.Unicode)
    creation_date=db.Column(db.TIMESTAMP,nullable=False)
    # 
    user=relationship("Users",back_populates='posth')
    post1=relationship("Posts",back_populates='posth1')

class Comments(db.Model):
    __tablename__='comments'
    id=db.Column(db.Integer,primary_key=True)
    post_id=db.Column(db.Integer,db.ForeignKey("posts.id"),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    score=db.Column(db.Integer,nullable=False)
    content_license=db.Column(db.String(64),nullable=False)
    user_display_name=db.Column(db.String(64))
    text=db.Column(db.Unicode)
    creation_date=db.Column(db.TIMESTAMP,nullable=False)
    #
    user=relationship("Users",back_populates='comment')
    post=relationship("Posts",back_populates='comm')

class Votes(db.Model):
    __tablename__='votes'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"))
    post_id=db.Column(db.Integer,nullable=False)
    vote_type_id=db.Column(db.Integer,nullable=False)
    bounty_amount=db.Column(db.Integer)
    creation_date=db.Column(db.TIMESTAMP,nullable=False)
    #
    user=relationship("Users",back_populates='vote')

class Badges(db.Model):
    __tablename__='badges'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    clas=db.Column(db.Integer,nullable=False)
    name=db.Column(db.String(64),nullable=False)
    tag_based=db.Column(db.BOOLEAN,nullable=False)
    date=db.Column(db.TIMESTAMP,nullable=False)
    #
    user=relationship("Users",back_populates='badge')

class Tags(db.Model):
    __tablename__='tags'
    id=db.Column(db.Integer,primary_key=True)
    excerpt_post=db.Column(db.Integer)
    wiki_post_id=db.Column(db.Integer)
    tag_name=db.Column(db.String(255))
    count=db.Column(db.Integer,default=0)

db.create_all()