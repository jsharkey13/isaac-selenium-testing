import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form, assert_logged_in
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException

__all__ = ["groups_page_access"]


#####
# Test : Access Groups Page As Users
#####
@TestWithDependency("GROUPS_PAGE_ACCESS", ["LOGIN", "LOGOUT"])
def groups_page_access(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test access to groups page is suitably restricted.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)

    groups_page_access_fail = False

    try:
        log(INFO, "Test if logged out user can access '/groups'.")
        driver.get(ISAAC_WEB + "/groups")
        time.sleep(WAIT_DUR)
        url_redirected = ("/login?target=%2Fgroups" in driver.current_url) or ("/login?target=~2Fgroups" in driver.current_url)
        assert url_redirected, "Expected '/login?target=%2Fgroups' (or '~2Fgroups') in URL, found '%s'!" % driver.current_url
        log(INFO, "Logged out users can't access groups page.")
        time.sleep(WAIT_DUR)
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logging out to start from same initial page each time.")
        time.sleep(WAIT_DUR)
    except AssertionError, e:
        groups_page_access_fail = True
        image_div(driver, "ERROR_unexpected_groups_access")
        log(INFO, e.message)
        log(ERROR, "Logged out user accessed '/groups'; see 'ERROR_unexpected_groups_access.png'!")

    student_login = [("Student", Users.Student)]
    for i_type, user in student_login:
        log(INFO, "Test if '%s' users can access groups page." % i_type)
        try:
            driver.get(ISAAC_WEB + "/groups")
            time.sleep(WAIT_DUR)
            submit_login_form(driver, user=user, wait_dur=WAIT_DUR)
            time.sleep(WAIT_DUR)
            assert_logged_in(driver, user, wait_dur=WAIT_DUR)
            wait_for_xpath_element(driver, "//h1[text()='Unauthorised']")
            log(INFO, "User of type '%s' can't access groups page." % i_type)
        except TimeoutException:
            groups_page_access_fail = True
            image_div(driver, "ERROR_unexpected_groups_access")
            log(ERROR, "User of type '%s' accessed '/groups'; see 'ERROR_unexpected_groups_access.png'!")
        except AssertionError:
            log(ERROR, "Couldn't log user in to test '/groups' access!")
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
            site_admin_link = driver.find_element_by_xpath("//a[@ui-sref='groups']")
            site_admin_link.click()
            time.sleep(WAIT_DUR)
            wait_for_xpath_element(driver, "//h1[text()='Manage Groups']")
            time.sleep(WAIT_DUR)
            log(INFO, "'%s' users can access '/groups'." % i_type)
        except TimeoutException:
            groups_page_access_fail = True
            image_div(driver, "ERROR_no_admin_access")
            log(ERROR, "'%s' user can't access '/groups'; see 'ERROR_no_groups_access.png'!" % i_type)
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logged out '%s' user." % i_type)
        time.sleep(3)

    if not groups_page_access_fail:
        log(PASS, "Access to groups page restricted appropriately.")
        return True
    else:
        return False
