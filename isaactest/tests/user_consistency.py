import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form, assert_logged_in
from ..utils.i_selenium import assert_tab, new_tab, close_tab
from ..tests import TestWithDependency

__all__ = ["user_consistency"]


#####
# Test : User Consistency
#####
@TestWithDependency("USER_CONSISTENCY", ["LOGIN"])
def user_consistency(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test that users remain logged in in new tabs.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)

    submit_login_form(driver, user=Users.Student, wait_dur=WAIT_DUR)
    time.sleep(WAIT_DUR)

    try:
        assert_logged_in(driver, Users.Student, wait_dur=WAIT_DUR)
        log(INFO, "Login successful.")
    except AssertionError:
        log(INFO, "Login failed!")
        log(ERROR, "Can't login to continue testing user consistency!")
        return False

    new_tab(driver)
    driver.get(ISAAC_WEB)
    log(INFO, "Got: %s." % ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        assert_logged_in(driver, Users.Student, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
        log(PASS, "User still logged in in new tab.")
        return True
    except AssertionError:
        close_tab(driver)
        time.sleep(WAIT_DUR)
        log(ERROR, "User not still logged in in new tab; can't test user consistency!")
        return False
