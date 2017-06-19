import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..utils.isaac import open_accordion_section, close_accordion_section, wait_accordion_open, wait_accordion_closed
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["accordion_behavior"]


#####
# Test : Accordion Sections Open and Close
#####
@TestWithDependency("ACCORDION_BEHAVIOUR")
def accordion_behavior(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if accordions open and close as expected.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/questions/_regression_test_")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/questions/_regression_test_"))
    time.sleep(WAIT_DUR)
    log(INFO, "Check accordions open first section automatically.")
    try:
        wait_for_xpath_element(driver, "//p[text()='This is a quick question.']")
        log(INFO, "First accordion section open by default on question pages.")
        time.sleep(WAIT_DUR)
    except TimeoutException:
        image_div(driver, "ERROR_accordion_default")
        log(ERROR, "First accordion section not open by default; see 'ERROR_accordion_default.png'.")
        return False
    log(INFO, "Try closing an accordion section.")
    try:
        close_accordion_section(driver, 1)
        time.sleep(WAIT_DUR)
        wait_for_invisible_xpath(driver, "//p[text()='This is a quick question.']")
        log(INFO, "Accordions close as expected.")
    except NoSuchElementException:
        log(ERROR, "Can't find accordion title bar to click; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_accordion_closing")
        log(ERROR, "Accordion section did not close correctly; see 'ERROR_accordion_closing.png'")
        return False
    log(INFO, "Try reopening accordion section.")
    try:
        open_accordion_section(driver, 1)
        time.sleep(WAIT_DUR)
        wait_for_xpath_element(driver, "//p[text()='This is a quick question.']")
        log(INFO, "Accordions open as expected.")
        close_accordion_section(driver, 1)
        time.sleep(WAIT_DUR)
        log(INFO, "Closed accordion section; all should now be closed.")
    except NoSuchElementException:
        log(ERROR, "Can't find accordion title bar to click again; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_accordion_reopen")
        log(ERROR, "Accordion section did not reopen correctly; see 'ERROR_accordion_reopen.png'!")
        return False
    log(INFO, "Check all accordion sections work.")
    try:
        accordion_sections = driver.find_elements_by_xpath("//a[contains(@class, 'ru_accordion_titlebar')]")
        assert len(accordion_sections) == 6, "Expected 6 accordion sections, got %s!" % len(accordion_sections)
        log(INFO, "5 accordion sections on page as expected.")
        log(INFO, "Try to open each accordion section in turn.")
        for i, accordion_title in enumerate(accordion_sections):
            n = i + 1
            accordion_title.click()
            wait_accordion_open(driver, n)
            log(INFO, "Accordion section %s correctly shown." % n)
            accordion_title.click()
            wait_accordion_closed(driver, n)
            log(INFO, "Accordion section %s correctly hidden." % n)
            time.sleep(WAIT_DUR)
    except TimeoutException:
        log(ERROR, "Couldn't open all accordion sections!")
        return False
    except AssertionError, e:
        log(ERROR, e.message)
        return False
    log(PASS, "Accordion behavior is as expected.")
    return True
