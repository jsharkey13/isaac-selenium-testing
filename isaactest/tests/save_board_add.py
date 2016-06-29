import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import assert_logged_out
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException
__all__ = ['progress_page']

@TestWithDependency('SAVE_BOARD_ADD', ['LOGIN'])
def save_board_add(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether users can sign out of Isaac.
    
        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    driver.get(ISAAC_WEB + '/gameboards')
    try:
        previous_url = driver.current_url
        refresh = driver.find_element_by_xpath("//a[@ng-click='shuffleBoard()']")
        refresh.click()
        time.sleep(WAIT_DUR)
        assert previous_url != driver.current_url
        log(INFO, 'Board successfully refreshed.')
    except NoSuchElementException:
        log(INFO, 'Cannot click refresh button')
        return False
    except AssertionError:
        log(INFO, 'Refresh of board has failed.')
        return False

    try:
        board = driver.find_element_by_xpath("//a[contains(text(), 'Add to My Boards')]")
        board_id = board.get_attribute('href')[47:]
        log(INFO, 'Found board ID to be added: ' + board_id)
        board.click()
        time.sleep(WAIT_DUR)
        log(INFO, 'Clicked add to my boards.')
        time.sleep(WAIT_DUR)
        assert driver.current_url == ISAAC_WEB + '/boards'
    except NoSuchElementException:
        log(INFO, 'Failed to add ' + board_id + ' to my boards!')
        return False

    try:
        latest_board = driver.find_element_by_xpath("//li[@ng-model='boards'][1]//a[@class='board-share']")
        most_recent_board = latest_board.get_attribute('sharelink')[6:]
        log(INFO, 'Most recently added board has ID: ' + most_recent_board)
        assert most_recent_board == board_id
        time.sleep(WAIT_DUR)
        log(PASS, 'Successfully saved new board to my boards!')
        return True
    except NoSuchElementException:
        log(INFO, 'Unable to find latest tile.')
        return False
    except AssertionError:
        log(ERROR, 'Failed to save new board.')
        return False
