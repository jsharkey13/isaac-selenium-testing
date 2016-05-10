import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import answer_numeric_q, open_accordion_section
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["numeric_q_all_correct"]


#####
# Test : Numeric Questions Correct Answers
#####
@TestWithDependency("NUMERIC_Q_ALL_CORRECT", ["NUMERIC_Q_UNITS_SELECT"])
def numeric_q_all_correct(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if numeric questions can be answered correctly.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB + "/questions/_regression_test_")
    time.sleep(WAIT_DUR)
    try:
        open_accordion_section(driver, 3)
        num_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacNumericQuestion']")
    except NoSuchElementException:
        log(ERROR, "Can't find the numeric question; can't continue!")
        return False

    log(INFO, "Attempt to enter correct answer.")
    if not answer_numeric_q(num_question, "2.01", "\units{ m\,s^{-1} }", wait_dur=WAIT_DUR):
        log(ERROR, "Couldn't answer Numeric Question; can't continue!")
        return False
    time.sleep(WAIT_DUR)

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h1[text()='Correct!']")
        log(INFO, "A 'Correct!' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='This is a correct choice.'])[2]")
        log(INFO, "The editor entered explanation text was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//strong[text()='Well done!']")
        log(INFO, "The 'Well done!' message was correctly shown.")
        log(INFO, "Avoid rate limiting: wait 1 minute.")
        time.sleep(60)
        log(PASS, "Numeric Question 'correct value, correct unit' behavior as expected.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_all_correct")
        log(ERROR, "The messages shown for a correct answer were not all displayed; see 'ERROR_numeric_q_all_correct.png'!")
        return False
