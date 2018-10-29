import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..utils.isaac import open_accordion_section
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["numeric_q_units_select"]


#####
# Test : Numeric Question Units Dropdown
#####
@TestWithDependency("NUMERIC_Q_UNITS_SELECT", ["ACCORDION_BEHAVIOUR"])
def numeric_q_units_select(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if the units dropdown on numeric questions works as expected.

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
        log(INFO, "Accordion opened, numeric question displayed.")
    except NoSuchElementException:
        log(ERROR, "Can't find third accordion section to open; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_units_select")
        log(ERROR, "Accordion section did not open to display the numeric question; see 'ERROR_numeric_q_units_select.png'!")
        return False
    try:
        units_dropdown = num_question.find_element_by_xpath("//button[@ng-click='ctrl.showUnitsDropdown()']")
        units_dropdown.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Clicked to open units dropdown.")
        left = int(float(num_question.find_element_by_xpath(".//ul[contains(@class, 'f-dropdown')]").value_of_css_property('left').replace('px', '')))
        assert left > 0
        log(INFO, "Units dropdown displayed correctly.")
    except AssertionError:
        log(ERROR, "Units dropdown not opened correctly!")
        return False
    except NoSuchElementException:
        log(ERROR, "Can't find numeric question or units dropdown button; can't continue!")
        return False
    except ValueError:
        log(ERROR, "Couldn't read the CSS property 'left' for the dropdown. This probably constitues failure!")
        return False
    try:
        units_dropdown.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Clicked to close units dropdown.")
        left = int(num_question.find_element_by_xpath(".//ul[@class='f-dropdown']").value_of_css_property('left').replace('px', ''))
        assert left < 9000
        log(INFO, "Units dropdown hidden correctly.")
        log(PASS, "Numeric question units popup works correctly.")
        return True
    except AssertionError:
        log(ERROR, "Units dropdown did not close correctly!")
        return False
    except ValueError:
        log(ERROR, "Couldn't read the CSS property 'left' for the dropdown. This probably constitues failure!")
        return False
