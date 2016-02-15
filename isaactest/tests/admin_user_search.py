import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import Select

__all__ = ["admin_user_search"]


#####
# Test : Delete A User
#####
@TestWithDependency("ADMIN_USER_SEARCH")
def admin_user_search(driver, Users, ISAAC_WEB, WAIT_DUR):
    """Test if admin users can delete users.

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
    log(INFO, "Test user search page as admin.")
    driver.get(ISAAC_WEB + "/admin/usermanager")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/admin/usermanager"))
    time.sleep(WAIT_DUR)
    try:
        assert submit_login_form(driver, user=Users.Admin, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
    except AssertionError:
        log(ERROR, "Can't access User Manager; can't continue testing!")
        return False

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

    # Search by email address:
    try:
        log(INFO, "Test search by email address.")
        time.sleep(WAIT_DUR)
        email_field = driver.find_element_by_id("user-search-email")
        email_field.send_keys(Users.Teacher.email)
        time.sleep(WAIT_DUR)
        search_button = driver.find_elements_by_xpath("//button[@ng-click='findUsers()']")[0]
        search_button.click()
        wait_for_invisible_xpath(driver, "//h3[contains(text(), 'Manage Users ()')]")
        expected_results = driver.find_elements_by_xpath("//table//tr/td[text()='%s']" % Users.Teacher.email)
        assert len(expected_results) == 1, "Expected 1 result searching for Test Teacher, got '%s'!" % len(expected_results)
        log(INFO, "Search by email works as expected.")
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

    # Search by manually entered schools:
    try:
        log(INFO, "Test search by manually entered school name.")
        time.sleep(WAIT_DUR)
        school_dropdown = Select(driver.find_element_by_id("user-school-other"))
        time.sleep(WAIT_DUR)
        school_dropdown.select_by_value("A Manually Entered School")
        time.sleep(WAIT_DUR)
        search_button = driver.find_elements_by_xpath("//button[@ng-click='findUsers()']")[0]
        search_button.click()
        wait_for_invisible_xpath(driver, "//h3[contains(text(), 'Manage Users ()')]")
        expected_results = driver.find_elements_by_xpath("//table//tr/td[text()='%s']" % Users.Admin.email)
        assert len(expected_results) == 1, "Expected 1 result searching for Test Admin's 'Manually Entered School', got '%s'!" % len(expected_results)
        log(INFO, "Search by manual school works as expected.")
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

    # Search by school URN:
    try:
        log(INFO, "Test search by school URN.")
        time.sleep(WAIT_DUR)
        urn_field = driver.find_element_by_id("user-school-urn")
        urn_field.send_keys("133801")
        time.sleep(WAIT_DUR)
        search_button = driver.find_elements_by_xpath("//button[@ng-click='findUsers()']")[0]
        search_button.click()
        wait_for_invisible_xpath(driver, "//h3[contains(text(), 'Manage Users ()')]")
        expected_results = driver.find_elements_by_xpath("//table//tr/td[text()='%s']" % Users.Editor.email)
        assert len(expected_results) == 1, "Expected 1 result searching for Test Editor by School URN, got '%s'!" % len(expected_results)
        log(INFO, "Search by school URN works as expected.")
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
        text = str(driver.find_element_by_id("user-search-familyName").text)
        text += str(driver.find_element_by_id("user-search-email").text)
        text += str(driver.find_element_by_id("user-school-urn").text)
        assert text == "", "Expected form fields to be blank initially, got '%s'!" % text
        search_button = driver.find_elements_by_xpath("//button[@ng-click='findUsers()']")[0]
        search_button.click()
        wait_for_invisible_xpath(driver, "//div[@class='toast-message']/h4", 0.5)
        time.sleep(WAIT_DUR)
        results = driver.find_elements_by_xpath("//table//tr")
        assert len(results) > 40, "Expected at least 40 users, got '%s'!" % len(results)
        log(INFO, "Wildcard search works as expected.")
        driver.refresh()
        log(INFO, "Refresh the page to clear all results.")
        time.sleep(WAIT_DUR)
    except TimeoutException:
        image_div("ERROR_admin_user_search")
        log(ERROR, "Error message unexpectedly shown; see 'ERROR_admin_user_search.png'!")
        return False
    except NoSuchElementException:
        log(ERROR, "Can't find search boxes; can't continue testing!")
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
        search_button = driver.find_elements_by_xpath("//button[@ng-click='findUsers()']")[0]
        search_button.click()
        wait_for_invisible_xpath(driver, "//div[@class='toast-message']/h4", 0.5)
        time.sleep(WAIT_DUR)
        results = driver.find_elements_by_xpath("//table//tr/td[5]")
        for r in results:
            assert str(r.text) == "STUDENT", "Unexpected role '%s' in results for type 'STUDENT'; can't continue!" % r.text
        log(INFO, "Search by role works as expected.")
        driver.refresh()
        log(INFO, "Refresh the page to clear all results.")
        time.sleep(WAIT_DUR)
    except TimeoutException:
        image_div("ERROR_admin_user_search")
        log(ERROR, "Error message unexpectedly shown; see 'ERROR_admin_user_search.png'!")
        return False
    except NoSuchElementException:
        log(ERROR, "Can't find search boxes; can't continue testing!")
        return False
    except IndexError:
        log(ERROR, "Can't find the 'Search' button; can't continue!")
        return False
    except AssertionError, e:
        log(ERROR, e.message)
        return False

    log(PASS, "Search page functionality as expected.")
    return True
