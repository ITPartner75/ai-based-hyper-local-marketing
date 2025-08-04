# import requests, torch
# import clip
# import spacy
# import base64
# from mimetypes import guess_type
# from PIL import Image
# from multiprocessing import Pool, cpu_count
# from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
# import clip
# import spacy
# from mimetypes import guess_type
# from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration #large model
# from transformers import (
#     VisionEncoderDecoderModel,
#     ViTImageProcessor,
#     AutoTokenizer,
#     pipeline
# ) #small models
#############################################################################################
import base64
import re
import os
import requests
import traceback
import time
import torch
from io import BytesIO
from PIL import Image
from urllib.parse import urlparse, unquote
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
from multiprocessing import Pool, cpu_count, Process, Queue
from langdetect import detect, DetectorFactory

from app.util.file_utils import get_mime_type_from_bytes
from app.util.webscrap import get_website_image_urls, decode_data_image
from app.services.task_manager import task_manager
from app.util.logger import logger

device = "cuda" if torch.cuda.is_available() else "cpu"

#for large model    
DetectorFactory.seed = 0  # makes language detection deterministic


class SellableImageClassifier:
    UNSELLABLE_PHRASES = [
        "download", "app store", "google play", "get it on", "iphone",
        "android", "mobile app", "available on", "scan the qr", "qr code",
        "button", "icon", "ui element", "interface", "promotion",
        "logo", "symbol", "brand", "favicon",
        "event", "celebration", "festival", "party", "gathering",
        "concert", "wedding", "ceremony", "invitation", "announcement"
    ]

    SELLABLE_PROMPTS = {
        "restaurant": ["menu item", "plated food", "coffee cup", "dessert", "drink glass", "beverage"],
        "gym": ["fitness class", "personal training", "gym equipment", "membership card", "program nutrition", "program weightloss", "program strength", "program cardio",
                "program body building", "program wellness", "fitness program", "workout routine", "training plan"],
        "ecommerce": ["product", "item for sale", "clothing item", "accessory"],
        "salon": ["haircut", "hair styling", "beauty service", "treatment", "facial treatment", "manicure", "pedicure", "makeup service"],
        "parlour": ["treatment", "beauty treatment", "facial", "makeup", "eyebrow shaping", "waxing service", "hair spa"],
        "pet grooming": ["pet grooming", "dog washing", "cat grooming", "pet haircut", "animal care service"],
        "auto repair": ["mechanic", "vehicle service", "car repair", "garage repair", "oil change", "tire replacement", "car engine repair"]
    }

    def __init__(self, business_type: str, device: str = "cpu"):
        self.business_type = business_type.lower()
        self.device = device
        self.caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    def extract_caption_from_filename(self, image_url: str) -> str | None:
        try:
            path = urlparse(image_url).path
            filename = unquote(os.path.basename(path))
            name, _ = os.path.splitext(filename)
            cleaned = name.replace('_', ' ').replace('-', ' ').strip()

            if len(cleaned) < 4 or cleaned.lower() in {"logo", "image", "img"}:
                return None
            if all(c.isdigit() or not c.isalnum() for c in cleaned):
                return None
            if re.search(r"\d{2,4}x\d{2,4}", cleaned.lower()):
                return None
            if re.match(r"^[A-Z0-9]{4,}$", cleaned.strip()):
                return None
            if detect(cleaned) != "en":
                return None
            return cleaned
        except Exception:
            return None

    def process(self, website_url: str, task_id: str | None = None) -> list[dict]:
        image_urls = get_website_image_urls(website_url)
        results = []
        total = len(image_urls)

        if task_id:
            task_manager.update(task_id, status="in_progress", progress=0)

        for idx, url in enumerate(image_urls):
            result = self.process_image(url)
            if result.get("is_valid"):
                results.append(result)

            if task_id:
                progress = int((idx + 1) / total * 100)
                task_manager.update(task_id, progress=progress)

        return results

    def process_image(self, image_url: str) -> dict:
        try:
            # Load image bytes
            if image_url.startswith("data:image"):
                image_bytes, mime = decode_data_image(image_url)
            else:
                res = requests.get(image_url, timeout=10)
                res.raise_for_status()
                content_type = res.headers.get("Content-Type", "")
                if not content_type.startswith("image/"):
                    raise ValueError("URL is not an image.")
                image_bytes = res.content
                mime = get_mime_type_from_bytes(image_bytes)

            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            if image.width < 32 or image.height < 32:
                raise ValueError("Image too small.")

            caption = self.extract_caption_from_filename(image_url)
            use_model_caption = True

            if caption and not any(p in caption.lower() for p in self.UNSELLABLE_PHRASES):
                prompts = self.SELLABLE_PROMPTS.get(self.business_type, [])
                result = self.classifier(caption, candidate_labels=prompts)
                score = result["scores"][0]
                if score >= 0.5:
                    use_model_caption = False
                    return {
                        "image_url": image_url,
                        "image_mime": mime,
                        "name": caption,
                        "description": caption,
                        "classification": result["labels"][0],
                        "is_valid": True
                    }

            if use_model_caption:
                inputs = self.caption_processor(image, return_tensors="pt").to(self.device)
                out = self.caption_model.generate(**inputs)
                caption = self.caption_processor.decode(out[0], skip_special_tokens=True)

                if not caption or any(p in caption.lower() for p in self.UNSELLABLE_PHRASES):
                    raise ValueError("Unsellable caption from model.")

                prompts = self.SELLABLE_PROMPTS.get(self.business_type, [])
                result = self.classifier(caption, candidate_labels=prompts)
                score = result["scores"][0]

                if score < 0.5:
                    raise ValueError("Low confidence in classification.")

                return {
                    "image_url": image_url,
                    "image_mime": mime,
                    "name": caption,
                    "description": caption,
                    "classification": result["labels"][0],
                    "is_valid": True
                }

        except Exception as e:
            return {
                "image_url": image_url,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "is_valid": False
            }