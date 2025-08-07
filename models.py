from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    emp_id = Column(Integer, unique=True, nullable=False)

    submissions = relationship("Submission", back_populates="user")


class Submission(Base):
    __tablename__ = 'submissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    submission_date = Column(Date)
    submitted = Column(Boolean, default=False)

    user = relationship("User", back_populates="submissions")


class AdminSettings(Base):
    __tablename__ = 'admin_settings'

    id = Column(Integer, primary_key=True)
    password = Column(String, nullable=False)
    poll_end_time = Column(String(5), default='18:30')
    poll_manually_ended = Column(Boolean, default=False)


# Database setup
DATABASE_URL = "sqlite:///dinner_poll.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
