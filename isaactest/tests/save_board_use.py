import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import assert_logged_out
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException
__all__ = ['save_board_add']

@TestWithDependency('SAVE_BOARD_USE', ['LOGIN'])
def save_board_use(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether users can sign out of Isaac.
    
        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    try:
        menu = driver.find_element_by_xpath("//button[@id='menu-button-dekstop']")
        menu.click()
        time.sleep(WAIT_DUR)
        myprogress_button = driver.find_element_by_xpath("//a[@ui-sref='boards']")
        myprogress_button.click()
        time.sleep(WAIT_DUR)
        assert driver.current_url == ISAAC_WEB + '/boards'
        log(INFO, 'Navigated to boards page successfully.')
    except NoSuchElementException:
        log(INFO, "Couldn't navigate to the boards page!")
        return False

    try:
        second_block = driver.find_element_by_xpath("//li[@ng-model='boards'][2]//a[@class='board-title-link ng-binding']")
        href = driver.find_element_by_xpath("//li[@ng-model='boards'][2]//a[@class='board-share']").get_attribute('sharelink')
        time.sleep(WAIT_DUR)
        print href[6:]
        second_block.click()
        time.sleep(WAIT_DUR)
        assert driver.current_url == ISAAC_WEB + '/gameboards#' + href[6:]
    except NoSuchElementException:
        log(INFO, 'Failed to navigate to the first block on the page.')
        return False

    try:
        hexagon = driver.find_element_by_xpath("//a[@class='ru-hex-home-content'][1]")
        hexagon.click()
        log(INFO, 'Hexagon question tiles function as expected.')
    except NoSuchElementException:
        log(INFO, 'Failed to navigate to the first question on the page.')
        return False

    try:
        time.sleep(WAIT_DUR)
        back = driver.find_element_by_xpath("//a[@ng-click='backToBoard()']")
        back.click()
        log(INFO, 'Successfully moved back to boards page!')
    except NoSuchElementException:
        log(INFO, 'Failed to find the back to board button!')
        return False

    try:
        menu = driver.find_element_by_xpath("//button[@id='menu-button-dekstop']")
        menu.click()
        time.sleep(WAIT_DUR)
        myprogress_button = driver.find_element_by_xpath("//a[@ui-sref='boards']")
        myprogress_button.click()
        time.sleep(WAIT_DUR)
        assert driver.current_url == ISAAC_WEB + '/boards'
        log(INFO, 'Navigated to boards page successfully.')
    except NoSuchElementException:
        log(INFO, "Couldn't navigate to the boards page!")
        return False

    try:
        time.sleep(WAIT_DUR)
        assert driver.find_element_by_xpath("//li[@ng-model='boards'][1]//a[@class='board-share']").get_attribute('sharelink') == href
        log(INFO, 'Board has saved successfully!')
        log(PASS, 'Board saving functionality works correctly.')
        return True
    except NoSuchElementException:
        log(ERROR, 'Failure to save board. ')
        return False
