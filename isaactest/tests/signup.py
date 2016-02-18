import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import sign_up_to_isaac
from ..utils.i_selenium import assert_tab
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException

__all__ = ["signup"]


#####
# Test : Sign Up to Isaac
#####
@TestWithDependency("SIGNUP", ["LOGIN", "LOGOUT"])
def signup(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether users can sign up to Isaac using an email address.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)

    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        login_tab = driver.find_element_by_id("login-tab")
        login_tab.click()
    except NoSuchElementException:
        log(ERROR, "Can't find login button; can't continue!")
        return False
    time.sleep(WAIT_DUR)
    if sign_up_to_isaac(driver, user=Users.Guerrilla, wait_dur=WAIT_DUR):
        log(PASS, "Successfully register new user '%s' on Isaac." % Users.Guerrilla.email)
        return True
    else:
        log(ERROR, "Can't register user!")
        return False
