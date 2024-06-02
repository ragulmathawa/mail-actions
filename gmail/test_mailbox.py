import pytest
from mailbox import parse_email_address


def test_parse_email_address():
    # Test with email without angle brackets
    email = "test@example.com"
    assert parse_email_address(email) == "test@example.com"

    # Test with email with angle brackets
    email = "John Doe <john.doe@example.com>"
    assert parse_email_address(email) == "john.doe@example.com"

    # Test with email with multiple angle brackets
    email = "Jane Smith <jane.smith@example.com>"
    assert parse_email_address(email) == "jane.smith@example.com"

    # Test with email with whitespace
    email = "  John Doe <john.doe@example.com>  "
    assert parse_email_address(email) == "john.doe@example.com"

    # Test with empty email
    email = ""
    assert parse_email_address(email) == ""

    # Test with email without domain
    email = "john.doe"
    assert parse_email_address(email) == "john.doe"
