from dataclasses import dataclass

@dataclass
class Login:
    login_url: str
    def __post_init__(self):
        if not isinstance(self.login_url, str) or not self.login_url:
            raise TypeError("login_url must be a non-empty string")

@dataclass
class Token:
    user_data: str
    oauth_token: str
    def __post_init__(self):
        if not isinstance(self.user_data, str) or not self.user_data:
            raise TypeError("user_data must be a non-empty string")
        if not isinstance(self.oauth_token, str) or not self.oauth_token:
            raise TypeError("oauth_token must be a non-empty string")