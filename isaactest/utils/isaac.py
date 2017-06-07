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


class MobileIsaac(object):
    """A context manager to help test Isaac in mobile mode.

       To use Isaac in mobile mode, it suffices to put the code inside a with block:

           with MobileIsaac(driver) as mobile_driver:
               ...

       and then use `mobile_driver` instead of the standard driver object (though
       this isn't technically neccesary)."""

    def __init__(self, driver):
        """Create using a WebDriver object.

           Keep an internal reference to the WebDriver object, which is requred
           to resize the screen down and restore the window to the old saved
           dimensions once the context block is exited."""
        self.driver = driver
        self.window_size = driver.get_window_size()

    def __enter__(self):
        """This class is just a transparent proxy to the ordinary driver object.

           By returning the driver in the __enter__() method, simply pass all
           behavior on to it. To initialise, resize the window to be the size of
           a small mobile screen."""
        self.driver.set_window_size(360, 640)
        self.driver.refresh()
        log(INFO, "Resized window to mobile size.")
        return self.driver

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """On exit, just restore the screen to the size it was and maximise if possible."""
        self.driver.set_window_size(self.window_size["width"], self.window_size["height"])
        self.driver.maximize_window()
        self.driver.refresh()
        log(INFO, "Restored window dimensions.")


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
    driver.execute_script("window.localStorage.setItem('%s', %s);" % ("lastNotificationTime", epoch_time))
    time.sleep(2)


def snooze_email_verification(driver):
    """Snooze the email verification warning.

       To prevent the banner from getting in the way of tests, snooze the email
       verification warning. On mobile devices the banner obstructs the menu fully
       and prevents tests from passing.
        - 'driver' should be a Selenium WebDriver.
    """
    try:
        banner_xpath = "//div[@data-alert]/div[contains(@ng-if, 'emailVerificationStatus')]/div[3]/a"
        snooze_link = wait_for_xpath_element(driver, banner_xpath, duration=5)
        log(INFO, "Snoozing email verification warning. (It obstructs menu on mobile).")
        snooze_link.click()
        try:
            wait_for_invisible_xpath(driver, "//div[@data-alert]/div[contains(@ng-if, 'emailVerificationStatus')]/div[3]/a")
            return True
        except TimeoutException:
            log(ERROR, "Email verification snooze button doesn't work!")
            return False
    except TimeoutException:
        # If it's not there in the first place, we don't need to snooze it!
        return True


def submit_login_form(driver, username="", password="", user=None, disable_popup=True,
                      wait_dur=2, mobile=False):
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
    # There are two login form boxes on each page, irritatingly. Pick correct one:
    i = 1 if mobile else 2
    try:
        user = driver.find_element_by_xpath("(//input[@name='email'])[%s]" % i)
        user.clear()
        user.send_keys(username)
        pwd = driver.find_element_by_xpath("(//input[@name='password'])[%s]" % i)
        pwd.clear()
        pwd.send_keys(password)
        login = driver.find_element_by_xpath("(//input[@value='Log in'])[%s]" % i)
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
            log(INFO, "AssertLoggedIn: A user '%s' (%s) may be logged in." % (u_firstname, u_email))
            raise AssertionError("AssertLoggedIn: Not logged in!")


def assert_logged_out(driver, wait_dur=2):
    """Assert that no user is logged in to Isaac.

       Raises an AssertionError if a user is logged in.
        - 'driver' should be a Selenium WebDriver.
        - 'wait_dur' ensures JavaScript elements have time to react given different
          browser speeds.
    """
    time.sleep(wait_dur)
    user_id = driver.execute_script("return angular.element('head').scope().user._id;")
    if user_id is None:
        log(INFO, "AssertLoggedOut: All users are logged out.")
    else:
        log(ERROR, "AssertLoggedOut: A user (%s) is still logged in!" % user_id)
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
            image_div(driver, "ERROR_signup_form")
            log(ERROR, "Can't fill out signup form for '%s'; see 'ERROR_signup_form.png'!" % username)
        return False
    except AssertionError, e:
        if not suppress:
            log(INFO, e.message)
            image_div(driver, "ERROR_signup_form.png")
            log(ERROR, "Submitting signup form failed for '%s'; see 'ERROR_signup_form.png'!" % username)
        return False


def open_accordion_section(driver, n):
    """Open the n-th accordion section on a page.

       Will raise NoSuchElementException if there are no accordion sections on
       the page, or if n larger than the number of accordion sections.
        - 'driver' should be a Selenium WebDriver.
        - 'n' is the integer number of the accordion section to open counting from 1.
    """
    accordion_title = driver.find_element_by_xpath("(//a[contains(@class, 'ru_accordion_titlebar')])[%s]" % n)
    accordion_content = accordion_title.find_element_by_xpath("./../div")
    if accordion_content.is_displayed():
        log(INFO, "Accordion section %s already open." % n)
    else:
        accordion_title.click()
        log(INFO, "Opened accordion section %s." % n)
        time.sleep(0.5)


def close_accordion_section(driver, n):
    """Close the n-th accordion section on a page.

       Will raise NoSuchElementException if there are no accordion sections on
       the page, or if n larger than the number of accordion sections.
        - 'driver' should be a Selenium WebDriver.
        - 'n' is the integer number of the accordion section to close counting from 1.
    """
    accordion_title = driver.find_element_by_xpath("(//a[contains(@class, 'ru_accordion_titlebar')])[%s]" % n)
    accordion_content = accordion_title.find_element_by_xpath("./../div")
    if accordion_content.is_displayed():
        accordion_title.click()
        log(INFO, "Closed accordion section %s." % n)
        time.sleep(0.5)
    else:
        log(INFO, "Accordion section %s already closed." % n)


def wait_accordion_open(driver, n, duration=5):
    """Wait for the n-th accordion section on a page to be open.

        - 'driver' should be a Selenium WebDriver.
        - 'n' is the integer number of the accordion section counting from 1.
        - 'duration' is how long to wait before raising TimeoutException.
    """
    return wait_for_xpath_element(driver, "(//dd/a[@class='ru_accordion_titlebar']/../div)[%s]" % n, duration)


def wait_accordion_closed(driver, n, duration=5):
    """Wait for the n-th accordion section on a page to be closed.

        - 'driver' should be a Selenium WebDriver.
        - 'n' is the integer number of the accordion section counting from 1.
        - 'duration' is how long to wait before raising TimeoutException.
    """
    return wait_for_invisible_xpath(driver, "(//dd/a[@class='ru_accordion_titlebar']/../div)[%s]" % n, duration)


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
        answer_box = num_question.find_element_by_xpath(".//input[@ng-model='ctrl.selectedValue']")
        answer_box.clear()
        answer_box.send_keys(value)
        log(INFO, "Entered value '%s'." % value)
        time.sleep(wait_dur)
        units_dropdown = num_question.find_element_by_xpath(".//button[@ng-click='ctrl.showUnitsDropdown()']")
        units_dropdown.click()
        log(INFO, "Clicked to open units dropdown.")
        time.sleep(wait_dur)
        if correct_unit == "None" and not get_unit_wrong:
            correct_u = num_question.find_element_by_xpath(".//a[contains(@ng-click,'ctrl.selectedUnits') and text()='None']")
            correct_u.click()
            correct_u_text = str(correct_u.get_attribute('innerHTML'))
            log(INFO, "Selected correct unit '%s' (to match '%s')." % (correct_u_text, correct_unit))
        elif not get_unit_wrong:
            correct_u = num_question.find_element_by_xpath(".//a[contains(@ng-click,'ctrl.selectedUnits')]//script[contains(text(), '%s')]/.." % correct_unit)
            correct_u.click()
            correct_u_text = str(correct_u.find_element_by_xpath("./script").get_attribute('innerHTML'))
            log(INFO, "Selected correct unit '%s' (to match '%s')." % (correct_u_text, correct_unit))
        else:
            choices = num_question.find_elements_by_xpath(".//a[contains(@ng-click,'ctrl.selectedUnits')]")
            n = 1  # Skip the "None" option, which is element 0
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


def clear_question_filter(driver, wait_dur=2):
    """Clear the filter to a blank state, with nothing selected.

       Assuming this is run on the "/gameboards" page and the filter is open,
       it will unclick both Physics and Maths if necessary to set the filter to
       a fresh state.
        - 'driver' should be a Selenium WebDriver.
        - 'wait_dur' ensures JavaScript elements have time to react given different
          browser speeds.
    """
    filter_blank = False
    while not filter_blank:
        items = driver.find_elements_by_xpath("(//*[local-name() = 'svg']//*[name()='path' and contains(@class,'enabled')])[1]")
        if len(items) > 0:
            items[0].click()
            time.sleep(wait_dur)
        else:
            filter_blank = True
    log(INFO, "Set tag filter to blank state!")
    selected_levels = driver.find_elements_by_xpath("(//div[@id='difficulty-hexagons'])[1]/a[@class='ru-diff-hex']/div[@class='diff-hex-selected']/..")
    while len(selected_levels) > 0:
        selected_levels[0].click()
        selected_levels = driver.find_elements_by_xpath("(//div[@id='difficulty-hexagons'])[1]/a[@class='ru-diff-hex']/div[@class='diff-hex-selected']/..")
    log(INFO, "Set the level filter to blank state!")
    time.sleep(wait_dur)


def set_filter_state(driver, tag_list, level_list, wait_dur=2):
    """Set the filter to the state specified in 'tag_list'.

       After opening the filter and clearing it using 'clear_question_filter()',
       this function can be used to set the filter to a desired state. The tags
       should be given in hierarchical order, else it may fail!
        - 'driver' should be a Selenium WebDriver.
        - 'tag_list' should be a list of tag names to select using the filter,
          in hierarchical order. '["Physics", "Mechanics", "Dynamics"]' for example.
        - 'wait_dur' ensures JavaScript elements have time to react given different
          browser speeds.
    """
    try:
        for tag in tag_list:
            button_name = tag
            data_item = driver.find_element_by_xpath("(//div[@id='hexfilter-text'])[1]//p[text()='%s']/../.." % button_name).get_attribute("data-item")
            filter_button = driver.find_element_by_xpath("(//*[local-name() = 'svg']//*[name()='path' and @data-item='%s'])[1]" % data_item)
            filter_button.click()
            time.sleep(wait_dur)
        level_buttons = driver.find_elements_by_xpath("(//div[@id='difficulty-hexagons'])[1]/a[@class='ru-diff-hex']")
        assert len(level_buttons) == 6
        for l in level_list:
            level_buttons[l - 1].click()
            level_buttons = driver.find_elements_by_xpath("(//div[@id='difficulty-hexagons'])[1]/a[@class='ru-diff-hex']")
        return True
    except NoSuchElementException:
        log(ERROR, "Could not set filter to desired state!")
        return False
    except AssertionError:
        log(ERROR, "Couldn't find level filter buttons; couldn't set filter to desired state!")
        return False
    except IndexError:
        log(ERROR, "Invalid level requested!")
        return False


def get_hexagon_properties(hexagon_element):
    """Given the WedDriver element for the hexagon, return a dict of properties.

       The element must be the 'a' element for the hexagon, otherwise the properties
       cannot be found. Any unknown or unset properties will be returned as the
       empty string.
        - 'hexagon_element' should be a WebElement for the hexagon in question.
    """
    if len(hexagon_element.find_elements_by_xpath("./div[@class='ru-hex-home-content-wild']")) > 0:
        return dict(type='Wildcard')
    try:
        level = int(hexagon_element.find_element_by_xpath("./div[contains(@class, 'ru-hex-level-')]").get_attribute("class").replace('ru-hex-level-', ''))
        topic = str(hexagon_element.find_element_by_xpath("./div[@class='ru-hex-home-title']").text)
        field = str(hexagon_element.find_element_by_xpath("./div[contains(@class, 'ru-hex-home-field')]")
                    .get_attribute("class").replace('ru-hex-home-field', '').replace('-', '')).strip().title()
        title = str(hexagon_element.find_element_by_xpath("./div[@class='ru-hex-home-desc']").text)
        if len(hexagon_element.find_elements_by_xpath(".//*[local-name() = 'svg']//*[name()='path' and contains(@class, 'physics')]")) > 0:
            subject = "Physics"
        elif len(hexagon_element.find_elements_by_xpath(".//*[local-name() = 'svg']//*[name()='path' and contains(@class, 'maths')]")) > 0:
            subject = "Maths"
        else:
            subject = ""
        return dict(type='Question', level=level, topic=topic, field=field, title=title, subject=subject)
    except NoSuchElementException:
        log(ERROR, "Failed to find hexagon properties!")
        return None
