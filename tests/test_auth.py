import pytest
import unittest.mock as mocker
import json
from mail_actions.auth import get_credentials, save_credentials, get_saved_credentials


def test_save_credentials(tmp_path):
    # Create a temporary directory for the test
    temp_dir = tmp_path
    token_file = temp_dir / "token.json"

    mock_creds = mocker.Mock()
    mock_creds.to_json.return_value = '{"access_token": "mock_token"}'

    save_credentials(mock_creds, token_file.absolute())

    assert token_file.exists()

    with open(token_file, "r") as f:
        token_data = json.load(f)

    assert token_data == {"access_token": "mock_token"}


def test_get_saved_credentials(tmp_path):
    # Create a temporary directory for the test
    temp_dir = tmp_path
    token_file = temp_dir / "token.json"

    with open(token_file, "w") as f:
        json.dump(
            {
                "refresh_token": "mock_token",
                "client_id": "mock_id",
                "client_secret": "secret",
            },
            f,
        )

    creds = get_saved_credentials(token_file.absolute())

    assert creds is not None
    assert creds.refresh_token == "mock_token"
    assert creds.client_id == "mock_id"
    assert creds.client_secret == "secret"
