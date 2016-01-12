# Selenium Utility Functions
import time
import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotVisibleException
from PIL import Image
import re
import pickle

SAFENAMECHARS = '[^-a-zA-Z0-9_ ]+'

INFO = "INFO"
PASS = "PASS"
ERROR = "ERROR"
FATAL = "FATAL"

LOGFILE = None
tests_passed = 0
errors = 0

# Customise which log events are printed:
OUTPUT_LOGGING_LEVELS = [INFO, PASS, ERROR, FATAL]


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


def start_testing():
    global LOGFILE
    log_time = "[%s]" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print "%s \t Starting Regression Testing." % log_time
    LOGFILE = open("_TEST_LOG.txt", "a")
    LOGFILE.write("%s \t Starting Regression Testing.\n" % log_time)


def end_testing():
    global LOGFILE, tests_passed, errors
    log_time = "[%s]" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print "%s \t Testing Finished. %s passes, %s errors.\n\n" % (log_time, tests_passed, errors)
    LOGFILE.write("%s \t Testing Finished. %s passes, %s errors.\n\n\n" % (log_time, tests_passed, errors))
    LOGFILE.close()


def stop(driver, message="Fatal Error! Stopping"):
    log(FATAL, message)
    raw_input("Paused (Press Enter to Quit)")
#    driver.quit()
    end_testing()
    raise SystemExit


def log(level, message):
    """NOT THREAD SAFE YET!"""
    global OUTPUT_LOGGING_LEVELS, FATAL, ERROR, tests_passed, errors
    if level == PASS:
        tests_passed += 1
    if ((level == ERROR) or (level == FATAL)):
        errors += 1
    if (level in OUTPUT_LOGGING_LEVELS) or (level == FATAL):
        log_time = "[%s]" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = "[%s]" % level.ljust(5)
        log_item = "%s %s\t- %s" % (log_time, level, message)
        print log_item
        LOGFILE.write(log_item + "\n")
        LOGFILE.flush()


def new_tab(driver):
    driver.find_element_by_xpath("//body").send_keys(Keys.CONTROL + 't')
    time.sleep(1)
    log(INFO, "Opened new tab.")


def change_tab(driver):
    main_window = driver.current_window_handle
    driver.find_element_by_xpath("//body").send_keys(Keys.CONTROL + Keys.TAB)
    time.sleep(0.5)
    driver.switch_to_window(main_window)
    url = driver.current_url
    time.sleep(0.5)
    log(INFO, "Changed tab to %s." % url)


def close_tab(driver):
    main_window = driver.current_window_handle
    old_url = driver.current_url
    driver.find_element_by_xpath("//body").send_keys(Keys.CONTROL + 'w')
    time.sleep(0.5)
    driver.switch_to_window(main_window)
    new_url = driver.current_url
    time.sleep(0.5)
    log(INFO, "Closed tab %s. Now on %s" % (old_url, new_url))


def assert_tab(driver, url_part):
    log(INFO, "AssertTab: Changing to tab with url containing '%s'." % url_part)
    urls = [driver.current_url]
    if url_part in urls[0]:
        return
    else:
        while not any(url_part in u for u in urls):
            change_tab(driver)
            current_url = driver.current_url
            if current_url in urls:
                stop(driver, "AssertTab: Couldn't reach required tab with url containing '%s'!" % url_part)
            urls.append(current_url)


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


def wait_for_xpath_element(driver, element, duration=10, visible=True):
    if visible:
        return WebDriverWait(driver, duration).until(EC.visibility_of_element_located((By.XPATH, element)))
    else:
        return WebDriverWait(driver, duration).until(EC.presence_of_element_located((By.XPATH, element)))


def wait_for_invisible_xpath(driver, element, duration=10):
    return WebDriverWait(driver, duration).until(EC.invisibility_of_element_located((By.XPATH, element)))


def image_div(driver, fname, div_element=None):
    driver.save_screenshot(fname)
    if div_element is None:
        log(INFO, "Saved image '%s'." % fname)
        return
    div_loc = div_element.location
    div_size = div_element.size
    l, t = div_loc['x'], div_loc['y']
    r, b = l + div_size['width'], t + div_size['height'] - 1
    if (l == r) or (t == b):
        log(INFO, "Element had no size. Saving whole screen")
        return
    image = Image.open(fname)
    image = image.crop((l, t, r, b))
    image.save(fname)
    log(INFO, "Saved image '%s'." % fname)


def save_element_html(element, fname):
    element_html = str(element.get_attribute('innerHTML'))
    with open(fname, "w") as f:
        f.write(element_html)
    log(INFO, "Saved element HTML as '%s'." % fname)


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


def set_guerrilla_mail_address(driver, guerrilla_email=None):
    try:
        use_alias = driver.find_element_by_id("use-alias")
        if use_alias.is_selected():
            use_alias.click()
        if guerrilla_email is not None:
            set_email_button = driver.find_element_by_id("inbox-id")
            set_email_button.click()
            set_email = driver.find_element_by_xpath("//span[@id='inbox-id']/input[@type='text']")
            set_email.clear()
            set_email.send_keys(guerrilla_email.split("@")[0])
            set_email_button = driver.find_element_by_xpath("//span[@id='inbox-id']/button[text()='Set']")
            set_email_button.click()
            time.sleep(1)
            email_box = driver.find_element_by_id("email-widget")
            if guerrilla_email != str(email_box.text):
                stop(driver, "Failed to change GuerrillaMail email address!")
            return guerrilla_email
        else:
            email_box = driver.find_element_by_id("email-widget")
            guerrilla_email = str(email_box.text)
            log(INFO, "Set GuerrillaMail email address to %s" % guerrilla_email)
            return guerrilla_email
    except NoSuchElementException:
        image_div(driver, "ERROR_set_guerrillamail.png")
        stop(driver, "Can't fill out signup form; see 'ERROR_set_guerrillamail.png'!")


class GuerrillaInbox():
    GUERRILLAMAIL = "www.guerrillamail.com"

    def __init__(self, driver):
        log(INFO, "Creating GuerrillaInbox object.")
        self._driver = driver
        self.emails = [GuerrillaEmail(driver, e) for e in driver.find_elements_by_xpath("//tr[contains(@class, 'mail_row')]")]
        self.unread = [GuerrillaEmail(driver, e) for e in driver.find_elements_by_xpath("//tr[contains(@class, 'email_unread')]")]

    def refresh(self):
        log(INFO, "Refreshing GuerrillaInbox object.")
        del(self.emails)
        del(self.unread)
        self.emails = [GuerrillaEmail(self._driver, e) for e in self._driver.find_elements_by_xpath("//tr[contains(@class, 'mail_row')]")]
        self.unread = [GuerrillaEmail(self._driver, e) for e in self._driver.find_elements_by_xpath("//tr[contains(@class, 'email_unread')]")]

    def delete_email(self, email):
        log(INFO, "Deleting %s." % email)
        email._delete()
        try:
            self.emails.remove(email)
            self.unread.remove(email)
        except ValueError:
            pass
        time.sleep(1)

    def get_by_time(self, timestamp):
        matches = [e for e in self.emails if e.time == timestamp]
        return matches

    def get_by_subject(self, subject, unread=False):
        if unread:
            matches = [e for e in self.unread if subject in e.subject]
        else:
            matches = [e for e in self.emails if subject in e.subject]
        return matches


class GuerrillaEmail():

    def __init__(self, driver, row_element):
        self._driver = driver
        self._row_element = row_element
        self.sender_element = row_element.find_element_by_xpath("./td[@class='td2']")
        self.sender = str(self.sender_element.text).lstrip().rstrip()
        self.subject_element = row_element.find_element_by_xpath("./td[@class='td3']")
        self.subject = str(self.subject_element.text).lstrip().rstrip()
        self.excerpt_element = self.subject_element.find_element_by_xpath("./span[@class='email-excerpt']")
        self.excerpt = str(self.excerpt_element.text).lstrip().rstrip()
        self.time_element = row_element.find_element_by_xpath("./td[@class='td4']")
        self.time = str(self.time_element.text).lstrip().rstrip()

    def __str__(self):
        return "<Email from '%s' at '%s'>" % (self.sender, self.time)

    def __repr__(self):
        return str(self)

    def _delete(self):
        self.close()
        self.select()
        del_button = self._driver.find_element_by_id("del_button")
        del_button.click()
        time.sleep(1)

    def select(self):
        tickbox = self._row_element.find_element_by_xpath("./td[@class='td1']/input")
        if not tickbox.is_selected():
            tickbox.click()
        time.sleep(0.5)

    def view(self, images=True):
        log(INFO, "Viewing %s" % self)
        self.sender_element.click()
        time.sleep(1)
        if images:
            show_images = self._driver.find_element_by_id("display_images")
            show_images.click()
            body = self._driver.find_element_by_xpath("//div[@class='email_body']")
            height = body.size['height'] + 125
            self._driver.execute_script("document.getElementsByClassName('email')[0].style.height = '%spx';" % height)
            time.sleep(1)

    def image(self, fname=None):
        log(INFO, "Imaging %s." % self)
        if fname is None:
            fname = (self.subject + "_" + self.time).lstrip().replace(" ", "_").replace(":", "")
            fname = re.sub(SAFENAMECHARS, '', fname) + ".png"
        self.view()
        email = self._driver.find_element_by_xpath("//div[@class='email']")
        image_div(self._driver, fname, email)
        self.close()

    def get_email_body_element(self):
        return self._driver.find_element_by_xpath("//div[@class='email_body']")

    def save_html_body(self, fname=None):
        log(INFO, "Saving HTML of %s." % self)
        if fname is None:
            fname = (self.subject + "_" + self.time).lstrip().replace(" ", "_").replace(":", "")
            fname = re.sub(SAFENAMECHARS, '', fname) + ".html"
        self.view()
        body_element = self.get_email_body_element()
        body_html = str(body_element.get_attribute('innerHTML'))
        with open(fname, "w") as f:
            f.write(body_html)
        self.close()

    def close(self):
        try:
            close_button = self._driver.find_element_by_id("back_to_inbox_link")
            log(INFO, "Closing %s." % self)
            close_button.click()
            time.sleep(1)
        except (NoSuchElementException, ElementNotVisibleException):
            pass
