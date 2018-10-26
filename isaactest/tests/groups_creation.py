import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form
from ..utils.i_selenium import assert_tab
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException

__all__ = ["groups_creation"]


#####
# Test : Create groups As Users
#####
@TestWithDependency("GROUPS_CREATION", ["LOGIN", "LOGOUT", "GROUPS_PAGE_ACCESS"])
def groups_creation(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if eligible users can create groups.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)

    group_creation_fail = False

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
            site_groups_link = driver.find_element_by_xpath("//a[@ui-sref='groups']")
            site_groups_link.click()
            time.sleep(WAIT_DUR)
            group_editor = driver.find_element_by_xpath("//div[@class='panel ng-scope']")
            group_name = group_editor.find_element_by_xpath(".//input[@ng-model='newGroup.groupName']")
            group_name.clear()
            group_name.send_keys("testGroup")
            log(INFO, "Entered 'testGroup' as the group name.")
            time.sleep(WAIT_DUR)
            creation_button = group_editor.find_element_by_xpath("(.//a[contains(@ng-click, 'saveGroup(selectedGroup != null)')])")
            creation_button.click()
            time.sleep(WAIT_DUR)
        except NoSuchElementException:
            group_creation_fail = True
            log(ERROR, "Can't create the group 'testGroup' for %s; can't continue!" % i_type)
            return False
        group_modal = driver.find_element_by_id('isaacModal')
        group_modal_button = group_modal.find_element_by_class_name('close-reveal-modal')
        group_modal_button.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Created group named 'testGroup' for %s." % i_type)
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logged out '%s' user." % i_type)
        time.sleep(WAIT_DUR)

    if not group_creation_fail:
        log(PASS, "Creating the group 'testGroup' works for expected types.")
        return True
    else:
        return False
