"""Core logic for OSM OAuth."""

import base64
import json
import logging

from itsdangerous import BadSignature, SignatureExpired
from itsdangerous.url_safe import URLSafeSerializer
from requests_oauthlib import OAuth2Session

from . import Login, Token

log = logging.getLogger(__name__)


class Auth:
    """Main class for OSM login."""

    def __init__(self, osm_url, client_id, client_secret, secret_key, login_redirect_uri, scope):
        """Set object params and get OAuth2 session."""
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
        return json.loads(Login(login_url=login_url).model_dump_json())

    def callback(self, callback_url: str) -> dict:
        """Performs token exchange between OSM and the callback website.

        Core will use Oauth secret key from configuration while deserializing token,
        provides access token that can be used for authorized endpoints.

        NOTE to keep backward compatibility, we have 'access_token' in the returned
        dictionary. However, this would better be described as encoded_user_data.
        The 'access_token' (encoded user data) can only be deserialised via the
        'deserialize_access_token' method in this module.

        NOTE 'raw_token' is the second item in the returned dictionary, which is
        the actual OSM token for the API. This should not be stored in a frontend
        and can be discarded if not required. It could, however, be stored in a
        secure httpOnly cookie in the frontend if required, for subsequent calls.

        Args:
            callback_url(str): Absolute URL should be passed which
                is catched from login_redirect_uri.

        Returns:
            dict: The encoded user details and encoded raw access token.
        """
        token_url = f"{self.osm_url}/oauth2/token"
        token = self.oauth.fetch_token(
            token_url,
            authorization_response=callback_url,
            client_secret=self.client_secret,
        )
        # NOTE this is the actual token for the OSM API
        raw_osm_access_token = token.get("access_token")

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

        # NOTE this encodes the data in a URL safe format using a secret key
        serializer = URLSafeSerializer(self.secret_key)
        serialized_user_data = serializer.dumps(user_data)
        serialized_raw_token = serializer.dumps(raw_osm_access_token)
        # NOTE here the encoded data is (further) base64 encoded
        encoded_user_data = base64.b64encode(bytes(serialized_user_data, "utf-8")).decode("utf-8")
        encoded_raw_token = base64.b64encode(bytes(serialized_raw_token, "utf-8")).decode("utf-8")

        # The actual response from this endpoint {"access_token": xxx, "raw_token": xxx}
        token = Token(access_token=encoded_user_data, raw_token=encoded_raw_token)
        return token.model_dump()

    def deserialize_access_token(self, access_token: str) -> dict:
        """Returns the userdata as JSON from access token.

        Can be used for login required decorator or to check
        the access token provided.

        Args:
            access_token(str): The access token from Auth.callback()

        Returns:
            deserialized_data(dict): A deserialized JSON data.
        """
        deserializer = URLSafeSerializer(self.secret_key)

        try:
            decoded_token = base64.b64decode(access_token)
        except Exception as e:
            log.error(e)
            log.error(f"Could not decode token: {access_token}")
            raise ValueError("Could not decode token") from e

        try:
            deserialized_data = deserializer.loads(decoded_token)
        except (SignatureExpired, BadSignature) as e:
            log.error(e)
            raise ValueError("Auth token is invalid or expired") from e

        return deserialized_data
