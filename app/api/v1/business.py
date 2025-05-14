from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.core.security import get_current_user
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessOut
# from schemas.combined_details import MediaCreate, ContactCreate, BusinessDetailsCreate
from app.crud import business as business_crud

router = APIRouter()

# BUSINESS CRUD

@router.post("/business", response_model=BusinessOut)
def create_business(data: BusinessCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return business_crud.create_business(db, user_id=int(user["user_id"]), data=data)

@router.get("/business/{business_id}", response_model=BusinessOut)
def get_business(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    business = business_crud.get_business(db, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.get("/business", response_model=list[BusinessOut])
def list_businesses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return business_crud.get_all_businesses(db)

@router.put("/business/{business_id}", response_model=BusinessOut)
def update_business(business_id: int, data: BusinessUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    updated = business_crud.update_business(db, business_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Business not found")
    return updated

@router.delete("/business/{business_id}")
def delete_business(business_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    deleted = business_crud.delete_business(db, business_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Business not found")
    return {"detail": "Business deleted"}

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
