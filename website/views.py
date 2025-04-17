from flask import Blueprint,render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db
from werkzeug.utils import secure_filename
import os
import uuid

views = Blueprint("views", __name__)

@views.route('/')
@views.route('/home')
@login_required
def home():
    posts = Post.query.all()
    posts = Post.query.order_by(Post.date_created.desc()).all()
    return render_template("home.html", user=current_user, posts=posts)

@views.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty!', category='error')
        
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post has been created!', category='success')
            return redirect(url_for('views.home'))
    

    return render_template("create_post.html", user=current_user)

@views.route('/delete-post/<id>')
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash('Post does not exist!', category='error')
    elif current_user.id != post.author:  
        flash('You do not have permission to delete this post!', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post has been deleted!', category='success')
        
    return redirect(url_for('views.home'))



@views.route("/create-comment/<post_id>", methods=["POST"])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty!', category='error')
    else:
        post = Post.query.filter_by(id=post_id)

        if post:
            comment = Comment(text=text, author = current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exists!', category='error')

    return redirect(url_for('views.home'))

@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()


    if not comment:
        flash('Comment does not exist!', category='error')

    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('Thou shall not have permission to delete this comment.', category='error')

    else:
        db.session.delete(comment)
        db.session.commit()



    return redirect(url_for('views.home'))

@views.route("/like-post/<post_id>", methods=["GET"])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id)
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()

    if not post:
        flash('That post does not exist!', category='error')
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return redirect(url_for('views.home'))

@views.route('/follow/<int:user_id>')
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)
    if not current_user.is_following(user):
        current_user.follow(user)
        db.session.commit()
    return redirect(url_for('views.profile', user_id=user.id))

@views.route('/unfollow/<int:user_id>')
@login_required
def unfollow(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.is_following(user):
        current_user.unfollow(user)
        db.session.commit()
    return redirect(url_for('views.profile', user_id=user.id))


@views.route("/profile/<int:id>")
@login_required
def profile(id):
    user = User.query.get_or_404(id)
    posts = Post.query.filter_by(author=id).order_by(Post.date_created.desc()).all()
    return render_template("profile.html", user=user, posts=posts)



@views.route('/users')
@login_required
def list_users():
    users = User.query.all()
    return render_template("user_list.html", users=users, user=current_user)


@views.route("/followers/<int:user_id>")
@login_required
def followers(user_id):
    user = User.query.get_or_404(user_id)
    followers = user.followers.all()  # returns list of Follow objects
    return render_template("followers.html", user=user, followers=followers)


@views.route("/following/<int:user_id>")
@login_required
def following(user_id):
    user = User.query.get_or_404(user_id)
    following = user.followed.all()  # returns list of Follow objects
    return render_template("following.html", user=user, following=following)


@views.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    UPLOAD_FOLDER = os.path.join('website', 'static', 'uploads')

    if request.method == 'POST':
        username = request.form.get("username")
        bio = request.form.get("bio")

        if len(username) < 2:
            flash('Username is too short!', category='error')
        else:
            # Handle profile picture upload
            f = request.files.get('file')
            if f and f.filename != '':
                # Delete the old profile picture if it exists
                if current_user.profile_image:
                    old_path = os.path.join(UPLOAD_FOLDER, current_user.profile_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                # Generate unique filename
                ext = os.path.splitext(f.filename)[1]  # Gets file extension
                unique_filename = f"{uuid.uuid4().hex}{ext}"
                save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                f.save(save_path)

                # Update profile image field
                current_user.profile_image = unique_filename

            # Update other fields
            current_user.username = username
            current_user.bio = bio
            db.session.commit()
            flash('Profile updated!', category='success')
            return redirect(url_for('views.profile', user_id=current_user.id))

    return render_template("edit_profile.html", user=current_user)

