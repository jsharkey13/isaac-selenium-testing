import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_invisible_xpath, wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotVisibleException
from selenium.webdriver.support.ui import Select

__all__ = ["user_role_change"]


#####
# Test : User Search as Admin
#####
@TestWithDependency("USER_ROLE_CHANGE")#, ["ADMIN_USER_SEARCH"])
def user_role_change(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if user roles can be changed.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out logged in user.")
    time.sleep(WAIT_DUR)
    log(INFO, "Test user role change as Event Manager from User Manager.")
    driver.get(ISAAC_WEB + "/admin/usermanager")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/admin/usermanager"))
    time.sleep(WAIT_DUR)
    try:
        assert submit_login_form(driver, user=Users.Event, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
    except AssertionError:
        log(ERROR, "Can't access User Manager; can't continue testing!")
        return False

    # Search for user:
    try:
        log(INFO, "Find the 'Test Student' user.")
        name_field = driver.find_element_by_id("user-search-familyName")
        name_field.send_keys(Users.Student.lastname)
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't find 'familyName' search box; can't continue testing!")
        return False
    try:
        search_button = driver.find_elements_by_xpath("//button[@type='submit']")[0]
        search_button.click()
        wait_for_invisible_xpath(driver, "//h3[contains(text(), 'Manage Users ()')]")
        user_select_box = driver.find_element_by_xpath("//table//tr/td[text()='%s']/../td[1]/input" % Users.Student.email)
        log(INFO, "Select the 'Test Student' user.")
        user_select_box.click()
        time.sleep(WAIT_DUR)
    except TimeoutException:
        log(ERROR, "Search button did not work; can't continue testing!")
        return False
    except NoSuchElementException:
        log(ERROR, "Can't find tick box for the user; can't continue testing!")
        return False
    except IndexError:
        log(ERROR, "Can't find the 'Search' button; can't continue!")
        return False

    # Promote user:
    try:
        elevate_dropdown = driver.find_element_by_xpath("//a[@data-dropdown='elevateDropdown']")
        elevate_dropdown.click()
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't find elevate dropdown menu; can't continue!")
        return False
    try:
        elevate_button = elevate_dropdown.find_element_by_xpath("./..//a[contains(@ng-click,'TEACHER')]")
        elevate_button.click()
        log(INFO, "Click the promote to 'Teacher' button.")
        time.sleep(WAIT_DUR)
        #
        alert = driver.switch_to.alert
        alert_text = alert.text
        log(INFO, "Alert, with message: '%s'." % alert_text)
        expected = "Are you really sure you want to promote unverified user: (%s)?" % Users.Student.email
        assert expected in alert_text, "Alert contained unexpected message '%s'!" % alert_text
        alert.accept()
        log(INFO, "Accepted the alert.")
        time.sleep(WAIT_DUR)
        #
        driver.find_elements_by_xpath("//table//tr/td[text()='%s']/../td[contains(text(),'TEACHER')]" % Users.Student.email)[0]
        # Do something odd here: we need to ensure no error message is displayed. Wait for one, and use the
        # Timeout exception to indicate success!
        err = wait_for_xpath_element(driver, "//div[@class='toast-message']/p", WAIT_DUR)
        log(ERROR, "Error message displayed: '%s'! Can't continue!" % err.text)
        return False
    except TimeoutException:
        log(INFO, "Succesfully promoted user to Teacher status.")
    except (NoSuchElementException, ElementNotVisibleException):
        log(ERROR, "Can't elevate user to teacher; did the dropdown menu open correctly? See 'ERROR_event_manager_elevate_user.png'!")
        image_div(driver, "ERROR_event_manager_elevate_user")
        return False
    except IndexError:
        log(ERROR, "Elevation appears to have failed. See 'ERROR_event_manager_elevate_user.png'!")
        image_div(driver, "ERROR_event_manager_elevate_user")
        return False

    # Demote user:
    try:
        user_select_box = driver.find_elements_by_xpath("//table//tr/td[text()='%s']/../td[1]/input" % Users.Student.email)[0]
        log(INFO, "Select the 'Test Student' user again.")
        user_select_box.click()
        time.sleep(WAIT_DUR)
        elevate_dropdown = driver.find_element_by_xpath("//a[@data-dropdown='demoteDropdown']")
        elevate_dropdown.click()
        time.sleep(WAIT_DUR)
    except IndexError:
        log(ERROR, "Can't find tick box for the user; can't continue testing! 'Test Student' must be fixed by hand!")
        return False
    except NoSuchElementException:
        log(ERROR, "Can't find demote dropdown menu; can't continue! 'Test Student' must be fixed by hand!")
        return False
    try:
        elevate_button = elevate_dropdown.find_element_by_xpath("./..//a[contains(@ng-click,'STUDENT')]")
        elevate_button.click()
        log(INFO, "Click the demote to 'Student' button.")
        time.sleep(WAIT_DUR)
        driver.find_elements_by_xpath("//table//tr/td[text()='%s']/../td[contains(text(),'STUDENT')]" % Users.Student.email)[0]
        # Do something odd here: we need to ensure no error message is displayed. Wait for one, and use the
        # Timeout exception to indicate success!
        err = wait_for_xpath_element(driver, "//div[@class='toast-message']/p", WAIT_DUR)
        log(ERROR, "Error message displayed: '%s'! Can't continue!" % err.text)
        return False
    except TimeoutException:
        log(INFO, "Succesfully demoted user back to Student status.")
    except (NoSuchElementException, ElementNotVisibleException):
        log(ERROR, "Can't demote user to student; did the dropdown menu open correctly? See 'ERROR_event_manager_elevate_user.png'!")
        image_div(driver, "ERROR_event_manager_elevate_user")
        return False
    except IndexError:
        log(ERROR, "Demotion appears to have failed. 'Test Student' must be fixed by hand! See 'ERROR_event_manager_elevate_user.png'!")
        image_div(driver, "ERROR_event_manager_elevate_user")
        return False

    # Now test as an Admin user by going to profile:
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out logged in user.")
    time.sleep(WAIT_DUR)
    log(INFO, "Test user role change as Admin from user's Account page.")
    driver.get(ISAAC_WEB + "/admin/usermanager")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/admin/usermanager"))
    time.sleep(WAIT_DUR)
    try:
        assert submit_login_form(driver, user=Users.Admin, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
    except AssertionError:
        log(ERROR, "Can't access User Manager; can't continue testing!")
        return False

    try:
        log(INFO, "Find the 'Test Student' user.")
        name_field = driver.find_element_by_id("user-search-familyName")
        name_field.send_keys(Users.Student.lastname)
        time.sleep(WAIT_DUR)
        search_button = driver.find_elements_by_xpath("//button[@type='submit']")[0]
        search_button.click()
        wait_for_invisible_xpath(driver, "//h3[contains(text(), 'Manage Users ()')]")
        user_edit_button = driver.find_element_by_xpath("//table//tr/td[text()='%s']/../td[2]/a[2]" % Users.Student.email)
        edit_url = user_edit_button.get_attribute("href")
        driver.get(edit_url)
        log(INFO, "Editing the 'Test Student' user: got '%s'." % edit_url)
        time.sleep(WAIT_DUR)
    except TimeoutException:
        log(ERROR, "Search button did not work; can't continue testing!")
        return False
    except NoSuchElementException:
        log(ERROR, "Can't find edit button for the user; can't continue testing!")
        return False
    except IndexError:
        log(ERROR, "Can't find the 'Search' button; can't continue!")
        return False

    try:
        log(INFO, "Attempt to change role to Content Editor.")
        user_role = Select(driver.find_element_by_xpath("//select[@ng-model='user.role']"))
        time.sleep(WAIT_DUR)
        assert user_role.first_selected_option.get_attribute("value") == "STUDENT"
        user_role.select_by_value("CONTENT_EDITOR")
        time.sleep(WAIT_DUR)
        save_button = driver.find_elements_by_xpath("//a[contains(@ng-click, 'save')]")[0]
        save_button.click()
        wait_for_invisible_xpath(driver, "//h1[contains(text(), 'Manage another user')]")
        time.sleep(WAIT_DUR)
        log(INFO, "Successfully changed user role. Sent to '%s'." % driver.current_url)
    except NoSuchElementException:
        log(ERROR, "Can't find role dropdown; can't change role or continue!")
        return False
    except IndexError:
        log(ERROR, "Can't find 'Save' button; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_admin_role_change")
        log(ERROR, "Can't change user role; see 'ERROR_admin_role_change.png'!")
        return False
    except AssertionError:
        log(ERROR, "User was not a Student to begin with! Something is very wrong!")
        return False

    try:
        driver.get(edit_url)
        log(INFO, "Fixing the 'Test Student' user: got '%s'." % edit_url)
        time.sleep(WAIT_DUR)
        log(INFO, "Attempt to change role back to Student.")
        user_role = Select(driver.find_element_by_xpath("//select[@ng-model='user.role']"))
        time.sleep(WAIT_DUR)
        role = user_role.first_selected_option.get_attribute("value")
        assert role == "CONTENT_EDITOR", "Expected user to be a 'CONTENT_EDITOR', found '%s'!" % role
        user_role.select_by_value("STUDENT")
        time.sleep(WAIT_DUR)
        save_button = driver.find_elements_by_xpath("//a[contains(@ng-click, 'save')]")[0]
        save_button.click()
        wait_for_invisible_xpath(driver, "//h1[contains(text(), 'Manage another user')]")
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't find role dropdown; can't change role or continue! 'Test Student' must be fixed by hand!")
        return False
    except IndexError:
        log(ERROR, "Can't find 'Save' button; can't continue! 'Test Student' must be fixed by hand!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_admin_role_change")
        log(ERROR, "Can't restore user role; see 'ERROR_admin_role_change.png'! 'Test Student' must be fixed by hand!")
        return False
    except AssertionError, e:
        log(ERROR, e.message)

    log(PASS, "User role change functionality as expected.")
    return True
