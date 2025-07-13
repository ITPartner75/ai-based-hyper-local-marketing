import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dataclasses import asdict
from app.schemas.business import Product

def get_website_logo_bytes(url) -> bytes | None:
    try:
        # Get the HTML content of the website
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find image elements that might be a logo
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '').lower()
            class_name = ' '.join(img.get('class', [])).lower()

            if 'logo' in src.lower() or 'logo' in alt or 'logo' in class_name:
                logo_url = urljoin(url, src)

                # Fetch the image content as bytes
                img_response = requests.get(logo_url, timeout=10)
                img_response.raise_for_status()
                print(img_response.content)
                return img_response.content  # ✅ bytes of the logo image

        return None  # No logo found

    except Exception as e:
        print(f"Error: {e}")
        return None
    
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
                if name is not None or price is not None:
                    product_obj = Product(name=name, description=description, price=price,image_data=image)
                    products.append(asdict(product_obj))
        return products
    except Exception as e:
        print(f"Error: {e}")
        return None