"""Module for authentication"""
from config import AUTH_PASSWORD, AUTH_USERNAME


def user_loader(username, password):
    """Authenticate the provided credentials"""
    return (username == AUTH_USERNAME) and (password == AUTH_PASSWORD)
