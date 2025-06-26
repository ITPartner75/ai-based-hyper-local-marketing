from sqlalchemy.orm import Session
from app.models.business_details import *
from app.schemas.business import BusinessDetailsOut, MediaBase, ContactBase
from app.util.webscrap import get_website_logo_bytes
from fastapi.responses import StreamingResponse
import base64, io

def unset_active_records(db: Session, model: str, business_id: int, active_id: int):
    all_active = db.query(model).filter(model.business_id == business_id,
                                  model.is_active == True,
                                  model.id != active_id).all()
    print(all_active)
    for rec in all_active:
        setattr(rec, "is_active", False)
        db.commit()
        db.refresh(rec)

def create_business(db: Session, user_id: int, data):
    business = Business(user_id=user_id, **data.dict())
    print(f"Business: {business}")
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
    business = db.query(Business).filter(Business.id == business_id,
                                         Business.is_active == True).first()
    if not business:
        return None
    setattr(business, "is_active", False)
    db.commit()
    db.refresh(business)
    return business

#media
def standardize_media(media: Media):
    print(media.__dict__)
    media.images = base64.b64encode(media.images).decode("utf-8") if media.images else None
    media.logo = base64.b64encode(media.logo).decode("utf-8") if media.logo else None
    media.brochure = base64.b64encode(media.brouchure).decode("utf-8") if media.brouchure else None
    media.report = base64.b64encode(media.report).decode("utf-8") if media.report else None
    media.videos = base64.b64encode(media.videos).decode("utf-8") if media.videos else None
    return media

def create_media(db: Session, user_id: int, business_id: int, data):
    contact = get_contact(db=db, business_id=business_id)
    if contact.website:
        if data.logo is None:
            logo_bytes = get_website_logo_bytes(contact.website)
            data.logo = logo_bytes
    media = Media(user_id=user_id, business_id=business_id, **data.dict())
    print(f"Media: {media.logo}")
    db.add(media)
    db.commit()
    db.refresh(media)
    unset_active_records(db=db, model=Media, business_id=media.business_id, active_id=media.id)
    
    return standardize_media(media)

def get_media(db: Session, business_id: int, field_name: str=None):
    media = db.query(Media).filter(Media.business_id == business_id,
                                  Media.is_active == True).first()
    if not media:
        return None
    if field_name:
        valid_fields = {"images", "logo", "brouchure", "report", "videos"}
        if field_name not in valid_fields:
            return "invalid"
        binary_data = getattr(media, field_name)
        if not binary_data:
            return None

        mime_type = {
            "images": "image/png",
            "logo": "image/png",
            "brouchure": "application/pdf",
            "report": "application/pdf",
            "videos": "video/mp4",
        }.get(field_name, "application/octet-stream")
        return StreamingResponse(io.BytesIO(binary_data), media_type=mime_type)
    return standardize_media(media)

def update_media(db: Session, business_id: int, data):
    media = db.query(Media).filter(Media.business_id == business_id,
                                   Media.is_active == True).first()
    if not media:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(media, key, value)
    db.commit()
    db.refresh(media)
    return standardize_media(media)

def delete_media(db: Session, business_id: int):
    media = db.query(Media).filter(Media.business_id == business_id,
                                   Media.is_active == True).first()
    if not media:
        return None
    setattr(media, "is_active", False)
    db.commit()
    db.refresh(media)
    return standardize_media(media)

#contact
def create_contact(db: Session, user_id: int, business_id: int, data):
    contact = Contact(user_id=user_id, business_id=business_id, **data.dict())
    print(f"Contact: {contact}")
    db.add(contact)
    db.commit()
    db.refresh(contact)
    unset_active_records(db=db, model=Contact, business_id=contact.business_id, 
                         active_id=contact.id)
    return contact

def get_contact(db: Session, business_id: int):
    return db.query(Contact).filter(Contact.business_id == business_id,
                                    Contact.is_active == True).first()

def update_contact(db: Session, business_id: int, data):
    contact = db.query(Contact).filter(Contact.business_id == business_id,
                                       Contact.is_active == True).first()
    if not contact:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(contact, key, value)
    db.commit()
    db.refresh(contact)
    if "website" in list(data.dict(exclude_unset=True).keys()):
        media = get_media(db=db, business_id=business_id)
        if media:
            if media.logo is None:
                logo_bytes = get_website_logo_bytes(contact.website)
                media.logo = logo_bytes
                db.commit()
                db.refresh(media)
    return contact

def delete_contact(db: Session, business_id: int):
    contact = db.query(Contact).filter(Contact.business_id == business_id,
                                       Contact.is_active == True).first()
    if not contact:
        return None
    setattr(contact, "is_active", False)
    db.commit()
    db.refresh(contact)
    return contact

#business details
def create_business_details(db: Session, user_id: int, business_id: int, data):
    contact = get_contact(db=db, business_id=business_id)
    media = get_media(db=db, business_id=business_id)
    business_details = BusinessDetails(user_id=user_id, business_id=business_id, 
                                       media_id=media.id, contact_id=contact.id, 
                                       **data.dict())
    print(f"Business: {business_details}")
    db.add(business_details)
    db.commit()
    db.refresh(business_details)
    unset_active_records(db=db, model=BusinessDetails, business_id=business_details.business_id, 
                         active_id=business_details.id)
    business_details_out = BusinessDetailsOut(media=MediaBase.model_validate(media), 
                                              contact=ContactBase.model_validate(contact),
                                              products=business_details.products
                                              )
    return business_details_out

def get_business_details(db: Session, business_id: int):
    business_details = db.query(BusinessDetails).filter(BusinessDetails.business_id == business_id,
                                            BusinessDetails.is_active == True).first()
    if business_details:
        contact = get_contact(db=db, business_id=business_details.business_id)
        media = get_media(db=db, business_id=business_details.business_id)
        business_details_out = BusinessDetailsOut(media=MediaBase.model_validate(media), 
                                                  contact=ContactBase.model_validate(contact),
                                                  products=business_details.products
                                                )
    else:
        business_details_out = BusinessDetailsOut()
        
    return business_details_out


def update_business_details(db: Session, business_id: int, data):
    business_details = db.query(BusinessDetails).filter(BusinessDetails.business_id == business_id,
                                                        BusinessDetails.is_active == True).first()
    if not business_details:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(business_details, key, value)
    db.commit()
    db.refresh(business_details)
    contact = get_contact(db=db, business_id=business_details.business_id)
    media = get_media(db=db, business_id=business_details.business_id)
    business_details_out = BusinessDetailsOut(media=MediaBase.model_validate(media), 
                                                contact=ContactBase.model_validate(contact),
                                                products=business_details.products
                                            )
        
    return business_details_out

def delete_business_details(db: Session, business_id: int):
    business_details = db.query(BusinessDetails).filter(BusinessDetails.business_id == business_id,
                                                        BusinessDetails.is_active == True).first()
    
    if not business_details:
        return None 
    setattr(business_details, "is_active", False)
    db.commit()
    db.refresh(business_details)
    contact = get_contact(db=db, business_id=business_details.business_id)
    media = get_media(db=db, business_id=business_details.business_id)
    business_details_out = BusinessDetailsOut(media=MediaBase.model_validate(media), 
                                            contact=ContactBase.model_validate(contact),
                                            products=business_details.products
                                        )
    return business_details_out