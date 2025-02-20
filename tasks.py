import os
import requests
import jinja2
from dotenv import load_dotenv

load_dotenv()

MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN", "sandbox6b22c5506eb34ceab981289922bc8f04.mailgun.org")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")

template_loader = jinja2.FileSystemLoader("templates")
template_env = jinja2.Environment(loader=template_loader)

def render_template(template_filename, **context):
    return template_env.get_template(template_filename).render(**context)

def send_simple_email(to_email: str, subject: str, message: str, html: str = None) -> dict:
    if not MAILGUN_API_KEY:
        raise ValueError("MAILGUN_API_KEY is not set")

    data = {
        "from": f"Sender <postmaster@{MAILGUN_DOMAIN}>",
        "to": [to_email],
        "subject": subject,
        "text": message,
    }

    if html:
        data["html"] = html

    response = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data=data
    )

    print(f"Mailgun response: {response.status_code}, {response.text}")
    return response.json()

def send_user_registration_email(email, username):
    return send_simple_email(
        to_email=email,
        subject="Successfully signed up",
        message=f"Hi {username}! You have successfully signed up to our platform.",
        html=render_template("email/registration.html", username=username)
    )
