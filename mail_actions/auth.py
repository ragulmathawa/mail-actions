from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import json as json
import os as os

scope = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def get_credentials() -> Credentials:
    """
    Retrieves the credentials required for authentication using the OAuth2 flow.
    This function will open a browser window to authenticate the user and get the credentials.
    A local server will be started to handle the authentication callback.

    Returns:
        Credentials: The credentials object containing the authentication information.

    Raises:
        Exception: If failed to get credentials.
    """
    # show Oauth2 link to click
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scope)
    creds = flow.run_local_server(port=0)
    if not creds or not creds.valid:
        raise Exception("Failed to get credentials")

    return creds


def save_credentials(creds: Credentials, token_file: str):
    """
    Saves the provided credentials to a file named "token.json".

    Args:
        creds (Credentials): The credentials object to be saved.
    """
    with open(token_file, "w") as token:
        json.dump(json.loads(creds.to_json()), token)


def get_saved_credentials(token_file: str) -> Credentials | None:
    """
    Retrieves saved credentials from a token file.

    Returns:
        Credentials | None: The saved credentials if the token file exists, otherwise None.
    """
    if not os.path.exists(token_file):
        return None
    with open(token_file, "r") as token:
        creds = json.load(token)
        return Credentials.from_authorized_user_info(creds)
