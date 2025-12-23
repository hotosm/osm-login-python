"""Test the main module logic."""


def test_serialize_deserialize(auth):
    """Simple check to see if the serialization works as intended."""
    dummy_osm_token = "jdsifcjh984h3fhj40efh4j39t8gh4eg985tr"
    serialized_dummy_osm_token = auth._serialize_encode_data(dummy_osm_token)
    deserialized_dummy_osm_token = auth.deserialize_data(serialized_dummy_osm_token)

    assert deserialized_dummy_osm_token == dummy_osm_token


def test_login(auth, mocker):
    """Test the login() method returns a URL."""
    # Mock the authorization_url returned by the OAuth session
    mocker.patch.object(auth.oauth, "authorization_url", return_value=("https://openstreetmap.org/oauth2/authorize", "state"))

    # Test the login method using mock data
    result = auth.login()
    assert result == {"login_url": "https://openstreetmap.org/oauth2/authorize"}


def test_callback(auth, mocker):
    """Test the callback() method returns serialized data."""
    # Patch the requests_oauthlib fetch_token method with a mock access_token
    mocker.patch.object(auth.oauth, "fetch_token", return_value={"access_token": "fswfhewuihfewuhew"})

    # Mock OSM user data and patch GET request
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "user": {"id": 12345, "display_name": "testuser", "img": {"href": "https://example.com/image.jpg"}}
    }
    mocker.patch.object(auth.oauth, "get", return_value=mock_response)

    # Compare expected responses with actual responses from callback()
    api_result = auth.callback("https://example.com/callback")

    expected_user_data = auth._serialize_encode_data(
        {"id": 12345, "username": "testuser", "img_url": "https://example.com/image.jpg"}
    )
    expected_oauth_token = auth._serialize_encode_data("fswfhewuihfewuhew")

    assert api_result == {"user_data": expected_user_data, "oauth_token": expected_oauth_token}
