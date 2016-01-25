import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["pwd_reset_throttle"]


#####
# Test : Forgot My Password Button Limit
#####
@TestWithDependency("PWD_RESET_THROTTLE", ["LOGIN", "LOGOUT", "SIGNUP"])
def pwd_reset_throttle(driver, Users, ISAAC_WEB, WAIT_DUR):
    """Test that there is a limit on the number of password reset requests.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)

    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)
    password_resets = 0
    forgot_pwd_request_limit = 4
    try:
        user = driver.find_element_by_xpath("(//input[@name='email'])[2]")
        user.clear()
        user.send_keys(Users.Guerrilla.email)
        for i in range(10):
            forgot_password_button = driver.find_element_by_xpath("(//a[@ng-click='resetPassword()'])[2]")
            log(INFO, "Clicking password reset button.")
            forgot_password_button.click()
            time.sleep(0.1)
            image_div(driver, "reset_password_button_message_%s" % i)
            password_resets += 1
            if i <= forgot_pwd_request_limit - 1:  # i starts from 0 not 1
                try:
                    wait_for_invisible_xpath(driver, "//div[@class='toast-message']/h4", 0.5)
                except TimeoutException:
                    raise TimeoutException("Password reset error message unexpectedly shown after %s requests!" % password_resets)
                time.sleep(0.5)
                message = driver.find_element_by_xpath("(//p[@ng-show='passwordResetFlag'])[2]")
                assert "Your password request is being processed." in message.text
            else:
                try:
                    wait_for_xpath_element(driver, "//div[@class='toast-message']/h4")
                except TimeoutException:
                    raise TimeoutException("Password reset error message not shown after %s requests." % password_resets)
                log(INFO, "Password reset error message shown after %s attempts." % password_resets)
                break
            time.sleep(WAIT_DUR)
        log(PASS, "Password reset error message shown after %s requests." % password_resets)
        return True
    except AssertionError:
        log(ERROR, "Incorrect password reset message shown; see 'reset_password_button_message.png'!")
        return False
    except NoSuchElementException:
        log(ERROR, "No password reset messagew shown; see 'reset_password_button_message.png'!")
        return False
    except TimeoutException, e:
        log(ERROR, e.msg)
        return False
