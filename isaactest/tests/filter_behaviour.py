import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import clear_question_filter, set_filter_state, get_hexagon_properties
from ..utils.i_selenium import assert_tab
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["filter_behaviour"]


######
# Test : Check Filter Behaviour
######
@TestWithDependency("FILTER_BEHAVIOUR")
def filter_behaviour(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test the behavior of the gameboard filter for subjects and levels.

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
    success = set_filter_state(driver, ["Physics", "Mechanics", "Dynamics"], [1], WAIT_DUR)
    if not success:
        log(ERROR, "Failed to set required filter state; can't complete test!")
        return False

    try:
        time.sleep(WAIT_DUR)
        hexagons = driver.find_elements_by_xpath("//a[@class='ru-hex-home-content']")
        assert len(hexagons) == 11, "Expected 11 hexagons, got %s; can't continue!" % len(hexagons)
        hexagons = map(get_hexagon_properties, hexagons)
        for h in hexagons:
            if h["type"] == "Question":
                assert h["topic"] == "Dynamics", "Unexpected question with topic '%s' in Dynamics questions!" % h["topic"]
                assert h["level"] == 1, "Unexpected question with level '%s' in Dynamics Level 1 questions!" % h["level"]
        log(INFO, "Filter worked for Dynamics Level 1 questions.")

        tag_state = ["Physics", "Mechanics", "Waves"]
        levels = [1, 3, 6]
        clear_question_filter(driver, WAIT_DUR)
        set_filter_state(driver, tag_state, levels, WAIT_DUR)
        hexagons = driver.find_elements_by_xpath("//a[@class='ru-hex-home-content']")
        hexagons = map(get_hexagon_properties, hexagons)
        for h in hexagons:
            if h["type"] == "Question":
                assert h["field"] in tag_state, "Unexpected question with field '%s' in %s questions!" % (h["field"], tag_state)
                assert h["level"] in levels, "Unexpected question with level '%s' in Level %s questions!" % (h["level"], levels)
        log(INFO, "Behaviour for %s questions in levels %s as expected." % (tag_state, levels))

        log(PASS, "Filter behaviour as expected.")
        return True
    except AssertionError, e:
        log(ERROR, e.message)
        return False
