import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["accept_cookies"]


#####
# Test : Global Navigation Menu
#####
@TestWithDependency("ACCEPT_COOKIES", ["LOGIN"])
def accept_cookies(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether the banner disappears after accepting cookies.

        Should be run after "LOGIN" has been run, and before "LOGOUT".
        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        wait_for_xpath_element(driver, "//div[@data-alert and contains(@class, 'cookies-message')]")
        log(INFO, "Clicking 'Accept' on the cookies message.")
        cookie_message = driver.find_element_by_xpath("//a[contains(@class, 'cookies-accepted')]")
        cookie_message.click()
    except TimeoutException:
        log(ERROR, "WARNING: Can't find cookies message! Has it already been accepted?!")
        pass
    except NoSuchElementException:
        log(ERROR, "Unable to accept cookies!")
        return False

    try:
        wait_for_invisible_xpath(driver, "//div[@data-alert and contains(@class, 'cookies-message')]")
    except TimeoutException:
        log(ERROR, "Cookie message didn't hide after being clicked!")
        return False

    try:
        log(INFO, "Reloading the page to see if cookie message stays gone.")
        driver.refresh()
        time.sleep(WAIT_DUR)
        wait_for_invisible_xpath(driver, "//div[@data-alert and contains(@class, 'cookies-message')]")
        log(INFO, "Cookies message does not reappear.")
        log(PASS, "The cookie message behaves as expected.")
        return True
    except TimeoutException:
        log(ERROR, "Cookie message reappeared after page refresh!")
        return False
