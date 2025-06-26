import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
