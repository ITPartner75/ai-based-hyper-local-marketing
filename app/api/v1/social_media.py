from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi import status
from app.services import facebook, google_business
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
    token_data = await google_business.exchange_code_for_token(code)
    profile_info = await google_business.get_profile_info(token_data['access_token'])
    return profile_info