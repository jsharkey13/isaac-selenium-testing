import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import open_accordion_section
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["numeric_q_answer_reloaded"]


#####
# Test : Numeric Questions Select 'None' as Units Option
#####
@TestWithDependency("NUMERIC_Q_ANSWER_RELOADED", ["NUMERIC_Q_ALL_CORRECT"])
def numeric_q_answer_reloaded(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test reloading of correct answers on page refresh.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB + "/questions/_regression_test_")
    time.sleep(WAIT_DUR)
    log(INFO, "Refreshing the page.")
    driver.refresh()
    time.sleep(WAIT_DUR)
    try:
        open_accordion_section(driver, 3)
        num_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacNumericQuestion']")
    except NoSuchElementException:
        log(ERROR, "Can't find the numeric question; can't continue!")
        return False

    time.sleep(WAIT_DUR)

    try:
        log(INFO, "Checking previously entered answer is present after reload.")
        value_box = num_question.find_element_by_xpath(".//input[@ng-model='ctrl.selectedValue']")
        assert str(value_box.get_attribute('value')) == "2.01", "Value incorrectly reloaded. Expected '2.01', got '%s'!" % value_box.get_attribute('value')
        units_dropdown = num_question.find_element_by_xpath(".//button[@ng-click='ctrl.showUnitsDropdown()']")
        units_text = units_dropdown.find_element_by_xpath("./span/script").get_attribute('innerHTML')
        assert units_text.strip() == "\units{m\,s^{-1}}", "Units incorrectly reloaded. Expected '\units{m\,s^{-1}}', got '%s'!" % units_text
        log(INFO, "Value and units correctly reloaded after page refresh.")
    except NoSuchElementException:
        image_div(driver, "ERROR_numeric_q_units_none")
        log(ERROR, "Can't find value and units box for numeric question after reload! See ERROR_numeric_q_units_none.png")
        return False
    except AssertionError, e:
        log(ERROR, e.message)
        return False

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h1[text()='Correct!']")
        log(INFO, "The 'correct' message was displayed again.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='This is a correct choice.'])[2]")
        log(INFO, "The content editor entered message was correctly reloaded.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//strong[text()='Well done!']")
        log(INFO, "The 'Well Done' message was correctly reloaded.")
        time.sleep(WAIT_DUR)
        log(PASS, "Numeric Question answers reloaded correctly.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_units_none")
        log(ERROR, "The messages shown for an answer were not all reloaded; see 'ERROR_numeric_q_units_none.png'!")
        return False
