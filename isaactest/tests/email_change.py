import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException

__all__ = ["email_change"]


#####
# Test : Change Email Address
#####
@TestWithDependency("EMAIL_CHANGE", ["LOGIN", "GLOBAL_NAV", "SIGNUP", "RECIEVE_VERIFY_EMAILS"])
def email_change(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if users can change their email address.

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
    log(INFO, "Attempting to change email address for '%s'." % Users.Guerrilla.email)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)
    submit_login_form(driver, user=Users.Guerrilla, wait_dur=WAIT_DUR)
    time.sleep(WAIT_DUR)

    try:
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
    try:
        start_url = driver.current_url
        assert "/account" in start_url, "'/account' not in URL: '%s'!" % start_url
        email_address_box = driver.find_element_by_xpath("//input[@id='account-email']")
        image_div(driver, "change_email_old_email", email_address_box.find_element_by_xpath(".."))
        email_address_box.clear()
        email_address_box.send_keys(Users.Guerrilla.new_email)
        time.sleep(WAIT_DUR)
        image_div(driver, "change_email_new_email", email_address_box.find_element_by_xpath(".."))
        save_button = driver.find_element_by_xpath("//a[text()='Save']")
        save_button.click()
        time.sleep(WAIT_DUR)
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        time.sleep(WAIT_DUR)
        log(INFO, "Have to accept an alert.")
        assert "You have edited your email address." in alert_text, "Alert contained unexpected message '%s'!" % alert_text
        log(INFO, "Alert said: '%s'." % alert_text)
        time.sleep(WAIT_DUR)
        end_url = driver.current_url
        assert end_url != start_url, "Expected to leave account page, but still on '%s'!" % end_url
        end_loc = end_url.split("#")[0]
        assert end_loc == ISAAC_WEB + "/", "Should have redirected to homepage, went to '%s' instead!" % end_url
        log(PASS, "Email changed in account setting successfully.")
        return True
    except AssertionError, e:
        image_div(driver, "ERROR_change_email_page")
        log(ERROR, e.message)
        return False
    except NoSuchElementException:
        image_div(driver, "ERROR_change_email_page")
        log(ERROR, "Couldn't change password on 'My Account' page; see 'ERROR_change_email_page.png'!")
        return False
