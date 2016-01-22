# Selenium Testing of Isaac Physics
# Python Imports:
import os
import time
import datetime
from collections import OrderedDict
# Custom Package Imports:
from isaactest.emails.guerrillamail import set_guerrilla_mail_address, GuerrillaInbox
from isaactest.utils.log import log, INFO, ERROR, PASS, start_testing, end_testing
from isaactest.utils.isaac import submit_login_form, assert_logged_in, assert_logged_out, sign_up_to_isaac
from isaactest.utils.isaac import kill_irritating_popup, disable_irritating_popup
from isaactest.utils.isaac import TestUsers, User
from isaactest.utils.isaac import answer_numeric_q
from isaactest.utils.i_selenium import assert_tab, new_tab, close_tab, image_div, save_element_html
from isaactest.utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from isaactest.tests import TestWithDependency
# Selenium Imports:
import selenium.webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotVisibleException

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

# Some important global constants:
ISAAC_WEB = "https://staging.isaacphysics.org"
GUERRILLAMAIL = "https://www.guerrillamail.com"


# Global objects:
def define_users():
    Users = TestUsers.load()
    Guerrilla = User("isaactest@sharklasers.com", "Temp",
                     "Test", "test")
    Users.Guerrilla = Guerrilla
    Users.Guerrilla.new_email = "isaactesttwo@sharklasers.com"
    Users.Guerrilla.new_password = "testing123"
    return Users
Users = define_users()
Results = OrderedDict()


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


#####
# Test -1 : Start up Selenium
#####
def selenium_startup(Users):
    # Selenium Start-up:
    driver = selenium.webdriver.Firefox()
    # driver = selenium.webdriver.Chrome(PATH_TO_CHROMEDRIVER)
    driver.set_window_size(1920, 1080)
    driver.maximize_window()
    log(INFO, "Opened Selenium Driver for '%s'." % driver.name.title())
    time.sleep(WAIT_DUR)
    # Navigate to Staging:
    driver.get(ISAAC_WEB)
    log(INFO, "Got: %s" % ISAAC_WEB)
    time.sleep(WAIT_DUR)
    # Open GuerrillaMail:
    new_tab(driver)
    time.sleep(WAIT_DUR)
    driver.get(GUERRILLAMAIL)
    log(INFO, "Got: %s" % GUERRILLAMAIL)
    # Set Guerrilla Mail email address:
    time.sleep(WAIT_DUR)
    Users.Guerrilla.email = set_guerrilla_mail_address(driver, Users.Guerrilla.email)
    time.sleep(WAIT_DUR)
    inbox = GuerrillaInbox(driver)
    time.sleep(WAIT_DUR)
    # Delete GuerrillaMail welcome:
    initial_emails = inbox.get_by_subject("Welcome to Guerrilla Mail")
    for e in initial_emails:
        inbox.delete_email(e)
    time.sleep(WAIT_DUR)
    return driver, inbox
driver, inbox = selenium_startup(Users)  # Delete


#####
# Test 1 : Logging In
#####
@TestWithDependency("LOGIN", Results)
def login(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    try:
        login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
        login_tab.click()
        submit_login_form(driver, user=Users.Student, disable_popup=False, wait_dur=WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Couldn't click login tab; can't login!")
        return False
    time.sleep(WAIT_DUR)
    try:
        assert_logged_in(driver, Users.Student, wait_dur=WAIT_DUR)
        log(INFO, "Login successful.")
        log(PASS, "Login using username and password successful.")
        return True
    except AssertionError:
        log(INFO, "Login failed!")
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Can't login; see 'ERROR_not_logging_in.png'!")
        return False


#####
# Test 2 : Questionnaire Popup
#####
@TestWithDependency("QUESTIONNAIRE", Results, ["LOGIN"])
def questionnaire(driver):
    assert_tab(driver, ISAAC_WEB)
    disable_irritating_popup(driver, undo=True)  # Make sure we've not disabled it at all!
    if kill_irritating_popup(driver, 15):
        log(PASS, "Questionnaire popup shown and closed.")
        return True
    else:
        log(ERROR, "Questionnaire popup not shown!")
        return False


#####
# Test 2.5 : Global Navigation Menu
#####
@TestWithDependency("GLOBAL_NAV", Results)
def global_nav(driver):
    assert_tab(driver, ISAAC_WEB)
    try:
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        log(INFO, "Clicked menu button.")
        time.sleep(WAIT_DUR)
        wait_for_xpath_element(driver, "//nav[@class='dl-nav']")
        log(INFO, "Global navigation successfully opened.")
    except NoSuchElementException:
        log(ERROR, "Can't find menu button to click; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Global navigation didn't open!")
        return False
    time.sleep(WAIT_DUR)
    try:
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        time.sleep(WAIT_DUR)
        wait_for_invisible_xpath(driver, "//nav[@class='dl-nav']")
        log(INFO, "Global navigation successfuly closed.")
        log(PASS, "Global navigation functions as expected.")
        return True
    except TimeoutException:
        log(ERROR, "Global navigation didn't close!")
        return False


#####
# Test 3 : Logout Button
#####
@TestWithDependency("LOGOUT", Results, ["LOGIN", "GLOBAL_NAV"])
def logout(driver):
    assert_tab(driver, ISAAC_WEB)
    try:
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        time.sleep(WAIT_DUR)
        logout_button = driver.find_element_by_xpath("//a[@ui-sref='logout']")
        logout_button.click()
    except NoSuchElementException:
        image_div(driver, "ERROR_logout_failure")
        log(ERROR, "Can't find logout button; can't logout, see 'ERROR_logout_failure.png'!")
        return False
    time.sleep(WAIT_DUR)
    try:
        assert_logged_out(driver, wait_dur=WAIT_DUR)
        log(INFO, "Logged out.")
        log(PASS, "Log out button works.")
        return True
    except AssertionError:
        image_div(driver, "ERROR_logout_failure")
        log(ERROR, "Couldn't logout; see 'ERROR_logout_failure.png'!")
        return False


#####
# Test 4 : 11 Login Attempts
#####
@TestWithDependency("LOGIN_THROTTLE", Results)
def login_throttle(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    try:
        login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
        login_tab.click()
    except NoSuchElementException:
        log(ERROR, "Couldn't find login button; can't continue!")
        return False
    for i in range(11):
        submit_login_form(driver, username=Users.Student.email, password="wrongpassword", wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
    try:
        driver.find_element_by_xpath("//strong[contains(text(), 'too many attempts to login')]")
        log(PASS, "11 login attempts. Warning message and locked out for 10 mins.")
        return True
    except NoSuchElementException:
        image_div(driver, "11_login_attempts")
        log(ERROR, "Tried to log in 11 times. No error message; see '11_login_attempts.png'!")
        return False


#####
# Test 5 : 10 Minute Lockout
#####
@TestWithDependency("LOGIN_TIMEOUT", Results, ["LOGIN", "LOGIN_THROTTLE"])
def login_timeout(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    log(INFO, "Waiting for 10 minute timout to expire.")
    for i in range(10):
        log(INFO, "Still waiting. %s mins remaining." % (10 - i))
        time.sleep(60)
    time.sleep(10)
    log(INFO, "Finished waiting.")

    submit_login_form(driver, user=Users.Student)
    time.sleep(WAIT_DUR)
    try:
        assert_logged_in(driver, Users.Student, wait_dur=WAIT_DUR)
        log(INFO, "Login successful.")
        log(PASS, "Login after 10 minute lockout.")
        return True
    except AssertionError:
        log(INFO, "Login failed!")
        image_div(driver, "ERROR_login_after_lockout")
        log(ERROR, "Can't login after 10 minute lockout; see 'login_error.png'!")
        return False


#####
# Test 6 : Sign Up to Isaac
#####
@TestWithDependency("SIGNUP", Results, ["LOGIN", "LOGOUT"])
def signup(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)

    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        login_tab = driver.find_element_by_id("login-tab")
        login_tab.click()
    except NoSuchElementException:
        log(ERROR, "Can't find login button; can't continue!")
        return False
    time.sleep(WAIT_DUR)
    if sign_up_to_isaac(driver, user=Users.Guerrilla, wait_dur=WAIT_DUR):
        log(PASS, "Successfully register new user '%s' on Isaac." % Users.Guerrilla.email)
        return True
    else:
        log(ERROR, "Can't register user!")
        return False


#####
# Test 7 : Welcome Email Recieved
#####
@TestWithDependency("WELCOME_EMAIL", Results, ["SIGNUP"])
def welcome_email(driver, inbox):
    assert_tab(driver, GUERRILLAMAIL)
    log(INFO, "Waiting 10 seconds for page to update.")
    time.sleep(11)
    inbox.refresh()

    log(INFO, "GuerrillaMail: Access welcome email in inbox.")
    try:
        welcome_emails = inbox.get_by_subject("Welcome to Isaac Physics!")
        assert len(welcome_emails) == 1, "Expected to recieve a welcome email, recieved %s emails!" % len(welcome_emails)
        welcome_email = welcome_emails[0]
        log(INFO, "Got welcome email as expected.")
        welcome_email.image()
        welcome_email.save_html_body()
        log(PASS, "Welcome email recieved!")
        return True
    except AssertionError, e:
        image_div(driver, "ERROR_not_isaac_email")
        log(ERROR, e.message + " See 'ERROR_not_isaac_email.png'!")
        return False


######
# Test 8 : Request Verification Emails
######
@TestWithDependency("REQ_VERIFY_EMAILS", Results, ["SIGNUP"])
def req_verify_emails(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        request_verify_email = driver.find_element_by_xpath("//a[@ng-click='requestEmailVerification()']")
    except NoSuchElementException:
        log(ERROR, "Can't access verification request link in banner; can't continue! Are we logged in?")
        return False

    email_verification_popup_shown_yet = False
    verify_popup_xpath = "//div[@class='toast-message']/h4[@class='ng-binding']"
    verification_email_request_limit = 4
    verification_requests = 0
    try:
        for i in range(verification_email_request_limit + 1):
            log(INFO, "Clicking request email verification link.")
            request_verify_email.click()
            popup = wait_for_xpath_element(driver, verify_popup_xpath)
            popup_text = popup.text
            image_div(driver, "email_verification_request_popup_%s" % i)
            email_verification_popup_shown_yet = True
            wait_for_invisible_xpath(driver, verify_popup_xpath)
            email_verification_popup_shown_yet = False
            time.sleep(WAIT_DUR)
            if i <= verification_email_request_limit - 1:  # i starts from 0, not 1
                assert popup_text == "Email verification request succeeded."
                log(INFO, "Success message shown.")
                verification_requests += 1
            else:
                if popup_text == "Email verification request failed.":
                    log(INFO, "Error message shown as expected.")
                    log(PASS, "Email verification link shows warning on 5th click, success on others.")
                    return True
                else:
                    log(ERROR, "Warning not shown after %s requests!" % verification_requests)
                    return False
    except TimeoutException:
        if email_verification_popup_shown_yet:
            log(ERROR, "Verification Popup didn't close; see 'email_verification_request_popup.png'!")
            return False
        else:
            log(ERROR, "Verification Popup didn't appear!")
            return False
    except AssertionError:
        log(ERROR, "Success text not shown on request %s!" % (verification_requests + 1))
        return False


#####
# Test 9 : Recieve Verification Emails
#####
@TestWithDependency("RECIEVE_VERIFY_EMAILS", Results, ["REQ_VERIFY_EMAILS"])
def recieve_verify_emails(driver, inbox):
    verification_email_request_limit = 4
    assert_tab(driver, GUERRILLAMAIL)
    log(INFO, "Waiting 10 seconds for page to update.")
    time.sleep(11)
    inbox.refresh()

    verification_emails_recived = 0
    log(INFO, "Checking if verification emails recieved.")
    try:
        verification_emails = inbox.get_by_subject("Verify your email")
        verification_emails_recived = len(verification_emails)
        assert verification_emails_recived == verification_email_request_limit
        for email in verification_emails:
            email.image()
            email.save_html_body()
        log(PASS, "%s verification emails recieved." % verification_emails_recived)
        return True
    except AssertionError:
        image_div(driver, "ERROR_recieve_verification")
        log(ERROR, "Expected %s verification emails, recieved %s. See 'ERROR_recieve_verification.png'!" % (verification_email_request_limit, verification_emails_recived))
        return False


#####
# Test 10 : Verification Link Works
#####
@TestWithDependency("VERIFY_LINK", Results, ["RECIEVE_VERIFY_EMAILS"])
def verify_link(driver, inbox):
    assert_tab(driver, GUERRILLAMAIL)
    log(INFO, "About to check latest verification link works.")
    try:
        verification_email = inbox.get_by_subject("Verify your email")[0]
        verification_email.view()
        log(INFO, "Selecting most recent email '%s'." % verification_email)
        time.sleep(WAIT_DUR)
        email_body = verification_email.get_email_body_element()
        verification_link = email_body.find_element_by_xpath(".//a[text()='Verify your email address']")
        verification_link.send_keys(Keys.CONTROL + Keys.ENTER)
        log(INFO, "Opening verification link from email in new tab.")
        time.sleep(WAIT_DUR)
        verification_email.close()
        time.sleep(WAIT_DUR)
        assert_tab(driver, ISAAC_WEB + "/verifyemail")
        log(INFO, "Verification URL: '%s'." % driver.current_url)
        wait_for_xpath_element(driver, "//h2[@ng-if='verificationState==verificationStates.SUCCESS']")
        close_tab(driver)
        log(PASS, "Email address verified successfully.")
        time.sleep(WAIT_DUR)
        return True
    except TimeoutException:
        image_div(driver, "ERROR_verification_status")
        log(ERROR, "Verification Failed; see 'ERROR_verification_status.png'!")
        return False
    except IndexError:
        log(ERROR, "No verification emails recieved! Can't continue.")
        return False
    except NoSuchElementException:
        log(ERROR, "Can't access verification link in email; can't continue!")
        return False


#####
# Test 11 : Verification Banner Gone
#####
@TestWithDependency("VERIFY_BANNER_GONE", Results, ["VERIFY_LINK"])
def verify_banner_gone(driver):
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


#####
# Test 12 : Forgot My Password Button Limit
#####
@TestWithDependency("PWD_RESET_THROTTLE", Results, ["LOGIN", "LOGOUT", "SIGNUP"])
def pwd_reset_throttle(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)

    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)
    password_resets = 0
    forgot_pwd_request_limit = 4
    try:
        user = driver.find_element_by_xpath("(//input[@name='email'])[2]")
        user.clear()
        user.send_keys(Users.Guerrilla.email)
        for i in range(10):
            forgot_password_button = driver.find_element_by_xpath("(//a[@ng-click='resetPassword()'])[2]")
            log(INFO, "Clicking password reset button.")
            forgot_password_button.click()
            time.sleep(0.1)
            image_div(driver, "reset_password_button_message_%s" % i)
            password_resets += 1
            if i <= forgot_pwd_request_limit - 1:  # i starts from 0 not 1
                try:
                    wait_for_invisible_xpath(driver, "//div[@class='toast-message']/h4", 0.5)
                except TimeoutException:
                    raise TimeoutException("Password reset error message unexpectedly shown after %s requests!" % password_resets)
                time.sleep(0.5)
                message = driver.find_element_by_xpath("(//p[@ng-show='passwordResetFlag'])[2]")
                assert "Your password request is being processed." in message.text
            else:
                try:
                    wait_for_xpath_element(driver, "//div[@class='toast-message']/h4")
                except TimeoutException:
                    raise TimeoutException("Password reset error message not shown after %s requests." % password_resets)
                log(INFO, "Password reset error message shown after %s attempts." % password_resets)
                break
            time.sleep(WAIT_DUR)
        log(PASS, "Password reset error message shown after %s requests." % password_resets)
        return True
    except AssertionError:
        log(ERROR, "Incorrect password reset message shown; see 'reset_password_button_message.png'!")
        return False
    except NoSuchElementException:
        log(ERROR, "No password reset messagew shown; see 'reset_password_button_message.png'!")
        return False
    except TimeoutException, e:
        log(ERROR, e.msg)
        return False


#####
# Test 13 : 4 password reset emails recieved
#####
@TestWithDependency("RECIEVE_PWD_RESET_EMAILS", Results, ["PWD_RESET_THROTTLE"])
def recieve_pwd_reset_emails(driver, inbox):
    forgot_pwd_request_limit = 4
    assert_tab(driver, GUERRILLAMAIL)
    log(INFO, "Waiting 10 seconds for page to update.")
    time.sleep(11)
    inbox.refresh()
    time.sleep(WAIT_DUR)

    forgot_password_emails_recieved = 0
    log(INFO, "Checking if password reset emails recieved.")
    try:
        reset_email_list = inbox.get_by_subject("Password Reset Request", unread=True)
        log(INFO, "Getting all unread emails with subject 'Password Reset Request'.")
        forgot_password_emails_recieved = len(reset_email_list)
        assert forgot_password_emails_recieved == forgot_pwd_request_limit
        log(INFO, "Recieved the expected %s password reset emails." % forgot_pwd_request_limit)
        for email in reset_email_list:
            email.image()
            email.save_html_body()
        log(PASS, "%s reset password emails recieved." % forgot_pwd_request_limit)
        return True
    except AssertionError:
        image_div(driver, "ERROR_recieve_reset_pwd")
        log(ERROR, "Expected %s password reset emails, recieved %s. See 'ERROR_recieve_reset_pwd.png'!" % (forgot_pwd_request_limit, forgot_password_emails_recieved))
        return False


#####
# Test 14 : Reset Password Link Works
#####
@TestWithDependency("PWD_RESET_LINK", Results, ["RECIEVE_PWD_RESET_EMAILS"])
def pwd_reset_link(driver, inbox, Users):
    assert_tab(driver, GUERRILLAMAIL)
    log(INFO, "About to check latest reset password link works.")
    try:
        reset_email = inbox.get_by_subject("Password Reset Request")[0]
        reset_email.view()
        log(INFO, "Selecting most recent password reset email '%s'." % reset_email)
        time.sleep(WAIT_DUR)
        email_body = reset_email.get_email_body_element()
        verification_link = email_body.find_element_by_xpath(".//a[text()='Click Here']")
        verification_link.send_keys(Keys.CONTROL + Keys.ENTER)
        log(INFO, "Opening reset password link from email in new tab.")
        reset_email.close()
        time.sleep(WAIT_DUR)
        assert_tab(driver, ISAAC_WEB + "/resetpassword")
        log(INFO, "Reset Password URL: '%s'." % driver.current_url)
    except NoSuchElementException:
        log(ERROR, "Can't access reset password link in email; can't continue!")
        return False
    try:
        pwd1 = driver.find_element_by_xpath("//input[@id='password']")
        pwd1.clear()
        pwd1.send_keys(Users.Guerrilla.new_password)
        pwd2 = driver.find_element_by_xpath("//input[@id='confirm-password']")
        pwd2.clear()
        pwd2.send_keys(Users.Guerrilla.new_password)
        change_password = driver.find_element_by_xpath("//button[@ng-click='resetPassword()']")
        change_password.click()
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't access reset password form correctly; can't continue!")
        return False
    try:
        driver.find_element_by_xpath("//div[@ng-switch='submitted']/div[contains(text(), 'reset successfully')]")
        Users.Guerrilla.password = Users.Guerrilla.new_password
        close_tab(driver)
        time.sleep(WAIT_DUR)
        log(PASS, "Reset password link works.")
        return True
    except NoSuchElementException:
        image_div(driver, "ERROR_resetting_password")
        log(ERROR, "Resetting password failed; see 'ERROR_resetting_password.png'!")
        return False


#####
# Test 15 : Logging In With New Password
#####
@TestWithDependency("RESET_PWD_LOGIN", Results, ["LOGIN", "PWD_RESET_LINK"])
def reset_pwd_login(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB)
    log(INFO, "Got: %s" % ISAAC_WEB)
    time.sleep(WAIT_DUR)

    try:
        login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
        login_tab.click()
        submit_login_form(driver, user=Users.Guerrilla, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't access login tab; can't continue!")
        return False
    try:
        assert_logged_in(driver, Users.Guerrilla, wait_dur=WAIT_DUR)
        log(INFO, "Login successful.")
        log(PASS, "Login using username and new password successful.")
        return True
    except AssertionError:
        log(INFO, "Login failed!")
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Can't login with new password; see 'ERROR_not_logging_in.png'!")
        return False


#####
# Test 16 : Login Email Case Sensitivity
#####
@TestWithDependency("LOGIN_UPPERCASE", Results, ["LOGIN"])
def login_uppercase(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)
    try:
        login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
        login_tab.click()
        submit_login_form(driver, Users.Student.email.upper(), Users.Student.password, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't access login tab; can't continue!")
        return False
    try:
        assert_logged_in(driver, Users.Student, wait_dur=WAIT_DUR)
        log(INFO, "Login successful.")
        log(PASS, "Login using uppercase version of email successful.")
        return True
    except AssertionError:
        log(INFO, "Login failed!")
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Can't login with uppercase email; see 'ERROR_logging_in_uppercase.png'!")
        return False


#####
# Test 17 : Signup Email Case Sensitivity
#####
@TestWithDependency("SIGNUP_UPPERCASE", Results, ["LOGIN", "SIGNUP"])
def signup_uppercase(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)
    try:
        login_tab = driver.find_element_by_id("login-tab")
        login_tab.click()
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't access login tab; can't continue!")
        return False
    try:
        log(INFO, "Try to sign up with uppercase version of already used email.")
        assert not sign_up_to_isaac(driver, Users.Guerrilla.email.upper(), Users.Guerrilla.firstname, Users.Guerrilla.lastname, Users.Guerrilla.password, suppress=True, wait_dur=WAIT_DUR)
        wait_for_xpath_element(driver, "//h4[contains(text(), 'Registration Failed')]/span[contains(text(), 'An account already exists with the e-mail address')]")
        time.sleep(WAIT_DUR)
        log(INFO, "Couldn't sign up, as expected.")
        driver.get(ISAAC_WEB)
        log(INFO, "Got: %s" % ISAAC_WEB)
        time.sleep(WAIT_DUR)
        log(PASS, "Cannot sign up with uppercase form of existing email.")
        return True
    except TimeoutException:
        log(ERROR, "Sign up with uppercase password failed with wrong error message!")
        return False
    except AssertionError:
        log(ERROR, "Sign up successful despite being uppercase form of existing account!")
        return False


#####
# Test 18 : User Consistency
#####
@TestWithDependency("USER_CONSISTENCY", Results, ["LOGIN"])
def user_consistency(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)

    submit_login_form(driver, user=Users.Student, wait_dur=WAIT_DUR)
    time.sleep(WAIT_DUR)

    try:
        assert_logged_in(driver, Users.Student, wait_dur=WAIT_DUR)
        log(INFO, "Login successful.")
    except AssertionError:
        log(INFO, "Login failed!")
        log(ERROR, "Can't login to continue testing user consistency!")
        return False

    new_tab(driver)
    driver.get(ISAAC_WEB)
    log(INFO, "Got: %s." % ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        assert_logged_in(driver, Users.Student, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
        log(PASS, "User still logged in in new tab.")
        return True
    except AssertionError:
        close_tab(driver)
        time.sleep(WAIT_DUR)
        log(ERROR, "User not still logged in in new tab; can't test user consistency!")
        return False


#####
# Test 19 : User Consistency Popup
#####
@TestWithDependency("USER_CONSISTENCY_POPUP", Results, ["USER_CONSISTENCY"])
def user_consistency_popup(driver):
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out the user in the new tab.")
    time.sleep(WAIT_DUR)
    try:
        assert_logged_out(driver, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
        log(INFO, "Logged out in new tab successfully.")
    except AssertionError:
        image_div(driver, "ERROR_logout_failure")
        close_tab(driver)
        time.sleep(WAIT_DUR)
        log(ERROR, "Couldn't logout in new tab; see 'ERROR_logout_failure.png'!")
        return False

    non_isaac_url = "http://www.bbc.co.uk"
    driver.get(non_isaac_url)
    log(INFO, "Navigating away from Isaac (to '%s') to avoid muddling tabs." % non_isaac_url)
    time.sleep(WAIT_DUR)

    assert_tab(driver, ISAAC_WEB)
    try:
        consistency_popup = wait_for_xpath_element(driver, "//div[@isaac-modal='userConsistencyError']")
        log(INFO, "User consistency popup shown.")
        image_div(driver, "user_consistency_popup", consistency_popup)
        save_element_html(consistency_popup, "user_consistency_popup")
    except TimeoutException:
        image_div(driver, "ERROR_user_consistency_not_shown")
        close_tab(driver)
        time.sleep(WAIT_DUR)
        log(ERROR, "User consistency popup not shown; see 'ERROR_user_consistency_not_shown.png'!")
        return False

    try:
        continue_button = driver.find_element_by_xpath("//div[@id='isaacModal']//div[@isaac-modal='userConsistencyError']//button[text()='Continue']")
        continue_button.click()
        time.sleep(WAIT_DUR)
        assert_logged_out(driver, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
        assert_tab(driver, non_isaac_url)
        close_tab(driver)
        log(PASS, "User consistency popup shown and forced logout.")
        return True
    except NoSuchElementException:
        close_tab(driver)
        time.sleep(WAIT_DUR)
        log(ERROR, "Cannot click 'Continue' button; see 'user_consistency_popup.png'!")
        return False
    except AssertionError:
        close_tab(driver)
        time.sleep(WAIT_DUR)
        log(ERROR, "User inconsistency did not force logout!")
        return False


#####
# Test 20 : Change Email Address
#####
@TestWithDependency("EMAIL_CHANGE", Results, ["LOGIN", "GLOBAL_NAV", "SIGNUP", "RECIEVE_VERIFY_EMAILS"])
def email_change(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)
    log(INFO, "Attempting to change email address for '%s'." % Users.Guerrilla.email)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)
    submit_login_form(driver, user=Users.Guerrilla, wait_dur=WAIT_DUR)
    time.sleep(WAIT_DUR)

    try:
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        log(INFO, "Opened global nav (menu bar).")
        time.sleep(WAIT_DUR)
        my_account_link = driver.find_element_by_xpath("(//a[@ui-sref='accountSettings'])[2]")
        my_account_link.click()
        log(INFO, "Clicked 'My Account' button.")
        time.sleep(WAIT_DUR)
    except (NoSuchElementException, ElementNotVisibleException):
        image_div(driver, "ERROR_account_global_nav")
        log(ERROR, "Couldn't access 'My Account' link from global nav; see ERROR_account_global_nav.png'")
        return False
    try:
        start_url = driver.current_url
        assert "/account" in start_url, "'/account' not in URL: '%s'!" % start_url
        email_address_box = driver.find_element_by_xpath("//input[@id='account-email']")
        image_div(driver, "change_email_old_email", email_address_box.find_element_by_xpath(".."))
        email_address_box.clear()
        email_address_box.send_keys(Users.Guerrilla.new_email)
        time.sleep(WAIT_DUR)
        image_div(driver, "change_email_new_email", email_address_box.find_element_by_xpath(".."))
        save_button = driver.find_element_by_xpath("//a[text()='Save']")
        save_button.click()
        time.sleep(WAIT_DUR)
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        time.sleep(WAIT_DUR)
        log(INFO, "Have to accept an alert.")
        assert "You have edited your email address." in alert_text, "Alert contained unexpected message '%s'!" % alert_text
        log(INFO, "Alert said: '%s'." % alert_text)
        time.sleep(WAIT_DUR)
        end_url = driver.current_url
        assert end_url != start_url, "Expected to leave account page, but still on '%s'!" % end_url
        end_loc = end_url.split("#")[0]
        assert end_loc == ISAAC_WEB + "/", "Should have redirected to homepage, went to '%s' instead!" % end_url
        log(PASS, "Email changed in account setting successfully.")
        return True
    except AssertionError, e:
        image_div(driver, "ERROR_change_email_page")
        log(ERROR, e.message)
        return False
    except NoSuchElementException:
        image_div(driver, "ERROR_change_email_page")
        log(ERROR, "Couldn't change password on 'My Account' page; see 'ERROR_change_email_page.png'!")
        return False


#####
# Test 21 : Check Change Email Emails Recieved
#####
@TestWithDependency("EMAIL_CHANGE_EMAILS", Results, ["EMAIL_CHANGE"])
def email_change_emails(driver, inbox, Users):
    assert_tab(driver, GUERRILLAMAIL)
    log(INFO, "Checking if emails were sent after changing account email.")
    log(INFO, "Wating 10 seconds for emails to arrive.")
    time.sleep(11)

    inbox.refresh()
    time.sleep(WAIT_DUR)
    try:
        old_warning_email = inbox.get_by_subject("Change in Isaac Physics email address requested!")[0]
        log(INFO, "Old warning email recieved and has expected subject line.")
        old_warning_email.image("change_email_old_email.png")
        old_warning_email.save_html_body("change_email_old_email")
        old_warning_email.view()
        email_body = old_warning_email.get_email_body_element()
        email_body.find_element_by_xpath("//a[text()='%s']" % Users.Guerrilla.new_email)
        old_warning_email.close()
        log(INFO, "Warning email successfully sent to old address.")
    except IndexError:
        image_div(driver, "ERROR_no_old_email_warning")
        log(ERROR, "No warning email recieved in old email inbox; see 'ERROR_no_old_email_warning.png'!")
        return False
    except NoSuchElementException:
        log(ERROR, "Link to new address not in old warning email, see image!")
        return False
    time.sleep(WAIT_DUR)
    set_guerrilla_mail_address(driver, Users.Guerrilla.new_email)
    log(INFO, "Wating 10 seconds for emails to arrive.")
    time.sleep(11)
    inbox.refresh()

    try:
        new_verify_email = inbox.get_by_subject("Verify your email")[0]
        log(INFO, "New verify email recieved and has expected subject line.")
        new_verify_email.image("change_email_new_email.png")
        new_verify_email.save_html_body("change_email_new_email")
        new_verify_email.view()
        time.sleep(WAIT_DUR)
        email_body = new_verify_email.get_email_body_element()
        verification_link = email_body.find_element_by_xpath(".//a[text()='Verify your email address']")
        Users.Guerrilla.verify_link = str(verification_link.get_attribute("href"))
        log(INFO, "Copied verification link.")
        new_verify_email.close()
        time.sleep(WAIT_DUR)
        log(PASS, "Emails recieved for old and new accounts after changing email address.")
        return True
    except IndexError:
        image_div(driver, "ERROR_verify_new_not_recieved")
        log(ERROR, "Verification email for new email not recieved; see 'ERROR_verify_new_not_recieved.png'!")
        return False
    except NoSuchElementException:
        driver.get(GUERRILLAMAIL)
        log(INFO, "Couldn't access expected parts of email. Refresh page to cleanup.")
        time.sleep(WAIT_DUR)
        log(ERROR, "Couldn't access new email verification link in email!")
        return False


#####
# Test 22 : Check Login Status After Email Change
#####
@TestWithDependency("EMAIL_CHANGE_LOGIN_STATUS", Results, ["EMAIL_CHANGE_EMAILS"])
def email_change_login_status(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    log(INFO, "Now testing login conditions; old email should work until after verification, then new email only.")
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)
    ###
    submit_login_form(driver, user=Users.Guerrilla, wait_dur=WAIT_DUR)
    log(INFO, "Submitted login form with old credentials.")
    time.sleep(WAIT_DUR)
    try:
        assert_logged_in(driver, Users.Guerrilla, wait_dur=WAIT_DUR)
        log(INFO, "Login successful with old email before verification of new email.")
    except AssertionError:
        log(INFO, "Login failed.")
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Login failed with old email before verification of new email; see 'ERROR_not_logging_in.png'!")
        return False
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out again.")
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)
    try:
        log(INFO, "Submit login form with new credentials.")
        submit_login_form(driver, Users.Guerrilla.new_email, Users.Guerrilla.password, wait_dur=WAIT_DUR)
        wait_for_xpath_element(driver, "//strong[text()='Incorrect credentials provided.']", 5)
        log(INFO, "Login failed with new email before verification of new email.")
    except TimeoutException:
        image_div(driver, "ERROR_logged_in_unexpectedly")
        log(ERROR, "Login succeeded with old email before verification of new email; see 'ERROR_logged_in_unexpectedly.png'!")
        return False
    driver.refresh()
    time.sleep(WAIT_DUR)
    ###
    log(INFO, "Now verifying new email address.")
    new_tab(driver)
    time.sleep(WAIT_DUR)
    try:
        driver.get(Users.Guerrilla.verify_link)
        log(INFO, "Got: %s" % Users.Guerrilla.verify_link)
        wait_for_xpath_element(driver, "//h2[@ng-if='verificationState==verificationStates.SUCCESS']")
        time.sleep(WAIT_DUR)
        log(INFO, "Verification of new email address succeeded.")
        close_tab(driver)
    except TimeoutException:
        image_div(driver, "ERROR_change_email_verify_fail")
        close_tab(driver)
        time.sleep(WAIT_DUR)
        log(ERROR, "New email verification failed, can't continue. See 'ERROR_change_email_verify_fail.png'!")
        return False
    except AttributeError:
        close_tab(driver)
        time.sleep(WAIT_DUR)
        log(ERROR, "New email verfication link not saved. Can't complete test!")
        return False
    ###
    assert_tab(driver, ISAAC_WEB)
    submit_login_form(driver, user=Users.Guerrilla, wait_dur=WAIT_DUR)
    log(INFO, "Submitted login form with old credentials.")
    try:
        wait_for_xpath_element(driver, "//strong[text()='Incorrect credentials provided.']", 5)
        log(INFO, "Login failed with old email after verification of new email.")
    except TimeoutException:
        image_div(driver, "ERROR_logged_in_unexpectedly")
        log(ERROR, "Login suceeded with old email after verification of new email; see 'ERROR_logged_in_unexpectedly.png'!")
        return False
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)
    try:
        submit_login_form(driver, Users.Guerrilla.new_email, Users.Guerrilla.password, wait_dur=WAIT_DUR)
        log(INFO, "Submitted login form with new credentials.")
        time.sleep(WAIT_DUR)
        assert_logged_in(driver, wait_dur=WAIT_DUR)
        log(INFO, "Login successful with new email after verification of new email.")
    except AssertionError:
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Login failed with new email after verification of new email; see 'ERROR_not_logging_in.png'!")
        return False
    time.sleep(WAIT_DUR)
    Users.Guerrilla.old_email = Users.Guerrilla.email
    Users.Guerrilla.email = Users.Guerrilla.new_email
    log(PASS, "Old login worked until verification of new, then stopped. New didn't work until verification.")
    return True


#####
# Test 23 : Access Admin Page As Users
#####
@TestWithDependency("ADMIN_PAGE_ACCESS", Results, ["LOGIN", "LOGOUT"])
def admin_page_access(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)

    admin_access_fail = False

    try:
        log(INFO, "Test if logged out user can access '/admin'.")
        driver.get(ISAAC_WEB + "/admin")
        time.sleep(WAIT_DUR)
        assert "/login?target=%2Fadmin" in driver.current_url
        log(INFO, "Logged out users can't access admin page.")
        time.sleep(WAIT_DUR)
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logging out to start from same initial page each time.")
        time.sleep(WAIT_DUR)
    except AssertionError:
        admin_access_fail = True
        image_div(driver, "ERROR_unexpected_admin_access")
        log(ERROR, "Logged out user accessed '/admin'; see 'ERROR_unexpected_admin_access.png'!")

    access_cases = [("Student", Users.Student), ("Teacher", Users.Teacher), ("Content Editor", Users.Editor)]
    for i_type, user in access_cases:
        log(INFO, "Test if '%s' users can access admin page." % i_type)
        try:
            driver.get(ISAAC_WEB + "/admin")
            time.sleep(WAIT_DUR)
            submit_login_form(driver, user=user, wait_dur=WAIT_DUR)
            time.sleep(WAIT_DUR)
            assert_logged_in(driver, user, wait_dur=WAIT_DUR)
            wait_for_xpath_element(driver, "//h1[text()='Unauthorised']")
            log(INFO, "User of type '%s' can't access admin page." % i_type)
        except TimeoutException:
            admin_access_fail = True
            image_div(driver, "ERROR_unexpected_admin_access")
            log(ERROR, "User of type '%s' accessed '/admin'; see 'ERROR_unexpected_admin_access.png'!")
        except AssertionError:
            log(ERROR, "Couldn't log user in to test '/admin' access!")
            return False
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logged out '%s' user." % i_type)
        time.sleep(3)

    access_cases = [("Event Manager", Users.Event), ("Admin", Users.Admin)]
    for i_type, user in access_cases:
        driver.get(ISAAC_WEB + "/login")
        log(INFO, "Got '%s'. As admin, try to use global nav." % (ISAAC_WEB + "/login"))
        time.sleep(WAIT_DUR)
        try:
            submit_login_form(driver, user=user, wait_dur=WAIT_DUR)
            time.sleep(WAIT_DUR)
            global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
            global_nav.click()
            time.sleep(WAIT_DUR)
            site_admin_link = driver.find_element_by_xpath("//a[@ui-sref='admin']")
            site_admin_link.click()
            time.sleep(WAIT_DUR)
            wait_for_xpath_element(driver, "//h1[text()='Isaac Administration']")
            time.sleep(WAIT_DUR)
            log(INFO, "'%s' users can access '/admin'." % i_type)
        except TimeoutException:
            admin_access_fail = True
            image_div(driver, "ERROR_no_admin_access")
            log(ERROR, "'%s' user can't access '/admin'; see 'ERROR_no_admin_access.png'!" % i_type)
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logged out '%s' user." % i_type)
        time.sleep(3)

    if not admin_access_fail:
        log(PASS, "Access to admin page restricted appropriately.")
        return True
    else:
        return False


#####
# Test 24 : Delete A User
#####
@TestWithDependency("DELETE_USER", Results, ["LOGIN", "SIGNUP"])
def delete_user(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    log(INFO, "Attempt to delete temporary user.")
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(WAIT_DUR)
    try:
        submit_login_form(driver, user=Users.Admin, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        time.sleep(WAIT_DUR)
        user_manager_link = driver.find_element_by_xpath("//a[@ui-sref='adminUserManager']")
        user_manager_link.click()
    except NoSuchElementException:
        log(ERROR, "Can't access User Manager from Global Nav; can't continue testing!")
        return False
    try:
        time.sleep(WAIT_DUR)
        email_field = driver.find_element_by_id("user-search-email")
        email_field.send_keys(Users.Guerrilla.email)
        time.sleep(WAIT_DUR)
        search_button = driver.find_element_by_xpath("//a[@ng-click='findUsers()']")
        search_button.click()
        wait_for_invisible_xpath(driver, "//h3[contains(text(), 'Manage Users ()')]")
    except TimeoutException:
        log(ERROR, "Search button did not work; can't continue testing!")
        return False
    try:
        del_button_xpath = "//td[text()='%s']/..//a[contains(@ng-click, 'deleteUser')]" % Users.Guerrilla.email
        delete_button = driver.find_element_by_xpath(del_button_xpath)
        delete_button.click()
        time.sleep(4)
        alert = driver.switch_to.alert
        alert_text = alert.text
        log(INFO, "Alert, with message: '%s'." % alert_text)
        expected = "Are you sure you want to delete the account with email address: %s?" % Users.Guerrilla.email
        assert expected in alert_text, "Alert contained unexpected message '%s'!" % alert_text
        log(INFO, "Accepted the alert.")
        alert.accept()
        popup = wait_for_xpath_element(driver, "//div[@class='toast-message']/p")
        popup_text = popup.text
        log(INFO, "Popup said: '%s'." % popup_text)
        assert 'successfully deleted' in popup_text
        time.sleep(WAIT_DUR)
        log(INFO, "User deleted.")
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logging out the admin user.")
        time.sleep(WAIT_DUR)
        log(PASS, "User '%s' deleted successfuly." % Users.Guerrilla.email)
        return True
    except NoSuchElementException:
        log(ERROR, "No user matching the email found by search; can't delete the account!")
        return False
    except AssertionError, e:
        if "Alert" in e.message:
            alert = driver.switch_to.alert
            alert.dismiss
            log(ERROR, "Dismiss the alert, do not accept!")
            return False
        else:
            log(ERROR, "Successful deletion message not shown!")
            return False
    except TimeoutException:
        log(ERROR, "No deletion confirmation message shown!")
        return False


#####
# Test 25 : Accordion Sections Open and Close
#####
@TestWithDependency("ACCORDION_BEHAVIOUR", Results)
def accordion_behavior(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/questions/_regression_test_")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/questions/_regression_test_"))
    time.sleep(WAIT_DUR)
    log(INFO, "Check accordions open first section automatically.")
    try:
        wait_for_xpath_element(driver, "//p[text()='This is a quick question.']")
        log(INFO, "First accordion section open by default on question pages.")
        time.sleep(WAIT_DUR)
    except TimeoutException:
        image_div(driver, "ERROR_accordion_default")
        log(ERROR, "First accordion section not open by default; see 'ERROR_accordion_default.png'.")
        return False
    log(INFO, "Try closing an accordion section.")
    try:
        first_accordion_title = driver.find_element_by_xpath("(//a[contains(@class, 'ru_accordion_titlebar')])[1]")
        first_accordion_title.click()
        time.sleep(WAIT_DUR)
        wait_for_invisible_xpath(driver, "//p[text()='This is a quick question.']")
        log(INFO, "Accordions close as expected.")
    except NoSuchElementException:
        log(ERROR, "Can't find accordion title bar to click; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_accordion_closing")
        log(ERROR, "Accordion section did not close correctly; see 'ERROR_accordion_closing.png'")
        return False
    log(INFO, "Try reopening accordion section.")
    try:
        first_accordion_title = driver.find_element_by_xpath("(//a[contains(@class, 'ru_accordion_titlebar')])[1]")
        first_accordion_title.click()
        time.sleep(WAIT_DUR)
        wait_for_xpath_element(driver, "//p[text()='This is a quick question.']")
        log(INFO, "Accordions open as expected.")
        first_accordion_title = driver.find_element_by_xpath("(//a[contains(@class, 'ru_accordion_titlebar')])[1]")
        first_accordion_title.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Closed accordion section; all should now be closed.")
    except NoSuchElementException:
        log(ERROR, "Can't find accordion title bar to click again; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_accordion_reopen")
        log(ERROR, "Accordion section did not reopen correctly; see 'ERROR_accordion_reopen.png'!")
        return False
    log(INFO, "Check all accordion sections work.")
    try:
        accordion_sections = driver.find_elements_by_xpath("//a[contains(@class, 'ru_accordion_titlebar')]")
        assert len(accordion_sections) == 4
        log(INFO, "4 accordion sections on page as expected.")
        log(INFO, "Try to open each accordion section in turn.")
        for i, accordion_title in enumerate(accordion_sections):
            n = i + 1
            accordion_title.click()
            wait_for_xpath_element(driver, "(//dd/a[@class='ru_accordion_titlebar']/../div)[%s]" % n)
            log(INFO, "Accordion section %s correctly shown." % n)
            accordion_title.click()
            wait_for_invisible_xpath(driver, "(//dd/a[@class='ru_accordion_titlebar']/../div)[%s]" % n)
            log(INFO, "Accordion section %s correctly hidden." % n)
            time.sleep(WAIT_DUR)
    except TimeoutException:
        log(ERROR, "Couldn't open all accordion sections!")
        return False
    log(PASS, "Accordion behavior is as expected.")
    return True


#####
# Test 26 : Quick Questions
#####
@TestWithDependency("QUICK_QUESTIONS", Results, ["ACCORDION_BEHAVIOUR"])
def quick_questions(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/questions/_regression_test_")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/questions/_regression_test_"))
    time.sleep(WAIT_DUR)
    try:
        log(INFO, "Check that answer is not initially visible.")
        wait_for_invisible_xpath(driver, "//p[text()='This is the answer.']")
        log(INFO, "Answer not initially visible.")
    except TimeoutException:
        log(ERROR, "Quick question answer initially shown!")
        return False
    try:
        wait_for_xpath_element(driver, "//span[text()='Show answer']")
        log(INFO, "'Show answer' text is initially displayed.")
    except TimeoutException:
        log(ERROR, "'Show answer' text not initially displayed!")
        return False
    try:
        log(INFO, "Try clicking the 'Show answer' button.")
        show = driver.find_element_by_xpath("//div[contains(@class, 'ru_answer_reveal')]/div[@ng-click='isVisible=!isVisible']")
        show.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Check answer was shown.")
        wait_for_xpath_element(driver, "//p[text()='This is the answer.']")
        log(INFO, "Answer was displayed correctly.")
    except NoSuchElementException:
        log(ERROR, "Couldn't find 'Show answer' button to click; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Answer was not displayed after clicking 'Show answer'!")
        return False
    try:
        wait_for_xpath_element(driver, "//span[text()='Hide answer']")
        log(INFO, "'Hide answer' text displayed as expected.")
    except TimeoutException:
        log(ERROR, "'Hide answer' text not shown after answer displayed!")
        return False
    try:
        log(INFO, "Try clicking the 'Hide answer' button to hide answer again.")
        hide = driver.find_element_by_xpath("//div[contains(@class, 'ru_answer_reveal')]/div[@ng-click='isVisible=!isVisible']")
        hide.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Check answer was hidden again.")
        wait_for_invisible_xpath(driver, "//p[text()='This is the answer.']")
        log(INFO, "Answer was hidden again correctly.")
        time.sleep(WAIT_DUR)
        log(PASS, "Quick question behavior as expected.")
        return True
    except NoSuchElementException:
        log(ERROR, "Couldn't find 'Hide answer' button to click; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Answer was not hidden again after clicking 'Hide answer'!")
        return False


#####
# Test 27 : Multiple Choice Questions
#####
@TestWithDependency("MULTIPLE_CHOICE_QUESTIONS", Results, ["ACCORDION_BEHAVIOUR"])
def multiple_choice_questions(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/questions/_regression_test_")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/questions/_regression_test_"))
    time.sleep(WAIT_DUR)
    try:
        second_accordion_title = driver.find_element_by_xpath("(//a[contains(@class, 'ru_accordion_titlebar')])[2]")
        second_accordion_title.click()
        time.sleep(WAIT_DUR)
        mc_question = wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']")
        log(INFO, "Accordion opened, multiple choice question displayed.")
    except NoSuchElementException:
        log(ERROR, "Can't find second accordion section to open; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_multiple_choice")
        log(ERROR, "Accordion section did not open to display the multiple choice question; see 'ERROR_multiple_choice.png'!")
        return False
    try:
        incorrect_choice = mc_question.find_element_by_xpath("//label//span[contains(text(), '%s')]" % "69")
        incorrect_choice.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Selected an incorrect answer.")
    except NoSuchElementException:
        log(ERROR, "Can't select incorrect answer on multiple choice question; can't continue!")
        return False
    try:
        check_answer_button = mc_question.find_element_by_xpath("//button[@ng-click='checkAnswer()']")
        check_answer_button.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Clicked 'Check my answer'.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//h2[text()='incorrect']")
        log(INFO, "An 'incorrect' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacMultiChoiceQuestion']//p[text()='This is an incorrect choice.'])[1]")
        log(INFO, "The editor entered explanation text was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//h5[text()='Please try again.']")
        log(INFO, "The 'Please try again' message was correctly shown.")
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Couldn't click the 'Check my answer' button; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_multiple_choice")
        log(ERROR, "The messages shown for an incorrect answer were not all displayed; see 'ERROR_multiple_choice.png'!")
        return False
    try:
        correct_choice = mc_question.find_element_by_xpath("//label//span[contains(text(), '%s')]" % "42")
        correct_choice.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Selected a correct choice.")
        wait_for_invisible_xpath(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//h2[text()='incorrect']")
        log(INFO, "The 'incorrect' message now correctly hidden after choosing new answer")
        time.sleep(WAIT_DUR)
    except NoSuchElementException:
        log(ERROR, "Can't select correct answer on multiple choice question; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "The 'incorrect' message was not hidden after choosing a new answer!")
        return False
    try:
        check_answer_button = mc_question.find_element_by_xpath("//button[@ng-click='checkAnswer()']")
        check_answer_button.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Clicked 'Check my answer'.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//h1[text()='Correct!']")
        log(INFO, "A 'Correct!' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacMultiChoiceQuestion']//p[text()='This is a correct choice.'])[2]")
        log(INFO, "The editor entered explanation text was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacMultiChoiceQuestion']//strong[text()='Well done!']")
        log(INFO, "The 'Well done!' message was correctly shown.")
        time.sleep(WAIT_DUR)
        log(PASS, "Multiple Choice Question behavior as expected.")
        return True
    except NoSuchElementException:
        log(ERROR, "Couldn't click the 'Check my answer' button; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_multiple_choice")
        log(ERROR, "The messages shown for a correct answer were not all displayed; see 'ERROR_multiple_choice.png'!")
        return False


#####
# Test 28 : Numeric Question Units Dropdown
#####
@TestWithDependency("NUMERIC_Q_UNITS_SELECT", Results, ["ACCORDION_BEHAVIOUR"])
def numeric_q_units_select(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/questions/_regression_test_")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/questions/_regression_test_"))
    time.sleep(WAIT_DUR)
    try:
        third_accordion_title = driver.find_element_by_xpath("(//a[contains(@class, 'ru_accordion_titlebar')])[3]")
        third_accordion_title.click()
        time.sleep(WAIT_DUR)
        num_question = wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']")
        log(INFO, "Accordion opened, numeric question displayed.")
    except NoSuchElementException:
        log(ERROR, "Can't find third accordion section to open; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_units_select")
        log(ERROR, "Accordion section did not open to display the numeric question; see 'ERROR_numeric_q_units_select.png'!")
        return False
    try:
        units_dropdown = num_question.find_element_by_xpath("//button[@ng-click='toggleUnitsDropdown()']")
        units_dropdown.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Clicked to open units dropdown.")
        left = int(float(num_question.find_element_by_xpath(".//ul[@class='f-dropdown']").value_of_css_property('left').replace('px', '')))
        assert left > 0
        log(INFO, "Units dropdown displayed correctly.")
    except AssertionError:
        log(ERROR, "Units dropdown not opened correctly!")
        return False
    except NoSuchElementException:
        log(ERROR, "Can't find numeric question or units dropdown button; can't continue!")
        return False
    except ValueError:
        log(ERROR, "Couldn't read the CSS property 'left' for the dropdown. This probably constitues failure!")
        return False
    try:
        units_dropdown.click()
        time.sleep(WAIT_DUR)
        log(INFO, "Clicked to close units dropdown.")
        left = int(num_question.find_element_by_xpath(".//ul[@class='f-dropdown']").value_of_css_property('left').replace('px', ''))
        assert left < 9000
        log(INFO, "Units dropdown hidden correctly.")
        log(PASS, "Numeric question units popup works correctly.")
        return True
    except AssertionError:
        log(ERROR, "Units dropdown did not close correctly!")
        return False
    except ValueError:
        log(ERROR, "Couldn't read the CSS property 'left' for the dropdown. This probably constitues failure!")
        return False


#####
# Test 29 : Numeric Questions Correct Answers
#####
@TestWithDependency("NUMERIC_Q_ALL_CORRECT", Results, ["NUMERIC_Q_UNITS_SELECT"])
def numeric_q_all_correct(driver):
    assert_tab(driver, ISAAC_WEB)
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
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='This is a correct choice.'])[2]")
        log(INFO, "The editor entered explanation text was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//strong[text()='Well done!']")
        log(INFO, "The 'Well done!' message was correctly shown.")
        time.sleep(WAIT_DUR)
        log(PASS, "Numeric Question 'correct value, correct unit' behavior as expected.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_all_correct")
        log(ERROR, "The messages shown for a correct answer were not all displayed; see 'ERROR_numeric_q_all_correct.png'!")
        return False


#####
# Test 30 : Numeric Questions Answer Change
#####
@TestWithDependency("NUMERIC_Q_ANSWER_CHANGE", Results, ["NUMERIC_Q_UNITS_SELECT", "NUMERIC_Q_ALL_CORRECT"])
def numeric_q_answer_change(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        num_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacNumericQuestion']")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h1[text()='Correct!']")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='This is a correct choice.'])[2]")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//strong[text()='Well done!']")
    except NoSuchElementException:
        log(ERROR, "Can't find the numeric question; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Correct answer text can't be found; can't check if it goes; can't continue!")
        return False

    try:
        log(INFO, "Alter previously typed answer.")
        value_box = num_question.find_element_by_xpath(".//input[@ng-model='selectedChoice.value']")
        value_box.send_keys("00")
    except NoSuchElementException:
        log(ERROR, "Can't find value box to try changing answer; can't continue!")
        return False

    try:
        wait_for_invisible_xpath(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h1[text()='Correct!']")
        wait_for_invisible_xpath(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='This is a correct choice.'])[2]")
        wait_for_invisible_xpath(driver, "//div[@ng-switch-when='isaacNumericQuestion']//strong[text()='Well done!']")
        time.sleep(WAIT_DUR)
        log(PASS, "Numeric Question answer text disappears upon changing answer.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_answer_change")
        log(ERROR, "The messages shown for an old answer do not disappear upon altering answer; see 'ERROR_numeric_q_answer_change.png'!")
        return False


#####
# Test 31 : Numeric Questions Incorrect Unit, Correct Value
#####
@TestWithDependency("NUMERIC_Q_INCORRECT_UNIT", Results, ["NUMERIC_Q_ANSWER_CHANGE"])
def numeric_q_incorrect_unit(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        num_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacNumericQuestion']")
    except NoSuchElementException:
        log(ERROR, "Can't find the numeric question; can't continue!")
        return False

    log(INFO, "Attempt to enter correct value, but incorrect units.")
    if not answer_numeric_q(num_question, "2.01", "\units{ m\,s^{-1} }", get_unit_wrong=True, wait_dur=WAIT_DUR):
        log(ERROR, "Couldn't answer Numeric Question; can't continue!")
        return False
    time.sleep(WAIT_DUR)

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h2[text()='incorrect']")
        log(INFO, "A 'incorrect' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='Check your units.'])[1]")
        log(INFO, "The 'Check your units.' message was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h5[text()='Please try again.']")
        log(INFO, "The 'Please try again.' message was correctly shown.")
        bg_colour = num_question.find_element_by_xpath("(.//div[@class='ru-answer-block-panel'])[2]").value_of_css_property('background-color')
        assert (bg_colour == '#be4c4c') or (bg_colour == 'rgba(190, 76, 76, 1)')
        log(INFO, "Red highlighting shown around units box.")
        time.sleep(WAIT_DUR)
        log(PASS, "Numeric Question 'incorrect unit, correct value' behavior as expected.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_incorrect_unit")
        log(ERROR, "The messages shown for an incorrect unit were not all displayed; see 'ERROR_numeric_q_incorrect_unit.png'!")
        return False
    except AssertionError:
        image_div(driver, "ERROR_numeric_q_incorrect_unit")
        log(ERROR, "The units box was not highlighted red; see 'ERROR_numeric_q_incorrect_unit.png'!")
        return False


#####
# Test 32 : Numeric Questions Correct Unit, Incorrect Value
#####
@TestWithDependency("NUMERIC_Q_INCORRECT_VALUE", Results, ["NUMERIC_Q_ANSWER_CHANGE"])
def numeric_q_incorrect_value(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        num_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacNumericQuestion']")
    except NoSuchElementException:
        log(ERROR, "Can't find the numeric question; can't continue!")
        return False

    log(INFO, "Attempt to enter unknown incorrect value, to correct sig figs and correct units.")
    if not answer_numeric_q(num_question, "4.33", "\units{ m\,s^{-1} }", wait_dur=WAIT_DUR):
        log(ERROR, "Couldn't answer Numeric Question; can't continue!")
        return False
    time.sleep(WAIT_DUR)

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h2[text()='incorrect']")
        log(INFO, "A 'incorrect' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='Check your working.'])[1]")
        log(INFO, "The 'Check your working.' message was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h5[text()='Please try again.']")
        log(INFO, "The 'Please try again.' message was correctly shown.")
        bg_colour = num_question.find_element_by_xpath("(.//div[@class='ru-answer-block-panel'])[1]").value_of_css_property('background-color')
        assert (bg_colour == '#be4c4c') or (bg_colour == 'rgba(190, 76, 76, 1)')
        log(INFO, "Red highlighting shown around value box.")
        time.sleep(WAIT_DUR)
        log(PASS, "Numeric Question 'correct unit, incorrect value' behavior as expected.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_incorrect_value")
        log(ERROR, "The messages shown for an incorrect value were not all displayed; see 'ERROR_numeric_q_incorrect_value.png'!")
        return False
    except AssertionError:
        image_div(driver, "ERROR_numeric_q_incorrect_value")
        log(ERROR, "The units box was not highlighted red; see 'ERROR_numeric_q_incorrect_value.png'!")
        return False


#####
# Test 33 : Numeric Questions Incorrect Value, Incorrect Unit
#####
@TestWithDependency("NUMERIC_Q_ALL_INCORRECT", Results, ["NUMERIC_Q_ANSWER_CHANGE"])
def numeric_q_all_incorrect(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        num_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacNumericQuestion']")
    except NoSuchElementException:
        log(ERROR, "Can't find the numeric question; can't continue!")
        return False

    log(INFO, "Attempt to enter unknown incorrect value, to correct sig figs and incorrect units.")
    if not answer_numeric_q(num_question, "4.33", "\units{ m\,s^{-1} }", get_unit_wrong=True, wait_dur=WAIT_DUR):
        log(ERROR, "Couldn't answer Numeric Question; can't continue!")
        return False
    time.sleep(WAIT_DUR)

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h2[text()='incorrect']")
        log(INFO, "A 'incorrect' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='Check your working.'])[1]")
        log(INFO, "The 'Check your working.' message was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h5[text()='Please try again.']")
        log(INFO, "The 'Please try again.' message was correctly shown.")
        bg_colour1 = num_question.find_element_by_xpath("(.//div[@class='ru-answer-block-panel'])[1]").value_of_css_property('background-color')
        assert (bg_colour1 == '#be4c4c') or (bg_colour1 == 'rgba(190, 76, 76, 1)')
        log(INFO, "Red highlighting shown around value box.")
        bg_colour2 = num_question.find_element_by_xpath("(.//div[@class='ru-answer-block-panel'])[2]").value_of_css_property('background-color')
        assert (bg_colour2 == '#be4c4c') or (bg_colour2 == 'rgba(190, 76, 76, 1)')
        log(INFO, "Red highlighting shown around units box.")
        time.sleep(WAIT_DUR)
        log(PASS, "Numeric Question 'incorrect value, incorrect unit' behavior as expected.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_all_incorrect")
        log(ERROR, "The messages shown for an incorrect answer were not all displayed; see 'ERROR_numeric_q_all_incorrect.png'!")
        return False
    except AssertionError:
        image_div(driver, "ERROR_numeric_q_all_incorrect")
        log(ERROR, "The answer boxes were not highlighted red correctly; see 'ERROR_numeric_q_all_incorrect.png'!")
        return False


#####
# Test 34 : Numeric Questions Incorrect Sig Figs
#####
@TestWithDependency("NUMERIC_Q_INCORRECT_SF", Results, ["NUMERIC_Q_ANSWER_CHANGE"])
def numeric_q_incorrect_sf(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        num_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacNumericQuestion']")
    except NoSuchElementException:
        log(ERROR, "Can't find the numeric question; can't continue!")
        return False

    log(INFO, "Attempt to enter correct value with correct units to incorrect sig figs.")
    if not answer_numeric_q(num_question, "2.0", "\units{ m\,s^{-1} }", wait_dur=WAIT_DUR):
        log(ERROR, "Couldn't answer Numeric Question; can't continue!")
        return False
    time.sleep(WAIT_DUR)

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h2[text()='incorrect']")
        log(INFO, "A 'incorrect' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p/strong[text()='Significant figures']/..)[1]")
        log(INFO, "The 'Significant figures' message was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h5[text()='Please try again.']")
        log(INFO, "The 'Please try again.' message was correctly shown.")
        bg_colour1 = num_question.find_element_by_xpath("(.//div[@class='ru-answer-block-panel'])[1]").value_of_css_property('background-color')
        assert (bg_colour1 == '#be4c4c') or (bg_colour1 == 'rgba(190, 76, 76, 1)')
        log(INFO, "Red highlighting shown around value box.")
        time.sleep(WAIT_DUR)
        log(PASS, "Numeric Question 'correct value, correct unit, incorrect sig fig' behavior as expected.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_incorrect_sf")
        log(ERROR, "The messages shown for an incorrect sig fig answer were not all displayed; see 'ERROR_numeric_q_incorrect_sf.png'!")
        return False
    except AssertionError:
        image_div(driver, "ERROR_numeric_q_incorrect_sf")
        log(ERROR, "The value box was not highlighted red correctly; see 'ERROR_numeric_q_incorrect_sf.png'!")
        return False


#####
# Test 35 : Numeric Questions Incorrect Sig Figs, Incorrect Unit
#####
@TestWithDependency("NUMERIC_Q_INCORRECT_SF_U", Results, ["NUMERIC_Q_ANSWER_CHANGE"])
def numeric_q_incorrect_sf_u(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        num_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacNumericQuestion']")
    except NoSuchElementException:
        log(ERROR, "Can't find the numeric question; can't continue!")
        return False

    log(INFO, "Attempt to enter correct value with incorrect units to incorrect sig figs.")
    if not answer_numeric_q(num_question, "2.0", "\units{ m\,s^{-1} }", get_unit_wrong=True, wait_dur=WAIT_DUR):
        log(ERROR, "Couldn't answer Numeric Question; can't continue!")
        return False
    time.sleep(WAIT_DUR)

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h2[text()='incorrect']")
        log(INFO, "A 'incorrect' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p/strong[text()='Significant figures']/..)[1]")
        log(INFO, "The 'Significant figures' message was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h5[text()='Please try again.']")
        log(INFO, "The 'Please try again.' message was correctly shown.")
        bg_colour1 = num_question.find_element_by_xpath("(.//div[@class='ru-answer-block-panel'])[1]").value_of_css_property('background-color')
        assert (bg_colour1 == '#be4c4c') or (bg_colour1 == 'rgba(190, 76, 76, 1)')
        log(INFO, "Red highlighting shown around value box.")
        bg_colour2 = num_question.find_element_by_xpath("(.//div[@class='ru-answer-block-panel'])[2]").value_of_css_property('background-color')
        assert (bg_colour2 == '#be4c4c') or (bg_colour2 == 'rgba(190, 76, 76, 1)')
        log(INFO, "Red highlighting shown around units box.")
        time.sleep(WAIT_DUR)
        log(PASS, "Numeric Question 'correct value, incorrect unit, incorrect sig fig' behavior as expected.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_incorrect_sf_u")
        log(ERROR, "The messages shown for an incorrect sig fig answer were not all displayed; see 'ERROR_numeric_q_incorrect_sf_u.png'!")
        return False
    except AssertionError:
        image_div(driver, "ERROR_numeric_q_incorrect_sf_u")
        log(ERROR, "The answer boxes were not highlighted red correctly; see 'ERROR_numeric_q_incorrect_sf_u.png'!")
        return False


#####
# Test 36 : Numeric Questions Known Wrong Answer
#####
@TestWithDependency("NUMERIC_Q_KNOWN_WRONG_ANS", Results, ["NUMERIC_Q_ANSWER_CHANGE"])
def numeric_q_known_wrong_ans(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        num_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacNumericQuestion']")
    except NoSuchElementException:
        log(ERROR, "Can't find the numeric question; can't continue!")
        return False

    log(INFO, "Attempt to enter known (content-editor specified) wrong answer.")
    if not answer_numeric_q(num_question, "5.00", "\units{ m\,s^{-1} }", wait_dur=WAIT_DUR):
        log(ERROR, "Couldn't answer Numeric Question; can't continue!")
        return False
    time.sleep(WAIT_DUR)

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h2[text()='incorrect']")
        log(INFO, "A 'incorrect' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='This is an incorrect choice.'])[1]")
        log(INFO, "The content editor entered message was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h5[text()='Please try again.']")
        log(INFO, "The 'Please try again.' message was correctly shown.")
        bg_colour1 = num_question.find_element_by_xpath("(.//div[@class='ru-answer-block-panel'])[1]").value_of_css_property('background-color')
        assert (bg_colour1 == '#be4c4c') or (bg_colour1 == 'rgba(190, 76, 76, 1)')
        log(INFO, "Red highlighting shown around value box.")
        time.sleep(WAIT_DUR)
        log(PASS, "Numeric Question 'correct value, correct unit, incorrect sig fig' behavior as expected.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_known_wrong_ans")
        log(ERROR, "The messages shown for a known incorrect answer were not all displayed; see 'ERROR_numeric_q_known_wrong_ans.png'!")
        return False
    except AssertionError:
        image_div(driver, "ERROR_numeric_q_known_wrong_ans")
        log(ERROR, "The value box was not highlighted red correctly; see 'ERROR_numeric_q_known_wrong_ans.png'!")
        return False


#####
# Test 37 : Numeric Questions Known Wrong Answer, Wrong Sig Figs
#####
@TestWithDependency("NUMERIC_Q_KNOWN_WRONG_SF", Results, ["NUMERIC_Q_ANSWER_CHANGE"])
def numeric_q_known_wrong_sf(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    try:
        num_question = driver.find_element_by_xpath("//div[@ng-switch-when='isaacNumericQuestion']")
    except NoSuchElementException:
        log(ERROR, "Can't find the numeric question; can't continue!")
        return False

    log(INFO, "Attempt to enter known (content-editor specified) wrong answer, to wrong sig figs.")
    if not answer_numeric_q(num_question, "42", "\units{ m\,s^{-1} }", wait_dur=WAIT_DUR):
        log(ERROR, "Couldn't answer Numeric Question; can't continue!")
        return False
    time.sleep(WAIT_DUR)

    try:
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h2[text()='incorrect']")
        log(INFO, "A 'incorrect' message was displayed as expected.")
        wait_for_xpath_element(driver, "(//div[@ng-switch-when='isaacNumericQuestion']//p[text()='Hello'])[1]")
        log(INFO, "The content editor entered message was correctly shown.")
        wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']//h5[text()='Please try again.']")
        log(INFO, "The 'Please try again.' message was correctly shown.")
        bg_colour1 = num_question.find_element_by_xpath("(.//div[@class='ru-answer-block-panel'])[1]").value_of_css_property('background-color')
        assert (bg_colour1 == '#be4c4c') or (bg_colour1 == 'rgba(190, 76, 76, 1)')
        log(INFO, "Red highlighting shown around value box.")
        time.sleep(WAIT_DUR)
        log(PASS, "Numeric Question 'correct value, correct unit, incorrect sig fig' behavior as expected.")
        return True
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_known_wrong_sf")
        log(INFO, "The sig fig warning should not have been shown. if it was, this is likely the error.")
        log(ERROR, "The messages shown for a known incorrect answer were not all displayed; see 'ERROR_numeric_q_known_wrong_sf.png'!")
        return False
    except AssertionError:
        image_div(driver, "ERROR_numeric_q_known_wrong_sf")
        log(ERROR, "The value box was not highlighted red correctly; see 'ERROR_numeric_q_known_wrong_sf.png'!")
        return False


#####
# Test M : Numeric Questions Help Popup
#####
@TestWithDependency("NUMERIC_Q_HELP_POPUP", Results, ["ACCORDION_BEHAVIOUR"])
def numeric_q_help_popup(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(WAIT_DUR)
    driver.get(ISAAC_WEB + "/questions/_regression_test_")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/questions/_regression_test_"))
    time.sleep(WAIT_DUR)
    try:
        third_accordion_title = driver.find_element_by_xpath("(//a[contains(@class, 'ru_accordion_titlebar')])[3]")
        third_accordion_title.click()
        time.sleep(WAIT_DUR)
        num_question = wait_for_xpath_element(driver, "//div[@ng-switch-when='isaacNumericQuestion']")
        log(INFO, "Accordion opened, multiple choice question displayed.")
    except NoSuchElementException:
        log(ERROR, "Can't find third accordion section to open; can't continue!")
        return False
    except TimeoutException:
        image_div(driver, "ERROR_numeric_q_help_popup")
        log(ERROR, "Accordion section did not open to display the numeric question; see 'ERROR_numeric_q_help_popup.png'!")
        return False
    try:
        help_mark = driver.find_element_by_xpath("//span[@class='value-help']")
        help_mark.click()
        wait_for_xpath_element(driver, "//span[@class='value-help']/div[@class='popup']")
        log(INFO, "Help message correctly shown on mouseover.")
        log(PASS, "Numeric question help message displays.")
        return True
    except NoSuchElementException:
        log(ERROR, "Couldn't find help button; can't continue!")
        return False
    except TimeoutException:
        log(ERROR, "Help message popup not shown!")
        return False

"//a[contains(@class, 'ru_accordion_titlebar')]"  # Accordion title bars
"//div[@isaac-question-tabs]"  # Container divs for questions
"//label//span[contains(text(), '%s')]"  # Multiple choice question options
"//div[contains(@class, 'ru_answer_reveal')]/div[@ng-click='isVisible=!isVisible']"  # Show/Hide button
"//a[contains(text(), 'Hint ')]"  # Hint tabs
"//button[@ng-click='checkAnswer()']"  # Check my answer button
"//input[@ng-model='selectedChoice.value']"  # Numeric answer box
"//button[@ng-click='toggleUnitsDropdown()']"  # Numeric units dropdown
"//a[@ng-click='selectUnit(u)']"  # Numeric unit choices
"//figure[contains(@class, 'ru_figure')]/.."  # Figure container div
"//figure[contains(@class, 'ru_figure')]/..//p"  # Figure caption

fatal_error = True
try:
    login(driver, Users)
    questionnaire(driver)
    global_nav(driver)
    logout(driver)
    login_throttle(driver, Users)
    login_timeout(driver, Users)
    signup(driver, Users)
    welcome_email(driver, inbox)
    req_verify_emails(driver)
    recieve_verify_emails(driver, inbox)
    verify_link(driver, inbox)
    verify_banner_gone(driver)
    pwd_reset_throttle(driver, Users)
    recieve_pwd_reset_emails(driver, inbox)
    pwd_reset_link(driver, inbox, Users)
    reset_pwd_login(driver, Users)
    login_uppercase(driver, Users)
    signup_uppercase(driver, Users)
    user_consistency(driver, Users)
    user_consistency_popup(driver)
    email_change(driver, Users)
    email_change_emails(driver, inbox, Users)
    email_change_login_status(driver, Users)
    admin_page_access(driver, Users)
    delete_user(driver, Users)
    accordion_behavior(driver)
    quick_questions(driver)
    multiple_choice_questions(driver)
    numeric_q_units_select(driver)
    numeric_q_all_correct(driver)
    numeric_q_answer_change(driver)
    numeric_q_incorrect_unit(driver)
    numeric_q_incorrect_value(driver)
    numeric_q_all_incorrect(driver)
    numeric_q_incorrect_sf(driver)
    numeric_q_incorrect_sf_u(driver)
    numeric_q_known_wrong_ans(driver)
    numeric_q_known_wrong_sf(driver)
    numeric_q_help_popup(driver)
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
    end_testing(Results, email=False, aborted=fatal_error)
