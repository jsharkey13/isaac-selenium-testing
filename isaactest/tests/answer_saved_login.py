import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form, assert_logged_in
from ..utils.isaac import answer_numeric_q, open_accordion_section
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["answer_saved_login"]


#####
# Test : Anonymous Answers Preserved On Login
#####
@TestWithDependency("ANSWER_SAVED_LOGIN", ["SIGNUP", "NUMERIC_Q_ALL_CORRECT"])
def answer_saved_login(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test that questions answered whilst logged out are retained once logged in.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/questions/_regression_test_")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/questions/_regression_test_"))
    time.sleep(WAIT_DUR)
    try:
        open_accordion_section(driver, 3)
        time.sleep(WAIT_DUR)
        num_question = wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']")
        log(INFO, "Accordion opened, numeric question displayed.")
    except NoSuchElementException:
        log(ERROR, "Can't find third accordion section to open; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_answer_saved_login")
        log(ERROR, "Accordion section did not open to display the numeric question; see 'ERROR_answer_saved_login.png'!")
        return False
    time.sleep(WAIT_DUR)
    try:
        num_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacNumericQuestion']")
    except NoSuchElementException:
        log(ERROR, "Can't find the numeric question; can't continue!")
        return False

    log(INFO, "Attempt to enter correct answer.")
    if not answer_numeric_q(num_question, "2.01", "\units{ m\,s^{-1} }", wait_dur=WAIT_DUR):
        log(ERROR, "Couldn't answer Numeric Question; can't continue!")
        return False
    time.sleep(WAIT_DUR)

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h1[text()='Correct!']")
        log(INFO, "A 'Correct!' message was displayed as expected.")
    except TimeoutException:
        image_div(driver, "ERROR_answer_saved_login")
        log(ERROR, "The 'Correct' message was not shown; see 'ERROR_answer_saved_login.png'!")
        return False

    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    try:
        time.sleep(WAIT_DUR)
        submit_login_form(driver, user=Users.Guerrilla, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
        assert_logged_in(driver, user=Users.Guerrilla, wait_dur=WAIT_DUR)
    except AssertionError:
        log(ERROR, "Can't login; can't continue testing!")
        return False
    driver.get(ISAAC_WEB + "/questions/_regression_test_")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/questions/_regression_test_"))
    time.sleep(WAIT_DUR)

    try:
        open_accordion_section(driver, 3)
        time.sleep(WAIT_DUR)
        num_question = wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']")
        log(INFO, "Accordion opened, numeric question displayed.")
    except NoSuchElementException:
        log(ERROR, "Can't find third accordion section to open again; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_answer_saved_login")
        log(ERROR, "Accordion section did not open again; see 'ERROR_answer_saved_login.png'!")
        return False

    try:
        log(INFO, "Now see if the 'Correct' message was preserved after logging in.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h1[text()='Correct!']")
        log(INFO, "A 'Correct!' message was retained after logging in.")
    except TimeoutException:
        image_div(driver, "ERROR_answer_saved_login")
        log(ERROR, "The 'Correct' message was not shown again; see 'ERROR_answer_saved_login.png'!")
        return False

    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out logged in user.")
    time.sleep(WAIT_DUR)
    log(PASS, "Anonymous question answers are preserved upon logging in.")
    return True
