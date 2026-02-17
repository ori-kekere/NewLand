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

verification_links = db.Table(
    'verification_links',
    db.Column('user_id', db.Integer),
    db.Column('user_email', db.Integer),
    db.Column('expiration_date', db.Integer),
    db.Column('is_used', db.Integer),
    db.Column('verification_url', db.Integer)
)


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# =========================
# USER
# =========================

class User(db.Model, UserMixin):

    __table_args__ = {'sqlite_autoincrement': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(125), unique=True)
    username = db.Column(db.String(60), unique=True, index=True)
    password = db.Column(db.String(100))
    account_verified = db.Column(db.Integer, default=False)
    is_verified = db.Column(db.Integer, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.Text, default="")
    profile_pic = db.Column(db.String(300), default="default.png")

    profile_image = db.Column(db.String(150), nullable=True, default=None)

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

    notifications = db.relationship(
    'Notification',
    foreign_keys='Notification.user_id',
    backref='user',
    lazy='dynamic',
    cascade='all, delete-orphan'
    )


    arts = db.relationship(
        'Art',
        backref='user',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    posts = db.relationship(
        'Post',
        backref='user',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    videos = db.relationship(
        'Video',
        backref='user',
        cascade='all, delete-orphan',
        passive_deletes=True
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
# TEXT POSTS 
# =========================

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False, index=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    comments = db.relationship('Comment', backref='post', passive_deletes=True)

    @property
    def likes(self):
        return Like.query.filter_by(post_id=self.id, post_type='post').all()

    @property
    def like_count(self):
        return len(self.likes)


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
    title = db.Column(db.String(150), index=True)
    art = db.Column(db.String(150), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )

    
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
    title = db.Column(db.String(150), index=True)
    video = db.Column(db.String(150), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )

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

# =========================
# NOTIFICATION 
# =========================

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    type = db.Column(db.String(20), nullable=False)  
    # 'follow', 'like', 'comment'

    object_id = db.Column(db.Integer, nullable=True)
    object_type = db.Column(db.String(20), nullable=True)
    # 'post', 'art', 'video'

    is_read = db.Column(db.Boolean, default=False)

    date_created = db.Column(db.DateTime, default=db.func.now())

    from_user = db.relationship(
        'User',
        foreign_keys=[from_user_id],
        backref='sent_notifications'
    )

