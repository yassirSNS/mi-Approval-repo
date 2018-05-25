from flask import request, jsonify
from models.user import User
from models.friend import FriendRequest
from . import db_session


def sync_contacts():
    if request.method == 'POST':
        try:
            json_req = request.get_json()
            token = str(json_req['token']).strip()
            contacts = str(json_req['contacts']).strip()
            user = User.verify_token(token)
            if user:
                contact_list = contacts.split(',')
                registered_contact_list = list()
                for contact in contact_list:
                    contact_user = db_session.query(User).filter_by(Mobile=contact).first()
                    if contact_user:
                        friend_request_status = False
                        # Check if user has sent friend request to this contact.
                        if db_session.query(FriendRequest).filter_by(UserID=user.UserID,
                                                                     FriendUserID=contact_user.UserID,
                                                                     Deleted=False).first():
                            friend_request_status = True
                        registered_contact_list.append(dict(mobile=contact,
                                                            isRequestSent=friend_request_status))
                return jsonify(status=1, message='success',
                               registeredContacts=[i for i in registered_contact_list])
            else:
                message = 'Invalid token'

        except Exception as e:
            db_session.rollback()
            message = format(e)

        return jsonify(status=0, message=message)