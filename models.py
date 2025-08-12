import os
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    emp_id = Column(Integer, unique=True, nullable=False)
    emp_name = Column(String(255), nullable=False)

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
    password = Column(String(255), nullable=False)
    poll_end_time = Column(String(5), default='18:30')
    poll_manually_ended = Column(Boolean, default=False)


# Database setup - MySQL configuration using environment variables
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PWD = os.getenv('DB_PWD')
DB_PORT = os.getenv('DB_PORT', '3306')

# MySQL connection string
DATABASE_URL = f"mysql+pymysql://{DB_USERNAME}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
