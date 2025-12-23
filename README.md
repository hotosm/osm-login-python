# osm-login-python

Package to manage OAuth 2.0 login for OSM in Python.

📖 [Documentation](https://hotosm.github.io/osm-login-python/)

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/hotosm/osm-login-python/main.svg)](https://results.pre-commit.ci/latest/github/hotosm/osm-login-python/main)

![coverage badge](./docs/coverage.svg)

## Install with [pip](https://pypi.org/project/osm-login-python/)

```bash
pip install osm-login-python
```

## Import Auth and initialize class with your credentials

```python
from osm_login_python.core import Auth
```

```python
osm_auth=Auth(
    osm_url=YOUR_OSM_URL,
    client_id=YOUR_OSM_CLIENT_ID,
    client_secret=YOUR_OSM_CLIENT_SECRET,
    secret_key=YOUR_OSM_SECRET_KEY,
    login_redirect_uri=YOUR_OSM_LOGIN_REDIRECT_URI,
    scope=YOUR_OSM_SCOPE_LIST,
)
```

## Usage

Three functions are provided:

1. login() -- Returns the login url for OSM.
   - The user must then access this URL and authorize the OAuth application
     to login.
   - The user will be redirected to the configured `login_redirect_uri` after
     successful login with OSM.
   - The web page must then call the `callback()` function below, sending the
     current URL to the function (which includes the OAuth authorization code).

2. callback() -- Returns the encoded and serialized data:
   - `user_data` a JSON of OSM user data.
   - `oauth_token` a string OSM OAuth token.
   - Both are encoded and serialized as an additional safety measure when used
     in URLs.

3. deserialize_data() -- returns decoded and deserialized data from `callback()`.

> [!NOTE]
> This package is primarily intended to return OSM user data.
>
> It is also possible to obtain the `oauth_token` as described above, for making
> authenticated requests against the OSM API from within a secure **backend**
> service.
>
> To use the OAuth token in a **frontend** please use caution and adhere
> to best practice security, such as embedding in a secure httpOnly cookie
> (do not store in localStorage, sessionStorage, or unsecure cookies).

## Example

In Django:

```python
import json
from django.conf import settings
from osm_login_python.core import Auth
from django.http import JsonResponse

# initialize osm_auth with our credentials
osm_auth = Auth(
    osm_url=YOUR_OSM_URL,
    client_id=YOUR_OSM_CLIENT_ID,
    client_secret=YOUR_OSM_CLIENT_SECRET,
    secret_key=YOUR_OSM_SECRET_KEY,
    login_redirect_uri=YOUR_OSM_LOGIN_REDIRECT_URI,
    scope=YOUR_OSM_SCOPE,
)

def login(request):
    login_url = osm_auth.login()
    return JsonResponse(login_url)

def callback(request):
    # Generating token through osm_auth library method
    token = osm_auth.callback(request.build_absolute_uri())
    return JsonResponse(token)

def get_my_data(request, serialized_user_data: str):
    user_data = osm_auth.deserialize_data(serialized_user_data)
    return JsonResponse(user_data)
```

- Django integration example here
  <https://github.com/hotosm/fAIr/tree/master/backend/login>

- FastAPI integration example here
  <https://github.com/hotosm/export-tool-api/tree/develop/API/auth>

### Version Control

Use [commitizen](https://pypi.org/project/commitizen/) for version control.

### Test Coverage

Generate a coverage badge:

```bash
uv sync --extra test
uv run coverage run -m pytest
# uv run coverage report
uv run coverage-badge -o docs/coverage.svg
```

### Contribute

Contributions are welcome!
