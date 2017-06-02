import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..utils.isaac import snooze_email_verification
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["global_nav_mobile"]


#####
# Test : Global Navigation Menu
#####
@TestWithDependency("GLOBAL_NAV_MOBILE", ["ACCEPT_COOKIES", "GLOBAL_NAV"])
def global_nav_mobile(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether the global navigation menu works.

        Should be run after "LOGIN" has been run, and before "LOGOUT".
        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    window_size = driver.get_window_size()
    driver.set_window_size(360, 640)
    driver.refresh()

    # The Email Verification warning obstructs the menu. If it's there, snooze it!
    if not snooze_email_verification(driver):
        log(ERROR, "Can't continue with this test since the banner obstructs the menu!")
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
        driver.find_element_by_xpath("(//a[contains(text(), 'My Account')])[2]")
        log(INFO, "Can access My Account button in the menu!")
        driver.set_window_size(window_size["width"], window_size["height"])
        driver.maximize_window()
        driver.refresh()
        time.sleep(WAIT_DUR)
        log(PASS, "Global navigation on mobile functions as expected.")
        return True
    except NoSuchElementException:
        image_div(driver, "ERROR_global_nav_mobile")
        log(ERROR, "Cannot access sub-menus! See 'ERROR_global_nav_mobile.png'!")
        driver.set_window_size(window_size["width"], window_size["height"])
        driver.maximize_window()
        return False
