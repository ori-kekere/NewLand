from flask import Blueprint,render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like, Art, ArtComment, Video, VideoComment
from . import db
from werkzeug.utils import secure_filename
import os
import uuid

views = Blueprint("views", __name__)

UPLOAD_FOLDER = os.path.join('website', 'static', 'art')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

VIDEO_UPLOAD_FOLDER = os.path.join('website', 'static', 'videos')
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov'}

def allowed_video(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

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
            post = Post(text=text, user_id=current_user.id)
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
    elif current_user.id != post.user_id:  
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
        post = Post.query.get(post_id)
        
        if post:
            comment = Comment(
                text=text,
                user_id=current_user.id,
                post_id=post.id
            )
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

    if comment.user_id != current_user.id and comment.post.user_id != current_user.id:
        abort(403)


    if current_user.id != comment.user_id and current_user.id != comment.post.user_id:
        flash('Thou shall not have permission to delete this comment.', category='error')

    else:
        db.session.delete(comment)
        db.session.commit()



    return redirect(url_for('views.home'))

@views.route('/like/<post_type>/<int:post_id>')
@login_required
def like_post(post_type, post_id):

    if post_type == 'post':
        item = Post.query.get_or_404(post_id)
    elif post_type == 'art':
        item = Art.query.get_or_404(post_id)
    elif post_type == 'video':
        item = Video.query.get_or_404(post_id)
    else:
        abort(400)

    like = Like.query.filter_by(
        user_id=current_user.id,
        post_id=post_id,
        post_type=post_type
    ).first()

    if like:
        db.session.delete(like)
    else:
        db.session.add(
            Like(user_id=current_user.id, post_id=post_id, post_type=post_type)
        )

    db.session.commit()
    return redirect(request.referrer)




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


@views.route("/profile/<int:user_id>")
def profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.date_created.desc()).all()
    arts = Art.query.filter_by(user_id=user.id)\
        .order_by(Art.date_created.desc()).all()

    videos = Video.query.filter_by(user_id=user.id)\
        .order_by(Video.date_created.desc()).all()

    return render_template("profile.html", user=user, posts=posts, arts=arts, videos=videos)




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


@views.route('/art', methods=['GET', 'POST'])
@login_required
def art():
    return redirect(url_for('views.media'))



@views.route("/comment-art/<int:art_id>", methods=["POST"])
@login_required
def comment_art(art_id):
    text = request.form.get("text")
    if not text.strip():
        flash("Comment cannot be empty.", category="error")
        return redirect(url_for("art"))

    comment = ArtComment(text=text, user_id=current_user.id, art_id=art_id)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for("views.art"))

@views.route("/delete-art-comment/<int:comment_id>")
@login_required
def delete_art_comment(comment_id):
    comment = ArtComment.query.get_or_404(comment_id)

    # Only the comment user_id or the art user_id can delete
    if comment.user_id != current_user.id and comment.art.user_id != current_user.id:
        flash("You don't have permission to delete this comment.", category="error")
        return redirect(url_for("art"))

    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted.", category="success")
    return redirect(url_for("views.art"))

@views.route('/videos', methods=['GET', 'POST'])
@login_required
def videos():
    return redirect(url_for('views.media'))


@views.route('/media', methods=['GET', 'POST'])
@login_required
def media():
    # Handle uploads
    if request.method == 'POST':
        file = request.files.get('file')
        upload_type = request.form.get('type')  # "art" or "video"

        if not file or file.filename == '':
            flash('No file selected.', category='error')
            return redirect(url_for('views.media'))

        # ART upload
        if upload_type == 'art' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            new_art = Art(art=filename, user_id=current_user.id)
            db.session.add(new_art)
            db.session.commit()
            flash('Art posted!', category='success')

        # VIDEO upload
        elif upload_type == 'video' and allowed_video(file.filename):
            os.makedirs(VIDEO_UPLOAD_FOLDER, exist_ok=True)

            ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(VIDEO_UPLOAD_FOLDER, filename)
            file.save(filepath)

            new_video = Video(video=filename, user_id=current_user.id)
            db.session.add(new_video)
            db.session.commit()
            flash('Video uploaded!', category='success')

        else:
            flash('Invalid file type.', category='error')

        return redirect(url_for('views.media'))

    # Fetch both
    arts = Art.query.order_by(Art.date_created.desc()).all()
    videos = Video.query.order_by(Video.date_created.desc()).all()

    return render_template(
        "gallery.html",
        user=current_user,
        arts=arts,
        videos=videos
    )

@views.route('/comment-video/<int:video_id>', methods=['POST'])
@login_required
def comment_video(video_id):
    text = request.form.get('text')
    video = Video.query.get_or_404(video_id)

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        comment = VideoComment(
            text=text,
            user_id=current_user.id,
            video_id=video.id
        )
        db.session.add(comment)
        db.session.commit()

    return redirect(request.referrer)

@views.route('/delete-video-comment/<int:comment_id>')
@login_required
def delete_video_comment(comment_id):
    comment = VideoComment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id and comment.video.user_id != current_user.id:
        abort(403)

    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', category='success')

    return redirect(request.referrer)

@views.route('/like/<string:post_type>/<int:post_id>')
@login_required
def like_media(post_type, post_id):
    if post_type not in ['art', 'video']:
        abort(404)

    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        post_id=post_id,
        post_type=post_type
    ).first()

    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
    else:
        like = Like(
            user_id=current_user.id,
            post_id=post_id,
            post_type=post_type
        )
        db.session.add(like)
        db.session.commit()

    return redirect(request.referrer)

