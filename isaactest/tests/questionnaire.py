from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import kill_irritating_popup, disable_irritating_popup
from ..utils.i_selenium import assert_tab
from ..tests import TestWithDependency

__all__ = ["questionnaire"]


#####
# Test : Questionnaire Popup
#####
@TestWithDependency("QUESTIONNAIRE", ["LOGIN"])
def questionnaire(driver, ISAAC_WEB):
    """Test if the questionnaire popup is shown.

    Must run immediately after the "LOGIN" test.
        - 'driver' should be a Selenium WebDriver.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
    """
    assert_tab(driver, ISAAC_WEB)
    log(INFO, "Ensure the popup has not been disabled, and wait 15 seconds for it to display.")
    disable_irritating_popup(driver, undo=True)  # Make sure we've not disabled it at all!
    if kill_irritating_popup(driver, 15):
        log(PASS, "Questionnaire popup shown and closed.")
        return True
    else:
        log(ERROR, "Questionnaire popup not shown!")
        return False