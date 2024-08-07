"""Models to return validated JSON."""

from pydantic import BaseModel


class Login(BaseModel):
    """Model to return the login url."""

    login_url: str


class Token(BaseModel):
    """Model to return the access token."""

    access_token: str
    raw_token: str
