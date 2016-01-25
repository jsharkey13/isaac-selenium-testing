import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form
from ..utils.i_selenium import assert_tab
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["delete_user"]


#####
# Test : Delete A User
#####
@TestWithDependency("DELETE_USER", ["LOGIN", "SIGNUP"])
def delete_user(driver, Users, ISAAC_WEB, WAIT_DUR):
    """Test if admin users can delete users.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    log(INFO, "Attempt to delete temporary user.")
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)
    try:
        submit_login_form(driver, user=Users.Admin, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        time.sleep(WAIT_DUR)
        user_manager_link = driver.find_element_by_xpath("//a[@ui-sref='adminUserManager']")
        user_manager_link.click()
    except NoSuchElementException:
        log(ERROR, "Can't access User Manager from Global Nav; can't continue testing!")
        return False
    try:
        time.sleep(WAIT_DUR)
        email_field = driver.find_element_by_id("user-search-email")
        email_field.send_keys(Users.Guerrilla.email)
        time.sleep(WAIT_DUR)
        search_button = driver.find_element_by_xpath("//a[@ng-click='findUsers()']")
        search_button.click()
        wait_for_invisible_xpath(driver, "//h3[contains(text(), 'Manage Users ()')]")
    except TimeoutException:
        log(ERROR, "Search button did not work; can't continue testing!")
        return False
    try:
        del_button_xpath = "//td[text()='%s']/..//a[contains(@ng-click, 'deleteUser')]" % Users.Guerrilla.email
        delete_button = driver.find_element_by_xpath(del_button_xpath)
        delete_button.click()
        time.sleep(4)
        alert = driver.switch_to.alert
        alert_text = alert.text
        log(INFO, "Alert, with message: '%s'." % alert_text)
        expected = "Are you sure you want to delete the account with email address: %s?" % Users.Guerrilla.email
        assert expected in alert_text, "Alert contained unexpected message '%s'!" % alert_text
        log(INFO, "Accepted the alert.")
        alert.accept()
        popup = wait_for_xpath_element(driver, "//div[@class='toast-message']/p")
        popup_text = popup.text
        log(INFO, "Popup said: '%s'." % popup_text)
        assert 'successfully deleted' in popup_text
        time.sleep(WAIT_DUR)
        log(INFO, "User deleted.")
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logging out the admin user.")
        time.sleep(WAIT_DUR)
        log(PASS, "User '%s' deleted successfuly." % Users.Guerrilla.email)
        return True
    except NoSuchElementException:
        log(ERROR, "No user matching the email found by search; can't delete the account!")
        return False
    except AssertionError, e:
        if "Alert" in e.message:
            alert = driver.switch_to.alert
            alert.dismiss
            log(ERROR, "Dismiss the alert, do not accept!")
            return False
        else:
            log(ERROR, "Successful deletion message not shown!")
            return False
    except TimeoutException:
        log(ERROR, "No deletion confirmation message shown!")
        return False
