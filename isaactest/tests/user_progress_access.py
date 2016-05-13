import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form, assert_logged_in
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException

__all__ = ["user_progress_access"]


#####
# Test : Access Users Progress Page
#####
@TestWithDependency("USER_PROGRESS_ACCESS", ["LOGIN", "LOGOUT"])
def user_progress_access(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test access to user progress page is suitably restricted.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)

    progress_access_fail = False

    try:
        log(INFO, "Test if logged out user can access '/progress/1'.")
        driver.get(ISAAC_WEB + "/progress/1")
        time.sleep(WAIT_DUR)
        assert "/login?target=%2Fprogress%2F1" in driver.current_url
        log(INFO, "Logged out users can't access progress pages.")
        time.sleep(WAIT_DUR)
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logging out to start from same initial page each time.")
        time.sleep(WAIT_DUR)
    except AssertionError:
        progress_access_fail = True
        image_div(driver, "ERROR_unexpected_admin_access")
        log(ERROR, "Logged out user may have accessed '/progress/1'; see 'ERROR_unexpected_admin_access.png'!")

    access_cases = [("Student", Users.Student), ("Teacher", Users.Teacher), ("Content Editor", Users.Editor), ("Event Manager", Users.Event)]
    for i_type, user in access_cases:
        log(INFO, "Test if '%s' users can access another users progress page." % i_type)
        try:
            driver.get(ISAAC_WEB + "/progress/1")
            time.sleep(WAIT_DUR)
            submit_login_form(driver, user=user, wait_dur=WAIT_DUR)
            time.sleep(WAIT_DUR)
            assert_logged_in(driver, user, wait_dur=WAIT_DUR)
            log(INFO, "Try loading progress page; no errors will be shown but have to wait to see if data loads.")
            # Oddly, we now *want* a TimeoutException for success; it should load endlessly
            wait_for_invisible_xpath(driver, "//div[@loading-overlay]", 30)
            # If we don't get a TimeoutException, then things have gone wrong
            progress_access_fail = True
            log(ERROR, "User of type '%s' accessed another users progress page!" % i_type)
        except TimeoutException:
            log(INFO, "'%s' users given endless loading screen as expected; can't access page." % i_type)
            driver.get(ISAAC_WEB + "/logout")
            log(INFO, "Logged out '%s' user." % i_type)
            time.sleep(WAIT_DUR)
            continue
        except AssertionError:
            log(ERROR, "Couldn't log user in to test '/progress/1' access!")
            return False
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logged out '%s' user." % i_type)
        time.sleep(WAIT_DUR)

    access_cases = [("Admin", Users.Admin)]
    for i_type, user in access_cases:
        log(INFO, "Test if '%s' users can access another users progress page." % i_type)
        try:
            driver.get(ISAAC_WEB + "/progress/1")
            time.sleep(WAIT_DUR)
            submit_login_form(driver, user=user, wait_dur=WAIT_DUR)
            time.sleep(WAIT_DUR)
            assert_logged_in(driver, user, wait_dur=WAIT_DUR)
            title = str(wait_for_xpath_element(driver, "(//h1)[1]").text)
            title = title.strip()
            assert len(title) > len("Progress for user:"), "Title is '%s', expected 'Progress for user: [name]'!"
            wait_for_xpath_element(driver, "//div[@d3-plot]//ul[@class='d3-plot-key']")
            time.sleep(WAIT_DUR)
            log(INFO, "'%s' users can access '/progress/1' as expected." % i_type)
        except TimeoutException:
            progress_access_fail = True
            image_div(driver, "ERROR_no_admin_access")
            log(ERROR, "'%s' user can't access '/progress/1'; see 'ERROR_no_admin_access.png'!" % i_type)
        except AssertionError, e:
            progress_access_fail = True
            image_div(driver, "ERROR_no_admin_access")
            log(ERROR, "Error accessing other user progress: %s See 'ERROR_no_admin_access.png'!" % e.message)
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logged out '%s' user." % i_type)
        time.sleep(3)

    if not progress_access_fail:
        log(PASS, "Access to another users progress page restricted appropriately.")
        return True
    else:
        log(ERROR, "Access not appropriately restricted! Fail!")
        return False
