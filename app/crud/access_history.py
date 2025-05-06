from sqlalchemy.orm import Session
from models.access_history import AccessHistory

def create_access_history(db: Session, username: str, hashed_password: str, access_status: int):
    try:
        access_history = AccessHistory(username=username, 
                                    hashed_password=hashed_password, 
                                    access_status=access_status)
        db.add(access_history)
        db.commit()
        db.refresh(access_history)
    except Exception as e:
        pass