# Selenium Testing of Isaac Physics
# Python Imports:
import os
import time
import datetime
# Custom Package Imports:
from isaactest.utils.log import log, INFO, ERROR, start_testing, end_testing
from isaactest.utils.initialisation import define_users, start_selenium
from isaactest.tests import TestWithDependency
from isaactest.utils.isaac import User, TestUsers
# Test Imports:
from isaactest.tests.login import login
from isaactest.tests.questionnaire import questionnaire
from isaactest.tests.global_nav import global_nav
from isaactest.tests.logout import logout
from isaactest.tests.login_throttle import login_throttle
from isaactest.tests.login_timeout import login_timeout
from isaactest.tests.signup import signup
from isaactest.tests.welcome_email import welcome_email
from isaactest.tests.req_verify_emails import req_verify_emails
from isaactest.tests.recieve_verify_emails import recieve_verify_emails
from isaactest.tests.verify_link import verify_link
from isaactest.tests.verify_banner_gone import verify_banner_gone
from isaactest.tests.pwd_reset_throttle import pwd_reset_throttle
from isaactest.tests.recieve_pwd_reset_emails import recieve_pwd_reset_emails
from isaactest.tests.pwd_reset_link import pwd_reset_link
from isaactest.tests.reset_pwd_login import reset_pwd_login
from isaactest.tests.login_uppercase import login_uppercase
from isaactest.tests.signup_uppercase import signup_uppercase
from isaactest.tests.user_consistency import user_consistency
from isaactest.tests.user_consistency_popup import user_consistency_popup
from isaactest.tests.email_change import email_change
from isaactest.tests.email_change_emails import email_change_emails
from isaactest.tests.email_change_login_status import email_change_login_status
from isaactest.tests.admin_page_access import admin_page_access
from isaactest.tests.delete_user import delete_user
from isaactest.tests.accordion_behaviour import accordion_behavior
from isaactest.tests.quick_questions import quick_questions
from isaactest.tests.multiple_choice_questions import multiple_choice_questions
from isaactest.tests.numeric_q_units_select import numeric_q_units_select
from isaactest.tests.numeric_q_all_correct import numeric_q_all_correct
from isaactest.tests.numeric_q_answer_change import numeric_q_answer_change
from isaactest.tests.numeric_q_incorrect_unit import numeric_q_incorrect_unit
from isaactest.tests.numeric_q_incorrect_value import numeric_q_incorrect_value
from isaactest.tests.numeric_q_all_incorrect import numeric_q_all_incorrect
from isaactest.tests.numeric_q_incorrect_sf import numeric_q_incorrect_sf
from isaactest.tests.numeric_q_incorrect_sf_u import numeric_q_incorrect_sf_u
from isaactest.tests.numeric_q_known_wrong_ans import numeric_q_known_wrong_ans
from isaactest.tests.numeric_q_known_wrong_sf import numeric_q_known_wrong_sf
from isaactest.tests.numeric_q_help_popup import numeric_q_help_popup


#####
# Setup:
#####

# If we're running in a headless VM do this:
try:
    from pyvirtualdisplay import Display
    PATH_TO_CHROMEDRIVER = "/usr/local/bin/chromedriver"
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
    # Can wait for less time on a real non-emulated browser with display:
    WAIT_DUR = 2

# Some important global constants and objects:
ISAAC_WEB = "https://staging.isaacphysics.org"
GUERRILLAMAIL = "https://www.guerrillamail.com"
Users = define_users()


# Open a folder just for this test:
RUNDATE = datetime.datetime.now().strftime("%Y%m%d_%H%M")
RUNDATE = ""
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
driver, inbox = start_selenium(Users, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR)
# driver, inbox = start_selenium(Users, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR, PATH_TO_CHROMEDRIVER)


fatal_error = True
try:
    login(driver, Users, ISAAC_WEB, WAIT_DUR)
    questionnaire(driver, ISAAC_WEB)
    global_nav(driver, ISAAC_WEB, WAIT_DUR)
    logout(driver, ISAAC_WEB, WAIT_DUR)
    login_throttle(driver, Users, ISAAC_WEB, WAIT_DUR)
    login_timeout(driver, Users, ISAAC_WEB, WAIT_DUR)
    signup(driver, Users)
    welcome_email(driver, inbox, GUERRILLAMAIL)
    req_verify_emails(driver, ISAAC_WEB, WAIT_DUR)
    recieve_verify_emails(driver, inbox, GUERRILLAMAIL)
    verify_link(driver, inbox, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR)
    verify_banner_gone(driver, ISAAC_WEB, WAIT_DUR)
    pwd_reset_throttle(driver, Users, ISAAC_WEB, WAIT_DUR)
    recieve_pwd_reset_emails(driver, inbox, GUERRILLAMAIL, WAIT_DUR)
    pwd_reset_link(driver, inbox, Users, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR)
    reset_pwd_login(driver, Users, ISAAC_WEB, WAIT_DUR)
    login_uppercase(driver, Users, ISAAC_WEB, WAIT_DUR)
    signup_uppercase(driver, Users, ISAAC_WEB, WAIT_DUR)
    user_consistency(driver, Users, ISAAC_WEB, WAIT_DUR)
    user_consistency_popup(driver, ISAAC_WEB, WAIT_DUR)
    email_change(driver, Users, ISAAC_WEB, WAIT_DUR)
    email_change_emails(driver, inbox, Users, GUERRILLAMAIL, WAIT_DUR)
    email_change_login_status(driver, Users, ISAAC_WEB, WAIT_DUR)
    admin_page_access(driver, Users, ISAAC_WEB, WAIT_DUR)
    delete_user(driver, Users, ISAAC_WEB, WAIT_DUR)
    accordion_behavior(driver, ISAAC_WEB, WAIT_DUR)
    quick_questions(driver, ISAAC_WEB, WAIT_DUR)
    multiple_choice_questions(driver, ISAAC_WEB, WAIT_DUR)
    numeric_q_units_select(driver, ISAAC_WEB, WAIT_DUR)
    numeric_q_all_correct(driver, ISAAC_WEB, WAIT_DUR)
    numeric_q_answer_change(driver, ISAAC_WEB, WAIT_DUR)
    numeric_q_incorrect_unit(driver, ISAAC_WEB, WAIT_DUR)
    numeric_q_incorrect_value(driver, ISAAC_WEB, WAIT_DUR)
    numeric_q_all_incorrect(driver, ISAAC_WEB, WAIT_DUR)
    numeric_q_incorrect_sf(driver, ISAAC_WEB, WAIT_DUR)
    numeric_q_incorrect_sf_u(driver, ISAAC_WEB, WAIT_DUR)
    numeric_q_known_wrong_ans(driver, ISAAC_WEB, WAIT_DUR)
    numeric_q_known_wrong_sf(driver, ISAAC_WEB, WAIT_DUR)
    numeric_q_help_popup(driver, ISAAC_WEB, WAIT_DUR)
    fatal_error = False
except Exception, e:
    log(ERROR, "FATAL ERROR! '%s'!" % e.message)
    raise  # This allows us to add the error to the email, but leave the traceback on stderr
finally:
    driver.quit()
    log(INFO, "Closed Selenium and Browser.")
    try:
        virtual_display.stop()
        log(INFO, "Closed the virtual display.")
    except NameError:
        pass
    duration = int((datetime.datetime.now() - start_time).total_seconds()/60)
    log(INFO, "Testing Finished, took %s minutes." % duration)
    end_testing(TestWithDependency.Results, email=False, aborted=fatal_error)
