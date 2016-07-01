import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import assert_logged_out
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException, WebDriverException
__all__ = ['rename_other_board']

@TestWithDependency('RENAME_OTHER_BOARD', ['LOGIN'])
def rename_other_board(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """ Test whether it is possible to rename another user's board by clicking on the title

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    board_default = "/gameboards#eqn_editor_beta"
    driver.get(ISAAC_WEB + board_default)
    time.sleep(WAIT_DUR)
    try:
        title = driver.find_element_by_xpath("//h2[@ng-click='editedGameBoardTitle=(user._id == gameBoard.ownerUserId ? (gameBoard.title || generateGameBoardTitle(gameBoard)) : null)']")
        title.click()
        log(ERROR, "Element is clickable")
        return False
    except WebDriverException:
        log(PASS, "Element is not clickable")
        return True


