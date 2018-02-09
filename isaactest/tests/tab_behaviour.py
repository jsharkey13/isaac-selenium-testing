import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab
from ..utils.i_selenium import wait_for_xpath_element
from ..utils.isaac import open_accordion_section, close_accordion_section
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["tab_behavior"]


#####
# Test : Accordion Sections Open and Close
#####
@TestWithDependency("TAB_BEHAVIOUR", ["ACCORDION_BEHAVIOUR"])
def tab_behavior(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if tabs can be used as expected.

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
    try:
        close_accordion_section(driver, 1)
        open_accordion_section(driver, 2)
        mc_question = wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']")
        hint_buttons = mc_question.find_elements_by_xpath(".//a[contains(text(), 'Hint ')]/..")
        assert len(hint_buttons) == 2
    except TimeoutException:
        log(ERROR, "Can't access multiple choice question; can't continue!.")
        return False
    except AssertionError:
        log(ERROR, "Expected 2 hint tabs, found %s! Can't continue!" % len(hint_buttons))
        return False
    try:
        time.sleep(WAIT_DUR / 10.0)  # Don't need to wait ages, but race condition occasionally!
        log(INFO, "Attempt to access Hint 1.")
        hint_buttons[0].click()
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//p[contains(text(), 'This is Hint 1.')]")
        log(INFO, "Hint 1 opens correctly. Try clicking the tab again.")
        hint_buttons[0].click()
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//p[text()='This is Hint 1.']")
        time.sleep(WAIT_DUR / 10.0)
        log(INFO, "Hint 1 remains open. Try clicking Hint 2.")
        hint_buttons[1].click()
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//p[contains(text(), 'This is Hint 2. It contains a figure!')]")
        log(INFO, "Hint 2 opens correctly, check if its figure is displayed correctly.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//figure[contains(@class, 'ru_figure')]/..")
        fig_caption = mc_question.find_element_by_xpath(".//figure[contains(@class, 'ru_figure')]/..//p")
        log(INFO, "Figure and caption displayed.")
        assert "This is a figure caption!" in str(fig_caption.text)
        log(INFO, "Caption text is as expected.")
    except TimeoutException:
        log(ERROR, "Couldn't access all tabs, or their content wasn't correctly displayed!")
        return False
    except AssertionError:
        log(ERROR, "Figure caption did not match expected caption!")
        return False
    try:
        close_accordion_section(driver, 2)
        time.sleep(WAIT_DUR)
        open_accordion_section(driver, 3)
        time.sleep(WAIT_DUR)
        num_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacNumericQuestion']")
        hint_buttons = num_question.find_elements_by_xpath(".//a[contains(text(), 'Hint ')]/..")
        log(INFO, "Try cycling through all hints.")
        for i, hint in enumerate(hint_buttons):
            n = i + 1
            hint.click()
            wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//p[contains(text(), 'This is Hint %s.')]" % n)
            time.sleep(WAIT_DUR / 10.0)
        log(INFO, "All numeric question hints loaded successfully.")
        log(PASS, "Tab behaviour as expected.")
        return True
    except NoSuchElementException:
        log(ERROR, "Couldn't find numeric question; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "A hint didn't load correctly; can't continue!")
        return False
