from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


# =========================
# FOLLOW SYSTEM
# =========================

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# =========================
# USER
# =========================

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(125), unique=True)
    username = db.Column(db.String(60), unique=True)
    password = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.Text, default="")
    profile_pic = db.Column(db.String(300), default="default.png")

    profile_image = db.Column(db.String(150), nullable=True, default=None)

    posts = db.relationship('Post', backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)
    

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


# =========================
# TEXT POSTS (optional)
# =========================

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    comments = db.relationship('Comment', backref='post', passive_deletes=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(225), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)


# =========================
# ART
# =========================

class Art(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    art = db.Column(db.String(150), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    user = db.relationship('User', backref='arts')
    comments = db.relationship(
        'ArtComment',
        backref='art',
        cascade='all, delete-orphan'
    )

    @property
    def likes(self):
        return Like.query.filter_by(post_id=self.id, post_type='art').all()

    @property
    def like_count(self):
        return len(self.likes)


class ArtComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(225), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    art_id = db.Column(db.Integer, db.ForeignKey('art.id', ondelete="CASCADE"), nullable=False)

    user = db.relationship('User', backref='art_comments')


# =========================
# VIDEO
# =========================

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video = db.Column(db.String(150), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    user = db.relationship('User', backref='videos')

    comments = db.relationship(
        'VideoComment',
        backref='video',
        cascade='all, delete-orphan'
    )

    @property
    def likes(self):
        return Like.query.filter_by(post_id=self.id, post_type='video').all()

    @property
    def like_count(self):
        return len(self.likes)


class VideoComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id', ondelete="CASCADE"), nullable=False)

    user = db.relationship('User')


# =========================
# LIKES (ART + VIDEO)
# =========================

class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete="CASCADE"),
        nullable=False
    )

    post_id = db.Column(db.Integer, nullable=False)
    post_type = db.Column(db.String(10), nullable=False)  # 'art' or 'video'

    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    __table_args__ = (
        db.UniqueConstraint(
            'user_id',
            'post_id',
            'post_type',
            name='unique_like'
        ),
    )

    # NO backref to avoid conflicts
    user = db.relationship('User')