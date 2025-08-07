from datetime import datetime, timedelta
import pytz
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from models import Base, User, Submission, AdminSettings, engine

IST_TZ = 'Asia/Kolkata'

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


def init_db():
    # Run migrations first
    try:
        run_migrations()
    except Exception:
        # Fallback to creating tables if migrations fail
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if admin settings exist, if not create default
        admin = db.query(AdminSettings).filter(AdminSettings.id == 1).first()
        if not admin:
            admin = AdminSettings(
                id=1, password='admin123', poll_end_time='18:30', poll_manually_ended=False)
            db.add(admin)
            db.commit()
    finally:
        db.close()


def get_users():
    db = SessionLocal()
    try:
        users = db.query(User.id, User.emp_id).order_by(User.emp_id).all()
        return users
    finally:
        db.close()


def get_user_submission_status(user_id, date_str):
    db = SessionLocal()
    try:
        submission = db.query(Submission).filter(
            Submission.user_id == user_id,
            Submission.submission_date == date_str
        ).first()
        return submission.submitted if submission else False
    finally:
        db.close()


def submit_poll(user_id, date_str):
    db = SessionLocal()
    try:
        submission = db.query(Submission).filter(
            Submission.user_id == user_id,
            Submission.submission_date == date_str
        ).first()

        if submission:
            submission.submitted = True
        else:
            submission = Submission(
                user_id=user_id, submission_date=date_str, submitted=True)
            db.add(submission)

        db.commit()
    finally:
        db.close()


def get_ist_date():
    ist = pytz.timezone(IST_TZ)
    return datetime.now(ist).date()


def is_poll_time_active():
    ist = pytz.timezone(IST_TZ)
    current_time = datetime.now(ist).time()
    cutoff_time = datetime.strptime(get_poll_end_time(), '%H:%M').time()
    return current_time < cutoff_time


def clear_old_submissions():
    db = SessionLocal()
    try:
        current_ist_date = str(get_ist_date())
        db.query(Submission).filter(
            Submission.submission_date < current_ist_date).delete()
        db.commit()
    finally:
        db.close()


def add_user(emp_id):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.emp_id == emp_id).first()
        if existing:
            return False

        user = User(emp_id=emp_id)
        db.add(user)
        db.commit()
        return True
    except Exception:
        return False
    finally:
        db.close()


def remove_user(emp_id):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.emp_id == emp_id).first()
        if user:
            db.query(Submission).filter(Submission.user_id == user.id).delete()
            db.delete(user)
            db.commit()
            return True
        return False
    finally:
        db.close()


def get_poll_stats(date_str):
    db = SessionLocal()
    try:
        from sqlalchemy import func
        stats = db.query(
            User.emp_id,
            func.coalesce(Submission.submitted, 0).label('submitted')
        ).outerjoin(
            Submission,
            (User.id == Submission.user_id) & (
                Submission.submission_date == date_str)
        ).order_by(User.emp_id).all()
        return stats
    finally:
        db.close()


def end_poll(date_str):
    db = SessionLocal()
    try:
        db.query(Submission).filter(
            Submission.submission_date == date_str).delete()
        # Mark poll as manually ended
        admin = db.query(AdminSettings).filter(AdminSettings.id == 1).first()
        if admin:
            admin.poll_manually_ended = True
        db.commit()
    finally:
        db.close()


def get_admin_password():
    db = SessionLocal()
    try:
        admin = db.query(AdminSettings).filter(AdminSettings.id == 1).first()
        return admin.password if admin else 'admin123'
    finally:
        db.close()


def update_admin_password(new_password):
    db = SessionLocal()
    try:
        admin = db.query(AdminSettings).filter(AdminSettings.id == 1).first()
        if admin:
            admin.password = new_password
            db.commit()
    finally:
        db.close()


def get_poll_end_time():
    db = SessionLocal()
    try:
        admin = db.query(AdminSettings).filter(AdminSettings.id == 1).first()
        return admin.poll_end_time if admin else '18:30'
    finally:
        db.close()


def extend_poll(minutes):
    current_end_time = get_poll_end_time()
    current_dt = datetime.strptime(current_end_time, '%H:%M')
    new_dt = current_dt + timedelta(minutes=minutes)
    new_time = new_dt.strftime('%H:%M')

    db = SessionLocal()
    try:
        admin = db.query(AdminSettings).filter(AdminSettings.id == 1).first()
        if admin:
            admin.poll_end_time = new_time
            db.commit()
    finally:
        db.close()

    return new_time


def reset_poll_time():
    db = SessionLocal()
    try:
        admin = db.query(AdminSettings).filter(AdminSettings.id == 1).first()
        if admin:
            admin.poll_end_time = '18:30'
            db.commit()
    finally:
        db.close()


def is_poll_manually_ended():
    db = SessionLocal()
    try:
        admin = db.query(AdminSettings).filter(AdminSettings.id == 1).first()
        return admin.poll_manually_ended if admin else False
    finally:
        db.close()


def set_poll_manually_ended(ended=True):
    db = SessionLocal()
    try:
        admin = db.query(AdminSettings).filter(AdminSettings.id == 1).first()
        if admin:
            admin.poll_manually_ended = ended
            db.commit()
    finally:
        db.close()
