# tests/mailer/test_sender.py
from unittest.mock import patch, MagicMock

from mailer.sender import send_email


def test_send_email_calls_sendgrid():
    with patch("mailer.sender.SendGridAPIClient") as mock_sg:
        mock_client = MagicMock()
        mock_client.send.return_value = MagicMock(status_code=202)
        mock_sg.return_value = mock_client

        result = send_email(
            subject="Test Subject",
            html_body="<h1>Test</h1>",
            api_key="fake-key",
            to_email="test@example.com",
            from_email="scout@example.com",
        )
        assert result is True
        mock_client.send.assert_called_once()


def test_send_email_returns_false_on_failure():
    with patch("mailer.sender.SendGridAPIClient") as mock_sg, \
         patch("mailer.sender.time.sleep"):
        mock_client = MagicMock()
        mock_client.send.side_effect = Exception("API error")
        mock_sg.return_value = mock_client

        result = send_email(
            subject="Test",
            html_body="<h1>Test</h1>",
            api_key="fake-key",
            to_email="test@example.com",
            from_email="scout@example.com",
        )
        assert result is False
