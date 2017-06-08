import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, wait_for_xpath_element
from ..utils.isaac import open_accordion_section, wait_accordion_open
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException, TimeoutException

__all__ = ["figure_behaviour"]


#####
# Test : Figure Numbering and Referencing on Question Pages
#####
@TestWithDependency("FIGURE_BEHAVIOUR", ["ACCORDION_BEHAVIOUR", "TAB_BEHAVIOR", "QUICK_QUESTIONS"])
def figure_behaviour(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether the figure numbering and referencing work as expected.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/questions/_regression_test_")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/questions/_regression_test_"))
    time.sleep(WAIT_DUR)

    try:
        log(INFO, "Figure numbering examples in accordion 6.")
        accordion_6 = open_accordion_section(driver, 6)
        wait_accordion_open(driver, 6)
        time.sleep(WAIT_DUR)

        log(INFO, "Checking \\ref{...} gets correctly transformed.")
        intro_text_p = accordion_6.find_elements_by_xpath(".//p")[0]
        intro_text = str(intro_text_p.text)
        assert "Figure" in intro_text and "\\ref" not in intro_text, "Expected figure references to be expanded!"
        assert "Figure 2, Figure 3 and Figure 4" in intro_text, "Expected figure references in order, found '%s'!" % intro_text

        log(INFO, "References work as expected, checking figure numbering for side by side figs.")
        figure_titles = accordion_6.find_elements_by_xpath(".//figcaption/div/strong")
        assert len(figure_titles) == 7, "Expected to find 7 figures in last accordion section!"
        side_by_side_figs = [str(element.text) for element in figure_titles[:3]]
        expected_side_by_side = ["Figure 2", "Figure 3", "Figure 4"]
        assert side_by_side_figs == expected_side_by_side, "Expected figure numbering in order for side by side figures, found '%s'!" % side_by_side_figs

        log(INFO, "Side by side figures numbered correctly, checking figures in tabs.")
        tab_buttons = accordion_6.find_elements_by_xpath(".//dd[@ng-click='activateTab($index)']")
        assert len(tab_buttons) == 3, "Expected to find 3 tabs in accordion section 6, found %d!" % len(tab_buttons)
        fig_title_5 = str(tab_buttons[0].find_element_by_xpath("../..//div[contains(@class, 'active')]//figcaption/div/strong").text)
        assert fig_title_5 == "Figure 5", "Expected figure in first tab to be figure 5, found '%s'!" % fig_title_5
        log(INFO, "Changing to tab 2.")
        tab_buttons[1].click()
        time.sleep(WAIT_DUR)
        fig_title_6 = str(tab_buttons[1].find_element_by_xpath("../..//div[contains(@class, 'active')]//figcaption/div/strong").text)
        assert fig_title_6 == "Figure 6", "Expected figure in second tab to be figure 6, found '%s'!" % fig_title_6
        log(INFO, "Changing to tab 3.")
        tab_buttons[2].click()
        time.sleep(WAIT_DUR)
        show_button = tab_buttons[2].find_element_by_xpath("../../div/div//div[@ng-click='isVisible=!isVisible']")
        show_button.click()
        log(INFO, "Checking figure inside a quick question.")
        time.sleep(WAIT_DUR)
        fig_title_7 = str(show_button.find_element_by_xpath("..//figcaption/div/strong").text)
        assert fig_title_7 == "Figure 7", "Expected figure in final tab quick question to be figure 7, found '%s'!" % fig_title_7

        log(INFO, "Figures in tabs and quick questions work correctly, checking detailed captions.")
        last_fig_cap = str(figure_titles[-1].text)
        assert last_fig_cap == "Figure 8", "Expected final figure on page to be figure 8, found '%s'!" % last_fig_cap
        long_captions = driver.find_elements_by_xpath("//div[contains(@class, 'caption')]//p")
        n_caps = len(long_captions)
        assert n_caps == 8, "Expected the 8 detailed captions, found %d!" % n_caps
        last_long_caption = str(long_captions[7].text)
        assert "This should be Figure 8." in last_long_caption, "Expected last detailed figure caption to mention Figure 8!"
        log(INFO, "Detailed captions are shown correctly.")

    except NoSuchElementException:
        log(ERROR, "Can't find required element, can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Accordion section didn't open; can't continue!")
        return False
    except IndexError:
        log(ERROR, "Can't find intro text in accordion section 6!")
        return False
    except AssertionError as e:
        log(ERROR, e.message)
        return False

    log(PASS, "Figure numbering, referencing and captioning work as expected.")
    return True
