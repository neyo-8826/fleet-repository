"""Module containing discord API session"""
from urllib.parse import urljoin

from requests import Session


class DiscordAPISession(Session):
    def __init__(self, base_url=None, *args, **kwargs):
        """Initialize the Session object"""
        super().__init__(*args, *kwargs)
        # store the base URL
        self.base_url = base_url

    def request(self, method, path, *args, **kwargs):
        """Handle requests"""
        # Join the base url and the provided path
        url = urljoin(self.base_url, path)
        return super().request(method, url, *args, **kwargs)
