from flask import Blueprint, jsonify
from .models import Video
from . import db

video_api = Blueprint("video_api", __name__)

@video_api.route("/video_api/increment_views/<int:video_id>", methods=["GET"])
def increment_video_views(video_id):
    video = Video.query.get(video_id)
    video.views += 1
    db.session.commit()
    return jsonify({"views": video.views})
