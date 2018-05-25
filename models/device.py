from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from db_setup import Base, engine
from models.user import User


class Device(Base):
    __tablename__ = 'device'

    DeviceID = Column(Integer, primary_key=True)
    DeviceType = Column(SmallInteger, nullable=False)
    DeviceDesc = Column(String(32), nullable=True)
    DeviceCode = Column(String(32), nullable=True)
    UserID = Column(Integer, ForeignKey(User.UserID), nullable=False)
    FcmID = Column(String(256), nullable=False)

    device_user = relationship('User', foreign_keys=UserID)


Base.metadata.create_all(engine())