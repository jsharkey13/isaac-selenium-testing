import time
import re
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
from ..utils.i_selenium import image_div
from ..utils.log import log, INFO, stop

__all__ = ['set_guerrilla_mail_address', 'GuerrillaInbox', 'GuerrillaEmail']

_SAFENAMECHARS = '[^-a-zA-Z0-9_ ]+'


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
    except (Exception, NoSuchElementException):
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
            fname = re.sub(_SAFENAMECHARS, '', fname) + ".png"
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
            fname = re.sub(_SAFENAMECHARS, '', fname) + ".html"
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
