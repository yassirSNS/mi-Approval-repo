import datetime
from sqlalchemy import Column, ForeignKey, Boolean, Integer, String, DateTime
from db_setup import Base, engine

# Base = declarative_base()


class FriendRequest(Base):
    __tablename__ = 'friend_request'

    FriendRequestID = Column(Integer, primary_key=True)
    UserID = Column(Integer, nullable=False)
    FriendUserID = Column(Integer, nullable=False)
    AcceptanceStatus = Column(Boolean)
    Deleted = Column(Boolean, default=False)
    RequestOn = Column(DateTime, default=datetime.datetime.utcnow)
    RespondOn = Column(DateTime)


class Friend(Base):
    __tablename__ = 'friend'

    FriendID = Column(Integer, primary_key=True)
    UserID = Column(Integer, nullable=False)
    FriendUserID = Column(Integer, nullable=False)
    AddedOn = Column(DateTime, default=datetime.datetime.utcnow)


Base.metadata.create_all(engine())