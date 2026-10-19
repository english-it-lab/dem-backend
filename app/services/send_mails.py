import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def send_email(to: str, subject: str, body: str):
    smtp_server = settings.smtp_server  # "smtp.yandex.ru" или smtp.gmail.com
    smtp_port = 587  # 587 для TLS, 465 для SSL, 25 без шифрования
    login = settings.email_login
    password = settings.email_password

    # Создание сообщения
    msg = MIMEMultipart()
    msg["From"] = login
    msg["To"] = to
    msg["Subject"] = subject

    # Текст письма
    body = body
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # Отправка
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Включаем шифрование TLS
            server.login(login, password)
            server.send_message(msg)
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
