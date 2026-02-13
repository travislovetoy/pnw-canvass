import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config


def send_welcome_email(to_email, full_name, username, password, login_url):
    """Send a welcome email with login credentials to a new sales rep."""
    if not config.SMTP_USERNAME or not config.SMTP_PASSWORD:
        return False, "SMTP credentials not configured"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Welcome to PNW Canvass"
    msg["From"] = config.SMTP_USERNAME
    msg["To"] = to_email

    html = f"""\
<html>
<body style="font-family: Arial, sans-serif; max-width: 500px;">
  <h2>Welcome to PNW Canvass, {full_name}!</h2>
  <p>Your account has been created. Use the credentials below to log in:</p>
  <table style="border-collapse: collapse; margin: 16px 0;">
    <tr><td style="padding: 4px 12px; font-weight: bold;">Username:</td><td style="padding: 4px 12px;">{username}</td></tr>
    <tr><td style="padding: 4px 12px; font-weight: bold;">Password:</td><td style="padding: 4px 12px;">{password}</td></tr>
  </table>
  <p><a href="{login_url}" style="display: inline-block; padding: 10px 20px; background: #0d6efd; color: #fff; text-decoration: none; border-radius: 4px;">Log In</a></p>
  <p style="color: #666; font-size: 13px;">Please change your password after your first login.</p>
</body>
</html>"""

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_USERNAME, to_email, msg.as_string())
        return True, None
    except Exception as e:
        return False, str(e)
