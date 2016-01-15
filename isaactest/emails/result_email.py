import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

__all__ = ['send_results']

_TO = ["test@test.com"]
_SERVER = "ppsw.cam.ac.uk"


def _format_recipients(recipients):
    """Take a list of recipient emails and format it nicely for emailing."""
    return ", ".join(recipients)


def send_results(timestamp, summary, recipients=_TO):
    """Send out an email containing the test results.

        - 'timestamp' should be a string describing when the test was run.
        - 'summary' should be a string giving a breakdown of the test results.
        - 'recipients' is an optional list of email addresses to send the results
          to. If not specified, the default email address will be used.
    """
    msg_text = "Isaac Regression Test on %s\n\n" % timestamp
    msg_text += summary
    msg = MIMEMultipart()
    msg['To'] = _format_recipients(recipients)
    msg['From'] = email.utils.formataddr(('Isaac Regression Test', 'cl-isaac-contact@lists.cam.ac.uk'))
    msg['Subject'] = "Isaac Regression Test on %s\n\n" % timestamp
    msg.attach(MIMEText(msg_text, 'plain', 'utf-8'))
    with open("_TEST_LOG.txt", "r") as f:
        msg.attach(MIMEApplication(f.read(), Content_Disposition="attachment; filename='test_results.txt'", Name="test_results.txt"))

    server = smtplib.SMTP(_SERVER)

    try:
        #  server.set_debuglevel(True)  # Print out full logging info?
        server.starttls()
        server.ehlo()
        server.sendmail('cl-isaac-contact@lists.cam.ac.uk', _TO, msg.as_string())
    finally:
        server.quit()
