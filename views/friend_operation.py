import datetime
from flask import request, jsonify
from sqlalchemy import or_, and_
from google.appengine.api import images
from models.user import User
from models.friend import FriendRequest, Friend
from common.fcm_notification import send_data
from common import notification_type
from . import db_session


def __friendship__(user_id_1, user_id_2):
    return db_session.query(Friend).filter(or_(
        and_(Friend.UserID == user_id_1, Friend.FriendUserID == user_id_2),
        and_(Friend.UserID == user_id_2, Friend.FriendUserID == user_id_1)
    )).first()


def friend_operation(operation):
    if request.method == 'POST':
        try:
            json_req = request.get_json()
            token = str(json_req['token']).strip()
            user = User.verify_token(token)
            if user:
                # call the respective function.
                return operation(json_req, user)
            else:
                message = 'Invalid token'

        except Exception as e:
            db_session.rollback()
            message = format(e)
        return jsonify(status=0, message=message)


def send_friend_request(json_req, user):
    status = 0
    friend_mobile = json_req['friendMobile']
    friend_user = db_session.query(User).filter_by(Mobile=friend_mobile).first()
    if friend_user:
        user_id = user.UserID
        friend_user_id = friend_user.UserID

        if not (__friendship__(user_id, friend_user_id) or user_id == friend_user_id):
            friend_requested = db_session.query(FriendRequest).filter_by(
                UserID=user_id, FriendUserID=friend_user_id, Deleted=False).first() \
                               or db_session.query(FriendRequest).filter_by(
                UserID=friend_user_id, FriendUserID=user_id, Deleted=False).first()
            if not friend_requested:
                new_friend_request = FriendRequest(UserID=user_id, FriendUserID=friend_user_id)
                db_session.add(new_friend_request)
                db_session.commit()

                # FCM Notification
                data = dict(type=notification_type.FRIEND_REQUEST_RECEIVE,
                            friendUserID=user_id,
                            friendName=user.Name,
                            friendMobile=user.Mobile,
                            imageURL=images.get_serving_url(
                                user.ImageKey, secure_url=True) if user.ImageKey else None)
                send_data(friend_user_id, data)

                status = 1
                message = 'success'
            else:
                message = 'Friend request already sent or received'
        else:
            message = 'You are already friend'
    else:
        message = 'User with mobile {} doesn\'t exist'.format(friend_mobile)
    return jsonify(status=status, message=message)


def respond_friend_request(json_req, user):
    status = 0
    friend_mobile = json_req['friendMobile']
    action = json_req['action']  # True: Accept, False: Reject
    friend_user = db_session.query(User).filter_by(Mobile=friend_mobile).first()
    if friend_user:
        user_id = user.UserID
        friend_user_id = friend_user.UserID

        if not (__friendship__(user_id, friend_user_id) or user_id == friend_user_id):
            friend_request_received = db_session.query(FriendRequest).filter_by(
                UserID=friend_user_id, FriendUserID=user_id, Deleted=False).first()
            if friend_request_received:
                if action:  # True: Accept
                    new_friend = Friend(UserID=friend_user_id, FriendUserID=user_id)
                    db_session.add(new_friend)

                friend_request_received.AcceptanceStatus = action
                friend_request_received.Deleted = True
                friend_request_received.RespondOn = datetime.datetime.utcnow()
                db_session.commit()

                # FCM Notification
                data = dict(type=notification_type.FRIEND_REQUEST_RESPOND,
                            acceptanceStatus=action,
                            friendUserID=user_id,
                            friendName=user.Name,
                            friendMobile=user.Mobile,
                            imageURL=images.get_serving_url(
                                user.ImageKey, secure_url=True) if user.ImageKey else None)
                send_data(friend_user_id, data)

                status = 1
                message = 'success'
            else:
                message = 'No such friend request'
        else:
            message = 'You are already friend'
    else:
        message = 'User with mobile {} doesn\'t exist'.format(friend_mobile)
    return jsonify(status=status, message=message)


def remove_friend(json_req, user):
    status = 0
    friend_mobile = json_req['friendMobile']
    friend = db_session.query(User).filter_by(Mobile=friend_mobile).first()
    if friend:
        user_id = user.UserID
        friend_user_id = friend.UserID
        friendship = __friendship__(user_id, friend_user_id)
        if friendship:
            db_session.delete(friendship)
            db_session.commit()

            # FCM Notification
            data = dict(type=notification_type.FRIEND_REMOVE,
                        friendUserID=user_id,
                        friendName=user.Name,
                        friendMobile=user.Mobile,
                        imageURL=images.get_serving_url(
                            user.ImageKey, secure_url=True) if user.ImageKey else None)
            send_data(friend_user_id, data)

            status = 1
            message = 'success'
        else:
            message = 'You are not friend with {}'.format(friend_mobile)
    else:
        message = 'User with mobile {} doesn\'t exist'.format(friend_mobile)
    return jsonify(status=status, message=message)


def get_friend_requests(json_req, user):
    user_id = user.UserID
    friend_requests = db_session.query(User, FriendRequest) \
        .filter(FriendRequest.FriendUserID == user_id, FriendRequest.Deleted == False) \
        .filter(FriendRequest.UserID == User.UserID).all()
    return jsonify(status=1, message='success',
                   friendRequests=[dict(userID=i.User.UserID,
                                        name=i.User.Name,
                                        mobile=i.User.Mobile,
                                        imageURL=images.get_serving_url(
                                            i.User.ImageKey, secure_url=True) if i.User.ImageKey else None
                                        ) for i in friend_requests])


def get_friends(json_req, user):
    user_id = user.UserID
    friends = db_session.query(User, Friend).filter(or_(
        and_(Friend.UserID == user_id, Friend.FriendUserID == User.UserID),
        and_(Friend.FriendUserID == user_id, Friend.UserID == User.UserID)
    )).all()
    return jsonify(status=1, message='success',
                   friends=[dict(userID=i.User.UserID,
                                 name=i.User.Name,
                                 mobile=i.User.Mobile,
                                 imageURL=images.get_serving_url(
                                     i.User.ImageKey, secure_url=True) if i.User.ImageKey else None
                                 ) for i in friends])
