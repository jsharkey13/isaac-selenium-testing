import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import answer_symbolic_q_text_entry, open_accordion_section, submit_login_form, assert_logged_in
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["symbolic_q_text_entry_correct"]


#####
# Test : Symbolic Questions Text Entry Correct Answers
#####
@TestWithDependency("SYMBOLIC_Q_TEXT_ENTRY_CORRECT")
def symbolic_q_text_entry_correct(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if symbolic questions can be answered correctly with text entry.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
    login_tab.click()
    time.sleep(WAIT_DUR)
    submit_login_form(driver, user=Users.Admin, disable_popup=False, wait_dur=WAIT_DUR)
    time.sleep(WAIT_DUR)
    assert_logged_in(driver, user=Users.Admin)
    global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
    global_nav.click()
    log(INFO, "Opened global nav (menu bar).")
    time.sleep(WAIT_DUR)
    my_account_link = driver.find_element_by_xpath("(//a[@ui-sref='accountSettings'])[2]")
    my_account_link.click()
    log(INFO, "Clicked 'My Account' button.")
    time.sleep(WAIT_DUR)
    beta_tab = driver.find_element_by_xpath("//dd[@ng-click='activateTab(4)']")
    beta_tab.click()
    log(INFO, "Clicked 'Beta Features' tab.")
    time.sleep(WAIT_DUR)
    text_entry = driver.find_element_by_xpath("(//input[@id='eqn-editor-text-entry'])")
    if 'ng-empty' in text_entry.get_attribute("class"):
        text_entry.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Text entry now enabled")
        save_button = driver.find_element_by_xpath("//a[text()='Save']")
        save_button.click()
        log(INFO, "Saving account changes.")
        time.sleep(WAIT_DUR)
    else:
        log(INFO, "Text entry already enabled")
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/questions/_regression_test_")
    time.sleep(WAIT_DUR)
    assert_tab(driver, ISAAC_WEB + "questions/_regression_test_")
    time.sleep(WAIT_DUR)
    try:
        open_accordion_section(driver, 4)
        sym_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacSymbolicQuestion']")
    except NoSuchElementException:
        log(ERROR, "Can't find the symbolic question; can't continue!")
        return False

    log(INFO, "Attempt to enter correct answer.")
    if not answer_symbolic_q_text_entry(sym_question, "(((x)))", wait_dur=WAIT_DUR):
        log(ERROR, "Couldn't answer symbolic Question; can't continue!")
        return False
    time.sleep(WAIT_DUR)

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacSymbolicQuestion']//h1[text()='Correct!']")
        log(INFO, "A 'Correct!' message was displayed as expected.")
        time.sleep(WAIT_DUR)
        log(PASS, "Symbolic Question 'correct value, correct unit' behavior as expected.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_symbolic_q_correct")
        log(ERROR, "The messages shown for a correct answer were not all displayed; see 'ERROR_symbolic_q_correct.png'!")
        return False
