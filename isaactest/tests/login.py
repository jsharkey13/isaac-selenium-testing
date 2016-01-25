import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form, assert_logged_in
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException

__all__ = ["login"]


#####
# Test : Logging In
#####
@TestWithDependency("LOGIN")
def login(driver, Users, ISAAC_WEB, WAIT_DUR):
    """Test whether users can sign in to Isaac.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    try:
        login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
        login_tab.click()
        submit_login_form(driver, user=Users.Student, disable_popup=False, wait_dur=WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Couldn't click login tab; can't login!")
        return False
    time.sleep(WAIT_DUR)
    try:
        assert_logged_in(driver, Users.Student, wait_dur=WAIT_DUR)
        log(INFO, "Login successful.")
        log(PASS, "Login using username and password successful.")
        return True
    except AssertionError:
        log(INFO, "Login failed!")
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Can't login; see 'ERROR_not_logging_in.png'!")
        return False
