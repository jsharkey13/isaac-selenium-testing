import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency

__all__ = ["recieve_pwd_reset_emails"]


#####
# Test : 4 password reset emails recieved
#####
@TestWithDependency("RECIEVE_PWD_RESET_EMAILS", ["PWD_RESET_THROTTLE"])
def recieve_pwd_reset_emails(driver, inbox, GUERRILLAMAIL, WAIT_DUR, **kwargs):
    """Test that the correct number of password reset emails are recieved after being requested.

        - 'driver' should be a Selenium WebDriver.
        - 'inbox' should be a GuerrillaInbox object.
        - 'GUERRILLAMAIL' is the string URL of GuerrillaMail.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    forgot_pwd_request_limit = 4
    assert_tab(driver, GUERRILLAMAIL)
    inbox.wait_for_email(WAIT_DUR, expected=forgot_pwd_request_limit)

    forgot_password_emails_recieved = 0
    log(INFO, "Checking if password reset emails recieved.")
    try:
        reset_email_list = inbox.get_by_subject("Password Reset Request", unread=True)
        log(INFO, "Getting all unread emails with subject 'Password Reset Request'.")
        forgot_password_emails_recieved = len(reset_email_list)
        assert forgot_password_emails_recieved == forgot_pwd_request_limit
        log(INFO, "Recieved the expected %s password reset emails." % forgot_pwd_request_limit)
        for email in reset_email_list:
            email.image()
            email.save_html_body()
        log(PASS, "%s reset password emails recieved." % forgot_pwd_request_limit)
        return True
    except AssertionError:
        image_div(driver, "ERROR_recieve_reset_pwd")
        log(ERROR, "Expected %s password reset emails, recieved %s. See 'ERROR_recieve_reset_pwd.png'!" % (forgot_pwd_request_limit, forgot_password_emails_recieved))
        return False
