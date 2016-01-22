import time
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .i_selenium import wait_for_xpath_element, wait_for_invisible_xpath, image_div
from .log import log, INFO, ERROR
import pickle

__all__ = ['User', 'TestUsers', 'kill_irritating_popup', 'disable_irritating_popup',
           'submit_login_form', 'assert_logged_in', 'assert_logged_out', 'sign_up_to_isaac',
           'answer_numeric_q']


class User():
    """A class to encapsulate an Isaac user."""

    def __init__(self, email, firstname, lastname, password):
        """Create using a string email address, firstname, lastname and password."""
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.password = password

    def __repr__(self):
        """Set Python's representation of the object to something useful."""
        return "<User: '%s' - '%s' '%s' - '%s'>" % (self.email, self.firstname, self.lastname, self.password)


class TestUsers():
    """A class to contain Isaac User objects.

       Also contains a 'load()' method to load a pickled form from file. Useful for
       encapsulating all the users in the hierarchy."""

    def __init__(self, Student, Teacher, Editor, Event, Admin):
        """Create using student, teacher, content editor, event manager and admin
           User objects."""
        self.Student = Student
        self.Teacher = Teacher
        self.Editor = Editor
        self.Event = Event
        self.Admin = Admin

    def __repr__(self):
        """Set Python's representation of the object to something useful."""
        return "<User List: 'Student', 'Teacher', 'Editor', 'Event', 'Admin'>"

    @staticmethod
    def load():
        """Return the TestUser object loaded from file."""
        f = open("TestUsers.pickle", 'rU')
        Users = pickle.load(f)
        f.close()
        return Users


def kill_irritating_popup(driver, wait_dur=60):
    """Wait for the annoying popup to popup and then close it.

        If it hasn't appeared after one minute, continue with code.
         - 'driver' should be a Selenium WebDriver.
         - 'wait_dur' is the interger time to wait in seconds.
    """
    try:
        popup = WebDriverWait(driver, wait_dur).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='close-reveal-modal']")))
        popup.click()
        time.sleep(1)
        log(INFO, "Popup Closed!")
        return True
    except TimeoutException:
        return False


def disable_irritating_popup(driver, undo=False):
    """Disable the questionnaire popup for the duration of the session.

       To prevent the popup from getting in the way of tests, set the local storage
       flag requred to disable it.
        - 'driver' should be a Selenium WebDriver.
        - 'undo' is a boolean flag to reset the disabling by pretending the last
          time the popup was seen was in 1970.
    """
    if undo:
        epoch_time = 0  # Pretend last time shown was 1/1/1970 !
    else:
        epoch_time = int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)
        one_month = 2592000000
        epoch_time += one_month  # Pretend last time shown was one month in future!
    driver.execute_script("window.localStorage.setItem('%s','%s');" % ("lastNotificationTime", epoch_time))
    time.sleep(2)


def submit_login_form(driver, username="", password="", user=None, disable_popup=True,
                      wait_dur=2):
    """Given that the browser is on the Isaac login page; fill in and submin the login form.

       This requires being on the login page to function. Will return 'False' if
       it cannot submit the form.
        - 'driver' should be a Selenium WebDriver.
        - 'username' is the username to use. It will be overridden if a 'user' is
          specified at all.
        - 'password' is the password to use. It will be overridden if a 'user' is
          specified at all.
        - 'user' is the User object to use to login. It will override any username
          and password otherwise set.
        - 'disable_popup' is an optional boolean flag to disable the questionnaire
          popup, to prevent it getting in the way of testing.
        - 'wait_dur' ensures JavaScript elements have time to react given different
          browser speeds.
    """
    if user is not None:
        username = user.email
        password = user.password
    try:
        user = driver.find_element_by_xpath("(//input[@name='email'])[2]")
        user.clear()
        user.send_keys(username)
        pwd = driver.find_element_by_xpath("(//input[@name='password'])[2]")
        pwd.clear()
        pwd.send_keys(password)
        login = driver.find_element_by_xpath("(//input[@value='Log in'])[2]")
        login.click()
        log(INFO, "Submitted login form for '%s'." % username)
        time.sleep(wait_dur)
        if disable_popup:
            disable_irritating_popup(driver)
        return True
    except NoSuchElementException:
        log(ERROR, "No login form to fill out!")
        return False


def assert_logged_in(driver, user=None, wait_dur=2):
    """Assert that a user is currently logged in to Isaac.

       Raises an AssertionError if no user is logged in. A specific user to check
       for can also be specified.
        - 'driver' should be a Selenium WebDriver.
        - 'user' is an optional User object to check if logged in. If this specific
          user is not logged in, an AssertionError will be raised.
        - 'wait_dur' ensures JavaScript elements have time to react given different
          browser speeds.
    """
    time.sleep(wait_dur)
    u_email = str(driver.execute_script("return angular.element('head').scope().user.email;"))
    u_firstname = str(driver.execute_script("return angular.element('head').scope().user.givenName;"))
    if user is None:
        if ((u_email is not None) and (u_firstname is not None)):
            log(INFO, "AssertLoggedIn: A user is logged in.")
        else:
            log(INFO, "AssertLoggedIn: No user is logged in!")
            raise AssertionError("AssertLoggedIn: Not logged in!")
    else:
        if ((u_email == user.email) and (u_firstname == user.firstname)):
            log(INFO, "AssertLoggedIn: The user '%s' is logged in." % user.firstname)
        else:
            log(INFO, "AssertLoggedIn: The user '%s' is not logged in!" % user.firstname)
            raise AssertionError("AssertLoggedIn: Not logged in!")


def assert_logged_out(driver, wait_dur=2):
    """Assert that no user is logged in to Isaac.

       Raises an AssertionError if a user is logged in.
        - 'driver' should be a Selenium WebDriver.
        - 'wait_dur' ensures JavaScript elements have time to react given different
          browser speeds.
    """
    time.sleep(wait_dur)
    user_obj = driver.execute_script("return angular.element('head').scope().user;")
    if "_id" not in user_obj:
        log(INFO, "AssertLoggedOut: All users are logged out.")
    else:
        log(INFO, "AssertLoggedOut: A user is still logged in!")
        raise AssertionError("AssertLoggedOut: Not logged out!")


def sign_up_to_isaac(driver, username="", firstname="", lastname="", password="", user=None,
                     suppress=False, wait_dur=2):
    """Sign a user up to Isaac.

       Fill out the first login form and then the subsequent registration form.
       Requires being on the login page when run.
        - 'driver' should be a Selenium WebDriver.
        - 'username' is the username to use. It will be overridden if a 'user' is
          specified.
        - 'firstname' is the first name to use. It will be overridden if a 'user' is
          specified.
        - 'lastname' is the last name to use. It will be overridden if a 'user' is
          specified.
        - 'password' is the password to use. It will be overridden if a 'user' is
          specified.
        - 'user' is the User object to use to sign up. It will override any username
          and password otherwise set.
        - 'suppress' is a boolean flag to silence any error message upon failure.
          It is useful for testing when the expected result is failure.
        - 'wait_dur' ensures JavaScript elements have time to react given different
          browser speeds.
    """
    if user is not None:
        username = user.email
        firstname = user.firstname
        lastname = user.lastname
        password = user.password
    try:
        # First form:
        user = driver.find_element_by_xpath("(//input[@name='email'])[2]")
        user.clear()
        user.send_keys(username)
        pwd = driver.find_element_by_xpath("(//input[@name='password'])[2]")
        pwd.clear()
        pwd.send_keys(password)
        sign_up = driver.find_element_by_xpath("(//a[@ui-sref='register'])[2]")
        sign_up.click()
        time.sleep(wait_dur)
        log(INFO, "Filled out login form to click Register.")
    except NoSuchElementException:
        log(ERROR, "No login/signup form to fill out!")
    try:
        start_url = driver.current_url
        # Second form:
        first_name = driver.find_element_by_xpath("//input[@id='account-firstname']")
        first_name.clear()
        first_name.send_keys(firstname)
        last_name = driver.find_element_by_xpath("//input[@id='account-lastname']")
        last_name.clear()
        last_name.send_keys(lastname)
        # Shouldn't need to fill in pwd1
        pwd2 = driver.find_element_by_xpath("//input[@id='account-password2']")
        pwd2.clear()
        pwd2.send_keys(password)
        # Shouldn't need to fill in email address
        submit_button = driver.find_element_by_xpath("//input[@value='Register Now']")
        submit_button.click()
        time.sleep(wait_dur)
        new_url = driver.current_url
        assert new_url != start_url, "Was on '%s', now still '%s'." % (start_url, new_url)
        log(INFO, "Registration form successfully submitted for '%s'." % username)
        return True
    except NoSuchElementException:
        if not suppress:
            image_div(driver, "ERROR_signup_form.png")
            log(ERROR, "Can't fill out signup form for '%s'; see 'ERROR_signup_form.png'!" % username)
        return False
    except AssertionError, e:
        if not suppress:
            log(INFO, e.message)
            image_div(driver, "ERROR_signup_form.png")
            log(ERROR, "Submitting signup form failed for '%s'; see 'ERROR_signup_form.png'!" % username)
        return False


def answer_numeric_q(num_question, value, correct_unit, get_unit_wrong=False, wait_dur=2):
    """Submit an answer to a numeric question, given a value and units.

       Given a numeric question WebElement, enter an answer; optionally choosing an
       incorrect unit for testing purposes if necessary.
        - 'num_question' should be the WebElement of the question, probably selected
          using '//div[@ng-switch-when='isaacNumericQuestion']' as the XPATH.
        - 'value' should be the numeric answer in string form.
        - 'correct_unit' should be the LaTeX of the correct unit in string form.
        - 'get_unit_wrong' allows choosing a definitely incorrect unit for testing.
        - 'wait_dur' ensures JavaScript elements have time to react given different
          browser speeds.
    """
    try:
        answer_box = num_question.find_element_by_xpath(".//input[@ng-model='selectedChoice.value']")
        answer_box.clear()
        answer_box.send_keys(value)
        log(INFO, "Entered value '%s'." % value)
        time.sleep(wait_dur)
        units_dropdown = num_question.find_element_by_xpath(".//button[@ng-click='toggleUnitsDropdown()']")
        units_dropdown.click()
        log(INFO, "Clicked to open units dropdown.")
        time.sleep(wait_dur)
        if not get_unit_wrong:
            correct_u = num_question.find_element_by_xpath(".//a[@ng-click='selectUnit(u)']//script[contains(text(), '%s')]/.." % correct_unit)
            correct_u.click()
            correct_u_text = str(correct_u.find_element_by_xpath("./script").get_attribute('innerHTML'))
            log(INFO, "Selected correct unit '%s' (to match '%s')." % (correct_u_text, correct_unit))
        else:
            choices = num_question.find_elements_by_xpath(".//a[@ng-click='selectUnit(u)']")
            n = 0
            u_text = str(choices[n].find_element_by_xpath("./script").get_attribute('innerHTML'))
            while correct_unit in u_text:
                n += 1
                u_text = str(choices[n].find_element_by_xpath("./script").get_attribute('innerHTML'))
            choices[n].click()
            log(INFO, "Selected incorrect unit '%s'." % str(u_text.encode('ascii', 'replace')))
        time.sleep(wait_dur)
        left = int(num_question.find_element_by_xpath(".//ul[@class='f-dropdown']").value_of_css_property('left').replace('px', ''))
        assert left < 9000
        log(INFO, "Selected answer, both value and unit.")
        time.sleep(wait_dur)
    except NoSuchElementException:
        log(ERROR, "Can't find part of the answer fields; can't continue!")
        return False
    except AssertionError:
        log(ERROR, "Units dropdown didn't disappear on clicking a unit; can't continue!")
        return False
    except ValueError:
        log(ERROR, "Couldn't read the CSS property 'left' for the dropdown. This probably constitues failure!")
        return False
    try:
        check_answer_button = num_question.find_element_by_xpath(".//button[@ng-click='checkAnswer()']")
        check_answer_button.click()
        log(INFO, "Clicked 'Check my answer'.")
        time.sleep(wait_dur)
        return True
    except NoSuchElementException:
        log(ERROR, "Couldn't click the 'Check my answer' button; can't continue!")
        return False
