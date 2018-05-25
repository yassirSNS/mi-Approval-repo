import datetime
from sqlalchemy import Column, ForeignKey, Boolean, Integer, String, Date, DateTime
from db_setup import Base, engine

# Base = declarative_base()


class Circle(Base):
    __tablename__ = 'circle'

    CircleID = Column(Integer, primary_key=True)
    CircleName = Column(String(50), nullable=False)
    ImageKey = Column(String(256), nullable=True)
    UserID = Column(Integer, nullable=False)
    Deleted = Column(Boolean, default=False)
    AgeDate = Column(Date, nullable=True)
    CreatedOn = Column(DateTime, default=datetime.datetime.utcnow)
    DeletedOn = Column(DateTime, nullable=True)


class CircleMember(Base):
    __tablename__ = 'circle_member'

    CircleMemberID = Column(Integer, primary_key=True)
    CircleID = Column(Integer, nullable=False)
    UserID = Column(Integer, nullable=False)
    IsAdmin = Column(Boolean, default=False)
    Removed = Column(Boolean, default=False)
    AddedOn = Column(DateTime, default=datetime.datetime.utcnow)
    RemovedOn = Column(DateTime, nullable=True)


Base.metadata.create_all(engine())