import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import sign_up_to_isaac
from ..utils.i_selenium import assert_tab
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["signup_uppercase"]


#####
# Test : Signup Email Case Sensitivity
#####
@TestWithDependency("SIGNUP_UPPERCASE", ["LOGIN", "SIGNUP"])
def signup_uppercase(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if users can sign up with the uppercase form of an already existing email.

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
        login_tab = driver.find_element_by_id("login-tab")
        login_tab.click()
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't access login tab; can't continue!")
        return False
    try:
        log(INFO, "Try to sign up with uppercase version of already used email.")
        assert not sign_up_to_isaac(driver, Users.Guerrilla.email.upper(), Users.Guerrilla.firstname, Users.Guerrilla.lastname, Users.Guerrilla.password, suppress=True, wait_dur=WAIT_DUR)
        wait_for_xpath_element(driver, "//h4[contains(text(), 'Registration Failed')]/span[contains(text(), 'An account already exists with the e-mail address')]")
        time.sleep(WAIT_DUR)
        log(INFO, "Couldn't sign up, as expected.")
        driver.get(ISAAC_WEB)
        log(INFO, "Got: %s" % ISAAC_WEB)
        time.sleep(WAIT_DUR)
        log(PASS, "Cannot sign up with uppercase form of existing email.")
        return True
    except TimeoutException:
        log(ERROR, "Sign up with uppercase password failed with wrong error message!")
        return False
    except AssertionError:
        log(ERROR, "Sign up successful despite being uppercase form of existing account!")
        return False
