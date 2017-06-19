import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form, assert_logged_in
from ..utils.i_selenium import assert_tab, new_tab, close_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException

__all__ = ["email_change_login_status"]


#####
# Test : Check Login Status After Email Change
#####
@TestWithDependency("EMAIL_CHANGE_LOGIN_STATUS", ["EMAIL_CHANGE_EMAILS"])
def email_change_login_status(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test login behavior after changing email before and after verifying new email.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    log(INFO, "Now testing login conditions; old email should work until after verification, then new email only.")
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)
    ###
    submit_login_form(driver, user=Users.Guerrilla, wait_dur=WAIT_DUR)
    log(INFO, "Submitted login form with old credentials.")
    time.sleep(WAIT_DUR)
    try:
        assert_logged_in(driver, Users.Guerrilla, wait_dur=WAIT_DUR)
        log(INFO, "Login successful with old email before verification of new email.")
    except AssertionError:
        log(INFO, "Login failed.")
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Login failed with old email before verification of new email; see 'ERROR_not_logging_in.png'!")
        return False
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out again.")
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)
    try:
        log(INFO, "Submit login form with new credentials.")
        submit_login_form(driver, Users.Guerrilla.new_email, Users.Guerrilla.password, wait_dur=WAIT_DUR)
        wait_for_xpath_element(driver, "//strong[text()='Incorrect credentials provided.']", 5)
        log(INFO, "Login failed with new email before verification of new email.")
    except TimeoutException:
        image_div(driver, "ERROR_logged_in_unexpectedly")
        log(ERROR, "Login succeeded with old email before verification of new email; see 'ERROR_logged_in_unexpectedly.png'!")
        return False
    driver.refresh()
    time.sleep(WAIT_DUR)
    ###
    log(INFO, "Now verifying new email address.")
    new_tab(driver)
    time.sleep(WAIT_DUR)
    try:
        driver.get(Users.Guerrilla.verify_link)
        log(INFO, "Got: %s" % Users.Guerrilla.verify_link)
        wait_for_xpath_element(driver, "//h2[@ng-if='verificationState==verificationStates.SUCCESS']")
        time.sleep(WAIT_DUR)
        log(INFO, "Verification of new email address succeeded.")
        # Update the credentials immediately to avoid any errors preventing update
        # and breaking subsequent tests:
        log(INFO, "Updating internal credentials to reflect new email address!")
        Users.Guerrilla.old_email = Users.Guerrilla.email
        Users.Guerrilla.email = Users.Guerrilla.new_email
        #
        close_tab(driver)
    except TimeoutException:
        image_div(driver, "ERROR_change_email_verify_fail")
        close_tab(driver)
        time.sleep(WAIT_DUR)
        log(ERROR, "New email verification failed, can't continue. See 'ERROR_change_email_verify_fail.png'!")
        return False
    except AttributeError:
        close_tab(driver)
        time.sleep(WAIT_DUR)
        log(ERROR, "New email verfication link not saved. Can't complete test!")
        return False
    ###
    assert_tab(driver, ISAAC_WEB)
    submit_login_form(driver, user=Users.Guerrilla, wait_dur=WAIT_DUR)
    log(INFO, "Submitted login form with old credentials.")
    try:
        wait_for_xpath_element(driver, "//strong[text()='Incorrect credentials provided.']", 5)
        log(INFO, "Login failed with old email after verification of new email.")
    except TimeoutException:
        image_div(driver, "ERROR_logged_in_unexpectedly")
        log(ERROR, "Login suceeded with old email after verification of new email; see 'ERROR_logged_in_unexpectedly.png'!")
        # Restore internal credentials to old working versions for later tests:
        log(INFO, "Reverting update to internal credentials as old email still working!")
        Users.Guerrilla.email = Users.Guerrilla.old_email
        #
        return False
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)
    try:
        submit_login_form(driver, Users.Guerrilla.new_email, Users.Guerrilla.password, wait_dur=WAIT_DUR)
        log(INFO, "Submitted login form with new credentials.")
        time.sleep(WAIT_DUR)
        assert_logged_in(driver, wait_dur=WAIT_DUR)
        log(INFO, "Login successful with new email after verification of new email.")
    except AssertionError:
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Login failed with new email after verification of new email; see 'ERROR_not_logging_in.png'!")
        return False
    time.sleep(WAIT_DUR)
    log(PASS, "Old login worked until verification of new, then stopped. New didn't work until verification.")
    return True
