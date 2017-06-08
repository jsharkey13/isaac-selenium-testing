import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException, TimeoutException

__all__ = ["concept_index_page"]


#####
# Test : Concept Index Page
#####
@TestWithDependency("CONCEPT_INDEX_PAGE")
def concept_index_page(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether the concept index page works as expected.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB)
    log(INFO, "Returning to homepage.")
    time.sleep(WAIT_DUR)
    try:
        log(INFO, "Attempting to click 'Concepts' tab button.")
        concept_button = driver.find_element_by_xpath("//div[@class='ru-desktop-nav']//a[@ui-sref='conceptIndex']")
        concept_button.click()
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't find concepts button; can't continue!")
        return False

    try:
        wait_for_xpath_element(driver, "//h1[@class='h1-concept-index']")
        log(INFO, "Concepts tab button worked.")
        concept_page_links = driver.find_elements_by_xpath("//a[contains(@ng-repeat, 'filteredConcepts')]")
        num_concept_pages = len(concept_page_links)
        assert num_concept_pages > 0, "Expected concept pages to be listed, none found!"
        log(INFO, "Found %d concept pages in index list." % num_concept_pages)

        log(INFO, "Checking that concept filtering works as expected.")
        concept_filter_box = driver.find_element_by_xpath("//input[@ng-model='searchText']")
        concept_filter_box.send_keys("newton")
        time.sleep(WAIT_DUR)

        filtered_links = driver.find_elements_by_xpath("//a[contains(@ng-repeat, 'filteredConcepts')]")
        num_filtered_newton = len(filtered_links)
        correctly_filtered = num_filtered_newton >= 3 and num_filtered_newton < num_concept_pages
        assert correctly_filtered, "Expected to find Newton's Laws concept pages when searching for 'newton'; found %d results!" % num_filtered_newton
        log(INFO, "Filtered by 'newton', found %d results." % num_filtered_newton)
        concept_filter_box.clear()
        log(INFO, "Clearing text filter.")
        time.sleep(WAIT_DUR)
    except TimeoutException:
        log(ERROR, "Concept index didn't load, can't continue!")
        return False
    except NoSuchElementException:
        log(ERROR, "Can't find concept filter box, can't continue!")
        return False
    except AssertionError as e:
        log(ERROR, e.message)
        return False

    try:
        log(INFO, "Checking both physics and maths concepts are shown initially.")
        unfiltered_phys_titles = driver.find_elements_by_xpath("//h4/span[@ng-show='physics']")
        unfiltered_maths_titles = driver.find_elements_by_xpath("//h4/span[@ng-show='maths']")
        phys_displayed = any([element.is_displayed() for element in unfiltered_phys_titles])
        maths_displayed = any([element.is_displayed() for element in unfiltered_maths_titles])
        assert phys_displayed and maths_displayed, "Expected to see both maths and physics concepts initially!"

        include_physics = driver.find_element_by_xpath("//input[@id='includePhysics']")
        include_maths = driver.find_element_by_xpath("//input[@id='includeMaths']")
        assert include_physics.is_selected(), "Expected 'Include Physics' to be ticked by default!"
        log(INFO, "Physics and Maths concepts shown initially, now try filter by Physics only.")
        include_maths.click()
        time.sleep(WAIT_DUR)

        phys_titles = driver.find_elements_by_xpath("//h4/span[@ng-show='physics']")
        is_physics_concept = [element.is_displayed() for element in phys_titles]
        assert len(phys_titles) > 0 and all(is_physics_concept), "Expected filter to only show Physics concepts; some non-Physics concepts shown!"
        log(INFO, "Filtering by subject works as expected; found %d Physics concepts." % len(phys_titles))
    except NoSuchElementException:
        log(ERROR, "Can't find subject filter boxes; can't continue!")
        return False
    except AssertionError as e:
        log(ERROR, e.message)
        return False

    log(PASS, "Concept index page works as expected.")
    return True
