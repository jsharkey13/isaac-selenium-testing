import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form
from ..utils.i_selenium import assert_tab, image_div
from ..utils.i_selenium import wait_for_xpath_element
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException

__all__ = ["admin_stats_summary"]


#####
# Test : Admin Stats "At a Glance" Page
#####
@TestWithDependency("ADMIN_STATS_SUMMARY")
def admin_stats_summary(driver, Users, ISAAC_WEB, WAIT_DUR):
    """Test if admin stats summary page works.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/admin/stats")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/admin/stats"))
    time.sleep(WAIT_DUR)
    try:
        assert submit_login_form(driver, user=Users.Admin, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
        wait_for_xpath_element(driver, "//h2[text()='Statistics Menu']")
        log(INFO, "Admin stats page loaded.")
    except AssertionError:
        image_div(driver, "ERROR_admin_stats")
        log(ERROR, "Can't login after visiting Admin Stats page logged out; see 'ERROR_admin_stats.png'!")
        return False
    except TimeoutException:
        log(ERROR, "Can't load Admin Stats page; can't continue testing!")
        return False

    try:
        users_text = driver.find_element_by_xpath("//div[@ng-show='statistics.totalUsers']//strong[contains(text(), 'Users:')]").text
        count = int(users_text.split(":")[3])
        assert count > 0, "Expected user registered count > 0, got '%s'!" % count
        log(INFO, "User registered count loaded: %s" % count)
    except NoSuchElementException:
        log(ERROR, "Can't find user summary text; can't continue!")
        return False
    except (ValueError, IndexError):
        log(ERROR, "Can't extract user count from string '%s'; can't continue!" % users_text)
        return False
    except AssertionError, e:
        log(ERROR, e.message)
        return False

    try:
        answer_events_text = driver.find_element_by_xpath("//div[@ng-show='statistics.totalUsers']//li[contains(text(), '# of Questions')]").text
        answers_count = int(answer_events_text.split("(")[1].replace(")", ""))
        assert answers_count > 0, "Expected question answer attempt count > 0, got '%s'!" % answers_count
        log(INFO, "Question attempt count loaded: %s" % answers_count)
    except NoSuchElementException:
        log(ERROR, "Can't find question attempts summary text; can't continue!")
        return False
    except (ValueError, IndexError):
        log(ERROR, "Can't extract answer attempt count from string '%s'; can't continue!" % users_text)
        return False
    except AssertionError, e:
        log(ERROR, e.message)
        return False

    log(PASS, "Admin 'Stats at a Glance' page contains info as expected.")
    return True
