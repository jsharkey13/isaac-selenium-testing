import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import answer_numeric_q, open_accordion_section
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["numeric_q_incorrect_unit"]


#####
# Test : Numeric Questions Incorrect Unit, Correct Value
#####
@TestWithDependency("NUMERIC_Q_INCORRECT_UNIT", ["NUMERIC_Q_ANSWER_CHANGE"])
def numeric_q_incorrect_unit(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test numeric question behaviour on incorrect units.

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

    log(INFO, "Attempt to enter correct value, but incorrect units.")
    if not answer_numeric_q(num_question, "2.01", "\units{ m\,s^{-1} }", get_unit_wrong=True, wait_dur=WAIT_DUR):
        log(ERROR, "Couldn't answer Numeric Question; can't continue!")
        return False
    time.sleep(WAIT_DUR)

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h2[text()='incorrect']")
        log(INFO, "A 'incorrect' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='Check your units.'])[1]")
        log(INFO, "The 'Check your units.' message was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h5[text()='Please try again.']")
        log(INFO, "The 'Please try again.' message was correctly shown.")
        bg_colour = num_question.find_element_by_xpath("(.//div[@class='ru-answer-block-panel'])[2]").value_of_css_property('background-color')
        assert (bg_colour == '#be4c4c') or (bg_colour == 'rgba(190, 76, 76, 1)')
        log(INFO, "Red highlighting shown around units box.")
        time.sleep(WAIT_DUR)
        log(PASS, "Numeric Question 'incorrect unit, correct value' behavior as expected.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_incorrect_unit")
        log(ERROR, "The messages shown for an incorrect unit were not all displayed; see 'ERROR_numeric_q_incorrect_unit.png'!")
        return False
    except AssertionError:
        image_div(driver, "ERROR_numeric_q_incorrect_unit")
        log(ERROR, "The units box was not highlighted red; see 'ERROR_numeric_q_incorrect_unit.png'!")
        return False
