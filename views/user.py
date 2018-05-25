import datetime
from flask import request, jsonify
from google.appengine.api import images
from models.user import User, OTPLog
from views.common.otp import generate_otp, send_otp, REGISTRATION, PASSWORD
from . import db_session


def register_mobile():
    if request.method == 'POST':
        try:
            json_req = request.get_json()
            country_code = str(json_req['countryCode']).strip()
            mobile = str(json_req['mobileNo']).strip()
            status = 0
            if db_session.query(User).filter_by(CountryCode=country_code, MobileNo=mobile).first():
                message = 'Mobile no. {}{} already registered'.format(country_code, mobile)
            else:
                log = db_session.query(OTPLog).filter(
                    OTPLog.CountryCode == country_code,
                    OTPLog.MobileNo == mobile,
                    OTPLog.Verified == False,
                    OTPLog.CreatedOn >= datetime.datetime.utcnow() - datetime.timedelta(minutes=2)
                ).first()
                if log:
                    message = 'OTP already sent or wait for 2 minutes.'
                else:
                    otp = generate_otp()

                    new_user = OTPLog(CountryCode=country_code, MobileNo=mobile, OTP=otp)
                    db_session.add(new_user)
                    db_session.commit()

                    # Sending OTP to mobile
                    send_otp(new_user.Mobile, otp, otp_type=REGISTRATION)

                    status = 1
                    message = 'success'
        except Exception as e:
            db_session.rollback()
            status = 0
            message = format(e)
        return jsonify(status=status, message=message)


def verify_mobile():
    if request.method == 'POST':
        try:
            json_req = request.get_json()
            country_code = str(json_req['countryCode']).strip()
            mobile = str(json_req['mobileNo']).strip()
            otp = str(json_req['otp']).strip()
            status = 0
            if db_session.query(User).filter_by(CountryCode=country_code, MobileNo=mobile).first():
                message = 'Mobile no. {}{} already registered'.format(country_code, mobile)
            else:
                log = db_session.query(OTPLog).filter(
                    OTPLog.CountryCode == country_code,
                    OTPLog.MobileNo == mobile,
                    OTPLog.OTP == otp,
                    OTPLog.Verified == False,
                    OTPLog.CreatedOn >= datetime.datetime.utcnow() - datetime.timedelta(minutes=2)
                    ).first()
                if not log:
                    message = 'Invalid OTP'
                else:
                    log.Verified = True
                    db_session.commit()
                    status = 1
                    message = 'success'
        except Exception as e:
            db_session.rollback()
            status = 0
            message = format(e)
        return jsonify(status=status, message=message)


def register_user():
    if request.method == 'POST':
        try:
            json_req = request.get_json()
            name = str(json_req['name']).strip()
            country_code = str(json_req['countryCode']).strip()
            mobile = str(json_req['mobileNo']).strip()
            password = str(json_req['password']).strip()
            status = 0
            if 'email' in json_req:
                email = str(json_req['email']).strip().lower()
            else:
                email = None
            if db_session.query(User).filter_by(CountryCode=country_code, MobileNo=mobile).first():
                message = "Mobile no. {}{} already registered".format(country_code, mobile)
            elif len(password) < 6 or len(password) > 20:
                message = 'Password must be between 6 to 20 characters long'
            else:
                verified = db_session.query(OTPLog).filter_by(CountryCode=country_code,
                                                              MobileNo=mobile,
                                                              Verified=True).first()
                if not verified:
                    message = 'Mobile number not verified, kindly verify it by OTP'
                else:
                    new_user = User(Name=name, CountryCode=country_code, MobileNo=mobile, EmailID=email)
                    new_user.hash_password(password)
                    db_session.add(new_user)
                    db_session.commit()
                    status = 1
                    message = "success"
        except Exception as e:
            db_session.rollback()
            status = 0
            message = format(e)
        return jsonify(status=status, message=message)


def login_user():
    if request.method == 'POST':
        try:
            json_req = request.get_json()
            mobile = str(json_req['mobile']).strip()
            password = str(json_req['password']).strip()
            user = db_session.query(User).filter_by(Mobile=mobile).first()
            if user and user.verify_password(password):
                token = user.generate_token()
                db_session.commit()
                return jsonify(status=1, message="success", token=token,
                               userID=user.UserID, name=user.Name,
                               mobile=user.Mobile, email=user.EmailID)
            message = "Invalid mobile or password."
        except Exception as e:
            db_session.rollback()
            message = format(e)
        return jsonify(status=0, message=message)


def forgot_password():
    if request.method == 'POST':
        try:
            json_req = request.get_json()
            country_code = str(json_req['countryCode']).strip()
            mobile = str(json_req['mobileNo']).strip()

            if not db_session.query(User).filter_by(CountryCode=country_code, MobileNo=mobile).first():
                msg = 'Mobile no. {}{} not registered. Please register.'.format(country_code, mobile)
                raise ValueError(msg)

            log = db_session.query(OTPLog).filter(
                OTPLog.CountryCode == country_code,
                OTPLog.MobileNo == mobile,
                OTPLog.Verified == False,
                OTPLog.CreatedOn >= datetime.datetime.utcnow() - datetime.timedelta(minutes=2)
            ).first()

            if log:
                raise ValueError('OTP already sent or wait for 2 minutes.')

            otp = generate_otp()

            new_otp = OTPLog(CountryCode=country_code, MobileNo=mobile, OTP=otp)
            db_session.add(new_otp)
            db_session.commit()

            # Sending OTP to mobile
            send_otp(new_otp.Mobile, otp, otp_type=PASSWORD)

            status = 1
            message = 'success'
        except Exception as e:
            db_session.rollback()
            status = 0
            message = format(e)
        return jsonify(status=status, message=message)


def reset_password():
    if request.method == 'POST':
        try:
            json_req = request.get_json()
            country_code = str(json_req['countryCode']).strip()
            mobile = str(json_req['mobileNo']).strip()
            password = str(json_req['password']).strip()
            otp = str(json_req['otp']).strip()

            user = db_session.query(User).filter_by(CountryCode=country_code,
                                                    MobileNo=mobile).first()
            if not user:
                msg = 'Mobile no. {}{} not registered. Please register.'.format(country_code, mobile)
                raise ValueError(msg)

            if len(password) < 6 or len(password) > 20:
                raise ValueError('Password must be between 6 to 20 characters long')

            log = db_session.query(OTPLog).filter(
                OTPLog.CountryCode == country_code,
                OTPLog.MobileNo == mobile,
                OTPLog.OTP == otp,
                OTPLog.Verified == False,
                OTPLog.CreatedOn >= datetime.datetime.utcnow() - datetime.timedelta(minutes=2)
            ).first()

            if log:
                # Update new password
                user.hash_password(password)
                # Update otp_log, since OTP is verified
                log.Verified = True
                db_session.commit()

                status = 1
                message = 'success'
            else:
                raise ValueError('Invalid OTP')
        except Exception as e:
            db_session.rollback()
            status = 0
            message = format(e)
        return jsonify(status=status, message=message)


def edit_profile():
    if request.method == 'POST':
        try:
            json_req = request.get_json()
            token = str(json_req['token']).strip()
            name = json_req['name']
            email = json_req['email']

            user = User.verify_token(token)
            if user:
                if name and name.strip():
                    user.Name = name.strip()
                if email and email.strip():
                    user.EmailID = email.strip()
                db_session.commit()
                return jsonify(status=1, message='success')
            raise ValueError('Invalid token')
        except Exception as e:
            db_session.rollback()
            message = format(e)
        return jsonify(status=0, message=message)


def get_profile():
    if request.method == 'POST':
        try:
            json_req = request.get_json()
            token = str(json_req['token']).strip()

            user = User.verify_token(token)
            if user:
                return jsonify(status=1, message="success", token=token,
                               userID=user.UserID, name=user.Name,
                               mobile=user.Mobile, email=user.EmailID,
                               imageURL=images.get_serving_url(
                                   user.ImageKey, secure_url=True) if user.ImageKey else None)
            raise ValueError('Invalid token')
        except Exception as e:
            db_session.rollback()
            message = format(e)
        return jsonify(status=0, message=message)
