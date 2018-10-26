import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form, assert_logged_in
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException

__all__ = ["set_assignments_page_access"]


#####
# Test : Access set_assignments Page As Users
#####
@TestWithDependency("SET_ASSIGNMENTS_PAGE_ACCESS", ["LOGIN", "LOGOUT"])
def set_assignments_page_access(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test access set assignments page is suitably restricted.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)

    admin_access_fail = False

    try:
        log(INFO, "Test if logged out user can access '/set_assignments'.")
        driver.get(ISAAC_WEB + "/set_assignments")
        time.sleep(WAIT_DUR)
        url_redirected = ("/login?target=%2Fset_assignments" in driver.current_url) or ("/login?target=~2Fset_assignments" in driver.current_url)
        assert url_redirected, "Expected '/login?target=%2Fset_assignemnts' (or '~2Fset_assignments') in URL, found '%s'!" % driver.current_url
        log(INFO, "Logged out users can't access set assignments page.")
        time.sleep(WAIT_DUR)
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logging out to start from same initial page each time.")
        time.sleep(WAIT_DUR)
    except AssertionError, e:
        admin_access_fail = True
        image_div(driver, "ERROR_unexpected_set_assignment_access")
        log(INFO, e.message)
        log(ERROR, "Logged out user accessed '/set_assignments'; see 'ERROR_unexpected_set_assignments_access.png'!")

    access_cases = [("Student", Users.Student)]
    for i_type, user in access_cases:
        log(INFO, "Test if '%s' users can access set_assignments page." % i_type)
        try:
            driver.get(ISAAC_WEB + "/set_assignments")
            time.sleep(WAIT_DUR)
            submit_login_form(driver, user=user, wait_dur=WAIT_DUR)
            time.sleep(WAIT_DUR)
            assert_logged_in(driver, user, wait_dur=WAIT_DUR)
            wait_for_xpath_element(driver, "//h1[text()='Unauthorised']")
            log(INFO, "User of type '%s' can't access set assignments page." % i_type)
        except TimeoutException:
            admin_access_fail = True
            image_div(driver, "ERROR_unexpected_set_assignments_access")
            log(ERROR, "User of type '%s' accessed '/set_assignments'; see 'ERROR_unexpected_assignments_access.png'!")
        except AssertionError:
            log(ERROR, "Couldn't log user in to test '/set_assignments' access!")
            return False
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logged out '%s' user." % i_type)
        time.sleep(3)

    access_cases = [("Teacher", Users.Teacher), ("Content Editor", Users.Editor), ("Event Manager", Users.Event), ("Admin", Users.Admin)]
    for i_type, user in access_cases:
        driver.get(ISAAC_WEB + "/login")
        log(INFO, "Got '%s'. As '%s', try to use global nav." % (ISAAC_WEB + "/login", i_type))
        time.sleep(WAIT_DUR)
        try:
            submit_login_form(driver, user=user, wait_dur=WAIT_DUR)
            time.sleep(WAIT_DUR)
            global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
            global_nav.click()
            time.sleep(WAIT_DUR)
            set_assignments_page_link = driver.find_element_by_xpath("//a[@href='/set_assignments']")
            set_assignments_page_link.click()
            time.sleep(WAIT_DUR)
            wait_for_xpath_element(driver, "//h1[text()='Set Assignments']")
            time.sleep(WAIT_DUR)
            log(INFO, "'%s' users can access '/set_assignments'." % i_type)
        except TimeoutException:
            admin_access_fail = True
            image_div(driver, "ERROR_no_set_assignments_access")
            log(ERROR, "'%s' user can't access '/set_assignments'; see 'ERROR_no_set_assignments_access.png'!" % i_type)
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logged out '%s' user." % i_type)
        time.sleep(3)

    if not admin_access_fail:
        log(PASS, "Access to set assignments page restricted appropriately.")
        return True
    else:
        return False
