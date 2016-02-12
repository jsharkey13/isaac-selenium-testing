import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import clear_question_filter, get_hexagon_properties
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["filter_by_concept"]


######
# Test : Check Filter by Concept Behaviour
######
@TestWithDependency("FILTER_BY_CONCEPT", ["BACK_TO_BOARD"])
def filter_by_concept(driver, ISAAC_WEB, WAIT_DUR):
    """Test the behavior of the gameboard filter for concepts.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/gameboards")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/gameboards"))
    time.sleep(WAIT_DUR)
    try:
        filter_dropdown = driver.find_element_by_id("desktop-reveal")
        filter_dropdown.click()
        time.sleep(WAIT_DUR)
        wait_for_xpath_element(driver, "//div[@class='ru-desktop-panel-content']")
    except NoSuchElementException:
        log(ERROR, "Can't access filter dropdown button!")
        return False
    except TimeoutException:
        log(ERROR, "Filter dropdown didn't show the filter!")
        return False

    clear_question_filter(driver, WAIT_DUR)

    try:
        time.sleep(WAIT_DUR)
        concept_box = driver.find_element_by_xpath("//input[@ng-model='conceptInput']")
        concept_box.send_keys("Conservation of")
        concept = wait_for_xpath_element(driver, "//div[@id='concept-search-data']/div[@ng-click='selectConcept(c.id)']/div[contains(text(), 'Conservation of Energy')]/..")
        concept.click()
        log(INFO, "Selected 'Conservation of Energy'.")
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't find 'Search by concept' box; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Search by concept for 'Conservation of' did not produce expected result; can't continue!")
        return False
    try:
        hexagons = driver.find_elements_by_xpath("//a[@class='ru-hex-home-content']")
        N = len(hexagons)
        for i in range(N):
            h = get_hexagon_properties(hexagons[i])
            if h["type"] == "Question":
                hexagons[i].click()
                log(INFO, "Go to question '%s'." % h["title"])
                time.sleep(WAIT_DUR)
                driver.find_element_by_xpath("//div[contains(@class, 'ru_pod_concepts')]/..//a[text()='Conservation of Energy']")
                back_to_board_button = driver.find_elements_by_xpath("//a[@ng-click='backToBoard()']")[0]
                back_to_board_button.click()
                log(INFO, "Go Back to Board.")
                time.sleep(WAIT_DUR)
                hexagons = driver.find_elements_by_xpath("//a[@class='ru-hex-home-content']")  # We have to refresh the now stale elements
                assert len(hexagons) == N
        log(PASS, "Filter by concept behaviour as expected.")
        return True
    except NoSuchElementException:
        image_div(driver, "ERROR_filter_concept")
        log(ERROR, "Can't find 'Conservation of Energy' in related concepts; has search failed?! See 'ERROR_filter_concept.png'!")
        return False
    except IndexError:
        log(ERROR, "Can't find 'Back to Board' button; can't continue!")
        return False
    except AssertionError:
        image_div(driver, "ERROR_filter_concept")
        log(ERROR, "After going back to board, different number of hexagons! Did 'Back to Board' fail?! See 'ERROR_filter_concept.png'!")
        return False
