import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab,  image_div
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["numeric_q_answer_change"]


#####
# Test : Numeric Questions Answer Change
#####
@TestWithDependency("NUMERIC_Q_ANSWER_CHANGE", ["NUMERIC_Q_UNITS_SELECT", "NUMERIC_Q_ALL_CORRECT"])
def numeric_q_answer_change(driver, ISAAC_WEB, WAIT_DUR):
    """Test if numeric question answers behave correctly on attempting to enter
       a new answer.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        num_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacNumericQuestion']")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h1[text()='Correct!']")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='This is a correct choice.'])[2]")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//strong[text()='Well done!']")
    except NoSuchElementException:
        log(ERROR, "Can't find the numeric question; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Correct answer text can't be found; can't check if it goes; can't continue!")
        return False

    try:
        log(INFO, "Alter previously typed answer.")
        value_box = num_question.find_element_by_xpath(".//input[@ng-model='selectedChoice.value']")
        value_box.send_keys("00")
    except NoSuchElementException:
        log(ERROR, "Can't find value box to try changing answer; can't continue!")
        return False

    try:
        wait_for_invisible_xpath(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h1[text()='Correct!']")
        wait_for_invisible_xpath(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='This is a correct choice.'])[2]")
        wait_for_invisible_xpath(driver, "//div[@ng-switch-when='isaacNumericQuestion']//strong[text()='Well done!']")
        time.sleep(WAIT_DUR)
        log(PASS, "Numeric Question answer text disappears upon changing answer.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_answer_change")
        log(ERROR, "The messages shown for an old answer do not disappear upon altering answer; see 'ERROR_numeric_q_answer_change.png'!")
        return False
