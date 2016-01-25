import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import assert_logged_out
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException

__all__ = ["logout"]


#####
# Test : Logout Button
#####
@TestWithDependency("LOGOUT", ["LOGIN", "GLOBAL_NAV"])
def logout(driver, ISAAC_WEB, WAIT_DUR):
    """Test whether users can sign out of Isaac.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    try:
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        time.sleep(WAIT_DUR)
        logout_button = driver.find_element_by_xpath("//a[@ui-sref='logout']")
        logout_button.click()
    except NoSuchElementException:
        image_div(driver, "ERROR_logout_failure")
        log(ERROR, "Can't find logout button; can't logout, see 'ERROR_logout_failure.png'!")
        return False
    time.sleep(WAIT_DUR)
    try:
        assert_logged_out(driver, wait_dur=WAIT_DUR)
        log(INFO, "Logged out.")
        log(PASS, "Log out button works.")
        return True
    except AssertionError:
        image_div(driver, "ERROR_logout_failure")
        log(ERROR, "Couldn't logout; see 'ERROR_logout_failure.png'!")
        return False
