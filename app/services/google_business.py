import httpx
import aiohttp
from urllib.parse import urlencode
from app.core.config import settings
from app.schemas.business import LocationModel
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from typing import Union

ACCOUNTS_URL = "https://mybusinessaccountmanagement.googleapis.com/v1/accounts"
LOCATIONS_URL = "https://mybusinessbusinessinformation.googleapis.com/v1/accounts/{account_id}/locations"


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
    
async def get_accounts(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(ACCOUNTS_URL, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to get accounts: {await resp.text()}")
            data = await resp.json()
            return data.get("accounts", [])

async def get_locations(access_token: str, account_id: str):
    url = f"https://mybusinessbusinessinformation.googleapis.com/v1/accounts/{account_id}/locations"
    params = {
        # Start minimal to ensure success
        "readMask": "name,title,websiteUri,storeCode,openInfo,latlng,regularHours,phoneNumbers,storefrontAddress"
    }
    headers = {"Authorization": f"Bearer {access_token}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to get locations: {await resp.text()}")
            data = await resp.json()
            print(data)
            return data.get("locations", [])

        
def get_all_locations_from_google_business() -> Union[None, LocationModel]:
    """
    Authenticates with Google Business Profile API and returns all locations.

    Args:
        client_id: Google OAuth Client ID
        client_secret: Google OAuth Client Secret

    Returns:
        List of LocationModel objects
    """
    SCOPES = ["https://www.googleapis.com/auth/business.manage"]

    # Create OAuth flow configuration
    flow = InstalledAppFlow.from_client_config(
        {
            "installed": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        SCOPES
    )

    # Authenticate (opens browser)
    creds = flow.run_local_server(port=0)

    # Build service clients
    accounts_service = build("mybusinessaccountmanagement", "v1", credentials=creds)
    locations_service = build("mybusinessbusinessinformation", "v1", credentials=creds)

    # Step 1: Get all accounts
    accounts_response = accounts_service.accounts().list().execute()
    accounts = accounts_response.get("accounts", [])

    # all_locations = []

    for account in accounts:
        account_name = account["name"]  # e.g., "accounts/123456789"

        # Step 2: Get all locations for the account
        locations_response = locations_service.accounts().locations().list(parent=account_name).execute()
        locations = locations_response.get("locations", [])

        for loc in locations:
            lat = loc.get("latLng", {}).get("latitude")
            lng = loc.get("latLng", {}).get("longitude")
            location_str = f"{lat},{lng}" if lat and lng else None

            addr = loc.get("address", {})
            city = addr.get("locality")
            state = addr.get("administrativeArea")
            country = addr.get("regionCode")
            postal_code = addr.get("postalCode")

            # all_locations.append(
            return LocationModel(
                city=city,
                state=state,
                country=country,
                postal_code=postal_code,
                location=location_str
            )
            # )
    return None