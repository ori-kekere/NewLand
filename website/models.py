from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(125), unique=True)
    username = db.Column(db.String(60), unique=True)
    password = db.Column(db.String(100))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    bio = db.Column(db.Text, default="")
    profile_pic = db.Column(db.String(300), default="default.png")
    posts = db.relationship('Post', backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)
    likes = db.relationship('Like', backref='user', passive_deletes=True)
    profile_image = db.Column(db.String(150), nullable=True, default=None)

    followed = db.relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        backref='follower_user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    followers = db.relationship(
        'Follow',
        foreign_keys='Follow.followed_id',
        backref='followed_user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def follow(self, user):
        if not self.is_following(user):
            db.session.add(Follow(follower_id=self.id, followed_id=user.id))

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)
    likes = db.relationship('Like', backref='post', passive_deletes=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(225), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)

class Art(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    art = db.Column(db.String(150), nullable=True, default=None)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    user = db.relationship('User', backref='arts')


class ArtComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(225), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    art_id = db.Column(db.Integer, db.ForeignKey('art.id', ondelete="CASCADE"), nullable=False)

    user = db.relationship('User', backref='art_comments')
    art = db.relationship('Art', backref='comments')

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    user = db.relationship('User', backref='videos')

