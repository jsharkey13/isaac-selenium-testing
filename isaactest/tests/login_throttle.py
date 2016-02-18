import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException

__all__ = ["login_throttle"]


#####
# Test : 11 Login Attempts
#####
@TestWithDependency("LOGIN_THROTTLE", ["LOGIN"])
def login_throttle(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether users are locked out after 10 failed login attempts.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    try:
        login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
        login_tab.click()
        log(INFO, "Clicked login tab. Now incorrectly submit login form eleven times.")
    except NoSuchElementException:
        log(ERROR, "Couldn't find login button; can't continue!")
        return False
    for i in range(11):
        submit_login_form(driver, username=Users.Student.email, password="wrongpassword", wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
    try:
        driver.find_element_by_xpath("//strong[contains(text(), 'too many attempts to login')]")
        log(PASS, "11 login attempts. Warning message and locked out for 10 mins.")
        return True
    except NoSuchElementException:
        image_div(driver, "11_login_attempts")
        log(ERROR, "Tried to log in 11 times. No error message; see '11_login_attempts.png'!")
        return False
