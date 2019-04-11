import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form, assert_logged_in
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotVisibleException, ElementNotInteractableException
from selenium.webdriver.support.ui import Select

__all__ = ["account_settings"]


#####
# Test : Update Account Settings
#####
@TestWithDependency("ACCOUNT_SETTINGS", ["SIGNUP"])
def account_settings(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if users account settings can be accessed and changed.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)
    submit_login_form(driver, user=Users.Guerrilla, wait_dur=WAIT_DUR)
    time.sleep(WAIT_DUR)

    try:
        assert_logged_in(driver, user=Users.Guerrilla)
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        log(INFO, "Opened global nav (menu bar).")
        time.sleep(WAIT_DUR)
        my_account_link = driver.find_element_by_xpath("(//a[@ui-sref='accountSettings'])[2]")
        my_account_link.click()
        log(INFO, "Clicked 'My Account' button.")
        time.sleep(WAIT_DUR)
    except (NoSuchElementException, ElementNotVisibleException):
        image_div(driver, "ERROR_account_global_nav")
        log(ERROR, "Couldn't access 'My Account' link from global nav; see ERROR_account_global_nav.png'")
        return False
    except AssertionError:
        log(ERROR, "Login failed!")
        return False

    try:
        email_address_box = driver.find_element_by_xpath("//input[@id='account-email']")
        account_email = str(email_address_box.get_property("value"))
        assert account_email == Users.Guerrilla.email, "Expected to see correct email on account setting page, found '%s'!" % account_email
    except AssertionError as e:
        log(ERROR, e.message)
        return False
    except NoSuchElementException:
        log(ERROR, "Can't find account email box, can't continue!")
        return False

    try:
        gender_other_box = driver.find_element_by_xpath("//div[@id='account-gender']//input[@value='OTHER']")
        gender_other_box.click()
        log(INFO, "Changed account Gender.")
        time.sleep(WAIT_DUR)
        dob_selects = driver.find_elements_by_xpath("//ul[contains(@class,'dob-wrap')]//select")
        assert len(dob_selects) == 3, "Can't find date of birth selection, can't continue!"
        dob_day = Select(dob_selects[0])
        dob_month = Select(dob_selects[1])
        dob_year = Select(dob_selects[2])
        dob_day.select_by_visible_text("23")
        dob_month.select_by_visible_text("Jun")
        dob_year.select_by_visible_text("1912")
        log(INFO, "Changed account Date of Birth.")

    except AssertionError as e:
        log(ERROR, e.message)
        return False
    except NoSuchElementException:
        log(ERROR, "Can't find gender select box, can't continue!")
        return False

    school_name = "University of Cambridge"

    try:
        school_dropdown_search = driver.find_element_by_xpath("//div[@school-dropdown]//input")
        school_dropdown_search.send_keys(school_name)
        wait_for_xpath_element(driver, "//li[@ng-click='selection.school=school']")
        school_option = driver.find_elements_by_xpath("//div[@school-dropdown]//li/span[contains(text(), '%s')]/.." % school_name)[0]
        school_option.click()
        log(INFO, "Changed account School.")
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't find school dropdown, can't continue!")
        return False
    except ElementNotInteractableException:
        log(ERROR, "Can't set school; perhaps one is already set?! Can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "No results listed for school search! Can't continue!")
        return False
    except IndexError:
        log(ERROR, "School not found from search term! Can't continue!")
        return False

    try:
        old_url = str(driver.current_url)
        save_button = driver.find_element_by_xpath("//a[text()='Save']")
        save_button.click()
        log(INFO, "Saving account changes.")
        time.sleep(WAIT_DUR)
        new_url = driver.current_url
        assert new_url != old_url, "Expected to be redirected to homepage on save!"
        log(INFO, "Account changes saved successfully and redirected to '%s'." % new_url)
    except NoSuchElementException:
        log(ERROR, "Can't find Save button, can't continue!")
        return False
    except AssertionError as e:
        log(ERROR, e.message + " See 'ERROR_my_account_save.png'. Can't continue!")
        image_div(driver, "ERROR_my_account_save")
        return False

    try:
        driver.get(ISAAC_WEB + "/account")
        log(INFO, "Returning to My Account page.")
        time.sleep(WAIT_DUR)

        log(INFO, "Checking account settings changes were persisted.")
        gender_other_box = driver.find_element_by_xpath("//div[@id='account-gender']//input[@value='OTHER']")
        assert gender_other_box.is_selected(), "Expected gender change to be persisted; changes lost!"

        dob_selects = driver.find_elements_by_xpath("//ul[contains(@class,'dob-wrap')]//select")
        dob_day = Select(dob_selects[0]).first_selected_option.text
        dob_month = Select(dob_selects[1]).first_selected_option.text
        dob_year = Select(dob_selects[2]).first_selected_option.text
        assert (dob_day == "23") and (dob_month == "Jun") and (dob_year == "1912"), "Expected date of birth changes to be persisted; changes lost!"

        school_name_box = driver.find_element_by_xpath("//div[@ng-show='selection.school.name']/span[1]")
        assert school_name in school_name_box.text, "Expected school change to be persisted; changes lost!"
    except AssertionError as e:
        log(ERROR, e.message + " See 'ERROR_my_account_persist.png'. Can't continue!")
        image_div(driver, 'ERROR_my_account_persist')
        return False
    except NoSuchElementException:
        log(ERROR, "Can't find relevant page sections, can't continue!")
        return False

    log(PASS, "Changes to account settings successfully persisted!")
    return True
