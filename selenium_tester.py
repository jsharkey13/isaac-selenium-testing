# Selenium Test
import os
import time
import datetime
#####
from isaactest.emails.guerrillamail import set_guerrilla_mail_address, GuerrillaInbox
from isaactest.utils.log import log, INFO, ERROR, PASS, stop, start_testing, end_testing
from isaactest.utils.isaac import submit_login_form, assert_logged_in, assert_logged_out, sign_up_to_isaac
from isaactest.utils.isaac import kill_irritating_popup, disable_irritating_popup
from isaactest.utils.isaac import TestUsers, User
from isaactest.utils.i_selenium import assert_tab, new_tab, close_tab, image_div, save_element_html
from isaactest.utils.i_selenium import wait_for_xpath_element, wait_for_invisible_xpath
#####
import selenium.webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotVisibleException
####
# Set the working dir:
os.chdir("/path/to/dir")


# Some important global constants:
ISAAC_WEB = "https://staging.isaacphysics.org"
GUERRILLAMAIL = "https://www.guerrillamail.com"


# Global variables:
Users = TestUsers.load()
Guerrilla = User("isaactest@sharklasers.com", "Temp",
                 "Test", "test")
NewEmail = "isaactesttwo@sharklasers.com"
NewPassword = "testing123"


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


# Selenium Start-up:
driver = selenium.webdriver.Firefox()
# driver.set_window_size(1920, 1080)
driver.maximize_window()
log(INFO, "Opened Selenium.")
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
Guerrilla.email = set_guerrilla_mail_address(driver, Guerrilla.email)
time.sleep(1)
inbox = GuerrillaInbox(driver)
time.sleep(1)
# Delete GuerrillaMail welcome:
inbox.delete_email(inbox.emails[0])
time.sleep(1)

#####
# Test 1 : Logging In
#####
assert_tab(driver, ISAAC_WEB)
login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
login_tab.click()
submit_login_form(driver, user=Users.Student, disable_popup=False)
time.sleep(1)
try:
    assert_logged_in(driver, Users.Student)
    log(INFO, "Login successful.")
    log(PASS, "Login using username and password successful.")
except AssertionError:
    log(ERROR, "Login failed!")
    image_div(driver, "ERROR_not_logging_in.png")
    stop(driver, "Can't login to continue testing; see 'ERROR_not_logging_in.png'!")

#####
# Test 2 : Questionnaire Popup
#####
assert_tab(driver, ISAAC_WEB)
disable_irritating_popup(driver, undo=True)  # Make sure we've not disabled it at all!
if kill_irritating_popup(driver, 15):
    popup_killed = True
    log(PASS, "Questionnaire popup shown and closed.")

#####
# Test 3 : Logout Button
#####
assert_tab(driver, ISAAC_WEB)
logout_button = driver.find_element_by_xpath("//a[@ui-sref='logout']")
logout_button.click()
time.sleep(1)
try:
    assert_logged_out(driver)
    log(INFO, "Logged out.")
    log(PASS, "Log out button works.")
except AssertionError:
    image_div(driver, "ERROR_logout_failure.png")
    stop(driver, "Couldn't logout; see 'ERROR_logout_failure.png'!")

#####
# Test 4 : 11 Login Attempts
#####
assert_tab(driver, ISAAC_WEB)
login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
login_tab.click()
for i in range(11):
    submit_login_form(driver, username=Users.Student.email, password="wrongpassword")
    time.sleep(1)
try:
    driver.find_element_by_xpath("//strong[contains(text(), 'too many attempts to login')]")
    log(PASS, "11 login attempts. Warning message and locked out for 10 mins.")
except NoSuchElementException:
    image_div(driver, "11_login_attempts.png")
    stop(driver, "Tried to log in 11 times. No error message; see '11_login_attempts.png'!")

#####
# Test 5 : 10 Minute Lockout
#####
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
except AssertionError:
    log(ERROR, "Login failed!")
    image_div(driver, "login_error.png")
    stop(driver, "Can't login after 10 minute lockout; see 'login_error.png'!")

#####
# Test 6 : Sign Up to Isaac
#####
assert_tab(driver, ISAAC_WEB)
driver.get(ISAAC_WEB + "/logout")
log(INFO, "Logging out any logged in user.")
time.sleep(2)

assert_tab(driver, ISAAC_WEB)
time.sleep(2)
login_tab = driver.find_element_by_id("login-tab")
login_tab.click()
time.sleep(2)
if sign_up_to_isaac(driver, user=Guerrilla):
    log(PASS, "Successfully register new user '%s' on Isaac." % Guerrilla.email)
else:
    stop(driver, "Can't register user, so can't continue testing.")

#####
# Test 7 : Welcome Email Recieved
#####
assert_tab(driver, "guerrillamail")
log(INFO, "Waiting 10 seconds for page to update.")
time.sleep(11)
inbox.refresh()

log(INFO, "GuerrillaMail: Access first email in inbox.")
try:
    welcome_email = inbox.get_by_subject("Welcome to Isaac Physics!")[0]
    welcome_email.image()
    welcome_email.save_html_body()
except IndexError:
    image_div(driver, "ERROR_not_isaac_email.png")
    stop(driver, "Welcome email not recieved; see 'ERROR_not_isaac_email.png'!")

######
# Test 8 : Request Verification Emails
######
assert_tab(driver, ISAAC_WEB)
time.sleep(1)
request_verify_email = driver.find_element_by_xpath("//a[@ng-click='requestEmailVerification()']")

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
        image_div(driver, "email_verification_request_popup_%s.png" % i)
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
                break
            else:
                stop(driver, "Warning not shown after %s requests!" % verification_requests)
except TimeoutException:
    if email_verification_popup_shown_yet:
        stop(driver, "Verification Popup didn't close; see 'email_verification_request_popup.png'!")
    else:
        stop(driver, "Verification Popup didn't appear!")
except AssertionError:
    stop(driver, "Success text not shown on request %s!" % (verification_requests + 1))

#####
# Test 9 : Recieve Verification Emails
#####
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
except AssertionError:
    image_div(driver, "ERROR_recieve_verification.png")
    log(ERROR, "Expected %s verification emails, recieved %s. See 'ERROR_recieve_verification.png'!" % (verification_email_request_limit, verification_emails_recived))

#####
# Test 10 : Verification Link Works
#####
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
    log(PASS, "Email address verified successfully.")
    close_tab(driver)
    time.sleep(2)
except TimeoutException:
    image_div(driver, "ERROR_verification_status.png")
    stop(driver, "Verification Failed; see 'ERROR_verification_status.png'!")
except IndexError:
    stop(driver, "No verification emails recieved! Can't continue.")

#####
# Test 11 : Verification Banner Gone
#####
assert_tab(driver, ISAAC_WEB)
try:
    driver.refresh()
    time.sleep(2)
    log(INFO, "Checking if verification banner now gone.")
    wait_for_invisible_xpath(driver, "//a[@ng-click='requestEmailVerification()']")
    log(PASS, "Verification banner gone after verifying email.")
except TimeoutException:
    log(ERROR, "Verification banner still present after email verified; see 'ERROR_verification_banner.png'!")
time.sleep(5)

#####
# Test 12 : Forgot My Password Button Limit
#####
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
    user.send_keys(Guerrilla.email)
    for i in range(10):
        forgot_password_button = driver.find_element_by_xpath("(//a[@ng-click='resetPassword()'])[2]")
        log(INFO, "Clicking password reset button.")
        forgot_password_button.click()
        image_div(driver, "reset_password_button_message_%s.png" % i)
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
except AssertionError:
    stop(driver, "Incorrect password reset message shown; see 'reset_password_button_message.png'!")
except NoSuchElementException:
    stop(driver, "No password reset messagew shown; see 'reset_password_button_message.png'!")
except TimeoutException, e:
    stop(driver, e.msg)

#####
# Test 13 : 4 password reset emails recieved
#####
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
except AssertionError:
    image_div(driver, "ERROR_recieve_reset_pwd.png")
    stop(driver, "Expected %s password reset emails, recieved %s. See 'ERROR_recieve_reset_pwd.png'!" % (forgot_pwd_request_limit, forgot_password_emails_recieved))

#####
# Test 14 : Reset Password Link Works
#####
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

    pwd1 = driver.find_element_by_xpath("//input[@id='password']")
    pwd1.clear()
    pwd1.send_keys(NewPassword)
    pwd2 = driver.find_element_by_xpath("//input[@id='confirm-password']")
    pwd2.clear()
    pwd2.send_keys(NewPassword)
    change_password = driver.find_element_by_xpath("//button[@ng-click='resetPassword()']")
    change_password.click()
    time.sleep(1)
    driver.find_element_by_xpath("//div[@ng-switch='submitted']/div[contains(text(), 'reset successfully')]")
    Guerrilla.password = NewPassword
    log(PASS, "Reset password link works.")
    close_tab(driver)
    time.sleep(1)
except NoSuchElementException:
    image_div(driver, "ERROR_resetting_password.png")
    stop(driver, "Resetting password failed; see 'ERROR_resetting_password.png'!")

#####
# Test 15 : Logging In With New Password
#####
assert_tab(driver, ISAAC_WEB)
driver.get(ISAAC_WEB)
log(INFO, "Got: %s" % ISAAC_WEB)
time.sleep(1)

login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
login_tab.click()
submit_login_form(driver, user=Guerrilla)
time.sleep(2)

try:
    assert_logged_in(driver, Guerrilla)
    log(INFO, "Login successful.")
    log(PASS, "Login using username and password successful.")
except AssertionError:
    log(ERROR, "Login failed!")
    image_div(driver, "ERROR_not_logging_in.png")
    stop(driver, "Can't login to continue testing; see 'ERROR_not_logging_in.png'!")

#####
# Test 16 : Login Email Case Sensitivity
#####
assert_tab(driver, ISAAC_WEB)
driver.get(ISAAC_WEB + "/logout")
log(INFO, "Logging out any logged in user.")
time.sleep(2)

login_tab = driver.find_element_by_xpath("//a[@id='login-tab']")
login_tab.click()
submit_login_form(driver, Guerrilla.email.upper(), Guerrilla.password)
time.sleep(2)

try:
    assert_logged_in(driver, Guerrilla)
    log(INFO, "Login successful.")
    log(PASS, "Login using uppercase version of email successful.")
except AssertionError:
    log(ERROR, "Login failed!")
    image_div(driver, "ERROR_not_logging_in.png")
    stop(driver, "Can't login to continue testing; see 'ERROR_logging_in_uppercase.png'!")

#####
# Test 17 : Signup Email Case Sensitivity
#####
assert_tab(driver, ISAAC_WEB)
driver.get(ISAAC_WEB + "/logout")
log(INFO, "Logging out any logged in user.")
time.sleep(2)

login_tab = driver.find_element_by_id("login-tab")
login_tab.click()
time.sleep(2)
try:
    assert not sign_up_to_isaac(driver, Guerrilla.email.upper(), Guerrilla.firstname, Guerrilla.lastname, Guerrilla.password, suppress=True)
    error_message = driver.find_element_by_xpath("//h4[contains(text(), 'Registration Failed')]/span[contains(text(), 'An account already exists with the e-mail address')]")
    log(PASS, "Canot sign up with uppercase form of existing email.")
except NoSuchElementException:
    log(ERROR, "Sign up with uppercase password failed with wrong error message. See above image.")
except AssertionError:
    log(ERROR, "Sign up successful despite uppercase form of existing account!")

#####
# Test 18 : User Consistency
#####
assert_tab(driver, ISAAC_WEB)
driver.get(ISAAC_WEB + "/logout")
log(INFO, "Logging out any logged in user.")
time.sleep(1)
driver.get(ISAAC_WEB + "/login")
log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
time.sleep(1)

submit_login_form(driver, user=Guerrilla)
time.sleep(2)

try:
    assert_logged_in(driver, Guerrilla)
    log(INFO, "Login successful.")
    log(PASS, "Login using username and password successful.")
except AssertionError:
    log(ERROR, "Login failed!")
    stop(driver, "Can't login to continue testing user consistency!")

new_tab(driver)
driver.get(ISAAC_WEB)
log(INFO, "Got: %s." % ISAAC_WEB)
time.sleep(2)
try:
    assert_logged_in(driver, Guerrilla)
    log(PASS, "User still logged in in new tab.")
except AssertionError:
    log(ERROR, "User not still logged in in new tab!")
    stop(driver, "Not still logged in, can't continue testing user consistency!")
time.sleep(1)

#####
# Test 19 : User Consistency Popup
#####
driver.get(ISAAC_WEB + "/logout")
log(INFO, "Logging out the user in the new tab.")
time.sleep(2)
try:
    assert_logged_out(driver)
    log(INFO, "Logged out in new tab successfully.")
except AssertionError:
    image_div(driver, "ERROR_logout_failure.png")
    stop(driver, "Couldn't logout; see 'ERROR_logout_failure.png'!")

non_isaac_url = "http://www.bbc.co.uk"
driver.get(non_isaac_url)
log(INFO, "Navigating away from Isaac (to '%s') to avoid muddling tabs." % non_isaac_url)

assert_tab(driver, ISAAC_WEB)
try:
    consistency_popup = wait_for_xpath_element(driver, "//div[@isaac-modal='userConsistencyError']")
    log(INFO, "User consistency popup shown.")
    image_div(driver, "user_consistency_popup.png", consistency_popup)
    save_element_html(consistency_popup, "user_consistency_popup.html")
except TimeoutException:
    image_div(driver, "ERROR_user_consistency_not_shown.png")
    log(ERROR, "User consistency popup not shown!")
    stop(driver, "Popup not shown; see 'ERROR_user_consistency_not_shown.png'!")

try:
    continue_button = driver.find_element_by_xpath("//div[@id='isaacModal']//div[@isaac-modal='userConsistencyError']//button[text()='Continue']")
    continue_button.click()
    time.sleep(2)
    assert_logged_out(driver)
    log(PASS, "User consistency popup shown and forced logout.")
except NoSuchElementException:
    stop(driver, "Cannot click 'Continue' button; see 'user_consistency_popup.png'!")
except AssertionError:
    stop(driver, "User inconsistency did not force logout!")
assert_tab(driver, non_isaac_url)
close_tab(driver)

#####
# Test 20 : Change Email Address
#####
assert_tab(driver, ISAAC_WEB)
time.sleep(1)
log(INFO, "Attempting to change email address for '%s'." % Guerrilla.email)
driver.get(ISAAC_WEB + "/login")
log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
submit_login_form(driver, user=Guerrilla)
time.sleep(2)

try:
    global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
    global_nav.click()
    log(INFO, "Opened global nav (menu bar).")
    time.sleep(1)
    my_account_link = driver.find_element_by_xpath("(//a[@ui-sref='accountSettings'])[2]")
    my_account_link.click()
    log(INFO, "Clicked 'My Account' button.")
    time.sleep(2)
except (NoSuchElementException, ElementNotVisibleException):
    image_div(driver, "ERROR_account_global_nav.png")
    stop(driver, "Couldn't access 'My Account' link from global nav; see ERROR_account_global_nav.png'")
try:
    start_url = driver.current_url
    assert "/account" in start_url, "'/account' not in URL: '%s'!" % start_url
    email_address_box = driver.find_element_by_xpath("//input[@id='account-email']")
    image_div(driver, "change_email_old_email.png", email_address_box.find_element_by_xpath(".."))
    email_address_box.clear()
    email_address_box.send_keys(NewEmail)
    time.sleep(1)
    image_div(driver, "change_email_new_email.png", email_address_box.find_element_by_xpath(".."))
    save_button = driver.find_element_by_xpath("//a[text()='Save']")
    save_button.click()
    time.sleep(1)
    alert = driver.switch_to.alert
    alert_text = alert.text
    alert.accept()
    log(INFO, "Have to accept an alert.")
    assert "You have edited your email address." in alert_text, "Alert contained unexpected message '%s'!" % alert_text
    log(INFO, "Alert said: '%s'." % alert_text)
    time.sleep(1)
    end_url = driver.current_url
    assert end_url != start_url, "Expected to leave account page, but still on '%s'!" % end_url
    end_loc = end_url.split("#")[0]
    assert end_loc == ISAAC_WEB + "/", "Should have redirected to homepage, went to '%s' instead!" % end_url
    log(PASS, "Email changed in account setting successfully.")
except AssertionError, e:
    image_div(driver, "ERROR_change_email_page.png")
    stop(driver, e.message)
except NoSuchElementException:
    image_div(driver, "ERROR_change_email_page.png")
    stop(driver, "Couldn't change password on 'My Account' page; see 'ERROR_change_email_page.png'!")

#####
# Test 21 : Check Change Email Emails Recieved
#####
assert_tab(driver, GUERRILLAMAIL)
log(INFO, "Checking if emails were sent after changing account email.")
log(INFO, "Wating 10 seconds for emails to arrive.")
time.sleep(11)

new_email_verify_link = None
inbox.refresh()
time.sleep(1)
try:
    old_warning_email = inbox.get_by_subject("Change in Isaac Physics email address requested!")[0]
    log(INFO, "Old warning email recieved and has expected subject line.")
    old_warning_email.image("change_email_old_email.png")
    old_warning_email.save_html_body("change_email_old_email.html")
    old_warning_email.view()
    email_body = old_warning_email.get_email_body_element()
    email_body.find_element_by_xpath("//a[text()='%s']" % NewEmail)
    old_warning_email.close()
    log(INFO, "Warning email successfully sent to old address.")
except IndexError:
    image_div(driver, "ERROR_no_old_email_warning.png")
    stop(driver, "No warning email recieved in old email inbox; see 'ERROR_no_old_email_warning.png'!")
except NoSuchElementException:
    stop(driver, "Link to new address not in old warning email, see image!")
time.sleep(2)
set_guerrilla_mail_address(driver, NewEmail)
time.sleep(11)
inbox.refresh()

try:
    new_verify_email = inbox.get_by_subject("Verify your email")[0]
    log(INFO, "New verify email recieved and has expected subject line.")
    new_verify_email.image("change_email_new_email.png")
    new_verify_email.save_html_body("change_email_new_email.html")
    expected_subject = "Verify your email"
    new_verify_email.view()
    time.sleep(1)
    email_body = new_verify_email.get_email_body_element()
    verification_link = email_body.find_element_by_xpath(".//a[text()='Verify your email address']")
    new_email_verify_link = str(verification_link.get_attribute("href"))
    log(INFO, "Copied verification link.")
    new_verify_email.close()
    log(PASS, "Emails recieved for old and new accounts after changing email address.")
    time.sleep(1)
except IndexError:
    image_div(driver, "ERROR_verify_new_not_recieved.png")
    stop(driver, "Verification email for new email not recieved; see 'ERROR_verify_new_not_recieved.png'!")

#####
# Test 22 : Check Login Status After Email Change
#####
assert_tab(driver, ISAAC_WEB)
log(INFO, "Now testing login conditions; old email should work until after verification, then new email only.")
driver.get(ISAAC_WEB + "/logout")
log(INFO, "Logging out any logged in user.")
time.sleep(1)
driver.get(ISAAC_WEB + "/login")
log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
time.sleep(1)


submit_login_form(driver, user=Guerrilla)
log(INFO, "Submitted login form with old credentials.")
time.sleep(2)
try:
    assert_logged_in(driver, Guerrilla)
    log(INFO, "Login successful with old email before verification of new email.")
except AssertionError:
    log(ERROR, "Login failed with old email before verification of new email!")
    image_div(driver, "ERROR_not_logging_in.png")
    stop(driver, "Can't login to continue testing; see 'ERROR_not_logging_in.png'!")
driver.get(ISAAC_WEB + "/logout")
log(INFO, "Logging out again.")
time.sleep(1)
driver.get(ISAAC_WEB + "/login")
log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
time.sleep(1)
try:
    submit_login_form(driver, NewEmail, Guerrilla.password)
    log(INFO, "Submitted login form with new credentials.")
    failure_message = wait_for_xpath_element(driver, "//strong[text()='Incorrect credentials provided.']", 5)
    log(INFO, "Login failed with new email before verification of new email.")
except TimeoutException:
    log(ERROR, "Login succeeded with old email before verification of new email!")
    image_div(driver, "ERROR_logged_in_unexpectedly.png")
    stop(driver, "Can't login to continue testing; see 'ERROR_logged_in_unexpectedly.png'!")
driver.refresh()
time.sleep(2)


log(INFO, "Now verifying new email address.")
new_tab(driver)
time.sleep(1)
try:
    driver.get(new_email_verify_link)
    log(INFO, "Got: %s" % new_email_verify_link)
    wait_for_xpath_element(driver, "//h2[@ng-if='verificationState==verificationStates.SUCCESS']")
    time.sleep(1)
    log(INFO, "Verification of new email address succeeded.")
    close_tab(driver)
except TimeoutException:
    image_div(driver, "ERROR_change_email_verify_fail.png")
    stop(driver, "New email verification failed, can't continue. See 'ERROR_change_email_verify_fail.png'!")

assert_tab(driver, ISAAC_WEB)
submit_login_form(driver, user=Guerrilla)
log(INFO, "Submitted login form with old credentials.")
try:
    failure_message = wait_for_xpath_element(driver, "//strong[text()='Incorrect credentials provided.']", 5)
    log(INFO, "Login failed with old email after verification of new email.")
except TimeoutException:
    log(ERROR, "Login suceeded with old email after verification of new email!")
    image_div(driver, "ERROR_logged_in_unexpectedly.png")
    stop(driver, "Can't login to continue testing; see 'ERROR_logged_in_unexpectedly.png'!")
driver.get(ISAAC_WEB + "/login")
log(INFO, "Got: %s" % (ISAAC_WEB + "/login"))
time.sleep(1)
try:
    submit_login_form(driver, NewEmail, Guerrilla.password)
    log(INFO, "Submitted login form with new credentials.")
    time.sleep(2)
    assert_logged_in(driver)
    log(INFO, "Login successful with new email after verification of new email.")
except AssertionError:
    log(ERROR, "Login failed with new email after verification of new email!")
    image_div(driver, "ERROR_not_logging_in.png")
    stop(driver, "Can't login to continue testing; see 'ERROR_not_logging_in.png'!")

Guerrilla.old_email = Guerrilla.email
Guerrilla.email = NewEmail
log(PASS, "Old login worked until verification of new, then stopped. New didn't work until verification.")
time.sleep(2)

#####
# Test 23 : Access Admin Page As Users
#####
assert_tab(driver, ISAAC_WEB)
driver.get(ISAAC_WEB + "/logout")
log(INFO, "Logging out any logged in user.")
time.sleep(1)

access_cases = [("Student", Users.Student), ("Teacher", Users.Teacher), ("Content Editor", Users.Editor)]
admin_access_fail = False
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
        image_div(driver, "ERROR_unexpected_admin_access.png")
        log(ERROR, "User of type '%s' accessed '/admin'; see 'ERROR_unexpected_admin_access.png'!")
    except AssertionError:
        log(ERROR, "Couldn't log user in to test '/admin' access!")
        stop(driver, "Login error accessing admin page!")
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logged out '%s' user." % i_type)
    time.sleep(3)

driver.get(ISAAC_WEB + "/login")
log(INFO, "Got '%s'. As admin, try to use global nav." % (ISAAC_WEB + "/login"))
time.sleep(2)
try:
    submit_login_form(driver, user=Users.Admin)
    time.sleep(2)
    global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
    global_nav.click()
    time.sleep(1)
    site_admin_link = driver.find_element_by_xpath("//a[@ui-sref='admin']")
    site_admin_link.click()
    time.sleep(1)
    wait_for_xpath_element(driver, "//h1[text()='Isaac Administration']")
    time.sleep(1)
    log(INFO, "Admin users can access '/admin'.")
except TimeoutException:
    admin_access_fail = True
    image_div(driver, "ERROR_no_admin_access.png")
    log(ERROR, "Admin user can't access '/admin'; see 'ERROR_no_admin_access.png'!")
if not admin_access_fail:
    log(PASS, "Access to admin page restricted appropriately.")


driver.quit()
log(INFO, "Testing Finished. Closed Selenium.")
end_testing()
