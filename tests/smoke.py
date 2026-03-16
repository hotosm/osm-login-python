import logging
import os

from osm_login_python.core import Auth

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_DEBUG"] = "1"

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("oauthlib").setLevel(logging.DEBUG)

osm_auth = Auth(
    osm_url="https://www.openstreetmap.org",
    client_id="test",
    client_secret="test",
    secret_key="my-awesome-secret-key",
    login_redirect_uri="http://127.0.0.1:8000/api/v1/auth/callback/",
    scope="read_prefs",
)

login = osm_auth.login()
print("\nOpen this URL in browser and authorize:\n")
print(login["login_url"])

callback_url = input("\nPaste the full callback URL here: ").strip()
result = osm_auth.callback(callback_url)

print("\nEncoded callback result:")
print(result)

print("\nDecoded user_data:")
print(osm_auth.deserialize_data(result["user_data"]))

print("\nDecoded oauth_token:")
print(osm_auth.deserialize_data(result["oauth_token"]))
