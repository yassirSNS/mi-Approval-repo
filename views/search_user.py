from flask import jsonify
from sqlalchemy import or_
from google.appengine.api import images
from models.user import User
from . import db_session


def search_user(pattern):
    try:
        pattern = str(pattern).strip()
        users = db_session.query(User).filter(or_(User.Name.like('%{}%'.format(pattern)),
                                                  User.MobileNo.like('%{}%'.format(pattern))))
        return jsonify(status=1, message="success",
                       Users=[dict(userID=i.UserID,
                                   name=i.Name,
                                   mobile=i.Mobile,
                                   imageURL=images.get_serving_url(
                                       i.ImageKey, secure_url=True) if i.ImageKey else None
                                   ) for i in users])
    except Exception as e:
        db_session.rollback()
        return jsonify(status=0, message=format(e))


def show_all_users():
    try:
        users = db_session.query(User).all()
        return jsonify(Users=[dict(userID=i.UserID,
                                   name=i.Name,
                                   mobile=i.Mobile,
                                   email=i.EmailID,
                                   imageURL=images.get_serving_url(
                                       i.ImageKey, secure_url=True) if i.ImageKey else None,
                                   passwordHash=i.PasswordHash,
                                   token=i.Token) for i in users])
    except Exception as e:
        db_session.rollback()
        return jsonify(status=0, message=format(e))
