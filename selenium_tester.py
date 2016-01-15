# Selenium Test
import os
import time
import datetime
from collections import OrderedDict
#####
from isaactest.emails.guerrillamail import set_guerrilla_mail_address, GuerrillaInbox
from isaactest.utils.log import log, INFO, ERROR, PASS, start_testing, end_testing
from isaactest.utils.isaac import submit_login_form, assert_logged_in, assert_logged_out, sign_up_to_isaac
from isaactest.utils.isaac import kill_irritating_popup, disable_irritating_popup
from isaactest.utils.isaac import TestUsers, User
from isaactest.utils.i_selenium import assert_tab, new_tab, close_tab, image_div, save_element_html
from isaactest.utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
from isaactest.tests import TestWithDependency
#####
import selenium.webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotVisibleException
####
# Set the working dir:
os.chdir("/path/to/dir")

PATH_TO_CHROMEDRIVER = "../chromedriver"

# Some important global constants:
ISAAC_WEB = "https://staging.isaacphysics.org"
GUERRILLAMAIL = "https://www.guerrillamail.com"


# Global objects:
def define_users():
    Users = TestUsers.load()
    _Guerrilla = User("isaactest@sharklasers.com", "Temp",
                      "Test", "test")
    Users.Guerrilla = _Guerrilla
    Users.Guerrilla.new_email = "isaactesttwo@sharklasers.com"
    Users.Guerrilla.new_password = "testing123"
    return Users
Users = define_users()  # Delete
Results = OrderedDict()

# Open a folder just for this test:
RUNDATE = datetime.datetime.now().strftime("%Y%m%d_%H%M")
RUNDATE = ""
try:
    os.mkdir("test_" + RUNDATE)
except WindowsError:
    pass
os.chdir("test_" + RUNDATE)


# Start testing:
start_testing()


#####
# Test -1 : Start up Selenium
#####
def selenium_startup(Users):
    # Selenium Start-up:
    driver = selenium.webdriver.Firefox()
    #driver = selenium.webdriver.Chrome(PATH_TO_CHROMEDRIVER)
    driver.set_window_size(1920, 1080)
    log(INFO, "Opened Selenium Driver for '%s'." % driver.name.title())
    time.sleep(2)
    # Navigate to Staging:
    driver.get(ISAAC_WEB)
    log(INFO, "Got: %s" % ISAAC_WEB)
    time.sleep(2)
    # Open GuerrillaMail:
    new_tab(driver)
    time.sleep(1)
    driver.get(GUERRILLAMAIL)
    log(INFO, "Got: %s" % GUERRILLAMAIL)
    # Set Guerrilla Mail email address:
    time.sleep(1)
    Users.Guerrilla.email = set_guerrilla_mail_address(driver, Users.Guerrilla.email)
    time.sleep(1)
    inbox = GuerrillaInbox(driver)
    time.sleep(1)
    # Delete GuerrillaMail welcome:
    initial_emails = inbox.get_by_subject("Welcome to Guerrilla Mail")
    for e in initial_emails:
        inbox.delete_email(e)
    time.sleep(1)
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
        submit_login_form(driver, user=Users.Student, disable_popup=False)
    except NoSuchElementException:
        log(ERROR, "Couldn't click login tab; can't login!")
        return False
    time.sleep(1)
    try:
        assert_logged_in(driver, Users.Student)
        log(INFO, "Login successful.")
        log(PASS, "Login using username and password successful.")
        return True
    except AssertionError:
        log(INFO, "Login failed!")
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Can't login; see 'ERROR_not_logging_in.png'!")
        return False
login(driver, Users)  # Delete


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
questionnaire(driver)  # Delete


#####
# Test 3 : Logout Button
#####
@TestWithDependency("LOGOUT", Results, ["LOGIN"])
def logout(driver):
    assert_tab(driver, ISAAC_WEB)
    try:
        logout_button = driver.find_element_by_xpath("//a[@ui-sref='logout']")
        logout_button.click()
    except NoSuchElementException:
        image_div(driver, "ERROR_logout_failure")
        log(ERROR, "Can't find logout button; can't logout, see 'ERROR_logout_failure.png'!")
        return False
    time.sleep(1)
    try:
        assert_logged_out(driver)
        log(INFO, "Logged out.")
        log(PASS, "Log out button works.")
        return True
    except AssertionError:
        image_div(driver, "ERROR_logout_failure")
        log(ERROR, "Couldn't logout; see 'ERROR_logout_failure.png'!")
        return False
logout(driver)  # Delete


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
        submit_login_form(driver, username=Users.Student.email, password="wrongpassword")
        time.sleep(1)
    try:
        driver.find_element_by_xpath("//strong[contains(text(), 'too many attempts to login')]")
        log(PASS, "11 login attempts. Warning message and locked out for 10 mins.")
        return True
    except NoSuchElementException:
        image_div(driver, "11_login_attempts")
        log(ERROR, "Tried to log in 11 times. No error message; see '11_login_attempts.png'!")
        return False
login_throttle(driver, Users)  # Delete


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
    time.sleep(2)
    try:
        assert_logged_in(driver, Users.Student)
        log(INFO, "Login successful.")
        log(PASS, "Login after 10 minute lockout.")
        return True
    except AssertionError:
        log(INFO, "Login failed!")
        image_div(driver, "ERROR_login_after_lockout")
        log(ERROR, "Can't login after 10 minute lockout; see 'login_error.png'!")
        return False
login_timeout(driver, Users)  # Delete


#####
# Test 6 : Sign Up to Isaac
#####
@TestWithDependency("SIGNUP", Results, ["LOGIN", "LOGOUT"])
def signup(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(2)

    assert_tab(driver, ISAAC_WEB)
    time.sleep(2)
    try:
        login_tab = driver.find_element_by_id("login-tab")
        login_tab.click()
    except NoSuchElementException:
        log(ERROR, "Can't find login button; can't continue!")
        return False
    time.sleep(2)
    if sign_up_to_isaac(driver, user=Users.Guerrilla):
        log(PASS, "Successfully register new user '%s' on Isaac." % Users.Guerrilla.email)
        return True
    else:
        log(ERROR, "Can't register user!")
        return False
signup(driver, Users)  # Delete


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
welcome_email(driver, inbox)  # Delete


######
# Test 8 : Request Verification Emails
######
@TestWithDependency("REQ_VERIFY_EMAILS", Results, ["SIGNUP"])
def req_verify_emails(driver):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(1)
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
            time.sleep(1)
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
req_verify_emails(driver)  # Delete


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
recieve_verify_emails(driver, inbox)  # Delete


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
        time.sleep(1)
        email_body = verification_email.get_email_body_element()
        verification_link = email_body.find_element_by_xpath(".//a[text()='Verify your email address']")
        verification_link.send_keys(Keys.CONTROL + Keys.ENTER)
        log(INFO, "Opening verification link from email in new tab.")
        time.sleep(1)
        verification_email.close()
        time.sleep(1)
        assert_tab(driver, ISAAC_WEB + "/verifyemail")
        log(INFO, "Verification URL: '%s'." % driver.current_url)
        wait_for_xpath_element(driver, "//h2[@ng-if='verificationState==verificationStates.SUCCESS']")
        close_tab(driver)
        log(PASS, "Email address verified successfully.")
        time.sleep(2)
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
verify_link(driver, inbox)  # Delete


#####
# Test 11 : Verification Banner Gone
#####
@TestWithDependency("VERIFY_BANNER_GONE", Results, ["VERIFY_LINK"])
def verify_banner_gone(driver):
    assert_tab(driver, ISAAC_WEB)
    try:
        driver.refresh()
        time.sleep(2)
        log(INFO, "Checking if verification banner now gone.")
        wait_for_invisible_xpath(driver, "//a[@ng-click='requestEmailVerification()']")
        log(PASS, "Verification banner gone after verifying email.")
        return True
    except TimeoutException:
        log(ERROR, "Verification banner still present after email verified!")
        return False
verify_banner_gone(driver)  # Delete


#####
# Test 12 : Forgot My Password Button Limit
#####
@TestWithDependency("PWD_RESET_THROTTLE", Results, ["LOGIN", "LOGOUT", "SIGNUP"])
def pwd_reset_throttle(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(2)

    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(1)
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
            image_div(driver, "reset_password_button_message_%s" % i)
            password_resets += 1
            if i <= forgot_pwd_request_limit - 1:  # i starts from 0 not 1
                try:
                    wait_for_invisible_xpath(driver, "//div[@class='toast-message']/h4", 0.5)
                except TimeoutException:
                    raise TimeoutException("Password reset error message unexpectedly shown after %s requests!" % password_resets)
                message = driver.find_element_by_xpath("(//p[@ng-show='passwordResetFlag'])[2]")
                assert "Your password request is being processed." in message.text
            else:
                try:
                    wait_for_xpath_element(driver, "//div[@class='toast-message']/h4")
                except TimeoutException:
                    raise TimeoutException("Password reset error message not shown after %s requests." % password_resets)
                log(INFO, "Password reset error message shown after %s attempts." % password_resets)
                break
            time.sleep(2)
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
pwd_reset_throttle(driver, Users)  # Delete


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
    time.sleep(1)

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
recieve_pwd_reset_emails(driver, inbox)  # Delete


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
        time.sleep(1)
        email_body = reset_email.get_email_body_element()
        verification_link = email_body.find_element_by_xpath(".//a[text()='Click Here']")
        verification_link.send_keys(Keys.CONTROL + Keys.ENTER)
        log(INFO, "Opening reset password link from email in new tab.")
        reset_email.close()
        time.sleep(1)
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
        time.sleep(1)
    except NoSuchElementException:
        log(ERROR, "Can't access reset password form correctly; can't continue!")
        return False
    try:
        driver.find_element_by_xpath("//div[@ng-switch='submitted']/div[contains(text(), 'reset successfully')]")
        Users.Guerrilla.password = Users.Guerrilla.new_password
        close_tab(driver)
        time.sleep(1)
        log(PASS, "Reset password link works.")
        return True
    except NoSuchElementException:
        image_div(driver, "ERROR_resetting_password")
        log(ERROR, "Resetting password failed; see 'ERROR_resetting_password.png'!")
        return False
pwd_reset_link(driver, inbox, Users)  # Delete


#####
# Test 15 : Logging In With New Password
#####
@TestWithDependency("RESET_PWD_LOGIN", Results, ["LOGIN", "PWD_RESET_LINK"])
def reset_pwd_login(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB)
    log(INFO, "Got: %s" % ISAAC_WEB)
    time.sleep(1)

    try:
        login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
        login_tab.click()
        submit_login_form(driver, user=Users.Guerrilla)
        time.sleep(2)
    except NoSuchElementException:
        log(ERROR, "Can't access login tab; can't continue!")
        return False
    try:
        assert_logged_in(driver, Users.Guerrilla)
        log(INFO, "Login successful.")
        log(PASS, "Login using username and new password successful.")
        return True
    except AssertionError:
        log(INFO, "Login failed!")
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Can't login with new password; see 'ERROR_not_logging_in.png'!")
        return False
reset_pwd_login(driver, Users)  # Delete


#####
# Test 16 : Login Email Case Sensitivity
#####
@TestWithDependency("LOGIN_UPPERCASE", Results, ["LOGIN"])
def login_uppercase(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(2)
    try:
        login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
        login_tab.click()
        submit_login_form(driver, Users.Student.email.upper(), Users.Student.password)
        time.sleep(2)
    except NoSuchElementException:
        log(ERROR, "Can't access login tab; can't continue!")
        return False
    try:
        assert_logged_in(driver, Users.Student)
        log(INFO, "Login successful.")
        log(PASS, "Login using uppercase version of email successful.")
        return True
    except AssertionError:
        log(INFO, "Login failed!")
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Can't login with uppercase email; see 'ERROR_logging_in_uppercase.png'!")
        return False
login_uppercase(driver, Users)  # Delete


#####
# Test 17 : Signup Email Case Sensitivity
#####
@TestWithDependency("SIGNUP_UPPERCASE", Results, ["LOGIN", "SIGNUP"])
def signup_uppercase(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(2)
    try:
        login_tab = driver.find_element_by_id("login-tab")
        login_tab.click()
        time.sleep(2)
    except NoSuchElementException:
        log(ERROR, "Can't access login tab; can't continue!")
        return False
    try:
        assert not sign_up_to_isaac(driver, Users.Guerrilla.email.upper(), Users.Guerrilla.firstname, Users.Guerrilla.lastname, Users.Guerrilla.password, suppress=True)
        wait_for_xpath_element(driver, "//h4[contains(text(), 'Registration Failed')]/span[contains(text(), 'An account already exists with the e-mail address')]")
        time.sleep(1)
        driver.get(ISAAC_WEB)
        log(INFO, "Got: %s" % ISAAC_WEB)
        time.sleep(1)
        log(PASS, "Cannot sign up with uppercase form of existing email.")
        return True
    except TimeoutException:
        log(ERROR, "Sign up with uppercase password failed with wrong error message!")
        return False
    except AssertionError:
        log(ERROR, "Sign up successful despite being uppercase form of existing account!")
        return False
signup_uppercase(driver, Users)  # Delete


#####
# Test 18 : User Consistency
#####
@TestWithDependency("USER_CONSISTENCY", Results, ["LOGIN"])
def user_consistency(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(2)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(2)

    submit_login_form(driver, user=Users.Student)
    time.sleep(2)

    try:
        assert_logged_in(driver, Users.Student)
        log(INFO, "Login successful.")
    except AssertionError:
        log(INFO, "Login failed!")
        log(ERROR, "Can't login to continue testing user consistency!")
        return False

    new_tab(driver)
    driver.get(ISAAC_WEB)
    log(INFO, "Got: %s." % ISAAC_WEB)
    time.sleep(2)
    try:
        assert_logged_in(driver, Users.Student)
        time.sleep(1)
        log(PASS, "User still logged in in new tab.")
        return True
    except AssertionError:
        close_tab(driver)
        time.sleep(2)
        log(ERROR, "User not still logged in in new tab; can't test user consistency!")
        return False
user_consistency(driver, Users)  # Delete


#####
# Test 19 : User Consistency Popup
#####
@TestWithDependency("USER_CONSISTENCY_POPUP", Results, ["USER_CONSISTENCY"])
def user_consistency_popup(driver):
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out the user in the new tab.")
    time.sleep(2)
    try:
        assert_logged_out(driver)
        time.sleep(2)
        log(INFO, "Logged out in new tab successfully.")
    except AssertionError:
        image_div(driver, "ERROR_logout_failure")
        close_tab(driver)
        time.sleep(2)
        log(ERROR, "Couldn't logout in new tab; see 'ERROR_logout_failure.png'!")
        return False

    non_isaac_url = "http://www.bbc.co.uk"
    driver.get(non_isaac_url)
    log(INFO, "Navigating away from Isaac (to '%s') to avoid muddling tabs." % non_isaac_url)
    time.sleep(2)

    assert_tab(driver, ISAAC_WEB)
    try:
        consistency_popup = wait_for_xpath_element(driver, "//div[@isaac-modal='userConsistencyError']")
        log(INFO, "User consistency popup shown.")
        image_div(driver, "user_consistency_popup", consistency_popup)
        save_element_html(consistency_popup, "user_consistency_popup")
    except TimeoutException:
        image_div(driver, "ERROR_user_consistency_not_shown")
        close_tab(driver)
        time.sleep(2)
        log(ERROR, "User consistency popup not shown; see 'ERROR_user_consistency_not_shown.png'!")
        return False

    try:
        continue_button = driver.find_element_by_xpath("//div[@id='isaacModal']//div[@isaac-modal='userConsistencyError']//button[text()='Continue']")
        continue_button.click()
        time.sleep(2)
        assert_logged_out(driver)
        time.sleep(2)
        assert_tab(driver, non_isaac_url)
        close_tab(driver)
        log(PASS, "User consistency popup shown and forced logout.")
        return True
    except NoSuchElementException:
        close_tab(driver)
        time.sleep(2)
        log(ERROR, "Cannot click 'Continue' button; see 'user_consistency_popup.png'!")
        return False
    except AssertionError:
        close_tab(driver)
        time.sleep(2)
        log(ERROR, "User inconsistency did not force logout!")
        return False
user_consistency_popup(driver)  # Delete


#####
# Test 20 : Change Email Address
#####
@TestWithDependency("EMAIL_CHANGE", Results, ["LOGIN", "SIGNUP", "RECIEVE_VERIFY_EMAILS"])
def email_change(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(2)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(2)
    log(INFO, "Attempting to change email address for '%s'." % Users.Guerrilla.email)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(2)
    submit_login_form(driver, user=Users.Guerrilla)
    time.sleep(2)

    try:
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        log(INFO, "Opened global nav (menu bar).")
        time.sleep(2)
        my_account_link = driver.find_element_by_xpath("(//a[@ui-sref='accountSettings'])[2]")
        my_account_link.click()
        log(INFO, "Clicked 'My Account' button.")
        time.sleep(2)
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
        time.sleep(2)
        image_div(driver, "change_email_new_email", email_address_box.find_element_by_xpath(".."))
        save_button = driver.find_element_by_xpath("//a[text()='Save']")
        save_button.click()
        time.sleep(2)
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        log(INFO, "Have to accept an alert.")
        assert "You have edited your email address." in alert_text, "Alert contained unexpected message '%s'!" % alert_text
        log(INFO, "Alert said: '%s'." % alert_text)
        time.sleep(2)
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
email_change(driver, Users)  # Delete


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
    time.sleep(2)
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
    time.sleep(2)
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
        time.sleep(2)
        email_body = new_verify_email.get_email_body_element()
        verification_link = email_body.find_element_by_xpath(".//a[text()='Verify your email address']")
        Users.Guerrilla.verify_link = str(verification_link.get_attribute("href"))
        log(INFO, "Copied verification link.")
        new_verify_email.close()
        time.sleep(2)
        log(PASS, "Emails recieved for old and new accounts after changing email address.")
        return True
    except IndexError:
        image_div(driver, "ERROR_verify_new_not_recieved")
        log(ERROR, "Verification email for new email not recieved; see 'ERROR_verify_new_not_recieved.png'!")
        return False
    except NoSuchElementException:
        driver.get(GUERRILLAMAIL)
        log(INFO, "Couldn't access expected parts of email. Refresh page to cleanup.")
        time.sleep(2)
        log(ERROR, "Couldn't access new email verification link in email!")
        return False
email_change_emails(driver, inbox, Users)  # Delete


#####
# Test 22 : Check Login Status After Email Change
#####
@TestWithDependency("EMAIL_CHANGE_LOGIN_STATUS", Results, ["EMAIL_CHANGE_EMAILS"])
def email_change_login_status(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    log(INFO, "Now testing login conditions; old email should work until after verification, then new email only.")
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(2)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(2)
    ###
    submit_login_form(driver, user=Users.Guerrilla)
    log(INFO, "Submitted login form with old credentials.")
    time.sleep(2)
    try:
        assert_logged_in(driver, Users.Guerrilla)
        log(INFO, "Login successful with old email before verification of new email.")
    except AssertionError:
        log(INFO, "Login failed.")
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Login failed with old email before verification of new email; see 'ERROR_not_logging_in.png'!")
        return False
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out again.")
    time.sleep(2)
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
    time.sleep(2)
    try:
        log(INFO, "Submit login form with new credentials.")
        submit_login_form(driver, Users.Guerrilla.new_email, Users.Guerrilla.password)
        wait_for_xpath_element(driver, "//strong[text()='Incorrect credentials provided.']", 5)
        log(INFO, "Login failed with new email before verification of new email.")
    except TimeoutException:
        image_div(driver, "ERROR_logged_in_unexpectedly")
        log(ERROR, "Login succeeded with old email before verification of new email; see 'ERROR_logged_in_unexpectedly.png'!")
        return False
    driver.refresh()
    time.sleep(2)
    ###
    log(INFO, "Now verifying new email address.")
    new_tab(driver)
    time.sleep(2)
    try:
        driver.get(Users.Guerrilla.verify_link)
        log(INFO, "Got: %s" % Users.Guerrilla.verify_link)
        wait_for_xpath_element(driver, "//h2[@ng-if='verificationState==verificationStates.SUCCESS']")
        time.sleep(2)
        log(INFO, "Verification of new email address succeeded.")
        close_tab(driver)
    except TimeoutException:
        image_div(driver, "ERROR_change_email_verify_fail")
        close_tab(driver)
        time.sleep(2)
        log(ERROR, "New email verification failed, can't continue. See 'ERROR_change_email_verify_fail.png'!")
        return False
    except AttributeError:
        close_tab(driver)
        time.sleep(2)
        log(ERROR, "New email verfication link not saved. Can't complete test!")
        return False
    ###
    assert_tab(driver, ISAAC_WEB)
    submit_login_form(driver, user=Users.Guerrilla)
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
    time.sleep(2)
    try:
        submit_login_form(driver, Users.Guerrilla.new_email, Users.Guerrilla.password)
        log(INFO, "Submitted login form with new credentials.")
        time.sleep(2)
        assert_logged_in(driver)
        log(INFO, "Login successful with new email after verification of new email.")
    except AssertionError:
        image_div(driver, "ERROR_not_logging_in")
        log(ERROR, "Login failed with new email after verification of new email; see 'ERROR_not_logging_in.png'!")
        return False
    time.sleep(2)
    Users.Guerrilla.old_email = Users.Guerrilla.email
    Users.Guerrilla.email = Users.Guerrilla.new_email
    log(PASS, "Old login worked until verification of new, then stopped. New didn't work until verification.")
    return True
email_change_login_status(driver, Users)  # Delete


#####
# Test 23 : Access Admin Page As Users
#####
@TestWithDependency("ADMIN_PAGE_ACCESS", Results, ["LOGIN", "LOGOUT"])
def admin_page_access(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(2)

    admin_access_fail = False

    try:
        log(INFO, "Test if logged out user can access '/admin'.")
        driver.get(ISAAC_WEB + "/admin")
        time.sleep(2)
        wait_for_xpath_element(driver, "//h1[text()='Unauthorised']")
        log(INFO, "Logged out users can't access admin page.")
        time.sleep(2)
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logging out to start from same initial page each time.")
        time.sleep(2)
    except TimeoutException:
        admin_access_fail = True
        image_div(driver, "ERROR_unexpected_admin_access")
        log(ERROR, "Logged out user accessed '/admin'; see 'ERROR_unexpected_admin_access.png'!")

    access_cases = [("Student", Users.Student), ("Teacher", Users.Teacher), ("Content Editor", Users.Editor)]
    for i_type, user in access_cases:
        log(INFO, "Test if '%s' users can access admin page." % i_type)
        try:
            driver.get(ISAAC_WEB + "/admin")
            time.sleep(2)
            submit_login_form(driver, user=user)
            time.sleep(2)
            assert_logged_in(driver, user)
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
        time.sleep(2)
        try:
            submit_login_form(driver, user=user)
            time.sleep(2)
            global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
            global_nav.click()
            time.sleep(2)
            site_admin_link = driver.find_element_by_xpath("//a[@ui-sref='admin']")
            site_admin_link.click()
            time.sleep(2)
            wait_for_xpath_element(driver, "//h1[text()='Isaac Administration']")
            time.sleep(2)
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
admin_page_access(driver, Users)  # Delete


#####
# Test N : Delete A User
#####
@TestWithDependency("DELETE_USER", Results, ["LOGIN", "SIGNUP"])
def delete_user(driver, Users):
    assert_tab(driver, ISAAC_WEB)
    time.sleep(2)
    log(INFO, "Attempt to delete temporary user.")
    driver.get(ISAAC_WEB + "/login")
    log(INFO, "Got '%s'" % (ISAAC_WEB + "/login"))
    time.sleep(2)
    try:
        submit_login_form(driver, user=Users.Admin)
        time.sleep(2)
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        time.sleep(2)
        user_manager_link = driver.find_element_by_xpath("//a[@ui-sref='adminUserManager']")
        user_manager_link.click()
    except NoSuchElementException:
        log(ERROR, "Can't access User Manager from Global Nav; can't continue testing!")
        return False
    try:
        time.sleep(2)
        email_field = driver.find_element_by_id("user-search-email")
        email_field.send_keys(Users.Guerrilla.email)
        time.sleep(2)
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
        time.sleep(2)
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
delete_user(driver, Users)  # Delete


driver.quit()
log(INFO, "Testing Finished. Closed Selenium.")
end_testing(Results)
