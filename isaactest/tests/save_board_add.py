import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, wait_for_xpath_element
from ..utils.isaac import submit_login_form
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException, TimeoutException

__all__ = ['save_board_add']


#####
# Test : Save a Board to My Boards
#####
@TestWithDependency('SAVE_BOARD_ADD', ['LOGIN'])
def save_board_add(driver, ISAAC_WEB, WAIT_DUR, Users, **kwargs):
    """Test whether users can sign out of Isaac.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)
    try:
        driver.get(ISAAC_WEB + "/login")
        time.sleep(WAIT_DUR)
        assert submit_login_form(driver, user=Users.Student, wait_dur=WAIT_DUR)
    except AssertionError:
        log(ERROR, "Can't login, can't continue test!")
        return False
    driver.get(ISAAC_WEB + '/gameboards')
    time.sleep(WAIT_DUR)
    try:
        log(INFO, "Waiting for questions to load.")
        wait_for_xpath_element(driver, "//a[@class='ru-hex-home-content']", duration=15)
        previous_url = driver.current_url
        refresh = driver.find_element_by_xpath("//a[@ng-click='shuffleBoard()']")
        log(INFO, "Refreshing questions.")
        refresh.click()
        time.sleep(WAIT_DUR)
        assert previous_url != driver.current_url
        log(INFO, 'Board successfully refreshed.')
    except TimeoutException:
        log(ERROR, "No gameboard loaded in time! Can't continue!")
        return False
    except NoSuchElementException:
        log(ERROR, "Cannot click refresh board button.")
        return False
    except AssertionError:
        log(ERROR, 'Refresh of board failed.')
        return False

    try:
        board = driver.find_element_by_xpath("//span[contains(text(), 'Save to My Boards')]/..")
        board_id = board.get_attribute('href').split("/add_gameboard/")[1]
        log(INFO, "Found board ID to be added: '%s'." % board_id)
        board.click()
        log(INFO, "Clicked add to my boards, should be redirected to 'My Boards' page.")
        time.sleep(WAIT_DUR)
        assert driver.current_url == ISAAC_WEB + '/boards'
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't find 'Save to My Boards' button; can't continue!")
        return False
    except IndexError:
        log(ERROR, "Board add URL did not contain '/add_gameboard/'!")
        return False
    except AssertionError:
        log(ERROR, "Redirection to 'My Boards' page did not occur!")
        return False

    try:
        most_recent_board_element = driver.find_element_by_xpath("//li[@ng-model='boards'][1]//a[@class='board-share']")
        most_recent_board = most_recent_board_element.get_attribute('sharelink').replace("board/", "")
        log(INFO, "Most recently added board has ID: '%s'." % most_recent_board)
        assert most_recent_board == board_id
        log(INFO, "Most recently added board has the correct ID.")
        time.sleep(WAIT_DUR)
        log(PASS, 'Successfully saved new board to My Boards!')
        return True
    except NoSuchElementException:
        log(INFO, 'Unable to find latest tile.')
        return False
    except AssertionError:
        log(ERROR, 'Failed to save new board.')
        return False
