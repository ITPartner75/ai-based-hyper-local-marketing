import httpx
from urllib.parse import urlencode
from app.core.config import settings

def get_auth_url():
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "https://www.googleapis.com/auth/business.manage",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent"
    }
    print("get auth url:", f"{settings.GOOGLE_AUTH_URL}?{urlencode(params)}")
    return f"{settings.GOOGLE_AUTH_URL}?{urlencode(params)}"

async def exchange_code_for_token(code: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(settings.GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        })
        print("exchange code: ", response.json())
        return response.json()

async def get_profile_info(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BUSINESS_PROFILE_API}/accounts", headers={
            "Authorization": f"Bearer {access_token}"
        })
        print("get profile info: ", response.json())
        return response.json()