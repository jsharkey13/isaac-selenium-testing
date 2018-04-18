import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import answer_numeric_q, open_accordion_section
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["numeric_q_all_incorrect"]


#####
# Test : Numeric Questions Incorrect Value, Incorrect Unit
#####
@TestWithDependency("NUMERIC_Q_ALL_INCORRECT", ["NUMERIC_Q_ANSWER_CHANGE"])
def numeric_q_all_incorrect(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test numeric question behaviour on incorrect value and units.

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

    log(INFO, "Attempt to enter unknown incorrect value, to correct sig figs and incorrect units.")
    if not answer_numeric_q(num_question, "4.33", "\units{ m\,s^{-1} }", get_unit_wrong=True, wait_dur=WAIT_DUR):
        log(ERROR, "Couldn't answer Numeric Question; can't continue!")
        return False
    time.sleep(WAIT_DUR)

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h2[text()='Incorrect']")
        log(INFO, "An 'Incorrect' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='Check your working.'])[1]")
        log(INFO, "The 'Check your working.' message was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h5[text()='Please try again.']")
        log(INFO, "The 'Please try again.' message was correctly shown.")
        bg_colour1 = num_question.find_element_by_xpath("(.//div[@class='ru-answer-block-panel'])[1]").value_of_css_property('background-color')
        assert bg_colour1 in ['#be4c4c', 'rgba(190, 76, 76, 1)', 'rgb(190, 76, 76)']
        log(INFO, "Red highlighting shown around value box.")
        bg_colour2 = num_question.find_element_by_xpath("(.//div[@class='ru-answer-block-panel'])[2]").value_of_css_property('background-color')
        assert bg_colour2 in ['#be4c4c', 'rgba(190, 76, 76, 1)', 'rgb(190, 76, 76)']
        log(INFO, "Red highlighting shown around units box.")
        log(INFO, "Avoid rate limiting: wait 1 minute.")
        time.sleep(60)
        log(PASS, "Numeric Question 'incorrect value, incorrect unit' behavior as expected.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_all_incorrect")
        log(ERROR, "The messages shown for an incorrect answer were not all displayed; see 'ERROR_numeric_q_all_incorrect.png'!")
        return False
    except AssertionError:
        image_div(driver, "ERROR_numeric_q_all_incorrect")
        log(ERROR, "The answer boxes were not highlighted red correctly; see 'ERROR_numeric_q_all_incorrect.png'!")
        return False
