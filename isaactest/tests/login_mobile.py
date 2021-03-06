import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import MobileIsaac, submit_login_form, assert_logged_in, snooze_email_verification
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException

__all__ = ["login_mobile"]


#####
# Test : Logging In (Mobile Devices)
#####
@TestWithDependency("LOGIN_MOBILE", ["LOGOUT", "ACCEPT_COOKIES"])
def login_mobile(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether users can sign in to Isaac on mobile devices.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)

    with MobileIsaac(driver) as mobile_driver:

        time.sleep(WAIT_DUR)
        # The Email Verification warning obstructs the menu. If it's there, snooze it!
        if not snooze_email_verification(mobile_driver):
            log(ERROR, "Can't continue with this test since the banner obstructs the menu!")
            return False

        try:
            login_tab = mobile_driver.find_element_by_xpath("//div[@id='mobile-login']")
            login_tab.click()
            time.sleep(WAIT_DUR)
            submit_login_form(mobile_driver, user=Users.Student, wait_dur=WAIT_DUR, mobile=True)
            time.sleep(WAIT_DUR)
            assert_logged_in(mobile_driver, user=Users.Student, wait_dur=WAIT_DUR)
            log(INFO, "Login succeeded on mobile site.")
        except NoSuchElementException:
            image_div(mobile_driver, "ERROR_mobile_login")
            log(ERROR, "Cannot find mobile login button. See 'ERROR_mobile_login.png'!")
            return False
        except AssertionError:
            log(ERROR, "Failed to log in on mobile!")
            return False

    log(PASS, "Mobile login works as expected!")
    return True
