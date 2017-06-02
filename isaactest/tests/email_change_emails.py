import time
from ..emails.guerrillamail import set_guerrilla_mail_address
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException

__all__ = ["email_change_emails"]


#####
# Test : Check Change Email Emails Recieved
#####
@TestWithDependency("EMAIL_CHANGE_EMAILS", ["EMAIL_CHANGE"])
def email_change_emails(driver, inbox, Users, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR, **kwargs):
    """Test if the email change confirmation emails are recieved.

        - 'driver' should be a Selenium WebDriver.
        - 'inbox' should be a GuerrillaInbox object.
        - 'Users' must be a TestUsers object.
        - 'GUERRILLAMAIL' is the string URL of GuerrillaMail.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, GUERRILLAMAIL)
    log(INFO, "Checking if emails were sent after changing account email.")
    inbox.wait_for_email(WAIT_DUR)

    try:
        old_warning_email = inbox.get_by_subject("Change in Isaac Physics email address requested!")[0]
        log(INFO, "Old warning email recieved and has expected subject line.")
        old_warning_email.image("change_email_old_email.png")
        old_warning_email.save_html_body("change_email_old_email")
        old_warning_email.view()
        email_body = old_warning_email.get_email_body_element()
        email_body.find_element_by_xpath("//a[text()='%s']" % Users.Guerrilla.new_email)
        old_warning_email.close()
        log(INFO, "Warning email successfully sent to old address.")
    except IndexError:
        image_div(driver, "ERROR_no_old_email_warning")
        log(ERROR, "No warning email recieved in old email inbox; see 'ERROR_no_old_email_warning.png'!")
        return False
    except NoSuchElementException:
        log(ERROR, "Link to new address not in old warning email, see image!")
        return False
    time.sleep(WAIT_DUR)
    set_guerrilla_mail_address(driver, Users.Guerrilla.new_email)
    inbox.wait_for_email(WAIT_DUR)

    try:
        new_verify_email = inbox.get_by_subject("Verify your email")[0]
        log(INFO, "New verify email recieved and has expected subject line.")
        new_verify_email.image("change_email_new_email.png")
        new_verify_email.save_html_body("change_email_new_email")
        new_verify_email.view()
        time.sleep(WAIT_DUR)
        email_body = new_verify_email.get_email_body_element()
        verification_link = email_body.find_element_by_xpath(".//a[text()='Verify your email address']")
        Users.Guerrilla.verify_link = str(verification_link.get_attribute("href")).replace("https://localhost:8080/isaac-api", ISAAC_WEB)
        log(INFO, "Copied verification link.")
        new_verify_email.close()
        time.sleep(WAIT_DUR)
        log(PASS, "Emails recieved for old and new accounts after changing email address.")
        return True
    except IndexError:
        image_div(driver, "ERROR_verify_new_not_recieved")
        log(ERROR, "Verification email for new email not recieved; see 'ERROR_verify_new_not_recieved.png'!")
        return False
    except NoSuchElementException:
        driver.get(GUERRILLAMAIL)
        log(INFO, "Couldn't access expected parts of email. Refresh page to cleanup.")
        time.sleep(WAIT_DUR)
        log(ERROR, "Couldn't access new email verification link in email!")
        return False
