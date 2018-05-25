from flask import request, jsonify
from google.appengine.api import images
from models.user import User
from models.circle import Circle, CircleMember
from views.common.image import upload_image, USER_PROFILE, CIRCLE_PROFILE
from . import db_session


def image_operation(token, operation):
    if request.method == 'POST':
        try:
            user = User.verify_token(token)
            if user:
                # call the respective function.
                return operation(user)
            else:
                message = 'Invalid token'

        except Exception as e:
            db_session.rollback()
            message = format(e)
        return jsonify(status=0, message=message)


def upload_user_image(user):
    blob_key = upload_image(user.UserID, user.ImageKey, image_type=USER_PROFILE)
    user.ImageKey = blob_key
    db_session.commit()
    image_url = images.get_serving_url(blob_key, secure_url=True)
    return jsonify(status=1, message='success',
                   imageURL=image_url, thumbnailURL=image_url+'=s128')


def upload_circle_image(user):
    circle_id = request.form['circleID']
    circle = db_session.query(Circle).filter_by(CircleID=circle_id, Deleted=False).first()

    if circle:
        circle_id = circle.CircleID
        member = db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                          UserID=user.UserID,
                                                          Removed=False).first()
        # if it is member
        if member:
            blob_key = upload_image(circle_id, circle.ImageKey, image_type=CIRCLE_PROFILE)
            circle.ImageKey = blob_key
            db_session.commit()
            image_url = images.get_serving_url(blob_key, secure_url=True)
            return jsonify(status=1, message='success',
                           imageURL=image_url, thumbnailURL=image_url+'=s128')

        raise ValueError('Not a member of the circle')
    raise ValueError('Circle doesn\'t exists')