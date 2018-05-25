from flask import request, jsonify
from models.device import Device
from models.user import User
from . import db_session

ANDROID = 1
IOS = 2
OTHERS = 3


def device_operation(operation):
    if request.method == 'POST':
        try:
            json_req = request.get_json()
            token = str(json_req['token']).strip()
            user = User.verify_token(token)
            if user:
                # call the respective function.
                return operation(json_req, user)
            message = 'Invalid token'

        except Exception as e:
            db_session.rollback()
            message = format(e)
        return jsonify(status=0, message=message)


def register_device(json_req, user):
    device_type = json_req['deviceType']
    device_desc = json_req['deviceDescription']
    device_code = json_req['deviceCode']
    fcm_id = json_req['fcmID']

    if device_type not in (ANDROID, IOS, OTHERS):
        raise ValueError('Invalid deviceType')

    if fcm_id and fcm_id.strip():
        fcm_id = fcm_id.strip()
    else:
        raise ValueError('Invalid FCM ID')

    user_id = user.UserID
    device = db_session.query(Device).filter_by(DeviceType=device_type,
                                                UserID=user_id).first()

    if device:
        device.DeviceDesc = device_desc
        device.DeviceCode = device_code
        device.FcmID = fcm_id
        db_session.commit()
    else:
        new_device = Device(DeviceType=device_type,
                            DeviceDesc=device_desc,
                            DeviceCode=device_code,
                            UserID=user_id,
                            FcmID=fcm_id)
        db_session.add(new_device)
        db_session.commit()

    return jsonify(status=1, message='success')
