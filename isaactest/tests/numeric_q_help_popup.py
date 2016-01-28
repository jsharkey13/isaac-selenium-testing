import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..utils.isaac import open_accordion_section
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["numeric_q_help_popup"]


#####
# Test : Numeric Questions Help Popup
#####
@TestWithDependency("NUMERIC_Q_HELP_POPUP", ["ACCORDION_BEHAVIOUR"])
def numeric_q_help_popup(driver, ISAAC_WEB, WAIT_DUR):
    """Test if the mouseover help popup on numeric questions works.

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
        open_accordion_section(driver, 3)
        time.sleep(WAIT_DUR)
        num_question = wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']")
        log(INFO, "Accordion opened, multiple choice question displayed.")
    except NoSuchElementException:
        log(ERROR, "Can't find third accordion section to open; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_help_popup")
        log(ERROR, "Accordion section did not open to display the numeric question; see 'ERROR_numeric_q_help_popup.png'!")
        return False
    try:
        help_mark = num_question.find_element_by_xpath("//span[@class='value-help']")
        help_mark.click()
        wait_for_xpath_element(driver, "//span[@class='value-help']/div[@class='popup']")
        log(INFO, "Help message correctly shown on mouseover.")
        log(PASS, "Numeric question help message displays.")
        return True
    except NoSuchElementException:
        log(ERROR, "Couldn't find help button; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Help message popup not shown!")
        return False
