import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import assert_logged_out
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import NoSuchElementException, WebDriverException
__all__ = ['assignments_page']

@TestWithDependency('ASSIGNMENTS_PAGE')
def assignments_page(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """ Test whether it is possible to access the assignments page without being logged in

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """

    try:
        driver.get(ISAAC_WEB + "/assignments")
        time.sleep(WAIT_DUR)
        assert driver.current_url != ISAAC_WEB + "/assignments"
        time.sleep(WAIT_DUR)
        log(PASS, "Successfully redirected to the login page when attempting to access assignments.")
        return True
    except AssertionError:
        log(ERROR, "Failed to redirect to the login page correctly.")
        return False

