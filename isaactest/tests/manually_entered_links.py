import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..utils.isaac import open_accordion_section, close_accordion_section
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["manually_entered_links"]


#####
# Test : Check Manually Entered Links Work
#####
@TestWithDependency("MANUALLY_ENTERED_LINKS", ["ACCORDION_BEHAVIOUR", "TAB_BEHAVIOUR"])
def manually_entered_links(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if manually entered links in hints and pages work. Also check "Back to Question" button.

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
    url_before = str(driver.current_url)
    log(INFO, "Open third accordion section, then open hint.")
    try:
        close_accordion_section(driver, 1)
        open_accordion_section(driver, 3)
        time.sleep(WAIT_DUR)
        num_q = wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']")
        log(INFO, "Got question, opening hint.")
        hint_buttons = num_q.find_elements_by_xpath(".//a[contains(text(), 'Hint ')]/..")
        hint_buttons[0].click()
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't find accordion title bar to click; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Accordion section did not open correctly; can't continue!")
        return False
    try:
        concepts = num_q.find_elements_by_xpath(".//p/a[contains(@href, '/concepts/')]")
        assert len(concepts) == 3, "Expected to find 3 concept links, found %s!" % len(concepts)
        concepts[1].click()
        log(INFO, "Click concept a page link.")
        time.sleep(WAIT_DUR)
        wait_for_xpath_element(driver, "//h3[@class='subheader']/strong[contains(text(), 'Concept')]")
        log(INFO, "Taken to a concept page as expected.")
        back_to_q = driver.find_element_by_xpath("(//a[@ng-if='backButtonVisible']//em[text()='Back to your question'])[1]")
        back_to_q.click()
        log(INFO, "Click 'Back to question' button.")
        time.sleep(WAIT_DUR)
        assert url_before in str(driver.current_url), "Expected to be taken back to '%s', got '%s' instead!" % (url_before, driver.current_url)
        log(INFO, "Taken back to starting page as expected.")
    except TimeoutException:
        image_div(driver, "ERROR_link_concept_page")
        log(ERROR, "Concept page didn't load; see 'ERROR_link_concept_page.png'!")
        return False
    except AssertionError, e:
        log(ERROR, e.message)
        return False

    log(PASS, "Manually entered link behavior is as expected.")
    return True
