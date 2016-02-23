import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["admin_stats_schools"]


#####
# Test : Admin Stats Analytics Page - School Stats
#####
@TestWithDependency("ADMIN_STATS_SCHOOLS", ["ADMIN_STATS_GAMEBOARDS"])
def admin_stats_schools(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if admin stats schools info page works.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB + "/admin/stats")
    time.sleep(WAIT_DUR)
    try:
        gameboards_button = driver.find_element_by_xpath("//a[@ui-sref='adminStats.schoolUserSummaryList']")
        gameboards_button.click()
        log(INFO, "Clicked 'Show School Data' button.")
        wait_for_xpath_element(driver, "//h2[contains(text(), 'Schools By User Links ')]")
    except NoSuchElementException:
        log(ERROR, "Can't find 'School Data' button; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "School stats page didn't load after clicking button; can't continue!")
        return False

    try:
        log(INFO, "Page loaded; try finding info about Uni of Cam.")
        connected_text = driver.find_element_by_xpath("//tr/td[text()='University of Cambridge']/../td[5]").text
        connected_count = int(connected_text)
        assert connected_count > 0, "Expected connected user count to be > 0, got '%s'!" % connected_count
        log(INFO, "Found schools data. Sample: %s users at 'University of Cambridge'." % connected_count)
    except NoSuchElementException:
        log(ERROR, "Can't find 'University of Cambridge' in school list; can't continue!")
        return False
    except (ValueError, IndexError):
        log(ERROR, "Can't extract connected user count from string '%s'; can't continue!" % connected_text)
        return False
    except AssertionError, e:
        log(ERROR, e.message)
        return False

    try:
        log(INFO, "Try looking at school detail page linked to by URN column.")
        school_detail_link = str(driver.find_element_by_xpath("//tr/td[text()='University of Cambridge']/..//a").get_attribute("href"))
        driver.get(school_detail_link)
        log(INFO, "Got: '%s'" % (school_detail_link))
        time.sleep(WAIT_DUR)
        rows = driver.find_elements_by_xpath("//div/h2[contains(text(), 'University of Cambridge')]/..//..//table//tr")
        assert len(rows) == connected_count + 1, "Expected to find %s users, found %s!" % (connected_count, len(rows) - 1)
        log(INFO, "School detail page displays expected number of users.")

        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logging out any logged in user.")
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(INFO, "Can't find school detail link; can't continue!")
        return False

    log(PASS, "Admin Stats Schools page contains info as expected.")
    return True
