from unittest.mock import patch

import pytest

from app.core.config import settings
from app.services.send_mails import send_email


# Фикстура для мока настроек
@pytest.fixture
def mock_settings():
    with patch("app.core.config.settings") as mock:
        mock.smtp_server = "smtp.example.com"
        mock.smtp_port = 587
        mock.email_login = "test@example.com"
        mock.email_password = "test-password"
        yield mock


# TC-01: Успешная отправка
def test_send_email_success(capsys):
    with patch("smtplib.SMTP") as MockSMTP:
        mock_server = MockSMTP.return_value.__enter__.return_value
        mock_server.send_message.return_value = None

        send_email("user@example.com", "Hello", "Test body")

        MockSMTP.assert_called_once_with(settings.smtp_server, 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(settings.email_login, settings.email_password)
        mock_server.send_message.assert_called_once()

        captured = capsys.readouterr()
        assert "Ошибка" not in captured.out


# TC-02 / TC-03 / TC-04 / TC-05: Ошибка при отправке
def test_send_email_failure(capsys):
    with patch("smtplib.SMTP") as MockSMTP:
        mock_server = MockSMTP.return_value.__enter__.return_value
        mock_server.send_message.side_effect = Exception("SMTP error")

        send_email("user@example.com", "Hello", "Test body")

        captured = capsys.readouterr()
        assert "Ошибка при отправке: SMTP error" in captured.out


# Проверка, что порт 587 используется
def test_smtp_port():
    with patch("smtplib.SMTP") as MockSMTP, patch("builtins.print"):  # подавляем print
        send_email("a@b.c", "s", "b")
        MockSMTP.assert_called_once_with(settings.smtp_server, 587)
