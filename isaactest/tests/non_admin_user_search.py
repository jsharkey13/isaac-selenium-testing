import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select

__all__ = ["non_admin_user_search"]


#####
# Test : Attempt to Use User Search as Non-Admin
#####
@TestWithDependency("NON_ADMIN_USER_SEARCH", ["ADMIN_USER_SEARCH"])
def non_admin_user_search(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if non-admin users can search for users in a restricted way.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    log(INFO, "Test user search page as non-admin.")

    roles = [Users.Student, Users.Teacher, Users.Editor, Users.Event]
    not_allowed = [Users.Student, Users.Teacher, Users.Editor]

    for role in roles:
        try:
            driver.get(ISAAC_WEB + "/logout")
            log(INFO, "Logging out logged in user.")
            time.sleep(WAIT_DUR)
            driver.get(ISAAC_WEB + "/admin/usermanager")
            log(INFO, "Got: %s" % (ISAAC_WEB + "/admin/usermanager"))
            time.sleep(WAIT_DUR)
            assert submit_login_form(driver, user=role, wait_dur=WAIT_DUR), "Can't login to access User Manager!"
            log(INFO, "Logged in '%s' successfully." % role)
            time.sleep(WAIT_DUR)
            if role in not_allowed:
                wait_for_xpath_element(driver, "//h1[text()='Unauthorised']")
                log(INFO, "User '%s' not allowed access as expected." % role)
                continue
            errors = driver.find_elements_by_xpath("//h1[text()='Unauthorised']")
            assert len(errors) == 0, "Unexpected 'Unauthorised' message shown!"
        except AssertionError, e:
            log(ERROR, e.message)
            return False
        except TimeoutException:
            log(ERROR, "User '%s' shouldn't be able to access User Manager, but no error message shown!")
            continue

        # Search by family name:
        try:
            log(INFO, "Test search by family name.")
            name_field = driver.find_element_by_id("user-search-familyName")
            name_field.send_keys(Users.Student.lastname)
            time.sleep(WAIT_DUR)
            search_button = driver.find_elements_by_xpath("//button[@ng-click='findUsers()']")[0]
            search_button.click()
            wait_for_invisible_xpath(driver, "//h3[contains(text(), 'Manage Users ()')]")
            expected_results = driver.find_elements_by_xpath("//table//tr/td[text()='%s']" % Users.Student.email)
            assert len(expected_results) == 1, "Expected 1 result searching for Test Student, got '%s'!" % len(expected_results)
            log(INFO, "Search by family name works as expected.")
            driver.refresh()
            log(INFO, "Refresh the page to clear all results.")
            time.sleep(WAIT_DUR)
        except TimeoutException:
            log(ERROR, "Search button did not work; can't continue testing!")
            return False
        except NoSuchElementException:
            log(ERROR, "Can't find 'familyName' search box; can't continue testing!")
            return False
        except IndexError:
            log(ERROR, "Can't find the 'Search' button; can't continue!")
            return False
        except AssertionError, e:
            log(ERROR, e.message)
            return False

        # Global wildcard search:
        try:
            log(INFO, "Test wildcard searches.")
            time.sleep(WAIT_DUR)
            search_button = driver.find_elements_by_xpath("//button[@ng-click='findUsers()']")[0]
            search_button.click()
            popup = wait_for_xpath_element(driver, "//div[@class='toast-message']", 2)
            error_title = str(popup.find_element_by_xpath(".//h4").text)
            error_text = str(popup.find_element_by_xpath(".//p").text)
            title = "User Search Failed"
            text = "You do not have permission to do wildcard searches."
            assert title in error_title, "Expected error popup with title '%s', got '%s'!" % (title, error_title)
            assert text in error_text, "Expected error popup to say '%s', got '%s'!" % (text, error_text)
            log(INFO, "Error message displayed with expected message.")
            log(INFO, "Wildcard search fails as expected.")
            driver.refresh()
            log(INFO, "Refresh the page to clear all results.")
            time.sleep(WAIT_DUR)
        except TimeoutException:
            image_div(driver, "ERROR_non_admin_user_search")
            log(ERROR, "Error message not shown; see 'ERROR_non_admin_user_search.png'!")
            return False
        except NoSuchElementException:
            log(ERROR, "Can't find message inside error popup; can't continue!")
            return False
        except IndexError:
            log(ERROR, "Can't find the 'Search' button; can't continue!")
            return False
        except AssertionError, e:
            log(ERROR, e.message)
            return False

        # Search by user type:
        try:
            log(INFO, "Test search by user role.")
            time.sleep(WAIT_DUR)
            role_dropdown = Select(driver.find_element_by_id("user-search-role"))
            time.sleep(WAIT_DUR)
            role_dropdown.select_by_value("STUDENT")
            log(INFO, "Selected role 'STUDENT'.")
            search_button = driver.find_elements_by_xpath("//button[@ng-click='findUsers()']")[0]
            search_button.click()
            popup = wait_for_xpath_element(driver, "//div[@class='toast-message']", 2)
            error_title = str(popup.find_element_by_xpath(".//h4").text)
            error_text = str(popup.find_element_by_xpath(".//p").text)
            title = "User Search Failed"
            text = "You do not have permission to do wildcard searches."
            assert title in error_title, "Expected error popup with title '%s', got '%s'!" % (title, error_title)
            assert text in error_text, "Expected error popup to say '%s', got '%s'!" % (text, error_text)
            log(INFO, "Error message displayed with expected message.")
            log(INFO, "Wildcard search fails as expected.")
            driver.refresh()
            log(INFO, "Refresh the page to clear all results.")
            time.sleep(WAIT_DUR)
        except TimeoutException:
            image_div(driver, "ERROR_non_admin_user_search")
            log(ERROR, "Error message not shown; see 'ERROR_non_admin_user_search.png'!")
            return False
        except NoSuchElementException:
            log(ERROR, "Can't find required elements; can't continue testing!")
            return False
        except IndexError:
            log(ERROR, "Can't find the 'Search' button; can't continue!")
            return False
        except AssertionError, e:
            log(ERROR, e.message)
            return False

    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out logged in user.")
    time.sleep(WAIT_DUR)
    log(PASS, "Search page functionality for non-admin users as expected.")
    return True
