import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["global_nav"]


#####
# Test : Global Navigation Menu
#####
@TestWithDependency("GLOBAL_NAV", ["LOGIN"])
def global_nav(driver, ISAAC_WEB, WAIT_DUR):
    """Test whether the global navigation menu works.

        Should be run after "LOGIN" has been run, and before "LOGOUT".
        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    try:
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
        log(INFO, "Global navigation successfuly closed.")
        log(PASS, "Global navigation functions as expected.")
        return True
    except TimeoutException:
        log(ERROR, "Global navigation didn't close!")
        return False
