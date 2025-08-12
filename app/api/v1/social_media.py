from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi import status
from app.services import facebook, google_business
from app.schemas.business import LocationModel
from app.core.security import get_current_user


router = APIRouter()

@router.get("/login/facebook")
def login_facebook(user=Depends(get_current_user)):
    try:
        auth_url = facebook.get_auth_url()
        if not auth_url:
            return JSONResponse(
                content={"error": "Authorization URL could not be generated."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return JSONResponse(
            content={"auth_url": auth_url},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        # Optional: Log error here
        print(f"Facebook login error: {str(e)}")
        return JSONResponse(
            content={"error": "An error occurred while generating the Facebook login URL."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/callback/facebook")
async def callback_facebook(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "No code provided"}, status_code=400)
    token_data = await facebook.exchange_code_for_token(code)
    user_info = await facebook.get_user_profile(token_data['access_token'])
    return user_info

@router.get("/login/google")
def login_google(user=Depends(get_current_user)):
    try:
        auth_url = google_business.get_auth_url()
        if not auth_url:
            return JSONResponse(
                content={"error": "Authorization URL could not be generated."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return JSONResponse(
            content={"auth_url": auth_url},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        # Log the actual exception if needed
        print(f"Google login error: {str(e)}")
        return JSONResponse(
            content={"error": "An error occurred while generating the login URL."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/callback/google")
async def callback_google(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "No code provided"}, status_code=400)

    # Step 1: Exchange code for token
    token_data = await google_business.exchange_code_for_token(code)
    print(token_data)
    access_token = token_data["access_token"]

    # Step 2: Get profile info (Google account / business profile owner info)
    profile_info = await google_business.get_profile_info(access_token)

    # Step 3: Get accounts
    accounts = await google_business.get_accounts(access_token)
    if not accounts:
        return JSONResponse({"error": "No Google Business accounts found"}, status_code=404)

    # Just take the first account for now
    account_id = accounts[0]["name"].replace("accounts/", "")  # e.g., "accounts/123456789"

    # Step 4: Get locations for that account
    locations = await google_business.get_locations(access_token, account_id)
    if not locations:
        return {
            "profile": profile_info,
            "locations": []
        }

    # Step 5: Extract location details safely
    location_list = []
    for loc in locations:
        lat_lng = loc.get("latLng", {})
        lat = lat_lng.get("latitude")
        lng = lat_lng.get("longitude")
        coordinates = f"{lat},{lng}" if lat and lng else None

        addr = loc.get("address", {})
        city = addr.get("locality")
        state = addr.get("administrativeArea")
        country = addr.get("regionCode")
        postal_code = addr.get("postalCode")

        location_obj = LocationModel(
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
            coordinates=coordinates
        )

        location_list.append({
            "business_name": loc.get("title"),
            "category": loc.get("categories", {}).get("primaryCategory", {}).get("displayName"),
            "website": loc.get("websiteUri"),
            "location": location_obj.dict()  # Convert Pydantic model to dict
        })

    # Step 6: Return profile + locations
    return {
        "profile": profile_info,
        "locations": location_list
    }

