from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency

__all__ = ["recieve_verify_emails"]


#####
# Test : Recieve Verification Emails
#####
@TestWithDependency("RECIEVE_VERIFY_EMAILS", ["REQ_VERIFY_EMAILS"])
def recieve_verify_emails(driver, inbox, GUERRILLAMAIL, WAIT_DUR, **kwargs):
    """Test if the new verification emails are recieved.

        - 'driver' should be a Selenium WebDriver.
        - 'inbox' should be a GuerrillaInbox object.
        - 'GUERRILLAMAIL' is the string URL of GuerrillaMail.
    """
    verification_email_request_limit = 4
    assert_tab(driver, GUERRILLAMAIL)
    inbox.wait_for_email(WAIT_DUR)

    verification_emails_recived = 0
    log(INFO, "Checking if verification emails recieved.")
    try:
        verification_emails = inbox.get_by_subject("Verify your email")
        verification_emails_recived = len(verification_emails)
        assert verification_emails_recived == verification_email_request_limit
        for email in verification_emails:
            email.image()
            email.save_html_body()
        log(PASS, "%s verification emails recieved." % verification_emails_recived)
        return True
    except AssertionError:
        image_div(driver, "ERROR_recieve_verification")
        log(ERROR, "Expected %s verification emails, recieved %s. See 'ERROR_recieve_verification.png'!" % (verification_email_request_limit, verification_emails_recived))
        return False
