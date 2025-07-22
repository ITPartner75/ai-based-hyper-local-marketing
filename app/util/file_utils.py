# util/file_utils.py
import os, base64
from uuid import uuid4
from fastapi import UploadFile
from mimetypes import guess_type
from app.constants.base import ROOT_DIR, MEDIA_FILES, PRODUCT_FILES
from app.schemas.business import MediaFileDetails

MEDIA_UPLOAD_DIR = os.path.join(ROOT_DIR, MEDIA_FILES)
PRODUCT_UPLOAD_DIR = os.path.join(ROOT_DIR, PRODUCT_FILES)

def save_media_locally(upload_file: UploadFile) -> dict:
    os.makedirs(MEDIA_UPLOAD_DIR, exist_ok=True)

    extension = os.path.splitext(upload_file.filename)[-1]
    unique_filename = f"{uuid4().hex}{extension}"
    save_path = os.path.join(MEDIA_UPLOAD_DIR, unique_filename)
    print(f"trying to save file...")
    # with open(save_path, "wb") as buffer:
    #     buffer.write(upload_file.file.read())
    print("saved file...")
    file_data = upload_file.file.read()
    return MediaFileDetails(file_name=unique_filename,
                            file_data=base64.b64encode(file_data).decode("utf-8"),
                            file_url=os.path.join(MEDIA_UPLOAD_DIR, unique_filename),
                            mime_type=guess_type(save_path)[0],
                            file_size=len(file_data)).dict()
    # return {
    #     "file_name" : unique_filename,
    #     "file_data": file_data,
    #     "relative_path": os.path.join(MEDIA_UPLOAD_DIR, unique_filename),
    #     "mime_type": guess_type(save_path)[0],
    #     "file_size": len(file_data)
    # }

def save_product_locally(upload_file: UploadFile) -> dict:
    os.makedirs(PRODUCT_UPLOAD_DIR, exist_ok=True)

    extension = os.path.splitext(upload_file.filename)[-1]
    unique_filename = f"{uuid4().hex}{extension}"
    save_path = os.path.join(PRODUCT_UPLOAD_DIR, unique_filename)

    # with open(save_path, "wb") as buffer:
    #     buffer.write(upload_file.file.read())
    image_data = upload_file.file.read()
    return {
        "image_name" : unique_filename,
        "image_data": image_data,
        "image_url": os.path.join(PRODUCT_UPLOAD_DIR, unique_filename),
        "image_mime": guess_type(save_path)[0],
        "image_size": len(image_data)
    }
