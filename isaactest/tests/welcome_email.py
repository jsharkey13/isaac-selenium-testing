import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency

__all__ = ["welcome_email"]


#####
# Test : Welcome Email Recieved
#####
@TestWithDependency("WELCOME_EMAIL", ["SIGNUP"])
def welcome_email(driver, inbox, GUERRILLAMAIL, **kwargs):
    """Test if the registration confirmation/welcome email is recieved.

        - 'driver' should be a Selenium WebDriver.
        - 'inbox' should be a GuerrillaInbox object.
        - 'GUERRILLAMAIL' is the string URL of GuerrillaMail.
    """
    assert_tab(driver, GUERRILLAMAIL)
    log(INFO, "Waiting 10 seconds for page to update.")
    time.sleep(11)
    inbox.refresh()

    log(INFO, "GuerrillaMail: Access welcome email in inbox.")
    try:
        welcome_emails = inbox.get_by_subject("Welcome to Isaac Physics!")
        assert len(welcome_emails) == 1, "Expected to recieve a welcome email, recieved %s emails!" % len(welcome_emails)
        welcome_email = welcome_emails[0]
        log(INFO, "Got welcome email as expected.")
        welcome_email.image()
        welcome_email.save_html_body()
        log(PASS, "Welcome email recieved!")
        return True
    except AssertionError, e:
        image_div(driver, "ERROR_not_isaac_email")
        log(ERROR, e.message + " See 'ERROR_not_isaac_email.png'!")
        return False
