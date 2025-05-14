from sqlalchemy.orm import Session
from app.models.access_history import AccessHistory

def create_access_history(db: Session, mobile_number: str, hashed_password: str, access_status: int):
    try:
        access_history = AccessHistory(mobile_number=mobile_number, 
                                    hashed_password=hashed_password, 
                                    access_status=access_status)
        db.add(access_history)
        db.commit()
        db.refresh(access_history)
    except Exception as e:
        pass