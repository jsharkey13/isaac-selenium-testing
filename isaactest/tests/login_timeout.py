import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form, assert_logged_in
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency

__all__ = ["login_timeout"]


#####
# Test : 10 Minute Lockout
#####
@TestWithDependency("LOGIN_TIMEOUT", ["LOGIN_THROTTLE"])
def login_timeout(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether the login throttle lockout expires after 10 minutes.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    log(INFO, "Waiting for 10 minute timout to expire.")
    for i in range(10):
        log(INFO, "Still waiting. %s mins remaining." % (10 - i))
        time.sleep(60)
    time.sleep(10)
    log(INFO, "Finished waiting.")

    submit_login_form(driver, user=Users.Student)
    time.sleep(WAIT_DUR)
    try:
        assert_logged_in(driver, Users.Student, wait_dur=WAIT_DUR)
        log(INFO, "Login successful.")
        log(PASS, "Login after 10 minute lockout.")
        return True
    except AssertionError:
        log(INFO, "Login failed!")
        image_div(driver, "ERROR_login_after_lockout")
        log(ERROR, "Can't login after 10 minute lockout; see 'login_error.png'!")
        return False
