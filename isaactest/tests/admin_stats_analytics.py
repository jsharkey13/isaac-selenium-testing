import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["admin_stats_analytics"]


#####
# Test : Admin Stats Analytics Page
#####
@TestWithDependency("ADMIN_STATS_ANALYTICS", ["ADMIN_STATS_SUMMARY"])
def admin_stats_analytics(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if admin stats analyitcs page works.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB + "/admin/stats")
    time.sleep(WAIT_DUR)
    try:
        analytics_button = driver.find_element_by_xpath("//a[@ui-sref='adminStats.isaacAnalytics']")
        analytics_button.click()
        log(INFO, "Clicked 'View Analytics' button.")
        wait_for_xpath_element(driver, "//h2[contains(text(), 'Last user locations')]")
    except NoSuchElementException:
        log(ERROR, "Can't find 'Analytics' button; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Analytics page didn't load after clicking button; can't continue!")
        return False

    try:
        locations_button = driver.find_element_by_xpath("//a[@ng-click='getLocationData()']")
        locations_button.click()
        log(INFO, "Click 'Generate Location Data' button.")
        wait_for_xpath_element(driver, "//div[@class='angular-google-map']", 25)
        log(INFO, "Google Map of location data loaded successfully.")
    except NoSuchElementException:
        log(ERROR, "Can't find 'Generate Location Data' button; can't continue testing!")
        return False

    try:
        answer_graph_button = driver.find_element_by_xpath("//div[@ng-show='editingGraph']//li/label[text()='ANSWER_QUESTION']/../input")
        answer_graph_button.click()
        log(INFO, "Added 'ANSWER_QUESTION' events to graph.")
        graph_button = driver.find_elements_by_xpath("//a[@ng-click='updateGraph()']")[0]
        graph_button.click()
        log(INFO, "Clicked to generate graph.")
        wait_for_xpath_element(driver, "//div[@ng-show='questionsAnsweredOverTime']/div[@data='questionsAnsweredOverTime']", 25)
        log(INFO, "A graph was shown as expected.")
    except NoSuchElementException:
        log(ERROR, "Can't find graph tickbox for 'ANSWER_QUESTION' events; can't continue!")
        return False
    except IndexError:
        log(ERROR, "Can't find 'Update Graph' button; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Graph didn't load after clicking 'Update Graph' button; can't continue!")
        return False

    log(PASS, "Admin Stats Analytics page contains info as expected.")
    return True
