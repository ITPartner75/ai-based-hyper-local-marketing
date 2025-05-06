from sqlalchemy.orm import Session
from models.user import User

def get_user_by_mobile(db: Session, mobile_number: str):
    return db.query(User).filter(User.mobile_number == mobile_number).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, mobile_number: str, role: str = "Normal"):
    user = User(mobile_number=mobile_number, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_credentials(db: Session, user: User, username: str, hashed_password: str):
    user.username = username
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    return user
from sqlalchemy.orm import Session
from models.user import User

def get_user_by_mobile(db: Session, mobile_number: str):
    return db.query(User).filter(User.mobile_number == mobile_number).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, mobile_number: str, role: str = "Normal"):
    user = User(mobile_number=mobile_number, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_credentials(db: Session, user: User, username: str, hashed_password: str):
    user.username = username
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    return user
