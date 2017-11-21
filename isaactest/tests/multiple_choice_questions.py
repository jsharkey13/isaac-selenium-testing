import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from ..utils.isaac import open_accordion_section
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["multiple_choice_questions"]


#####
# Test : Multiple Choice Questions
#####
@TestWithDependency("MULTIPLE_CHOICE_QUESTIONS", ["ACCORDION_BEHAVIOUR"])
def multiple_choice_questions(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if multiple choice questions behave as expected.

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
        open_accordion_section(driver, 2)
        time.sleep(WAIT_DUR)
        mc_question = wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']")
        log(INFO, "Accordion opened, multiple choice question displayed.")
    except NoSuchElementException:
        log(ERROR, "Can't find second accordion section to open; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_multiple_choice")
        log(ERROR, "Accordion section did not open to display the multiple choice question; see 'ERROR_multiple_choice.png'!")
        return False
    try:
        incorrect_choice = mc_question.find_element_by_xpath("//label//span[contains(text(), '%s')]" % "69")
        incorrect_choice.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Selected an incorrect answer.")
    except NoSuchElementException:
        log(ERROR, "Can't select incorrect answer on multiple choice question; can't continue!")
        return False
    try:
        check_answer_button = mc_question.find_element_by_xpath("//button[text()='Check my answer']")
        check_answer_button.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Clicked 'Check my answer'.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//h2[text()='incorrect']")
        log(INFO, "An 'incorrect' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacMultiChoiceQuestion']//p[text()='This is an incorrect choice.'])[1]")
        log(INFO, "The editor entered explanation text was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//h5[text()='Please try again.']")
        log(INFO, "The 'Please try again' message was correctly shown.")
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Couldn't click the 'Check my answer' button; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_multiple_choice")
        log(ERROR, "The messages shown for an incorrect answer were not all displayed; see 'ERROR_multiple_choice.png'!")
        return False
    try:
        correct_choice = mc_question.find_element_by_xpath("//label//span[contains(text(), '%s')]" % "42")
        correct_choice.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Selected a correct choice.")
        wait_for_invisible_xpath(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//h2[text()='incorrect']")
        log(INFO, "The 'incorrect' message now correctly hidden after choosing new answer")
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't select correct answer on multiple choice question; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "The 'incorrect' message was not hidden after choosing a new answer!")
        return False
    try:
        check_answer_button = mc_question.find_element_by_xpath("//button[text()='Check my answer']")
        check_answer_button.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Clicked 'Check my answer'.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//h1[text()='Correct!']")
        log(INFO, "A 'Correct!' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacMultiChoiceQuestion']//p[text()='This is a correct choice.'])[2]")
        log(INFO, "The editor entered explanation text was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//strong[text()='Well done!']")
        log(INFO, "The 'Well done!' message was correctly shown.")
        time.sleep(WAIT_DUR)
        log(PASS, "Multiple Choice Question behavior as expected.")
        return True
    except NoSuchElementException:
        log(ERROR, "Couldn't click the 'Check my answer' button; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_multiple_choice")
        log(ERROR, "The messages shown for a correct answer were not all displayed; see 'ERROR_multiple_choice.png'!")
        return False
