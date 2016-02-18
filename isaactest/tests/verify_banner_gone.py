import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab
from ..utils.i_selenium import wait_for_invisible_xpath
from ..tests import TestWithDependency

from selenium.common.exceptions import TimeoutException

__all__ = ["verify_banner_gone"]


#####
# Test : Verification Banner Gone
#####
@TestWithDependency("VERIFY_BANNER_GONE", ["VERIFY_LINK"])
def verify_banner_gone(driver, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if the banner telling users to verify their email disappears after verifying.

        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    try:
        driver.refresh()
        time.sleep(WAIT_DUR)
        log(INFO, "Checking if verification banner now gone.")
        wait_for_invisible_xpath(driver, "//a[@ng-click='requestEmailVerification()']")
        log(PASS, "Verification banner gone after verifying email.")
        return True
    except TimeoutException:
        log(ERROR, "Verification banner still present after email verified!")
        return False
