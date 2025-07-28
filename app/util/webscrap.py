import requests
# import filetype
import base64
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dataclasses import asdict
from zipfile import ZipFile
from typing import Optional, Tuple, Union
from app.schemas.business import Product
from app.util.file_utils import get_mime_type_from_bytes


def decode_data_image(data_uri: str) -> Optional[Tuple[bytes, str]]:
    """
    Decode base64 encoded data URI to bytes and mime type.
    Returns (bytes, mime_type) or None if decoding fails.
    """
    try:
        header, encoded = data_uri.split(',', 1)
        mime_match = re.match(r'data:(.*?);base64', header)
        mime_type = mime_match.group(1) if mime_match else "application/octet-stream"
        decoded_bytes = base64.b64decode(encoded)
        return decoded_bytes, mime_type
    except Exception:
        return None

def get_website_logo_bytes(url: str) -> Optional[Tuple[bytes, str]]:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Search for images that have "logo" keyword in src, alt or class attribute
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or ''
            if not src:
                continue

            alt = img.get('alt', '').lower()
            class_name = ' '.join(img.get('class', [])).lower()

            if 'logo' in src.lower() or 'logo' in alt or 'logo' in class_name:
                # Handle base64 encoded images (data URIs)
                if src.startswith("data:image"):
                    continue
                    # decoded = decode_data_image(src)
                    # if decoded:
                    #     return decoded
                else:
                    logo_url = urljoin(url, src)
                    img_response = requests.get(logo_url, headers=headers, timeout=10)
                    img_response.raise_for_status()
                    mime_type = get_mime_type_from_bytes(img_response.content)
                    return img_response.content, mime_type

        # Fallback to favicon or shortcut icon link tags
        icon = soup.find("link", rel=lambda x: x and "icon" in x.lower())
        if icon and icon.get("href"):
            icon_href = icon["href"]
            if icon_href.startswith("data:image"):
                decoded = decode_data_image(icon_href)
                if decoded:
                    return decoded
            else:
                logo_url = urljoin(url, icon_href)
                img_response = requests.get(logo_url, headers=headers, timeout=10)
                img_response.raise_for_status()
                mime_type = get_mime_type_from_bytes(img_response.content)
                return img_response.content, mime_type

        return None

    except Exception as e:
        print(f"Error in get_website_logo_bytes: {e}")
        return None
    
def get_website_images(url, zip=True):
    try:
        # Download images
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        image_paths = []
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                img_url = urljoin(url, src)
                img_name = img_url.split("/")[-1].split("?")[0]
                try:
                    img_data = requests.get(img_url).content
                    with open(img_name, "wb") as f:
                        f.write(img_data)
                    if "logo" not in img_name.lower():
                        image_paths.append(img_name)
                        print(f"Downloaded {img_name}")
                except Exception as e:
                    print(f"Error downloading {img_url}: {e}")
        if not zip:
            return image_paths
        # Create ZIP
        zip_filename = "images.zip"
        with ZipFile(zip_filename, 'w') as zipf:
            for img in image_paths:
                zipf.write(img)
        return zip_filename
    except Exception as e:
        print(f"Error: {e}")
        return None

def is_likely_logo(url: str) -> bool:
    url = url.lower()
    return any(kw in url for kw in ["logo", "favicon", "icon", "sprite", "symbol", "brand"])

def get_website_image_urls(url: str, limit: int = 50):
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch website: {e}")
            return []

        soup = BeautifulSoup(res.text, "html.parser")
        image_urls = []
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src:
                full_url = urljoin(url, src)
                if not is_likely_logo(full_url):
                    image_urls.append(full_url)
            if len(image_urls) >= limit:
                break
        return image_urls

def get_website_products(url) -> list[Product] | None:
    try:
        # Get the HTML content of the website
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all product containers (customize the selector)
        product_containers = soup.find_all('div', class_='product')  # Adjust to actual class

        # Store data
        products = []

        for product in product_containers:
            name = product.find('h2', class_='product-title').get_text(strip=True)
            description = product.find('p', class_='product-description').get_text(strip=True)
            price = product.find('span', class_='price').get_text(strip=True)
            image = product.find('img')['src']
            if name is not None or price is not None:
                product_obj = Product(name=name, description=description, price=price,image_data=image)
                products.append(asdict(product_obj))
        if len(products) == 0:
            menu_items = soup.select('.menu-item')  # Example class—verify with inspect element
            print(menu_items)
            products = []
            for item in menu_items:
                name_tag = item.select_one('.menu-item-title')
                desc_tag = item.select_one('.menu-item-desc')
                price_tag = item.select_one('.menu-item-price')
                img_tag = item.select_one('img')

                name = name_tag.get_text(strip=True) if name_tag else None
                description = desc_tag.get_text(strip=True) if desc_tag else None
                price = price_tag.get_text(strip=True) if price_tag else None
                image = img_tag['src'] if img_tag and img_tag.has_attr('src') else None
                # if name is not None or price is not None:
                product_obj = Product(name=name, description=description, price=price,image_data=image)
                products.append(asdict(product_obj))
        return products
    except Exception as e:
        print(f"Error: {e}")
        return None