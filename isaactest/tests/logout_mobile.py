import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import assert_logged_out, snooze_email_verification
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException

__all__ = ['logout_mobile']


#####
# Test : Logging Out (Mobile Devices)
#####
@TestWithDependency('LOGOUT_MOBILE', ['LOGIN_MOBILE'])
def logout_mobile(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether users can sign out of Isaac on mobile devices.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    window_size = driver.get_window_size()
    driver.set_window_size(360, 640)
    driver.refresh()
    time.sleep(WAIT_DUR)

    # The Email Verification warning obstructs the menu. If it's there, snooze it!
    if not snooze_email_verification(driver):
        log(ERROR, "Can't continue with this test since the banner obstructs the menu!")
        return False

    try:
        account_settings_button = driver.find_element_by_xpath("(//a[@ui-sref='accountSettings'])[1]")
        account_settings_button.click()
        time.sleep(WAIT_DUR)
        logout_button = driver.find_elements_by_xpath("//a[contains(text(), 'Log out')]")[0]
        logout_button.click()
    except NoSuchElementException:
        image_div(driver, 'ERROR_logout_failure')
        log(ERROR, "Can't find account settings; can't logout, see 'ERROR_logout_failure.png'!")
        return False
    except IndexError:
        image_div(driver, 'ERROR_logout_failure')
        log(ERROR, "Can't find logout button; can't logout, see 'ERROR_logout_failure.png'!")
        return False

    try:
        assert_logged_out(driver, wait_dur=WAIT_DUR)
        log(INFO, 'Logged out successfully.')
        time.sleep(WAIT_DUR)
        driver.set_window_size(window_size["width"], window_size["height"])
        driver.maximize_window()
        log(PASS, 'Mobile log out works as expected.')
        return True
    except AssertionError:
        image_div(driver, 'ERROR_mobile_logout_failure')
        log(ERROR, "Couldn't logout; see 'ERROR_mobile_logout_failure.png'!")
        return False
