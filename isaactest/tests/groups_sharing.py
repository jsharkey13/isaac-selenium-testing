import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form, assert_logged_in
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["groups_sharing"]


#####
# Test : Access Admin Page As Users
#####
@TestWithDependency("GROUPS_SHARING", ["LOGIN", "LOGOUT", "GROUPS_CREATION"])
def groups_sharing(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
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

    group_sharing_fail = False

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
            selected_group = driver.find_element_by_class_name('group-nav-header ng-binding')
            selected_group.click()
            edit_group = driver.find_element_by_class_name('access-token')
            edit_group.click()
            # log(INFO, "Found the group creation box.")
            # group_name = group_editor.find_element_by_xpath(".//input[@ng-model='newGroup.groupName']")
            # group_name.clear()
            # group_name.send_keys("testGroup")
            # log(INFO, "Entered value 'testGroup'.")
            # time.sleep(WAIT_DUR)
            # creation_button = group_editor.find_element_by_xpath("(.//a[contains(@ng-click, 'saveGroup(selectedGroup != null)')])")
            # creation_button.click()
            # time.sleep(WAIT_DUR)
        except NoSuchElementException:
            group_sharing_fail = True
            log(ERROR, "Can't find the Create button; can't continue!")
            return False
        #popup = WebDriverWait(driver, WAIT_DUR).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='close-reveal-modal']")))
        # group_modal = driver.find_element_by_id('isaacModal')
        # group_modal_button = group_modal.find_element_by_class_name('close-reveal-modal')
        # # group_modal = driver.find_element_by_xpath(".//div[@id='isaacModal']")
        # group_modal_button.click()
        # time.sleep(WAIT_DUR)
        # log(INFO, "Created group named 'testGroup' for %s." % i_type)
        # driver.get(ISAAC_WEB + "/logout")
        # log(INFO, "Logged out '%s' user." % i_type)
        # time.sleep(WAIT_DUR)

    if not group_sharing_fail:
        log(PASS, "Sharing the group 'testGroup' works.")
        return True
    else:
        return False
