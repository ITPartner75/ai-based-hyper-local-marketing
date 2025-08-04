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
import clip
import spacy
from io import BytesIO
from PIL import Image
from urllib.parse import urlparse, unquote
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
from multiprocessing import Pool, cpu_count, Process, Queue
from langdetect import detect, DetectorFactory

from app.util.file_utils import get_mime_type_from_bytes
from app.util.webscrap import get_website_image_urls, decode_data_image
from app.util.logger import logger

device = "cuda" if torch.cuda.is_available() else "cpu"

#for large model    
DetectorFactory.seed = 0  # makes language detection deterministic


def extract_caption_from_filename(image_url: str) -> str | None:
    """Infer a meaningful, English-language caption from the filename."""
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

        # ✅ Language check
        lang = detect(cleaned)
        if lang != "en":
            return None

        return cleaned

    except Exception:
        return None


class Worker(Process):
    def __init__(self, task_queue: Queue, result_queue: Queue, business_type: str, device: str):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.business_type = business_type
        self.device = device

    def run(self):
        try:
            logger.info(f"[{self.name}] Loading models...")
            caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)
            classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
            logger.info(f"[{self.name}] Models loaded.")
        except Exception as e:
            logger.error(f"[{self.name}] Model loading failed: {e}")
            return

        while True:
            image_url = self.task_queue.get()
            if image_url is None:
                logger.info(f"[{self.name}] Exiting.")
                break

            try:
                # Load image bytes
                if image_url.startswith("data:image"):
                    image_bytes, mime = decode_data_image(image_url)
                    if not image_bytes:
                        raise ValueError("Invalid base64 image.")
                else:
                    res = requests.get(image_url, timeout=10)
                    res.raise_for_status()
                    content_type = res.headers.get("Content-Type", "")
                    if not content_type.startswith("image/"):
                        raise ValueError(f"URL is not an image. Content-Type: {content_type}")
                    image_bytes = res.content
                    mime = get_mime_type_from_bytes(image_bytes)

                # Load image
                image = Image.open(BytesIO(image_bytes)).convert("RGB")
                if image.width < 32 or image.height < 32:
                    raise ValueError(f"Image too small ({image.width}x{image.height})")

                # Step 1: Try caption from filename
                caption = extract_caption_from_filename(image_url)
                if caption:
                    logger.debug(f"Caption from filename: {caption}")
                else:
                    logger.debug("Filename caption not useful, generating with model...")
                use_model_caption = True
                if caption and not any(p in caption.lower() for p in SellableImageClassifier.UNSELLABLE_PHRASES):
                    prompts = SellableImageClassifier.SELLABLE_PROMPTS.get(self.business_type, [])
                    result = classifier(caption, candidate_labels=prompts)
                    label = result["labels"][0]
                    score = result["scores"][0]
                    if score >= 0.5:
                        use_model_caption = False
                        final_caption, final_label, final_score = caption, label, score

                # Step 2: Fallback to caption model
                if use_model_caption:
                    inputs = caption_processor(image, return_tensors="pt").to(self.device)
                    out = caption_model.generate(**inputs)
                    caption = caption_processor.decode(out[0], skip_special_tokens=True)

                    if not caption or any(p in caption.lower() for p in SellableImageClassifier.UNSELLABLE_PHRASES):
                        raise ValueError("Unsellable image based on caption.")

                    prompts = SellableImageClassifier.SELLABLE_PROMPTS.get(self.business_type, [])
                    result = classifier(caption, candidate_labels=prompts)
                    final_label = result["labels"][0]
                    final_score = result["scores"][0]
                    final_caption = caption

                # Step 3: Final validation
                if final_score >= 0.5:
                    self.result_queue.put({
                        "image_url": image_url,
                        "image_mime": mime,
                        "name": final_caption,
                        "description": final_caption,
                        "classification": final_label,
                        "is_valid": True
                    })
                else:
                    raise ValueError("Low classification confidence.")
            except Exception as e:
                tb = traceback.format_exc()
                logger.warning(f"[{self.name}] Error processing {image_url}: {e}")
                self.result_queue.put({
                    "image_url": image_url,
                    "error": str(e),
                    "traceback": tb,
                    "is_valid": False
                })


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

    active_workers = []

    def shutdown_previous_workers(self):
        for w in SellableImageClassifier.active_workers:
            if w.is_alive():
                logger.warning(f"Shutting down leftover worker {w.name}")
                w.terminate()
        SellableImageClassifier.active_workers.clear()

    def __init__(self, business_type: str, device: str = "cpu"):
        self.business_type = business_type.lower()
        self.device = device

    def process(self, website_url: str):
        logger.info(f"Processing website: {website_url}")
        image_urls = get_website_image_urls(website_url)
        logger.info(f"Found {len(image_urls)} images.")

        if not image_urls:
            return []

        task_queue = Queue()
        result_queue = Queue()
        num_workers = min(cpu_count(), len(image_urls), 4)
        logger.info(f"Using {num_workers} worker(s)")

        self.shutdown_previous_workers()

        # Start workers
        workers = [Worker(task_queue, result_queue, self.business_type, self.device) for _ in range(num_workers)]
        for w in workers:
            w.daemon = True  # Optional: terminates them when main process exits
            w.start()
        SellableImageClassifier.active_workers.extend(workers)
        # Send image tasks
        for url in image_urls:
            task_queue.put(url)
        for _ in workers:
            task_queue.put(None)

        results = []
        received = 0
        expected = len(image_urls)

        start_time = time.time()
        while received < expected:
            try:
                result = result_queue.get(timeout=120)  # seconds
                received += 1
                if result.get("is_valid"):
                    results.append(result)
                else:
                    logger.warning(f"Skipped: {result.get('image_url')} | Error: {result.get('error')}")
            except Exception:
                logger.warning(f"No response within timeout. {received}/{expected} collected.")
                # Try to collect more results until timeout or all are collected
                break

            # Safety: Hard timeout (e.g., 5 minutes)
            if time.time() - start_time > 300:
                logger.error("Global timeout: processing took too long.")
                break

        # Ensure all workers are terminated cleanly
        for w in workers:
            w.join(timeout=5)
            if w.is_alive():
                logger.warning(f"Worker {w.name} did not exit properly. Terminating...")
                w.terminate()
        SellableImageClassifier.active_workers.clear()

        logger.info(f"Valid sellable images: {len(results)}")
        return results
    