import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import assert_logged_out
from ..utils.i_selenium import assert_tab, close_tab, image_div, save_element_html
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["user_consistency_popup"]


#####
# Test : User Consistency Popup
#####
@TestWithDependency("USER_CONSISTENCY_POPUP", ["USER_CONSISTENCY"])
def user_consistency_popup(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if the user consistency popup is shown after logging out in another tab.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out the user in the new tab.")
    time.sleep(WAIT_DUR)
    non_isaac_url = "https://www.bbc.co.uk"

    try:
        assert_logged_out(driver, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
        log(INFO, "Logged out in new tab successfully.")
    except AssertionError:
        image_div(driver, "ERROR_logout_failure")
        close_tab(driver)
        driver.get(non_isaac_url)
        log(INFO, "[Navigating away from Isaac (to '%s') to avoid muddling tabs.]" % non_isaac_url)
        time.sleep(WAIT_DUR)
        log(ERROR, "Couldn't logout in new tab; see 'ERROR_logout_failure.png'!")
        return False

    driver.get(non_isaac_url)
    log(INFO, "Navigating away from Isaac (to '%s') to avoid muddling tabs." % non_isaac_url)
    time.sleep(WAIT_DUR)

    assert_tab(driver, ISAAC_WEB)
    try:
        consistency_popup = wait_for_xpath_element(driver, "//div[@isaac-modal='userConsistencyError']")
        log(INFO, "User consistency popup shown.")
        image_div(driver, "user_consistency_popup", consistency_popup)
        save_element_html(consistency_popup, "user_consistency_popup")
        time.sleep(WAIT_DUR)
    except TimeoutException:
        image_div(driver, "ERROR_user_consistency_not_shown")
        close_tab(driver)
        time.sleep(WAIT_DUR)
        log(ERROR, "User consistency popup not shown; see 'ERROR_user_consistency_not_shown.png'!")
        return False

    try:
        continue_button = driver.find_element_by_xpath("//div[@id='isaacModal']//div[@isaac-modal='userConsistencyError']//button[text()='Continue']")
        continue_button.click()
        log(INFO, "User Consistency popup closed.")
        time.sleep(WAIT_DUR)
        driver.refresh()
        time.sleep(WAIT_DUR)
        assert_logged_out(driver, wait_dur=WAIT_DUR)
    except AssertionError:
        log(ERROR, "User inconsistency did not force logout!")
        return False
    except NoSuchElementException:
        time.sleep(WAIT_DUR)
        log(ERROR, "Cannot click 'Continue' button; see 'user_consistency_popup.png'!")
        return False

    try:
        assert_tab(driver, non_isaac_url)
        time.sleep(WAIT_DUR)
        close_tab(driver)
    except AssertionError:
        log(ERROR, "Can't find non-Isaac tab to close!")

    log(PASS, "User consistency popup shown and forced logout.")
    return True
