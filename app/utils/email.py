import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_reset_email(email: str, reset_token: str) -> bool:
    try:
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured. Email will not be sent.")
        
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USERNAME
        msg['To'] = email
        msg['Subject'] = "Password Reset Request - E-commerce Platform"
        
        body = f"""
        Dear User,
        
        Please use the following secure token to reset your password:
        
        Reset Token: {reset_token}

        The token is valid for 30 minutes.
        
        Best regards,
        E-commerce Security Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email with proper error handling
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(settings.SMTP_USERNAME, email, text)
        
        logger.info(f"Password reset email sent successfully to {email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        logger.error(f"SMTP authentication failed for {email}")
        return False
    except smtplib.SMTPRecipientsRefused:
        logger.error(f"Invalid recipient email: {email}")
        return False
    except Exception as e:
        logger.error(f"Failed to send reset email to {email}")
        return False