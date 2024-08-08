"""Models to return validated JSON."""

from pydantic import BaseModel


class Login(BaseModel):
    """Model to return the login url."""

    login_url: str


class Token(BaseModel):
    """Model to return the user data and OSM OAuth token."""

    user_data: str
    oauth_token: str
