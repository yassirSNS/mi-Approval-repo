from sqlalchemy.orm import sessionmaker
from models.db_setup import Base, engine


Base.metadata.bind = engine()

DBSession = sessionmaker(bind=engine())
db_session = DBSession()
