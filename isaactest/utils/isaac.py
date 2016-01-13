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
           'submit_login_form', 'assert_logged_in', 'assert_logged_out', 'sign_up_to_isaac']


class User():
    def __init__(self, email, firstname, lastname, password):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.password = password

    def __repr__(self):
        return "<User: '%s' - '%s' '%s' - '%s'>" % (self.email, self.firstname, self.lastname, self.password)


class TestUsers():
    def __init__(self, Student, Teacher, Editor, Event, Admin):
        self.Student = Student
        self.Teacher = Teacher
        self.Editor = Editor
        self.Event = Event
        self.Admin = Admin

    def __repr__(self):
        return "<User List: 'Student', 'Teacher', 'Editor', 'Event', 'Admin'>"

    @staticmethod
    def load():
        f = open("TestUsers.pickle")
        Users = pickle.load(f)
        f.close()
        return Users


def kill_irritating_popup(driver, wait_dur=60):
    """Wait for the annoying popup to popup and then close it.

        If it hasn't appeared after one minute, continue with code."""
    try:
        popup = WebDriverWait(driver, wait_dur).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='close-reveal-modal']")))
        popup.click()
        log(INFO, "Popup Closed!")
        return True
    except TimeoutException:
        return False


def disable_irritating_popup(driver, undo=False):
    if undo:
        epoch_time = 0  # Pretend last time shown was 1/1/1970 !
    else:
        epoch_time = int((datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)
        one_month = 2592000000
        epoch_time += one_month  # Pretend last time shown was one month in future!
    driver.execute_script("window.localStorage.setItem('%s','%s');" % ("lastNotificationTime", epoch_time))


def submit_login_form(driver, username="", password="", user=None, disable_popup=True):
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
        time.sleep(1)
        if disable_popup:
            disable_irritating_popup(driver)
        return True
    except NoSuchElementException:
        log(ERROR, "No login form to fill out!")
        return False


def assert_logged_in(driver, user=None):
    time.sleep(0.5)
    if user is None:
        try:
            """angular.element("head").scope().user.familyName"""
            wait_for_invisible_xpath(driver, "//span[text()=' to Isaac']", 0.5)
        except TimeoutException:
            raise AssertionError("AssertLoggedIn: Not logged in!")
    else:
        try:
            wait_for_xpath_element(driver, "//span[contains(text(), '%s')]" % user.firstname, 0.5, False)
        except TimeoutException:
            raise AssertionError("AssertLoggedIn: Not logged in!")


def assert_logged_out(driver):
    time.sleep(0.5)
    try:
        wait_for_xpath_element(driver, "//span[text()=' to Isaac']", 0.5)
    except TimeoutException:
        raise AssertionError("AssertLoggedOut: Not logged out!")


def sign_up_to_isaac(driver, username="", firstname="", lastname="", password="", user=None, suppress=False):
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
        time.sleep(1)
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
        last_name = driver.find_element_by_xpath("//input[@id='account-lastname']")
        last_name.clear()
        last_name.send_keys(lastname)
        # Shouldn't need to fill in email address
        submit_button = driver.find_element_by_xpath("//input[@value='Register Now']")
        submit_button.click()
        time.sleep(1)
        new_url = driver.current_url
        assert new_url != start_url
        log(INFO, "Registration form successfully submitted for '%s'." % username)
        return True
    except NoSuchElementException:
        if not suppress:
            image_div(driver, "ERROR_signup_form.png")
            log(ERROR, "Can't fill out signup form for '%s'; see 'ERROR_signup_form.png'!" % username)
        return False
    except AssertionError:
        if not suppress:
            image_div(driver, "ERROR_signup_form.png")
            log(ERROR, "Submitting signup form failed for '%s'; see 'ERROR_signup_form.png'!" % username)
        return False
