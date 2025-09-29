from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login")
def login_for_access_token(data: OAuth2PasswordRequestForm = Depends()):
    if data.username != "admin@example.com" or data.password != "secret":
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": "fake-jwt-token-for-demo",
        "token_type": "bearer"
    }