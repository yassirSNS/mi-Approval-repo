import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import column_property
from passlib.apps import custom_app_context as pwd_context
import uuid
from db_setup import Base, engine
from views import db_session


class User(Base):
    __tablename__ = 'user'

    UserID = Column(Integer, primary_key=True)
    Name = Column(String(50), nullable=False)
    CountryCode = Column(String(5), nullable=False)
    MobileNo = Column(String(16), nullable=False)
    EmailID = Column(String(100), nullable=True)
    ImageKey = Column(String(256), nullable=True)
    PasswordHash = Column(String(128), nullable=False)
    Token = Column(String(128), nullable=True)
    RegisteredOn = Column(DateTime, default=datetime.datetime.utcnow)

    Mobile = column_property(CountryCode+MobileNo)

    def hash_password(self, password):
        self.PasswordHash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.PasswordHash)

    def generate_token(self):
        t = str(uuid.uuid1())
        self.Token = t
        return t

    @staticmethod
    def verify_token(token):
        return db_session.query(User).filter_by(Token=token).first()


class OTPLog(Base):
    __tablename__ = 'otp_log'

    LogID = Column(Integer, primary_key=True)
    CountryCode = Column(String(5), nullable=False)
    MobileNo = Column(String(16), nullable=False)
    OTP = Column(String(5), nullable=False)
    Verified = Column(Boolean, default=False)
    CreatedOn = Column(DateTime, default=datetime.datetime.utcnow)

    Mobile = column_property(CountryCode+MobileNo)


Base.metadata.create_all(engine())