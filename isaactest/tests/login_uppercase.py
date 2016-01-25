import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form, assert_logged_in
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException

__all__ = ["login_uppercase"]


#####
# Test : Login Email Case Sensitivity
#####
@TestWithDependency("LOGIN_UPPERCASE", ["LOGIN"])
def login_uppercase(driver, Users, ISAAC_WEB, WAIT_DUR):
    """Test if users can login with a case insensitive email address.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)
    try:
        login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
        login_tab.click()
        submit_login_form(driver, Users.Student.email.upper(), Users.Student.password, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't access login tab; can't continue!")
        return False
    try:
        assert_logged_in(driver, Users.Student, wait_dur=WAIT_DUR)
        log(INFO, "Login successful.")
        log(PASS, "Login using uppercase version of email successful.")
        return True
    except AssertionError:
        log(INFO, "Login failed!")
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Can't login with uppercase email; see 'ERROR_logging_in_uppercase.png'!")
        return False
