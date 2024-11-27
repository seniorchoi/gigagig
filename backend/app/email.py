import requests
from flask import current_app

def send_email(to_email, subject, html_content):
    api_key = current_app.config['MAILGUN_API_KEY']
    domain = current_app.config['MAILGUN_DOMAIN']
    sender = current_app.config['MAIL_DEFAULT_SENDER']
    base_url = current_app.config['MAILGUN_BASE_URL']

    if not api_key or not domain:
        print('Mailgun API key or domain not configured.')
        return

    try:
        response = requests.post(
            f"{base_url}/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": sender,
                "to": to_email,
                "subject": subject,
                "html": html_content
            }
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'Error sending email: {e}')
        return False
    return True
