import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["quick_questions"]


#####
# Test : Quick Questions
#####
@TestWithDependency("QUICK_QUESTIONS", ["ACCORDION_BEHAVIOUR"])
def quick_questions(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if quick questions behave as expected.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/questions/_regression_test_")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/questions/_regression_test_"))
    time.sleep(WAIT_DUR)
    try:
        log(INFO, "Check that answer is not initially visible.")
        wait_for_invisible_xpath(driver, "//p[text()='This is the answer.']")
        log(INFO, "Answer not initially visible.")
    except TimeoutException:
        log(ERROR, "Quick question answer initially shown!")
        return False
    try:
        wait_for_xpath_element(driver, "//span[text()='Show answer']")
        log(INFO, "'Show answer' text is initially displayed.")
    except TimeoutException:
        log(ERROR, "'Show answer' text not initially displayed!")
        return False
    try:
        log(INFO, "Try clicking the 'Show answer' button.")
        show = driver.find_element_by_xpath("//div[contains(@class, 'ru_answer_reveal')]/div[@ng-click='isVisible=!isVisible']")
        show.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Check answer was shown.")
        wait_for_xpath_element(driver, "//p[text()='This is the answer.']")
        log(INFO, "Answer was displayed correctly.")
    except NoSuchElementException:
        log(ERROR, "Couldn't find 'Show answer' button to click; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Answer was not displayed after clicking 'Show answer'!")
        return False
    try:
        wait_for_xpath_element(driver, "//span[text()='Hide answer']")
        log(INFO, "'Hide answer' text displayed as expected.")
    except TimeoutException:
        log(ERROR, "'Hide answer' text not shown after answer displayed!")
        return False
    try:
        log(INFO, "Try clicking the 'Hide answer' button to hide answer again.")
        hide = driver.find_element_by_xpath("//div[contains(@class, 'ru_answer_reveal')]/div[@ng-click='isVisible=!isVisible']")
        hide.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Check answer was hidden again.")
        wait_for_invisible_xpath(driver, "//p[text()='This is the answer.']")
        log(INFO, "Answer was hidden again correctly.")
        time.sleep(WAIT_DUR)
        log(PASS, "Quick question behavior as expected.")
        return True
    except NoSuchElementException:
        log(ERROR, "Couldn't find 'Hide answer' button to click; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Answer was not hidden again after clicking 'Hide answer'!")
        return False
