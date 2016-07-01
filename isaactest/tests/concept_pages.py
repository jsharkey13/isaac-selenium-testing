import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import assert_logged_out
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException
__all__ = ['concept_pages']

@TestWithDependency('CONCEPT_PAGES', ['LOGIN'])
def concept_pages(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether users can sign out of Isaac.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    driver.get(ISAAC_WEB + '/concepts')
    # navigate to a maths concept
    try:
        time.sleep(WAIT_DUR)
        first_maths_concept = driver.find_element_by_xpath("//a[@class='ru-mobile-answer-wrap ng-scope maths'][1]")
        id = first_maths_concept.get_attribute("href").replace(ISAAC_WEB, "")
        first_maths_concept.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Navigating to maths concept: " + id)
        assert driver.current_url == (ISAAC_WEB + id)
        log(INFO, "Successfully navigated to a maths concept page.")
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(INFO, "Unable to select the first maths concept")
        return False
    except AssertionError:
        log(INFO, "Failed to navigate to the first maths concept page!")
        return False
    # navigate to a physics concept
    try:
        driver.get(ISAAC_WEB + '/concepts')
        time.sleep(WAIT_DUR)
        first_physics_concept = driver.find_element_by_xpath("//a[@class='ru-mobile-answer-wrap ng-scope physics'][1]")
        id = first_physics_concept.get_attribute("href").replace(ISAAC_WEB, "")
        first_physics_concept.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Navigating to physics concept: " + id)
        assert driver.current_url == (ISAAC_WEB + id)
        log(INFO, "Successfully navigated to a physics concept page.")
        time.sleep(WAIT_DUR)
        log(PASS, "Both Maths & Physics concepts are visible and can be reached from the concepts page.")
        return True
    except NoSuchElementException:
        log(INFO, "Unable to select the first physics concept")
        log(ERROR, "Failed to find both Physics and Maths concepts.")
        return False
    except AssertionError:
        log(INFO, "Failed to navigate to the first physics concept page!")
        log(ERROR, "Failed to reach both Physics and Maths pages from the concept page.")
        return False

