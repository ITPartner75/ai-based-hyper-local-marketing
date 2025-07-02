# util/file_utils.py
import os
from uuid import uuid4
from fastapi import UploadFile
from mimetypes import guess_type
from app.constants.base import ROOT_DIR, MEDIA_FILES, PRODUCT_FILES

MEDIA_UPLOAD_DIR = os.path.join(ROOT_DIR, MEDIA_FILES)
PRODUCT_UPLOAD_DIR = os.path.join(ROOT_DIR, PRODUCT_FILES)

def save_media_locally(upload_file: UploadFile) -> dict:
    os.makedirs(MEDIA_UPLOAD_DIR, exist_ok=True)

    extension = os.path.splitext(upload_file.filename)[-1]
    unique_filename = f"{uuid4().hex}{extension}"
    save_path = os.path.join(MEDIA_UPLOAD_DIR, unique_filename)

    with open(save_path, "wb") as buffer:
        buffer.write(upload_file.file.read())

    return {
        "file_name" : unique_filename,
        "relative_path": os.path.join(MEDIA_UPLOAD_DIR, unique_filename),
        "mime_type": guess_type(save_path)[0],
        "file_size": os.path.getsize(save_path)
    }

def save_product_locally(upload_file: UploadFile) -> dict:
    os.makedirs(PRODUCT_UPLOAD_DIR, exist_ok=True)

    extension = os.path.splitext(upload_file.filename)[-1]
    unique_filename = f"{uuid4().hex}{extension}"
    save_path = os.path.join(PRODUCT_UPLOAD_DIR, unique_filename)

    with open(save_path, "wb") as buffer:
        buffer.write(upload_file.file.read())

    return {
        "image_name" : unique_filename,
        "image_url": os.path.join(PRODUCT_UPLOAD_DIR, unique_filename),
        "image_size": os.path.getsize(save_path)
    }
