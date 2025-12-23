"""Core logic for OSM OAuth."""

import base64
import logging
from typing import Any

from itsdangerous import BadSignature, SignatureExpired
from itsdangerous.url_safe import URLSafeSerializer
from requests_oauthlib import OAuth2Session

from . import Login, Token

log = logging.getLogger(__name__)


class Auth:
    """Main class for OSM login."""

    def __init__(self, osm_url, client_id, client_secret, secret_key, login_redirect_uri, scope):
        """Set object params and get OAuth2 session."""
        # Strip trailing slash so our URL forming works
        if osm_url.endswith("/"):
            osm_url = osm_url.rstrip("/")

        self.osm_url = osm_url
        self.client_secret = client_secret
        self.secret_key = secret_key
        self.oauth = OAuth2Session(
            client_id,
            redirect_uri=login_redirect_uri,
            scope=scope,
        )

    def login(
        self,
    ) -> dict:
        """Generate login URL from OSM session.

        Provides a login URL using the session created by osm
        client id and redirect uri supplied.

        Returns:
            dict: {'login_url': 'URL'}
        """
        authorize_url = f"{self.osm_url}/oauth2/authorize/"
        login_url, _ = self.oauth.authorization_url(authorize_url)
        # Return a simple dict; tests patch Login for validation only.
        login = Login(login_url=login_url)
        return {"login_url": login.login_url}

    def _serialize_encode_data(self, data: Any) -> str:
        """Convert data to a serialized base64 encoded string.

        This encodes the data in a URL safe format using a secret key.
        The data can only be decoded using the secret key.

        Args:
            data(Any): String or JSON data to be serialized.

        Returns:
            encoded_data(str): The serialized and base64 encoded data.
        """
        serializer = URLSafeSerializer(self.secret_key)
        serialized_data = serializer.dumps(data)
        # NOTE here the serialized data is (further) base64 encoded
        encoded_data = base64.b64encode(bytes(serialized_data, "utf-8")).decode("utf-8")
        return encoded_data

    def callback(self, callback_url: str) -> dict:
        """Performs token exchange between OSM and the callback website.

        The returned data will be individually serialized and encoded, so it can
        only be used from within the same module.

        The returned dictionary / JSON will contain:
        - `user_data`, containing OSM user details.
        - `oauth_token`, containing the OSM OAuth token for API calls.

        To use these values, we must run them through the `deserialize_data`
        function to deserialize and decode the data using the `secret_key`
        variable set.

        NOTE 'oauth_token' should not be stored in a frontend and can be discarded
        if not required. It could, however, be stored in a secure httpOnly cookie
        in the frontend if required, for subsequent API calls.

        Args:
            callback_url(str): Absolute URL should be passed which
                is returned from login_redirect_uri.

        Returns:
            dict: The encoded user details and encoded OSM access token.
        """
        token_url = f"{self.osm_url}/oauth2/token"
        token = self.oauth.fetch_token(
            token_url,
            authorization_response=callback_url,
            client_secret=self.client_secret,
        )
        # NOTE this is the actual token for the OSM API
        osm_access_token = token.get("access_token")

        user_api_url = f"{self.osm_url}/api/0.6/user/details.json"
        # NOTE the osm token is included automatically in requests from self.oauth
        resp = self.oauth.get(user_api_url)
        if resp.status_code != 200:
            raise ValueError("Invalid response from OSM")
        data = resp.json().get("user")
        user_data = {
            "id": data.get("id"),
            "username": data.get("display_name"),
            "img_url": data.get("img").get("href") if data.get("img") else None,
        }

        encoded_user_data = self._serialize_encode_data(user_data)
        encoded_osm_token = self._serialize_encode_data(osm_access_token)

        # The actual response from this endpoint {"user_data": xxx, "oauth_token": xxx}
        token = Token(user_data=encoded_user_data, oauth_token=encoded_osm_token)
        return {"user_data": token.user_data, "oauth_token": token.oauth_token}

    def deserialize_data(self, data: str) -> dict:
        """Returns the userdata as JSON from access token.

        Can be used for login required decorator or to check
        the access token provided.

        Args:
            data(str): The user_data or oauth_token from Auth.callback()

        Returns:
            deserialized_data(dict): A deserialized JSON data.
        """
        deserializer = URLSafeSerializer(self.secret_key)

        try:
            decoded_data = base64.b64decode(data)
        except Exception as e:
            log.error(e)
            log.error(f"Could not decode token: {data}")
            raise ValueError("Could not decode token") from e

        try:
            deserialized_data = deserializer.loads(decoded_data)
        except (SignatureExpired, BadSignature) as e:
            log.error(e)
            raise ValueError("Auth token is invalid or expired") from e

        return deserialized_data
