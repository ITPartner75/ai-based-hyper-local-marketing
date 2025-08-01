import httpx
from urllib.parse import urlencode
from app.core.config import settings

def get_auth_url():
    params = {
        "client_id": settings.FB_CLIENT_ID,
        "redirect_uri": settings.FB_REDIRECT_URI,
        "scope": "pages_show_list,instagram_basic,public_profile",
        "response_type": "code"
    }
    print(f"{settings.FB_AUTH_BASE}?{urlencode(params)}")
    return f"{settings.FB_AUTH_BASE}?{urlencode(params)}"

async def exchange_code_for_token(code: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(settings.FB_TOKEN_URL, params={
            "client_id": settings.FB_CLIENT_ID,
            "client_secret": settings.FB_CLIENT_SECRET,
            "redirect_uri": settings.FB_REDIRECT_URI,
            "code": code
        })
        print("exchange code:", response.json())
        return response.json()

async def get_user_profile(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.GRAPH_API_BASE}/me", params={
            "fields": "id,name,email",
            "access_token": access_token
        })
        print("get user profile:", response.json())
        return response.json()