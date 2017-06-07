import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, wait_for_xpath_element
from ..utils.isaac import open_accordion_section, wait_accordion_open
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException, TimeoutException

__all__ = ["concept_pages"]


#####
# Test : Concept Pages
#####
@TestWithDependency("CONCEPT_PAGES", ["CONCEPT_INDEX_PAGE", "ACCORDION_BEHAVIOUR"])
def concept_pages(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether the concept pages work as expected.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB)
    log(INFO, "Returning to homepage.")
    time.sleep(WAIT_DUR)
    try:
        log(INFO, "Click the 'Concepts' tab button.")
        concept_button = driver.find_element_by_xpath("//div[@class='ru-desktop-nav']//a[@ui-sref='conceptIndex']")
        concept_button.click()
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't find concepts button; can't continue!")
        return False

    try:
        wait_for_xpath_element(driver, "//h1[@class='h1-concept-index']")
        log(INFO, "Filtering concepts to find the 'Fields' concept page.")
        concept_filter_box = driver.find_element_by_xpath("//input[@ng-model='searchText']")
        concept_filter_box.send_keys("Fields")
        time.sleep(WAIT_DUR)

        field_button = driver.find_element_by_xpath("//a[contains(@ng-repeat, 'filteredConcepts')]//h4[text()[contains(.,'Fields')]]")
        field_button.click()
        log(INFO, "Clicking on 'Fields' concept page.")
        time.sleep(WAIT_DUR)
    except TimeoutException:
        log(ERROR, "Concept Index didn't load; can't continue!")
        return False
    except NoSuchElementException:
        log(ERROR, "Can't find 'Fields' concept page; can't continue!")
        return False

    try:
        log(INFO, "Checking page content has loaded.")
        first_paragraph = driver.find_element_by_xpath("//div[@isaac-content]//p")
        fields_text = str(first_paragraph.text).lower()
        assert "field" in fields_text, "Expected to find introductory text; it did not contain 'field'!"
        log(INFO, "First paragraph contains name of concept as expected.")
    except NoSuchElementException:
        log(ERROR, "Can't find first paragraph, can't continue!")
        return False
    except AssertionError as e:
        log(ERROR, e.message)

    try:
        log(INFO, "Checking accordions are displayed as expected.")
        accordion_level_element = driver.find_element_by_xpath("//div[contains(@class, 'ru_accordion_name')]")
        assert accordion_level_element.is_displayed(), "Expected to see level indicators on accordion sections!"
        accordion_level = int(accordion_level_element.text)
        assert accordion_level > 0 and accordion_level <= 6, "Expected to find a valid content level on accordion bar!"

        open_accordion_section(driver, 1)
        wait_accordion_open(driver, 1)
        first_section_p = driver.find_elements_by_xpath("//dd[@ng-repeat='c in doc.children']//p")[0]
        first_section_text = str(first_section_p.text).lower()
        assert "field" in first_section_text, "Expected to find text in first accordion section; didn't find 'field'!"
        log(INFO, "Concept accordion contain level information and content.")
    except NoSuchElementException:
        log(ERROR, "Can't find accordion, can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Accordion didn't open; can't continue!")
        return False
    except AssertionError as e:
        log(ERROR, e.message)
        return False
    except IndexError:
        log(ERROR, "Can't find text of first accordion section, can't continue!")
        return False

    log(PASS, "Concept pages work as expected.")
    return True
