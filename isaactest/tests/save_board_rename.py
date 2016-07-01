import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import assert_logged_out
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException
__all__ = ['progress_page']

@TestWithDependency('SAVE_BOARD_RENAME', ['LOGIN'])
def save_board_rename(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test whether users can sign out of Isaac.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    try:
        driver.get(ISAAC_WEB + "/boards")
        assert driver.current_url == ISAAC_WEB + '/boards'
        log(INFO, 'Navigated to boards page successfully.')
    except NoSuchElementException:
        log(INFO, "Couldn't navigate to the boards page!")
        return False



    try:
        time.sleep(WAIT_DUR)
        first_block = driver.find_element_by_xpath("//li[@ng-model='boards'][1]//a[@class='board-title-link ng-binding']")
        href = driver.find_element_by_xpath("//li[@ng-model='boards'][1]//a[@class='board-share']").get_attribute('sharelink')
        time.sleep(WAIT_DUR)
        print href[6:]
        first_block.click()
        time.sleep(WAIT_DUR)
        assert driver.current_url == ISAAC_WEB + '/gameboards#' + href[6:]
    except NoSuchElementException:
        log(INFO, 'Failed to navigate to the first block on the page.')
        return False

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
        log(INFO, "Attempting to rename the current board...")
        time.sleep(WAIT_DUR)
        rename = driver.find_element_by_xpath("//h2[@ng-click='editedGameBoardTitle=(user._id == gameBoard.ownerUserId ? (gameBoard.title || generateGameBoardTitle(gameBoard)) : null)']")
        rename.click()
        time.sleep(WAIT_DUR)
        input = driver.find_element_by_xpath("//input[@ng-model='editedGameBoardTitle']")
        input.clear()
        input.send_keys("Rename test")
        assert input.get_attribute("value") == "Rename test"
        log(INFO, "Board rename was successfull!")
        time.sleep(WAIT_DUR)
    except AssertionError:
        log(INFO, "Failed to rename the board!")
        return False
    except NoSuchElementException:
        log(ERROR, 'Failure to find the input box!')
        return False
    try:
        time.sleep(WAIT_DUR)
        log(INFO, "Attempting to save the renamed board...")
        submit = driver.find_element_by_xpath("//button[@ng-click='saveGameBoardTitle()']")
        submit.click()
        time.sleep(WAIT_DUR)
        board = driver.find_element_by_xpath("//a[contains(text(), 'Add to My Boards')]")
        board_id = board.get_attribute('href')[47:]
        log(INFO, 'Found board ID to be added: ' + board_id)
    except NoSuchElementException:
        log(INFO, "Couldn't save the board.")
        return False
    try:
        time.sleep(WAIT_DUR)
        driver.get(ISAAC_WEB + "/boards")
        time.sleep(WAIT_DUR)
        first_block_name = driver.find_element_by_xpath("//li[@ng-model='boards'][1]//a[@class='board-title-link ng-binding']").text
        assert first_block_name == "Rename test"
        log(INFO, 'Board has saved successfully!')
        log(PASS, 'Board saving functionality works correctly.')
        return True
    except NoSuchElementException:
        log(ERROR, 'Failure to save board. ')
        return False
