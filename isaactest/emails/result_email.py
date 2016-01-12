import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

__all__ = ['send_results']

_TO = ["test@test.com"]
_SERVER = "ppsw.cam.ac.uk"


def _format_recipients(recipients):
    return ", ".join(recipients)


def send_results(timestamp, recipients=_TO):
    msg_text = "Isaac Regression Test on %s\n\n" % timestamp
    msg = MIMEMultipart()
    msg['To'] = _format_recipients(recipients)
    msg['From'] = email.utils.formataddr(('Isaac Regression Test', 'cl-isaac-contact@lists.cam.ac.uk'))
    msg['Subject'] = "Isaac Regression Test on %s\n\n" % timestamp
    msg.attach(MIMEText(msg_text, 'plain', 'utf-8'))
    with open("_TEST_LOG.txt", "r") as f:
        msg.attach(MIMEApplication(f.read(), Content_Disposition="attachment; filename='test_results.txt'", Name="test_results.txt"))

    server = smtplib.SMTP(_SERVER)
    try:
        #  server.set_debuglevel(True)
        server.starttls()
        server.ehlo()
        server.sendmail('cl-isaac-contact@lists.cam.ac.uk', _TO, msg.as_string())
    finally:
        server.quit()
