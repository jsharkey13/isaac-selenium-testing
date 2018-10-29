import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["req_verify_emails"]


######
# Test : Request Verification Emails
######
@TestWithDependency("REQ_VERIFY_EMAILS", ["SIGNUP"])
def req_verify_emails(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test the behavior on requesting more email verification emails.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        request_verify_email = driver.find_element_by_xpath("//a[@ng-click='requestEmailVerification()']")
    except NoSuchElementException:
        log(ERROR, "Can't access verification request link in banner; can't continue! Are we logged in?")
        return False

    email_verification_popup_shown_yet = False
    verify_popup_xpath = "//div[@class='toast-message']/h4[@class='ng-binding']"
    verification_email_request_limit = 4
    verification_requests = 0
    try:
        for i in range(verification_email_request_limit + 1):
            log(INFO, "Clicking request email verification link.")
            request_verify_email.click()
            popup = wait_for_xpath_element(driver, verify_popup_xpath)
            popup_text = popup.text
            image_div(driver, "email_verification_request_popup_%s" % i)
            email_verification_popup_shown_yet = True
            wait_for_invisible_xpath(driver, verify_popup_xpath)
            email_verification_popup_shown_yet = False
            time.sleep(WAIT_DUR + 10)
            if i <= verification_email_request_limit - 1:  # i starts from 0, not 1
                assert popup_text == "Email verification request succeeded."
                log(INFO, "Success message shown.")
                verification_requests += 1
            else:
                if popup_text == "Email verification request failed.":
                    log(INFO, "Error message shown as expected.")
                    log(PASS, "Email verification link shows warning on 5th click, success on others.")
                    return True
                else:
                    log(ERROR, "Popup text was: '%s'!" % popup_text)
                    log(ERROR, "Warning not shown after %s requests!" % verification_requests)
                    return False
    except TimeoutException:
        if email_verification_popup_shown_yet:
            log(ERROR, "Verification Popup didn't close; see 'email_verification_request_popup.png'!")
            return False
        else:
            log(ERROR, "Verification Popup didn't appear!")
            return False
    except AssertionError:
        log(ERROR, "Success text not shown on request %s!" % (verification_requests + 1))
        return False
