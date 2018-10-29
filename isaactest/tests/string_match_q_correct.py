import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import open_accordion_section
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["string_match_q_correct"]


#####
# Test : String Match Questions Correct
#####
@TestWithDependency("STRING_MATCH_Q_CORRECT", ["ACCORDION_BEHAVIOUR"])
def string_match_q_correct(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if text entry questions work correctly.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)

    driver.get(ISAAC_WEB + "/questions/_regression_test_")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/questions/_regression_test_"))
    time.sleep(WAIT_DUR)

    try:
        open_accordion_section(driver, 6)
        time.sleep(WAIT_DUR)
        stringmatch_question = wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacStringMatchQuestion']")
        log(INFO, "Accordion opened, string match question displayed.")
        text_input = stringmatch_question.find_elements_by_xpath(".//input[@ng-model='ctrl.selectedValue']")[0]
    except NoSuchElementException:
        log(ERROR, "Can't find sixth accordion section to open; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Accordion section did not open to display the string match question; can't continue!")
        return False
    except IndexError:
        log(ERROR, "Could not find text entry box for string match question. Can't continue!")
        return False

    text_input.clear()
    text_input.send_keys("hello")
    log(INFO, "Typing answer into text entry box.")
    time.sleep(WAIT_DUR)

    try:
        check_answer_button = stringmatch_question.find_element_by_xpath(".//button[text()='Check my answer']")
        check_answer_button.click()
        log(INFO, "Clicked 'Check my answer'.")
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Couldn't click the 'Check my answer' button; can't continue!")
        return False

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacStringMatchQuestion']//h1[text()='Correct!']")
        log(INFO, "A 'Correct!' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacStringMatchQuestion']//p[text()='This needs a lower case \"h\".'])[2]")
        log(INFO, "The editor entered explanation text was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacStringMatchQuestion']//strong[text()='Well done!']")
        log(INFO, "The 'Well done!' message was correctly shown.")

        log(PASS, "String Match Question 'correct answer' behavior as expected.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_string_match_submit")
        log(ERROR, "The messages shown for a correct answer were not all displayed; see 'ERROR_string_match_submit.png'!")
        return False
