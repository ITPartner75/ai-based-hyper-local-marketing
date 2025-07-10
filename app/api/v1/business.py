from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.core.security import get_current_user
from app.schemas.business import *
# from schemas.combined_details import MediaCreate, ContactCreate, BusinessDetailsCreate
from app.crud import business as business_crud
from app.constants.business import ALLOWED_TYPES
from typing import List, Union

router = APIRouter()

# BUSINESS CRUD

@router.post("/business", response_model=BusinessOut)
def create_business(data: BusinessCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    print(f"Increate business:{user}")
    return business_crud.create_business(db=db, user_id=int(user["id"]), data=data)

@router.get("/business/{business_id}", response_model=BusinessOut)
def get_business(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    business = business_crud.get_business(db=db, business_id=int(business_id))
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.get("/business", response_model=list[BusinessOut])
def list_businesses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return business_crud.get_all_businesses(db)

@router.put("/business/{business_id}", response_model=BusinessOut)
def update_business(business_id: int, data: BusinessUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    print(data)
    updated = business_crud.update_business(db=db, business_id=int(business_id), data=data)
    if not updated:
        raise HTTPException(status_code=404, detail="Business not found")
    return updated

@router.delete("/business/{business_id}")
def delete_business(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    deleted = business_crud.delete_business(db=db, business_id=int(business_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Business not found")
    return {"detail": "Business deleted"}

#Contact
@router.post("/contact/{bussiness_id}", response_model=ContactOut)
def create_contact(business_id: int,  data: ContactCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    print(f"Increate business:{user}")
    return business_crud.create_contact(db=db, user_id=int(user["id"]), business_id=int(business_id), data=data)

@router.get("/contact/{business_id}", response_model=ContactOut)
def get_contact(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    contact = business_crud.get_contact(db=db, business_id=int(business_id))
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/contact/{business_id}", response_model=ContactOut)
def update_contact(business_id: int, data: ContactUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    print(data)
    updated = business_crud.update_contact(db=db, business_id=int(business_id), data=data)
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated

@router.delete("/contact/{business_id}")
def delete_contact(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    deleted = business_crud.delete_contact(db=db, business_id=int(business_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"detail": "Contact deleted"}

#Media
@router.post("/media/{business_id}", response_model=MediaOut)
def create_media(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return business_crud.create_media(db=db, user_id=int(user["id"]), business_id=int(business_id))

@router.get("/media/{business_id}", response_model=MediaOut)
def get_media(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    media = business_crud.get_media(db=db, business_id=int(business_id))
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media

@router.get("/media/{business_id}/{file_type}", response_model=Union[MediaFileOut, List[MediaFileOut]])
def get_media_files(business_id: int, file_type: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    media_files = business_crud.get_media(db=db, business_id=int(business_id), file_type=file_type)
    if not media_files:
        raise HTTPException(status_code=404, detail="Media Files not found")
    elif isinstance(media_files, str) and media_files.lower() == "invalid":
        raise HTTPException(status_code=400, detail="Invalid media field")
    return media_files

@router.get("/webscrap/logo/{business_id}")
def webscrap_logo(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    logo = business_crud.webscrap_logo(db=db, business_id=int(business_id))
    if not logo:
        raise HTTPException(status_code=404, detail="Logo not found")
    return logo

# @router.get("/media/{business_id}/{field_name}")
# def stream_media_field(business_id: int, field_name: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
#     media = business_crud.get_media(db=db, business_id=int(business_id), field_name=field_name)
#     if not media:
#         raise HTTPException(status_code=404, detail="Media not found")
#     elif isinstance(media, str) and media.lower() == "invalid":
#         raise HTTPException(status_code=400, detail="Invalid media field")
#     return media

@router.post("/media/file/upload", response_model=MediaFileOut)
def upload_media_file(
    business_id: int = Form(...),
    file_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    uploaded = business_crud.upload_media_file(db=db, 
                                               business_id=business_id,
                                               file_type=file_type,
                                               file=file)
    if isinstance(uploaded, str) and uploaded.lower() == "not_found":
        raise HTTPException(status_code=404, detail="Media not found")
    elif isinstance(uploaded, str) and uploaded.lower() == "invalid_file_type":
        raise HTTPException(status_code=400, detail=f"Invalid file_type. Allowed: {ALLOWED_TYPES}")
    if not uploaded:
        raise HTTPException(status_code=500, detail=f"Unable to upload file type: {file_type}")
    return uploaded

# @router.put("/media/{business_id}", response_model=MediaOut)
# def update_media(business_id: int, data: MediaUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
#     print(data)
#     updated = business_crud.update_media(db=db, business_id=int(business_id), data=data)
#     if not updated:
#         raise HTTPException(status_code=404, detail="Media not found")
#     return updated

@router.delete("/media/{business_id}")
def delete_media(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    deleted = business_crud.delete_media(db=db, business_id=int(business_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Media not found")
    return {"detail": "Media deleted"}

#Business Details
@router.post("/business/details/{business_id}", response_model=BusinessDetailsOut)
def create_business_details(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    print(f"Increate business:{user}")
    return business_crud.create_business_details(db=db, user_id=int(user["id"]), business_id=int(business_id))

@router.get("/business/details/{business_id}", response_model=BusinessDetailsOut)
def get_business_details(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    business_details = business_crud.get_business_details(db=db, business_id=int(business_id))
    if not business_details:
        raise HTTPException(status_code=404, detail="Business Details not found")
    return business_details

# @router.put("/business/details/{business_id}", response_model=BusinessDetailsOut)
# def update_business_details(business_id: int, data: BusinessDetailsUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
#     print(data)
#     updated = business_crud.update_business_details(db=db, business_id=int(business_id), data=data)
#     if not updated:
#         raise HTTPException(status_code=404, detail="Business Details not found")
#     return updated

@router.delete("/business/details/{business_id}")
def delete_business_details(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    deleted = business_crud.delete_business_details(db=db, business_id=int(business_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Business Details not found")
    return {"detail": "Business Details deleted"}

@router.post("/product", response_model=ProductOut)
def create_product(
    business_id: int = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    print("i:",image)
    product = business_crud.create_product(db=db,
                                           business_id=business_id,
                                           name=name,
                                           description=description,
                                           price=price,
                                           image=image)
    if isinstance(product, str) and product.lower() == "not_found":
        raise HTTPException(status_code=404, detail="Business Details not found")
    if not product:
        raise HTTPException(status_code=500, detail="Unable to create product")
    return product


@router.get("/products/{business_id}", response_model=List[ProductOut])
def get_products(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    products = business_crud.get_products(db=db, business_id=int(business_id))
    if not products:
        raise HTTPException(status_code=404, detail="Products not found")
    return products

@router.put("/product/update")
def update_product(product_id: int = Form(...),
                   name: str = Form(None),
                   description: str = Form(None),
                   price: Union[float, None] = Form(None),
                   image: UploadFile = File(None), 
                   db: Session = Depends(get_db), 
                   user=Depends(get_current_user)):
    updated = business_crud.update_product(db=db, product_id=int(product_id),
                                           name=name, description=description,
                                           price=price,
                                           image=image)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@router.delete("/products/{business_id}")
def delete_all_products(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    deleted = business_crud.delete_all_products(db=db, business_id=int(business_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Business Details not found")
    return {"detail": "Products deleted"}

@router.delete("/product/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    deleted = business_crud.delete_product(db=db, product_id=int(product_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"detail": "Product deleted"}

# # COMBINED DETAILS (MEDIA, CONTACT, BUSINESS_DETAILS)

# @router.post("/business-details")
# def create_full_details(
#     media: MediaCreate,
#     contact: ContactCreate,
#     details: BusinessDetailsCreate,
#     db: Session = Depends(get_db),
#     user=Depends(get_current_user)
# ):
#     media_obj = details_crud.create_media(db, user_id=int(user["user_id"]), data=media)
#     contact_obj = details_crud.create_contact(db, user_id=int(user["user_id"]), data=contact)
#     details_obj = details_crud.create_business_details(
#         db,
#         user_id=int(user["user_id"]),
#         data=BusinessDetailsCreate(
#             business_id=details.business_id,
#             media_id=media_obj.id,
#             contact_id=contact_obj.id,
#             products=details.products
#         )
#     )
#     return {
#         "media": media_obj,
#         "contact": contact_obj,
#         "business_details": details_obj
#     }

# @router.get("/business-details/{business_id}")
# def get_full_details(business_id: int, db: Session = Depends(get_db)):
#     return details_crud.get_business_details(db, business_id)

# @router.put("/business-details/{details_id}")
# def update_full_details(details_id: int, data: BusinessDetailsCreate, db: Session = Depends(get_db)):
#     updated = details_crud.update_business_details(db, details_id, data)
#     if not updated:
#         raise HTTPException(status_code=404, detail="Details not found")
#     return updated
