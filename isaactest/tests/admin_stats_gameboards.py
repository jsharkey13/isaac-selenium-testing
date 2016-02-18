import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["admin_stats_gameboards"]


#####
# Test : Admin Stats Analytics Page
#####
@TestWithDependency("ADMIN_STATS_GAMEBOARDS", ["ADMIN_STATS_ANALYTICS"])
def admin_stats_gameboards(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if admin stats gameboards page works.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB + "/admin/stats")
    time.sleep(WAIT_DUR)
    try:
        gameboards_button = driver.find_element_by_xpath("//a[@ui-sref='adminStats.popularGameboards']")
        gameboards_button.click()
        log(INFO, "Clicked 'Show Gameboard Data' button.")
        wait_for_xpath_element(driver, "//h2[contains(text(), 'Gameboards By Popularity ')]")
    except NoSuchElementException:
        log(ERROR, "Can't find 'Gameboard Data' button; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Gameboard stats page didn't load after clicking button; can't continue!")
        return False

    try:
        log(INFO, "Page loaded. Try finding data about sample board.")
        connected_text = driver.find_element_by_xpath("//tr/td[text()='Equation Editor Beta Questions']/../td[3]").text
        connected_count = int(connected_text)
        assert connected_count > 0, "Expected connected user count to be > 0, got '%s'!" % connected_count
        log(INFO, "Found gameboard data. Sample: %s users connected to 'Equation Editor Beta' board." % connected_count)
    except NoSuchElementException:
        log(ERROR, "Can't find 'Equation Editor Beta' gameboard; can't continue!")
        return False
    except (ValueError, IndexError):
        log(ERROR, "Can't extract answer attempt count from string '%s'; can't continue!" % connected_text)
        return False
    except AssertionError, e:
        log(ERROR, e.message)
        return False

    log(PASS, "Admin Stats Gameboard page contains info as expected.")
    return True
