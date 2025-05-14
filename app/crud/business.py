from sqlalchemy.orm import Session
from app.models.business_details import Business

def create_business(db: Session, user_id: int, data):
    business = Business(user_id=user_id, **data.dict())
    db.add(business)
    db.commit()
    db.refresh(business)
    return business

def get_business(db: Session, business_id: int):
    return db.query(Business).filter(Business.id == business_id).first()

def get_all_businesses(db: Session):
    return db.query(Business).all()

def update_business(db: Session, business_id: int, data):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(business, key, value)
    db.commit()
    db.refresh(business)
    return business

def delete_business(db: Session, business_id: int):
    business = db.query(Business).filter(Business.id == business_id).first()
    if business:
        db.delete(business)
        db.commit()
    return business
