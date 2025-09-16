import os
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv
from utils.helpers import load_json
from utils.log_config import setup_logger
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,
    Attachment,
    FileContent,
    FileName,
    FileType,
    Disposition,
    ContentId
)

load_dotenv()
logger = setup_logger(__name__)

class EmailSender:
    """
    Email sender class
    """
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = "imvt xokz krwj pwiv"
        self.receiver_email = os.getenv("RECEIVER_EMAIL")
        self.reward_json = os.getenv("REWARD_JSON")
        self.sendgrid_server = "smtp.sendgrid.net"
    
    def send_reward(self, day: str)->None:
        """
        send reward mail
        ARGS:
            day <str>: assessment day
        RETURNS:
            None
        """
        server = None 
        try:
            reward_data = load_json(self.reward_json)
            reward_mail = next((r for r in reward_data if r["day"] == day), None)

            if not reward_mail:
                raise ValueError(f"No reward found for {day}")
            
            #subject = reward_mail["subject"]
            body_html = reward_mail["reward_body"]
            img_path = reward_mail["reward_img"]

            # --- Create Email ---
            msg = MIMEMultipart("related")
            msg["From"] = self.sender_email
            msg["To"] = self.receiver_email
            msg["Subject"] = "Stolen Hours ✨"

            # Attach HTML body
            msg_alt = MIMEMultipart("alternative")
            msg.attach(msg_alt)
            msg_alt.attach(MIMEText(body_html, "html"))

            # Attach inline image
            if os.path.exists(img_path):
                with open(img_path, "rb") as img_file:
                    img = MIMEImage(img_file.read())
                    img.add_header("Content-ID", "<sampleimage>")
                    img.add_header("Content-Disposition", "inline", filename=os.path.basename(img_path))
                    msg.attach(img)
            else:
                logger.warning(f"Image {img_path} not found, sending email without image.")
            
            
            # --- Send Mail ---
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=15)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, self.receiver_email, msg.as_string())
            logger.info(f"Email for {day} sent successfully!")
        except Exception as e:
            logger.error(f"Email sender error: {str(e)}")
        finally:
            if server:
                try:
                    server.quit()
                except Exception as e:
                    logger.error(f"mail Server exit error:{str(e)}")
        return None
    
def send_reward_sendgrid(self, day: str) -> None:
    """
    Send reward mail via SendGrid.
    """
    try:
        reward_data = load_json(self.reward_json)
        reward_mail = next((r for r in reward_data if r["day"] == day), None)
        if not reward_mail:
            raise ValueError(f"No reward found for {day}")

        body_html = reward_mail["reward_body"]
        img_path  = reward_mail["reward_img"]

        message = Mail(
            from_email=self.sender_email,   # verified sender
            to_emails=self.receiver_email,
            subject="Stolen Hours ✨",
            html_content=body_html
        )

        # Optional inline image
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                img_data = f.read()
            encoded = base64.b64encode(img_data).decode()
            attachment = Attachment(
                FileContent(encoded),
                FileName(os.path.basename(img_path)),
                FileType("image/png"),
                Disposition("inline"),       # marks as inline
                ContentId("sampleimage")     # reference in HTML with <img src="cid:sampleimage">
            )
            message.attachment = attachment
        else:
            logger.warning(f"Image {img_path} not found, sending without image.")

        sg = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
        sg.send(message)
        logger.info(f"Email for {day} sent successfully via SendGrid.")
    except Exception as e:
        logger.error(f"SendGrid email error: {e}")
