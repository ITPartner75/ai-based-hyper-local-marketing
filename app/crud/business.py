from sqlalchemy.orm import Session
from app.models.business_details import *
from app.schemas.business import BusinessDetailsOut, MediaBase, ContactBase
from app.util.webscrap import get_website_logo_bytes, get_website_products, get_website_images
from app.util.file_utils import save_media_locally, save_product_locally
from app.util.ai_utils import CaptionImage, ClassifyImage
from app.constants.business import ALLOWED_TYPES
from fastapi.responses import StreamingResponse
from fastapi.responses import FileResponse
from fastapi import UploadFile
import base64
from io import BytesIO

def commit_db(db: Session, model: str):
    db.commit()
    db.refresh(model)

def add_to_db(db: Session, model: str):
    db.add(model)
    commit_db(db=db, model=model)

def update_db(db: Session, model: str, field: str, value):
    setattr(model, field, value)
    commit_db(db=db, model=model)

def unset_active_records(db: Session, model: str, business_id: int, active_id: int):
    all_active = db.query(model).filter(model.business_id == business_id,
                                  model.is_active == True,
                                  model.id != active_id).all()
    print(all_active)
    for rec in all_active:
        update_db(db=db, model=rec, field="is_active", value=False)
    
def create_business(db: Session, user_id: int, data):
    business = Business(user_id=user_id, **data.dict())
    add_to_db(db=db, model=business)
    return business

def get_business(db: Session, business_id: int):
    return db.query(Business).filter(Business.id == business_id,
                                     Business.is_active == True).first()

def get_all_businesses(db: Session):
    return db.query(Business).all()

def update_business(db: Session, business_id: int, data):
    business = get_business(db=db, business_id=business_id)
    if not business:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(business, key, value)
    commit_db(db=db, model=business)
    return business

def delete_business(db: Session, business_id: int):
    business = get_business(db=db, business_id=business_id)
    if not business:
        return None
    update_db(db=db, model=business, field="is_active", value=False)
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

def create_media(db: Session, user_id: int, business_id: int):
    media = Media(user_id=user_id, business_id=business_id)
    add_to_db(db=db, model=media)
    unset_active_records(db=db, model=Media, business_id=media.business_id, active_id=media.id)
    return media

def upload_media_file(db: Session, business_id: int, file_type: str, file: UploadFile):
    # Validate file_type
    if file_type not in ALLOWED_TYPES:
        return "invalid_file_type"

    # Check if media exists
    media = get_media(db=db, business_id=business_id)
    if not media:
        return None

    print(f"Got media...")
    # Save file
    file_info = save_media_locally(file)
    print(f"file info: {file_info}")

    # Save record in DB
    media_file = MediaFile(
        media_id=media.id,
        file_url=file_info["file_url"],
        file_name=file_info["file_name"],
        # file_data=base64.b64encode(file_info["file_data"]).decode("utf-8"),
        file_data=file_info["file_data"],
        file_type=file_type,
        mime_type=file_info["mime_type"],
        file_size=file_info["file_size"]
    )
    add_to_db(db=db, model=media_file)
    return media_file

def get_media(db: Session, business_id: int, file_type: str=None):
    media = db.query(Media).filter(Media.business_id == business_id,
                                  Media.is_active == True).first()
    if not media:
        return None
    if file_type:
        media_file = None
        if file_type not in ALLOWED_TYPES:
            return "invalid"
        media_file = db.query(MediaFile).filter(MediaFile.media_id == media.id, 
                                                MediaFile.file_type == file_type, 
                                                MediaFile.is_active == True).all()
        if not media_file:
            return None
        return media_file
    return media

def webscrap_logo(db: Session, business_id: int):
    contact = get_contact(db=db, business_id=business_id)
    if contact:
        if hasattr(contact, "website"):
            if contact.website not in [None, ""]:
                logo_bytes = get_website_logo_bytes(url=contact.website)
                if logo_bytes:
                    buffer = BytesIO(logo_bytes)
                    return StreamingResponse(buffer, media_type="application/octet-stream")
    return None

def predict_products_from_website(db: Session, business_id: int):
    contact = get_contact(db=db, business_id=business_id)
    if contact:
        if hasattr(contact, "website"):
            if contact.website not in [None, ""]:
                images = get_website_images(url=contact.website, zip=False)
                print(f"images: {images}")
                classified_images = ClassifyImage().classify_images(images)
                print(classified_images)
                sending_images_for_caption = []
                for data in classified_images:
                    if data["is_valid"]:
                        sending_images_for_caption.append(data["image"])
                if len(sending_images_for_caption)>0:
                    image_captions = CaptionImage().captionize_images(sending_images_for_caption)
                    print(image_captions)
                return image_captions
    return None


def webscrap_products(db: Session, business_id: int):
    contact = get_contact(db=db, business_id=business_id)
    if contact:
        if hasattr(contact, "website"):
            if contact.website not in [None, ""]:
                images = get_website_images(url=contact.website, zip=False)
                print(f"images: {images}")
                classified_images = ClassifyImage().classify_images(images)
                print(classified_images)
                sending_images_for_caption = []
                for data in classified_images:
                    print(f"data: {data}")
                    if data["is_valid"]:
                        sending_images_for_caption.append(data["image"])
                if len(sending_images_for_caption)>0:
                    image_captions = CaptionImage().captionize_images(sending_images_for_caption)
                    print(image_captions)
                    return image_captions
                # products = get_website_products(url=contact.website)
                # return products
    return None

def webscrap_images(db: Session, business_id: int):
    contact = get_contact(db=db, business_id=business_id)
    if contact:
        if hasattr(contact, "website"):
            if contact.website not in [None, ""]:
                images_zip = get_website_images(url=contact.website)
                if images_zip:
                    return FileResponse(images_zip, media_type='application/zip', filename="images.zip")
    return None

# def update_media(db: Session, business_id: int, data):
#     media = db.query(Media).filter(Media.business_id == business_id,
#                                    Media.is_active == True).first()
#     if not media:
#         return None
#     for key, value in data.dict(exclude_unset=True).items():
#         setattr(media, key, value)
#     db.commit()
#     db.refresh(media)
#     return standardize_media(media)

def get_media_files(db: Session, media_id: int):
    media_files = db.query(MediaFile).filter(MediaFile.media_id == media_id,
                                   MediaFile.is_active == True).all()
    return media_files

def delete_media(db: Session, business_id: int):
    media = get_media(db=db, business_id=business_id)
    if not media:
        return None
    update_db(db=db, model=media, field="is_active", value=False)
    media_files = get_media_files(db=db, media_id=media.id)
    if media_files:
        for file in media_files:
            update_db(db=db, model=file, field="is_active", value=False)
    return media

#contact
def create_contact(db: Session, user_id: int, business_id: int, data):
    contact = Contact(user_id=user_id, business_id=business_id, **data.dict())
    add_to_db(db=db, model=contact)
    unset_active_records(db=db, model=Contact, business_id=contact.business_id, 
                         active_id=contact.id)
    return contact

def get_contact(db: Session, business_id: int):
    return db.query(Contact).filter(Contact.business_id == business_id,
                                    Contact.is_active == True).first()

def update_contact(db: Session, business_id: int, data):
    contact = get_contact(db=db, business_id=business_id)
    if not contact:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(contact, key, value)
    commit_db(db=db, model=contact)
    return contact

def delete_contact(db: Session, business_id: int):
    contact = get_contact(db=db, business_id=business_id)
    if not contact:
        return None
    update_db(db=db, model=contact, field="is_active", value=False)
    return contact

#business details
def create_business_details(db: Session, user_id: int, business_id: int):
    contact = get_contact(db=db, business_id=business_id)
    media = get_media(db=db, business_id=business_id)
    business_details = BusinessDetails(user_id=user_id, business_id=business_id, 
                                       media_id=media.id, contact_id=contact.id)
    add_to_db(db=db, model=business_details)
    unset_active_records(db=db, model=BusinessDetails, business_id=business_details.business_id, 
                         active_id=business_details.id)
    return business_details

def get_business_details(db: Session, business_id: int):
    business_details = db.query(BusinessDetails).filter(BusinessDetails.business_id == business_id,
                                            BusinessDetails.is_active == True).first()
    return business_details


def update_business_details(db: Session, business_id: int, data):
    business_details = get_business_details(db=db, business_id=business_id) 
    if not business_details:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(business_details, key, value)
    commit_db(db=db, model=business_details)        
    return business_details

def delete_business_details(db: Session, business_id: int):
    business_details = get_business_details(db=db, business_id=business_id)
    if not business_details:
        return None
    update_db(db=db, model=business_details, field="is_active", value=False)
    delete_all_products(db=db, business_id=business_id)
    return business_details

#Products
def create_product(db: Session, business_id: int, name: str,
                   description:str, price:float, image:UploadFile):
    business_details = get_business_details(db=db, business_id=business_id)
    print("in crud product")
    if not business_details:
        return None
    
    # Save file
    if image is not None:
        file_info = save_product_locally(image)
    else:
        file_info = {
            "image_name" : None,
            "image_data": None,
            "image_url": None,
            "image_mime": None,
            "image_size": None
        }
    # Save record in DB
    product = Product(
        business_details_id=business_details.id,
        name=name,
        description=description,
        price=price,
        image_name=file_info["image_name"],
        image_url=file_info["image_url"],
        image_data=base64.b64encode(file_info["image_data"]).decode("utf-8") if file_info["image_data"] else None,
        image_mime=file_info["image_mime"],
        image_size=file_info["image_size"]      
    )
    add_to_db(db=db, model=product)
    return product


def get_product(product_id: int, db: Session):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    return product

def get_products(business_id: int, db: Session):
    business_details = get_business_details(db=db, business_id=business_id)
    
    if not business_details:
        return None
    products = db.query(Product).filter(Product.business_details_id == business_details.id, 
                                        Product.is_active == True).all()
    if not products:
        return None
    return products

def update_product(db: Session, product_id: int, name: str,
                   description:str, price:float, image:UploadFile):
    product = get_product(db=db, product_id=product_id)
    
    if not product:
        return None
    
    # Save file
    if image is not None:
        file_info = save_product_locally(image)
    else:
        file_info = {
            "image_name" : None,
            "image_data": None,
            "image_url": None,
            "image_mime": None,
            "image_size": None
        }
    if name not in [None, "null", ""]:
        product.name = name
    if description not in [None, "null", ""]:
        product.description = description
    if price is not None:
        product.price = price
    if image is not None:
        product.image_name=file_info["image_name"],
        product.image_url=file_info["image_url"],
        product.image_data=base64.b64encode(file_info["image_data"]).decode("utf-8") if file_info["image_data"] else None,
        product.image_mime=file_info["image_mime"],
        product.image_size=file_info["image_size"]
    commit_db(db=db, model=product)
    return product

def delete_all_products(db: Session, business_id: int):
    products = get_products(db=db, business_id=business_id)
    if products:
        for product in products:
            update_db(db=db, model=product, field="is_active", value=False)
    return products

def delete_product(db: Session, product_id: int):
    product = get_product(db=db, product_id=product_id)
    if product:
        update_db(db=db, model=product, field="is_active", value=False)
    return product