import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form_mobile, assert_logged_in
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException

__all__ = ["login_mobile"]


#####
# Test : Logging In
#####
@TestWithDependency("LOGIN_MOBILE")
def login_mobile(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether users can sign in to Isaac on a mobile device.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.set_window_size(360, 640)
    driver.refresh()
    try:
        cookie_message = driver.find_element_by_xpath("//a[contains(@class, 'cookies-accepted')]")
        cookie_message.click()
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Unable to accept cookies!")
        return False
    try:
        login_tab = driver.find_element_by_xpath("//div[@id='mobile-login']")
        login_tab.click()
        time.sleep(WAIT_DUR)
        submit_login_form_mobile(driver, user=Users.Student, disable_popup=False, wait_dur=WAIT_DUR)
        time.sleep(20)
        driver.maximize_window()
        return True
    except NoSuchElementException:
        log(ERROR, "Cannot select mobile login.")
        return False


