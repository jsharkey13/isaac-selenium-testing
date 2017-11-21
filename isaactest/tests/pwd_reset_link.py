import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, new_tab, close_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException

__all__ = ["pwd_reset_link"]


#####
# Test 14 : Reset Password Link Works
#####
@TestWithDependency("PWD_RESET_LINK", ["RECIEVE_PWD_RESET_EMAILS"])
def pwd_reset_link(driver, inbox, Users, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR, **kwargs):
    """Test that the emailed password reset link works.

        - 'driver' should be a Selenium WebDriver.
        - 'inbox' should be a GuerrillaInbox object.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'GUERRILLAMAIL' is the string URL of GuerrillaMail.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, GUERRILLAMAIL)
    log(INFO, "About to check latest reset password link works.")
    try:
        reset_email = inbox.get_by_subject("Password Reset Request")[0]
        reset_email.view()
        log(INFO, "Selecting most recent password reset email '%s'." % reset_email)
        time.sleep(WAIT_DUR)
        email_body = reset_email.get_email_body_element()
        reset_link = email_body.find_element_by_xpath(".//a[text()='click here']")
        reset_email.close()
        time.sleep(WAIT_DUR)
        reset_url = str(reset_link.get_attribute("href")).replace("https://localhost:8080/isaac-api", ISAAC_WEB)
        log(INFO, "Reset Password URL: '%s'." % reset_url)
        time.sleep(WAIT_DUR)
        new_tab(driver)
        log(INFO, "Opening verification link from email in new tab.")
        driver.get(reset_url)
        time.sleep(WAIT_DUR)
        assert_tab(driver, ISAAC_WEB + "/resetpassword")
    except NoSuchElementException:
        log(ERROR, "Can't access reset password link in email; can't continue!")
        return False
    try:
        pwd1 = driver.find_element_by_xpath("//input[@id='password']")
        pwd1.clear()
        pwd1.send_keys(Users.Guerrilla.new_password)
        pwd2 = driver.find_element_by_xpath("//input[@id='confirm-password']")
        pwd2.clear()
        pwd2.send_keys(Users.Guerrilla.new_password)
        change_password = driver.find_element_by_xpath("//button[@ng-click='resetPassword()']")
        log(INFO, "Submitting new password.")
        change_password.click()
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't access reset password form correctly; can't continue!")
        return False
    try:
        driver.find_element_by_xpath("//div[@ng-switch='submitted']/div[contains(text(), 'reset successfully')]")
        Users.Guerrilla.password = Users.Guerrilla.new_password
        close_tab(driver)
        time.sleep(WAIT_DUR)
        log(PASS, "Reset password link works.")
        return True
    except NoSuchElementException:
        image_div(driver, "ERROR_resetting_password")
        log(ERROR, "Resetting password failed; see 'ERROR_resetting_password.png'!")
        return False
