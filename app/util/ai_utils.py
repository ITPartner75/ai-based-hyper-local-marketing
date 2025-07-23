import requests, torch
import clip
import spacy
import base64
from mimetypes import guess_type
from PIL import Image
from multiprocessing import Pool, cpu_count
from transformers import BlipProcessor, BlipForConditionalGeneration

device = "cuda" if torch.cuda.is_available() else "cpu"

# Load the model globally (for GPU reuse in subprocesses if using fork backend)
# model, preprocess = clip.load("ViT-B/32", device=device)
class ClassifyImage:
    model, preprocess = clip.load("ViT-B/32", device=device)
    
    def __init__(self, threshold=0.3, prompts=None):
        self.labels = ["menu", "service", "product"]
        self.threshold = threshold
        self.prompts = prompts or [
            "a restaurant menu",
            "a person or organization providing customer service",
            "a product for sale such as a packaged item or house"
        ]
        

    def _classify_single_image(self, image_path):
        try:
            image = ClassifyImage.preprocess(Image.open(image_path)).unsqueeze(0).to(device)
            text_tokens = clip.tokenize(self.prompts).to(device)

            with torch.no_grad():
                image_features = ClassifyImage.model.encode_image(image)
                text_features = ClassifyImage.model.encode_text(text_tokens)
                image_features /= image_features.norm(dim=-1, keepdim=True)
                text_features /= text_features.norm(dim=-1, keepdim=True)
                logits = image_features @ text_features.T
                probs = logits.softmax(dim=-1).cpu().tolist()[0]

            max_idx = probs.index(max(probs))
            predicted_label = self.labels[max_idx]
            confidence = probs[max_idx]
            is_valid = confidence >= self.threshold

            return {
                "image": image_path,
                "label": predicted_label,
                "confidence": round(confidence, 4),
                "is_valid": bool(is_valid)
            }

        except Exception as e:
            print(f"❌ Error processing {image_path}: {e}")
            return {
                "image": image_path,
                "label": None,
                "confidence": 0.0,
                "is_valid": False
            }

    def classify_images(self, images):
        if not isinstance(images, list):
            images = [images]

        with Pool(min(cpu_count(), len(images))) as pool:
            return pool.map(self._classify_single_image, images)
        
class CaptionImage:
    nlp = spacy.load("en_core_web_sm")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to(device)
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")

    def _caption_single_image(self, image_path):
        mime_type = mime_type=guess_type(image_path)[0]
        try:
            image = Image.open(image_path).convert("RGB")
            inputs = CaptionImage.processor(image, return_tensors="pt").to(device)

            with torch.no_grad():
                out = CaptionImage.model.generate(**inputs)
            caption = CaptionImage.processor.decode(out[0], skip_special_tokens=True)
            # Extract subject from caption
            name = self._extract_contents(caption)
            # # If name is too generic, use fallback
            # if name.lower() in ["food", "plate", "table", "wall", "dish"]:
            #     name = self._extract_top_nouns(caption)
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            result = {
                      "image_data": base64.b64encode(image_bytes).decode("utf-8"),
                      "image_path": image_path,
                      "image_mime": mime_type,
                      "name": name, 
                      "description": caption}
            return result
        except Exception as e:
            print(f"❌ Error processing {image_path}: {e}")
            return {
                    "image_data": None, 
                    "image_path": image_path,
                    "image_mime": mime_type,
                    "name": None, 
                    "description": None}

    def _extract_contents(self,caption):
        doc = CaptionImage.nlp(caption)
        # 1. Try to extract object of "of"
        for token in doc:
            if token.text.lower() == "of" and token.dep_ == "prep":
                for child in token.children:
                    if child.dep_ == "pobj" and child.pos_ != "PRON":
                        # Get full chunk if available
                        chunk = next((chunk for chunk in doc.noun_chunks if child in chunk), None)
                        if chunk:
                            return chunk.text.strip()

        # 2. Fallback: return longest NOUN chunk (not PRONOUN)
        noun_chunks = [chunk.text for chunk in doc.noun_chunks if chunk.root.pos_ != "PRON"]
        if noun_chunks:
            return max(noun_chunks, key=len).strip()

        # 3. Fallback to top noun
        nouns = [token.text for token in doc if token.pos_ == "NOUN"]
        if nouns:
            return nouns[0]

        return caption

    # --- Optional fallback: top N nouns in caption ---
    def _extract_top_nouns(self, caption, max_n=3):
        doc = CaptionImage.nlp(caption)
        nouns = [token.text for token in doc if token.pos_ == "NOUN"]
        return ", ".join(nouns[:max_n]) if nouns else caption

        
    def captionize_images(self, images):
        if not isinstance(images, list):
            images = [images]

        # Multiprocessing (limit to CPU cores to avoid overloading)
        num_processes = min(cpu_count(), len(images))
        with Pool(processes=num_processes) as pool:
            results = pool.map(self._caption_single_image, images)

        # Combine into dictionary
        captions = list(results)
        return captions
        
