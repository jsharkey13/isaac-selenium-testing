import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import get_hexagon_properties
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException

__all__ = ["back_to_board"]


#####
# Test : Back to Board Button
#####
@TestWithDependency("BACK_TO_BOARD")
def back_to_board(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether the back to board button works.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB)
    log(INFO, "Got: %s" % ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        questions_tab = driver.find_element_by_xpath("//a[@ui-sref='gameBoards']")
        questions_tab.click()
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't find 'Questions' tab link; can't continue!")
        return False
    try:
        url = driver.current_url
        log(INFO, "Currently on '%s', attempt to access 5 hexagons." % url)
        for i in range(5):
            hexagons = driver.find_elements_by_xpath("//a[@class='ru-hex-home-content']")  # This has to be inside the loop
            hexagon = get_hexagon_properties(hexagons[i])                                  # so that we don't get stale elements.
            log(INFO, "Got hexagon %s." % (i + 1))
            if hexagon["type"] == "Question":
                hexagons[i].click()
                log(INFO, "Hexagon is a question; clicked on it.")
                time.sleep(WAIT_DUR)
                back_to_board_button = driver.find_element_by_xpath("//a[@ng-click='backToBoard()']")
                back_to_board_button.click()
                log(INFO, "Clicked back to board button.")
                time.sleep(WAIT_DUR)
                assert driver.current_url == url, "Expected to end on '%s', actually ended on '%s'!" % (url, driver.current_url)
        log(PASS, "Back to board button worked as expected.")
        return True
    except NoSuchElementException:
        image_div(driver, "ERROR_back_to_board")
        log(ERROR, "Couldn't find 'Back to Board' button; see 'ERROR_back_to_board.png'! Can't continue!")
        return False
    except AssertionError, e:
        image_div(driver, "ERROR_back_to_board")
        log(ERROR, "Back to board button failed! %s" % e.message)
        return False
    except IndexError:
        log(ERROR, "Not enough hexagons to click; can't continue!")
        return False
