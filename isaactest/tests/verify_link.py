import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, new_tab, close_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["verify_link"]


#####
# Test : Verification Link Works
#####
@TestWithDependency("VERIFY_LINK", ["RECIEVE_VERIFY_EMAILS"])
def verify_link(driver, inbox, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR, **kwargs):
    """Test if the verification link from the verification emails works.

        - 'driver' should be a Selenium WebDriver.
        - 'inbox' should be a GuerrillaInbox object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'GUERRILLAMAIL' is the string URL of GuerrillaMail.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, GUERRILLAMAIL)
    log(INFO, "About to check latest verification link works.")
    try:
        verification_email = inbox.get_by_subject("Verify your email")[0]
        verification_email.view()
        log(INFO, "Selecting most recent email '%s'." % verification_email)
        time.sleep(WAIT_DUR)
        email_body = verification_email.get_email_body_element()
        verification_link = email_body.find_element_by_xpath(".//a[text()='Verify your email address']")
        verification_url = str(verification_link.get_attribute("href")).replace("https://localhost:8080/isaac-api", ISAAC_WEB)
        time.sleep(WAIT_DUR)
        verification_email.close()
        time.sleep(WAIT_DUR)
        new_tab(driver)
        log(INFO, "Opening verification link from email in new tab.")
        driver.get(verification_url)
        assert_tab(driver, ISAAC_WEB + "/verifyemail")
        log(INFO, "Verification URL: '%s'." % driver.current_url)
        wait_for_xpath_element(driver, "//h2[@ng-if='verificationState==verificationStates.SUCCESS']")
        close_tab(driver)
        log(PASS, "Email address verified successfully.")
        time.sleep(WAIT_DUR)
        return True
    except TimeoutException:
        image_div(driver, "ERROR_verification_status")
        log(ERROR, "Verification Failed; see 'ERROR_verification_status.png'!")
        return False
    except IndexError:
        log(ERROR, "No verification emails recieved! Can't continue.")
        return False
    except NoSuchElementException:
        log(ERROR, "Can't access verification link in email; can't continue!")
        return False
