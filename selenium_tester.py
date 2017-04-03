# Selenium Testing of Isaac Physics
# Python Imports:
import os
import time
import datetime
# Custom Package Imports:
from isaactest.utils.log import log, INFO, ERROR, start_testing, end_testing
from isaactest.utils.initialisation import define_users, start_selenium
from isaactest.tests import TestWithDependency
from isaactest.utils.isaac import User, TestUsers  # Need this for the pickle loading


#####
# Setup:
#####

# If we're running in a headless VM do this:
try:
    from pyvirtualdisplay import Display
    PATH_TO_CHROMEDRIVER = "/usr/local/bin/chromedriver"
    PATH_TO_GECKODRIVER = "/usr/local/bin/geckodriver"
    virtual_display = Display(visible=False, size=(1920, 1080))
    virtual_display.start()
    time.sleep(5)
    os.chdir("/isaac-selenium-testing/testing")
    # No absolutely reliable way to ensure Javascript has loaded, just wait longer
    # on a headless machine to hope for the best...
    WAIT_DUR = 10
# Otherwise do this:
except ImportError:
    os.chdir("./testing")
    PATH_TO_CHROMEDRIVER = "../chromedriver"
    PATH_TO_GECKODRIVER = "../geckodriver"
    # Can wait for less time on a real non-emulated browser with display:
    WAIT_DUR = 3

# Some important global constants and objects:
ISAAC_WEB = "https://test.isaacphysics.org"
GUERRILLAMAIL = "https://www.guerrillamail.com"
Users = define_users()


# Open a folder just for this test:
RUNDATE = datetime.datetime.now().strftime("%Y%m%d_%H%M")
try:
    os.mkdir("test_" + RUNDATE)
except Exception:
    pass
os.chdir("test_" + RUNDATE)


#####
# Start Testing:
#####
start_testing()
start_time = datetime.datetime.now()
driver, inbox = start_selenium(Users, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR, PATH_TO_GECKODRIVER)
#driver, inbox = start_selenium(Users, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR, PATH_TO_CHROMEDRIVER) # https://bugs.chromium.org/p/chromedriver/issues/detail?id=1625


fatal_error = False
try:
    # Use the class method to run all tests in order they're designed to run in:
    TestWithDependency.run_all_tests(driver, inbox, Users, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR)

    # Comment out the above line and replace with below line to run a specific test:
    # TestWithDependency.run_test_with_deps("LOGIN", driver, inbox, Users, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR)
except Exception, e:
    fatal_error = True
    log(ERROR, "FATAL ERROR! %s: '%s'!" % (type(e).__name__, e.message))
    raise  # This allows us to add the error to the email, but leave the traceback on stderr
finally:
    driver.quit()
    log(INFO, "Closed Selenium and Browser.")
    try:
        virtual_display.stop()
        log(INFO, "Closed the virtual display.")
    except NameError:
        pass
    duration = int((datetime.datetime.now() - start_time).total_seconds()/60.0 + 0.5)  # int(...) rounds down
    log(INFO, "Testing Finished, took %s minutes." % duration)
    end_testing(TestWithDependency.Results, email=False, aborted=fatal_error)
