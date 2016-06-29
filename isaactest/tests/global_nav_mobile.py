import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..utils.isaac import kill_irritating_popup
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["global_nav_mobile"]


#####
# Test : Global Navigation Menu
#####
@TestWithDependency("GLOBAL_NAV_MOBILE")
def global_nav_mobile(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether the global navigation menu works.

        Should be run after "LOGIN" has been run, and before "LOGOUT".
        - 'driver' should be a Selenium WebDriver.
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
        time.sleep(WAIT_DUR)
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        log(INFO, "Clicked menu button.")
        time.sleep(WAIT_DUR)
        wait_for_xpath_element(driver, "//nav[@class='dl-nav']")
        log(INFO, "Global navigation successfully opened.")
    except NoSuchElementException:
        log(ERROR, "Can't find menu button to click; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Global navigation didn't open!")
        return False
    time.sleep(WAIT_DUR)
    try:
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        time.sleep(WAIT_DUR)
        wait_for_invisible_xpath(driver, "//nav[@class='dl-nav']")
        log(INFO, "Global navigation successfully closed.")
    except TimeoutException:
        log(ERROR, "Global navigation didn't close!")
        return False
    try:
        time.sleep(WAIT_DUR)
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        log(INFO, "Clicked menu button.")
        time.sleep(WAIT_DUR)
        wait_for_xpath_element(driver, "//nav[@class='dl-nav']")
        log(INFO, "Global navigation successfully opened.")
    except NoSuchElementException:
        log(ERROR, "Can't find menu button to click; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Global navigation didn't open!")
        return False
    try:
        my_isaac = driver.find_element_by_xpath("//h6[contains(text(), 'My Isaac')]")
        my_isaac.click()
        time.sleep(WAIT_DUR)
        wait_for_xpath_element(driver, "//ul[@class='dl-level2 dl-clone']")
        my_account = driver.find_element_by_xpath("(//a[contains(text(), 'My Account')])[2]")
        my_account.click()
        log(INFO, "Selected My Account from the menu!")
        log(PASS, "Global navigation functions as expected.")
        return True
    except NoSuchElementException:
        log(ERROR, "Cannot navigate to My Account")
        return False
