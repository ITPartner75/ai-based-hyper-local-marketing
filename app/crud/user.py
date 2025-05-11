from sqlalchemy.orm import Session
from schemas.user import UserCreate
from models.user import User

def get_user_by_mobile(db: Session, mobile_number: str):
    return db.query(User).filter(User.mobile_number == mobile_number).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session,hashed_password: str, data: UserCreate):
    user = User(
        mobile_number=data.mobile_number,
        username=f"{data.first_name}_{data.mobile_number}",
        hashed_password = hashed_password,
        first_name = data.first_name,
        last_name = data.last_name)
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
