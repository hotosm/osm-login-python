"""Configure fixtures for testing."""

import pytest

from osm_login_python.core import Auth


@pytest.fixture
def auth():
    """Setup the Auth object."""
    return Auth(
        osm_url="https://www.openstreetmap.org",
        client_id="xxxxx",
        client_secret="xxxxx",
        secret_key="superdupersecretkey",
        login_redirect_uri="https://someurl.com/callback",
        scope="read_prefs",
    )
