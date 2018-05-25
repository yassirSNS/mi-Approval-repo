import datetime
from flask import request, jsonify
from google.appengine.api import images
from models.user import User
from models.circle import Circle, CircleMember
from friend_operation import __friendship__
from views.common.image import delete_image
from common.fcm_notification import send_data, send_data_multiple
from common import notification_type
from . import db_session


def format_age_date(age_date):
    if age_date and age_date.strip():
        # Change string 'yyyy-mm-dd' to datetime, and then date
        return datetime.datetime.strptime(age_date.strip(), '%Y-%m-%d').date()
    # Or max date i.e. 9999-12-31
    return datetime.date.max


def circle_operation(operation):
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


def create_circle(json_req, user):
    circle_name = json_req['circleName'].strip()
    age_date = json_req['circleAgeDate']  # In the format 'yyyy-mm-dd'
    members = json_req['members']  # String of FriendUserIDs separated with comma

    user_id = user.UserID
    friend_user_id_list = list()

    # split string members in list and check which one is friend, then append it to friend_user_id_list
    if members and members.strip():
        member_list = members.split(',')
        for member in member_list:
            friend_user_id = int(member)
            if __friendship__(user_id, friend_user_id):
                friend_user_id_list.append(friend_user_id)

    age_date = format_age_date(age_date)

    if friend_user_id_list:
        # Age date should be in future
        if age_date > datetime.date.today():
            new_circle = Circle(CircleName=circle_name, UserID=user_id, AgeDate=age_date)
            db_session.add(new_circle)
            db_session.commit()

            circle_id = new_circle.CircleID

            # Adding owner in circle as member.
            new_member = CircleMember(CircleID=circle_id, UserID=user_id, IsAdmin=True)
            db_session.add(new_member)
            db_session.commit()

            # Adding members in circle, specified by owner.
            for friend_user_id in friend_user_id_list:
                new_member = CircleMember(CircleID=circle_id, UserID=friend_user_id)
                db_session.add(new_member)
                db_session.commit()

                # FCM Notification
                data = dict(type=notification_type.CIRCLE_MEMBERS_ADD,
                            circleID=circle_id,
                            circleName=circle_name,
                            circleImageURL=images.get_serving_url(
                                new_circle.ImageKey, secure_url=True) if new_circle.ImageKey else None,
                            addedBy=user.Name)
                send_data_multiple(friend_user_id_list, data)

            return get_circle(circle_id)

        message = 'Date of CircleAge must be in future'
    else:
        message = 'Select at least one member to add in circle'

    return jsonify(status=0, message=message)


def edit_circle(json_req, user):
    circle_id = json_req['circleID']
    circle_name = json_req['circleName']
    age_date = json_req['circleAgeDate']  # In the format 'yyyy-mm-dd'

    circle = db_session.query(Circle).filter_by(CircleID=circle_id, Deleted=False).first()

    if circle:
        circle_id = circle.CircleID
        user_id = user.UserID
        # if admin
        if db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                    UserID=user_id,
                                                    IsAdmin=True,
                                                    Removed=False).first():
            if circle_name and circle_name.strip():
                circle_name = circle_name.strip()
                age_date = format_age_date(age_date)
                # Age date should be in future
                if age_date > datetime.date.today():
                    circle.CircleName = circle_name
                    circle.AgeDate = age_date
                    db_session.commit()
                    return get_circle(circle_id)
                raise ValueError('Date of CircleAge must be in future')
            raise ValueError('Invalid Name')
        raise ValueError('You are not authorised to edit this circle')
    raise ValueError('Circle doesn\'t exists')


def add_members(json_req, user):
    circle_id = json_req['circleID']
    members = json_req['members']  # String of FriendUserIDs separated with comma

    user_id = user.UserID
    friend_user_id_list = list()

    circle = db_session.query(Circle).filter_by(CircleID=circle_id, Deleted=False).first()

    # split string members in list and check which one is friend, then append it to friend_user_id_list
    if members and members.strip() and circle:
        member_list = members.split(',')
        for member in member_list:
            friend_user_id = int(member)
            membership = db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                                  UserID=friend_user_id,
                                                                  Removed=False).first()
            # If friend_user is friend with admin and also already not member of circle.
            if __friendship__(user_id, friend_user_id) and not membership:
                friend_user_id_list.append(friend_user_id)

    if circle:
        circle_id = circle.CircleID
        # if admin
        if db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                    UserID=user_id,
                                                    IsAdmin=True,
                                                    Removed=False).first():
            if friend_user_id_list:
                # Adding members in circle, specified by admin.
                for friend_user_id in friend_user_id_list:
                    new_member = CircleMember(CircleID=circle_id, UserID=friend_user_id)
                    db_session.add(new_member)
                    db_session.commit()

                # FCM Notification
                data = dict(type=notification_type.CIRCLE_MEMBERS_ADD,
                            circleID=circle_id,
                            circleName=circle.CircleName,
                            circleImageURL=images.get_serving_url(
                                circle.ImageKey, secure_url=True) if circle.ImageKey else None,
                            addedBy=user.Name)
                send_data_multiple(friend_user_id_list, data)

                return get_circle(circle_id)
            else:
                message = 'Select at least one member to add in circle'
        else:
            message = 'You are not authorised to add members'
    else:
        message = 'Circle doesn\'t exists'

    return jsonify(status=0, message=message)


def remove_member(json_req, user):
    circle_id = json_req['circleID']
    member_user_id = json_req['memberUserID']
    user_id = user.UserID

    circle = db_session.query(Circle).filter_by(CircleID=circle_id, Deleted=False).first()

    if circle:
        circle_id = circle.CircleID
        # if admin
        if db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                    UserID=user_id,
                                                    IsAdmin=True,
                                                    Removed=False).first():

            member = db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                              UserID=member_user_id,
                                                              Removed=False).first()
            # if it is member
            if member:
                # if member to remove and admin are not same
                if member_user_id != user_id:
                    # Removing member from circle, specified by admin.
                    member.Removed = True
                    member.RemovedOn = datetime.datetime.utcnow()
                    db_session.commit()

                    # FCM Notification
                    data = dict(type=notification_type.CIRCLE_MEMBER_REMOVE,
                                circleID=circle_id,
                                circleName=circle.CircleName,
                                circleImageURL=images.get_serving_url(
                                    circle.ImageKey, secure_url=True) if circle.ImageKey else None,
                                removedBy=user.Name)
                    send_data(member_user_id, data)

                    return get_circle(circle_id)
                else:
                    message = 'Cannot remove yourself, use \'Leave circle\' instead'
            else:
                message = 'Not a member of the circle'
        else:
            message = 'You are not authorised to remove member'
    else:
        message = 'Circle doesn\'t exists'

    return jsonify(status=0, message=message)


def make_admin(json_req, user):
    circle_id = json_req['circleID']
    member_user_id = json_req['memberUserID']
    user_id = user.UserID

    circle = db_session.query(Circle).filter_by(CircleID=circle_id, Deleted=False).first()

    if circle:
        circle_id = circle.CircleID
        # if admin
        if db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                    UserID=user_id,
                                                    IsAdmin=True,
                                                    Removed=False).first():

            member = db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                              UserID=member_user_id,
                                                              Removed=False).first()

            # if it is member
            if member:
                # if member is already not admin
                if member.IsAdmin is False:
                    # Making this member admin, specified by admin.
                    member.IsAdmin = True
                    db_session.commit()

                    # FCM Notification
                    data = dict(type=notification_type.CIRCLE_MAKE_ADMIN,
                                circleID=circle_id,
                                circleName=circle.CircleName,
                                circleImageURL=images.get_serving_url(
                                    circle.ImageKey, secure_url=True) if circle.ImageKey else None,
                                madeBy=user.Name)
                    send_data(member_user_id, data)

                    return get_circle(circle_id)
                else:
                    message = 'Member is already an admin'
            else:
                message = 'Not a member of the circle'
        else:
            message = 'You are not authorised to make someone admin'
    else:
        message = 'Circle doesn\'t exists'

    return jsonify(status=0, message=message)


def leave_circle(json_req, user):
    circle_id = json_req['circleID']

    circle = db_session.query(Circle).filter_by(CircleID=circle_id, Deleted=False).first()

    if circle:
        circle_id = circle.CircleID
        user_id = user.UserID

        member = db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                          UserID=user_id,
                                                          Removed=False).first()
        # if it is member
        if member:
            admin = db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                             UserID=user_id,
                                                             IsAdmin=True,
                                                             Removed=False).first()

            admin_count = db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                                   IsAdmin=True,
                                                                   Removed=False).count()

            # if user is not admin or there is more than 1 admin
            if not admin or admin_count > 1:
                # Removing member from circle
                member.Removed = True
                member.RemovedOn = datetime.datetime.utcnow()
                db_session.commit()

                # FCM Notification
                data = dict(type=notification_type.CIRCLE_MEMBER_LEAVE,
                            circleID=circle_id,
                            circleName=circle.CircleName,
                            circleImageURL=images.get_serving_url(
                                circle.ImageKey, secure_url=True) if circle.ImageKey else None,
                            leftBy=user.Name)

                members = db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                                   Removed=False).all()
                member_user_id_list = list()
                for mem in members:
                    member_user_id_list.append(mem.UserID)
                send_data_multiple(member_user_id_list, data)

                return get_circles(None, user)
            else:
                message = 'You are only admin in circle, make someone admin before leaving'
        else:
            message = 'Not a member of the circle'
    else:
        message = 'Circle doesn\'t exists'

    return jsonify(status=0, message=message)


def delete_circle(json_req, user):
    circle_id = json_req['circleID']

    circle = db_session.query(Circle).filter_by(CircleID=circle_id, Deleted=False).first()

    if circle:
        circle_id = circle.CircleID
        user_id = user.UserID

        # if admin
        if db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                    UserID=user_id,
                                                    IsAdmin=True,
                                                    Removed=False).first():
            # Deleting circle
            circle.Deleted = True
            circle.DeletedOn = datetime.datetime.utcnow()
            db_session.commit()
            # Delete profile image of circle.
            delete_image(circle.ImageKey)

            # FCM Notification
            data = dict(type=notification_type.CIRCLE_DELETE,
                        circleID=circle_id,
                        circleName=circle.CircleName,
                        circleImageURL=images.get_serving_url(
                            circle.ImageKey, secure_url=True) if circle.ImageKey else None,
                        deletedBy=user.Name)

            members = db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                               Removed=False).all()
            member_user_id_list = list()
            for mem in members:
                member_user_id_list.append(mem.UserID)
            send_data_multiple(member_user_id_list, data)

            return get_circles(None, user)

        message = 'You are not authorised to delete circle'
    else:
        message = 'Circle doesn\'t exists'

    return jsonify(status=0, message=message)


def get_circle(circle_id):
    circle = db_session.query(Circle).filter_by(CircleID=circle_id, Deleted=False).first()

    if circle:
        circle_members = db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                                  Removed=False).all()
        members = list()

        for cm in circle_members:
            user = db_session.query(User).filter_by(UserID=cm.UserID).first()
            members.append(dict(memberUserID=user.UserID,
                                memberName=user.Name,
                                memberMobile=user.Mobile,
                                memberEmail=user.EmailID,
                                imageURL=images.get_serving_url(
                                    user.ImageKey, secure_url=True) if user.ImageKey else None,
                                isAdmin=cm.IsAdmin))

        return jsonify(status=1, message='success',
                       circle=dict(circleID=circle_id,
                                   circleName=circle.CircleName,
                                   circleAgeDate=circle.AgeDate.isoformat(),
                                   imageURL=images.get_serving_url(
                                       circle.ImageKey, secure_url=True) if circle.ImageKey else None,
                                   members=[i for i in members]))

    return jsonify(status=0, message='Circle doesn\'t exists')


def get_circles(json_req, user):
    user_id = user.UserID
    user_in_circles = db_session.query(CircleMember).filter_by(UserID=user_id,
                                                               Removed=False).all()
    circles = list()

    for uic in user_in_circles:
        members = list()
        circle_id = uic.CircleID
        circle = db_session.query(Circle).filter_by(CircleID=circle_id,
                                                    Deleted=False).first()
        if circle:
            circle_members = db_session.query(CircleMember).filter_by(CircleID=circle_id,
                                                                      Removed=False).all()
            for cm in circle_members:
                member_user = db_session.query(User).filter_by(UserID=cm.UserID).first()
                members.append(dict(memberUserID=member_user.UserID,
                                    memberName=member_user.Name,
                                    memberMobile=member_user.Mobile,
                                    memberEmail=member_user.EmailID,
                                    imageURL=images.get_serving_url(
                                        member_user.ImageKey, secure_url=True) if member_user.ImageKey else None,
                                    isAdmin=cm.IsAdmin))

            circles.append(dict(circleID=circle_id,
                                circleName=circle.CircleName,
                                circleAgeDate=circle.AgeDate.isoformat(),
                                imageURL=images.get_serving_url(
                                    circle.ImageKey, secure_url=True) if circle.ImageKey else None,
                                members=[i for i in members]))

    return jsonify(status=1, message='success',
                   circles=[i for i in circles])
