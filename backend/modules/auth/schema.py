from pydantic import BaseModel, EmailStr


# Token Response
class TokenResponse(BaseModel):
    """
    Schema returned after successful authentication.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
