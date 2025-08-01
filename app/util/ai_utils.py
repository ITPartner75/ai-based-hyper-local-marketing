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

# Load the model globally (for GPU reuse in subprocesses if using fork backend)
# model, preprocess = clip.load("ViT-B/32", device=device)
# class ClassifyImage:
    
#     def __init__(self, threshold=0.3, prompts=None):
#         self.labels = ["menu", "service", "product"]
#         self.threshold = threshold
#         self.prompts = prompts or [
#             "a restaurant menu",
#             "a person or organization providing customer service",
#             "a product for sale such as a packaged item or house"
#         ]
#         self.model, self.preprocess = clip.load("ViT-B/32", device=device)
        

#     def _classify_single_image(self, image_path):
        
#         try:
#             image = self.preprocess(Image.open(image_path)).unsqueeze(0).to(device)
#             text_tokens = clip.tokenize(self.prompts).to(device)

#             with torch.no_grad():
#                 image_features = self.model.encode_image(image)
#                 text_features = self.model.encode_text(text_tokens)
#                 image_features /= image_features.norm(dim=-1, keepdim=True)
#                 text_features /= text_features.norm(dim=-1, keepdim=True)
#                 logits = image_features @ text_features.T
#                 probs = logits.softmax(dim=-1).cpu().tolist()[0]

#             max_idx = probs.index(max(probs))
#             predicted_label = self.labels[max_idx]
#             confidence = probs[max_idx]
#             is_valid = confidence >= self.threshold
#             with open(image_path, "rb") as f:
#                 image_bytes = f.read()
#             mime_type = mime_type=guess_type(image_path)[0]
#             return {
#                 "image_path": image_path,
#                 "image_data": base64.b64encode(image_bytes).decode("utf-8"),
#                 "image_mime": mime_type,
#                 "label": predicted_label,
#                 "confidence": round(confidence, 4),
#                 "is_valid": bool(is_valid)
#             }

#         except Exception as e:
#             print(f"❌ Error processing {image_path}: {e}")
#             return {
#                 "image_path": image_path,
#                 "image_data": None,
#                 "image_mime": None,
#                 "label": None,
#                 "confidence": 0.0,
#                 "is_valid": False
#             }

#     def classify_images(self, images):
#         if not isinstance(images, list):
#             images = [images]
#         num_workers = min(cpu_count(), len(images))
#         if num_workers > 4:
#             num_workers = 4
#         with Pool(num_workers) as pool:
#             return pool.map(self._classify_single_image, images)
        
# class CaptionImage:

#     def __init__(self):
#         self.nlp = spacy.load("en_core_web_sm")
#         self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(device)
#         self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")

#     def _caption_single_image(self, image_path):
#         mime_type = mime_type=guess_type(image_path)[0]
#         try:
#             image = Image.open(image_path).convert("RGB")
#             inputs = self.processor(image, return_tensors="pt").to(device)

#             with torch.no_grad():
#                 out = self.model.generate(**inputs)
#             caption = self.processor.decode(out[0], skip_special_tokens=True)
#             # Extract subject from caption
#             name = self._extract_contents(caption)
#             # # If name is too generic, use fallback
#             # if name.lower() in ["food", "plate", "table", "wall", "dish"]:
#             #     name = self._extract_top_nouns(caption)
#             with open(image_path, "rb") as f:
#                 image_bytes = f.read()
#             result = {
#                       "image_data": base64.b64encode(image_bytes).decode("utf-8"),
#                       "image_path": image_path,
#                       "image_mime": mime_type,
#                       "name": name, 
#                       "description": caption}
#             return result
#         except Exception as e:
#             print(f"❌ Error processing {image_path}: {e}")
#             return {
#                     "image_data": None, 
#                     "image_path": image_path,
#                     "image_mime": mime_type,
#                     "name": None, 
#                     "description": None}

#     def _extract_contents(self,caption):
#         doc = self.nlp(caption)
#         # 1. Try to extract object of "of"
#         for token in doc:
#             if token.text.lower() == "of" and token.dep_ == "prep":
#                 for child in token.children:
#                     if child.dep_ == "pobj" and child.pos_ != "PRON":
#                         # Get full chunk if available
#                         chunk = next((chunk for chunk in doc.noun_chunks if child in chunk), None)
#                         if chunk:
#                             return chunk.text.strip()

#         # 2. Fallback: return longest NOUN chunk (not PRONOUN)
#         noun_chunks = [chunk.text for chunk in doc.noun_chunks if chunk.root.pos_ != "PRON"]
#         if noun_chunks:
#             return max(noun_chunks, key=len).strip()

#         # 3. Fallback to top noun
#         nouns = [token.text for token in doc if token.pos_ == "NOUN"]
#         if nouns:
#             return nouns[0]

#         return caption

#     # --- Optional fallback: top N nouns in caption ---
#     def _extract_top_nouns(self, caption, max_n=3):
#         doc = self.nlp(caption)
#         nouns = [token.text for token in doc if token.pos_ == "NOUN"]
#         return ", ".join(nouns[:max_n]) if nouns else caption

        
#     def captionize_images(self, images):
#         if not isinstance(images, list):
#             images = [images]

#         # Multiprocessing (limit to CPU cores to avoid overloading)
#         num_processes = min(cpu_count(), len(images))
#         if num_workers > 4:
#             num_workers = 4
#         with Pool(processes=num_processes) as pool:
#             results = pool.map(self._caption_single_image, images)

#         # Combine into dictionary
#         captions = list(results)
#         return captions

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


# class SellableImageClassifier:
#     UNSELLABLE_PHRASES = [
#         "download", "app store", "google play", "get it on", "iphone",
#         "android", "mobile app", "available on", "scan the qr", "qr code",
#         "button", "icon", "ui element", "interface", "promotion",
#         "logo", "symbol", "brand", "favicon",
#         "event", "celebration", "festival", "party", "gathering",
#         "concert", "wedding", "ceremony", "invitation", "announcement"
#     ]

#     SELLABLE_PROMPTS = {
#         "restaurant": ["menu item", "plated food", "coffee cup", "dessert", "drink glass"],
#         "gym": ["fitness class", "personal training", "gym equipment", "membership card"],
#         "ecommerce": ["product", "item for sale", "clothing item", "accessory"],
#         "salon": ["haircut", "hair styling", "beauty service", "facial treatment", "manicure", "pedicure", "makeup service"],
#         "parlour": ["beauty treatment", "facial", "makeup", "eyebrow shaping", "waxing service", "hair spa"],
#         "pet grooming": ["pet grooming", "dog washing", "cat grooming", "pet haircut", "animal care service"],
#         "auto repair": ["mechanic", "vehicle service", "car repair", "garage repair", "oil change", "tire replacement", "car engine repair"]
#     }

#     def __init__(self, business_type: str, device: str = "cpu"):
#         self.business_type = business_type.lower()
#         self.device = device
#         self.caption_model = None
#         self.caption_processor = None
#         self.caption_tokenizer = None
#         self.classifier = None

#     def load_models(self):
#         if self.caption_model is None:
#             self.caption_model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
#             self.caption_processor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
#             self.caption_tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
#             self.caption_model.to(self.device)

#         if self.classifier is None:
#             self.classifier = pipeline(
#                 "zero-shot-classification",
#                 model="typeform/distilbert-base-uncased-mnli",
#                 device=-1  # force CPU
#             )

#     def _generate_caption(self, image: Image.Image) -> str:
#         self.load_models()
#         pixel_values = self.caption_processor(images=[image], return_tensors="pt").pixel_values.to(self.device)
#         output_ids = self.caption_model.generate(pixel_values, max_length=16, num_beams=1)
#         caption = self.caption_tokenizer.decode(output_ids[0], skip_special_tokens=True)
#         return caption

#     def _process_single_image(self, image_url):
#         try:
#             self.load_models()
#             response = requests.get(image_url, timeout=10)
#             response.raise_for_status()
#             image = Image.open(BytesIO(response.content)).convert("RGB")

#             caption = self._generate_caption(image)

#             if not caption or any(phrase in caption.lower() for phrase in self.UNSELLABLE_PHRASES):
#                 return None

#             prompts = self.SELLABLE_PROMPTS.get(self.business_type, [])
#             result = self.classifier(caption, candidate_labels=prompts)
#             label = result["labels"][0]
#             score = result["scores"][0]
#             if score >= 0.5:
#                 image_bytes = response.content
#                 mime = get_mime_type_from_bytes(image_bytes)
#                 return {
#                     "image_url": image_url,
#                     # "image_data": base64.b64encode(image_bytes).decode("utf-8"),
#                     "image_mime": mime,
#                     "description": caption,
#                     "classification": label,
#                     "is_valid": True
#                 }
#         except Exception as e:
#             print(f"[Error] {image_url}: {e}")
#         return None

#     def _process_image_wrapper(self, image_url):
#         return self._process_single_image(image_url)

#     def process(self, website_url: str):
#         image_urls = get_website_image_urls(website_url)
#         print(f"Found {len(image_urls)} candidate images...")

#         num_workers = min(cpu_count(), len(image_urls), 4)
#         with Pool(num_workers) as pool:
#             results = pool.map(self._process_image_wrapper, image_urls)

#         return [res for res in results if res]