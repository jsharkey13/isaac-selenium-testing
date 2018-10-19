import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException

__all__ = ["my_assignments_page_access"]


#####
# Test : Access my_assignments Page As Users
#####
@TestWithDependency("MY_ASSIGNMENTS_PAGE_ACCESS", ["LOGIN", "LOGOUT"])
def my_assignments_page_access(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test access to admin page is suitably restricted.

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
        log(INFO, "Test if logged out user can access '/assignments'.")
        driver.get(ISAAC_WEB + "/assignments")
        time.sleep(WAIT_DUR)
        url_redirected = ("/login?target=%2Fassignments" in driver.current_url) or ("/login?target=~2Fassignments" in driver.current_url)
        assert url_redirected, "Expected '/login?target=%2Fassignemnts' (or '~2Fassignments') in URL, found '%s'!" % driver.current_url
        log(INFO, "Logged out users can't access my assignments page.")
        time.sleep(WAIT_DUR)
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logging out to start from same initial page each time.")
        time.sleep(WAIT_DUR)
    except AssertionError, e:
        admin_access_fail = True
        image_div(driver, "ERROR_unexpected_my_assignment_access")
        log(INFO, e.message)
        log(ERROR, "Logged out user accessed '/assignments'; see 'ERROR_unexpected_set_assignments_access.png'!")

    access_cases = [("Student", Users.Student), ("Teacher", Users.Teacher), ("Content Editor", Users.Editor), ("Event Manager", Users.Event), ("Admin", Users.Admin)]
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
            site_admin_link = driver.find_element_by_xpath("//a[@href='/assignments']")
            site_admin_link.click()
            time.sleep(WAIT_DUR)
            wait_for_xpath_element(driver, "//h1[text()='My Assignments']")
            time.sleep(WAIT_DUR)
            log(INFO, "'%s' users can access '/assignments'." % i_type)
        except TimeoutException:
            admin_access_fail = True
            image_div(driver, "ERROR_no_my_assignments_access")
            log(ERROR, "'%s' user can't access '/assignments'; see 'ERROR_no_my_assignments_access.png'!" % i_type)
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logged out '%s' user." % i_type)
        time.sleep(3)

    if not admin_access_fail:
        log(PASS, "Access to my assignments page restricted appropriately.")
        return True
    else:
        return False
