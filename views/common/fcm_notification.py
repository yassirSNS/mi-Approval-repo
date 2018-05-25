from pyfcm import FCMNotification
from models.device import Device
from .. import db_session

API_KEY = 'AAAAO41K1xA:APA91bH5XXwaX5bfnIo1wNDHGDmfTys6PpQchZHuu3aKwwISf8WQWTzVtswVvJZnrUXUSmBuoSj_6PtGAGnw_KqUOpDYuNB9J99L0Ii5R_-OisDpfZXtdd0yj9L9n8ugO6ml30mkQjCb'

push_service = FCMNotification(api_key=API_KEY, env='app_engine')

# OR initialize with proxies
# proxy_dict = {"http": "http://127.0.0.1",
#               "https": "http://127.0.0.1"}
#
# push_service = FCMNotification(api_key=API_KEY, proxy_dict=proxy_dict, env='app_engine')


def send(registration_id, message_title, message_body):
    result = push_service.notify_single_device(registration_id=registration_id,
                                               message_title=message_title,
                                               message_body=message_body)


def send_multiple(registration_ids, message_title, message_body):
    result = push_service.notify_multiple_devices(registration_ids=registration_ids,
                                                  message_title=message_title,
                                                  message_body=message_body)


# Client app is responsible for processing data messages. Data messages have only custom key-value pairs. (Python dict)
# Data messages let developers send up to 4KB of custom key-value pairs.

# Sending a data message only payload, do NOT include message_body also do NOT include notification body

def send_data(user_id, data_message):
    device = db_session.query(Device).filter_by(UserID=user_id).first()
    if device:
        registration_id = device.FcmID
        result = push_service.single_device_data_message(registration_id=registration_id,
                                                         data_message=data_message)


def send_data_multiple(user_ids, data_message):
    devices = db_session.query(Device).filter(Device.UserID.in_(user_ids)).all()
    registration_ids = list()
    for device in devices:
        registration_ids.append(device.FcmID)
    if registration_ids:
        result = push_service.multiple_devices_data_message(registration_ids=registration_ids,
                                                            data_message=data_message)
