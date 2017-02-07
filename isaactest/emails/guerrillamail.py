import time
import re
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, TimeoutException
from ..utils.i_selenium import image_div, wait_for_xpath_element
from ..utils.log import log, INFO, ERROR

__all__ = ['set_guerrilla_mail_address', 'GuerrillaInbox', 'GuerrillaEmail']

_SAFENAMECHARS = '[^-a-zA-Z0-9_ ]+'


class GuerrillaMailError(Exception):
    pass


def set_guerrilla_mail_address(driver, guerrilla_email=None):
    """Change or get the GuerrillaMail email address.

       If the optional argument 'geurrilla_email' is set, change the email address
       to this (split at the @ symbol). In all cases, the current email address is
       the return value of the function.
        - 'driver' should be a Selenium WebDriver.
        - 'guerrilla_email' should optionally be a string of the email address
          desired, where only the bit before the @ is used to set the email.
        - 'wait_dur' is the time in seconds to wait for the email to be changed.
    """
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
            wait_for_xpath_element(driver, "//div[contains(@class, 'status_alert')][text()='Email set to %s']" % guerrilla_email)
            email_box = driver.find_element_by_id("email-widget")
            if guerrilla_email != str(email_box.text):
                log(ERROR, "GM - Failed to change GuerrillaMail email address!")
                raise GuerrillaMailError
            log(INFO, "Set GuerrillaMail email address to %s" % guerrilla_email)
            return guerrilla_email
        else:
            email_box = driver.find_element_by_id("email-widget")
            guerrilla_email = str(email_box.text)
            log(INFO, "Set GuerrillaMail email address to %s" % guerrilla_email)
            return guerrilla_email
    except NoSuchElementException:
        image_div(driver, "ERROR_set_guerrillamail")
        log(ERROR, "GM - Can't fill out Guerrilla Mail form; see 'ERROR_set_guerrillamail.png'!")
        raise GuerrillaMailError
    except TimeoutException:
        log(ERROR, "GM - Failed to change GuerrillaMail email address!")
        raise GuerrillaMailError


class GuerrillaInbox():
    """A class to abstract away the GuerrillaMail inbox.

       It contains methods for refreshing its email list, accessing all emails,
       accessing unread emails, getting all emails matching a subject or timestamp
       and for deleting emails.
       '.emails' is a list of all emails as GuerrillaEmail objects, and '.unread'
       is a list of all unread emails, which is not updated when emails are read
       unless 'refresh()' is called.
    """
    GUERRILLAMAIL = "www.guerrillamail.com"

    def __init__(self, driver):
        """Create the inbox object.

           This should be run whilst on the GuerrillaMail website, and it is strongly
           reccommended that the tab be left open.
            - 'driver' should be a Selenium WebDriver.
        """
        log(INFO, "Creating GuerrillaInbox object.")
        self._driver = driver
        try:
            self.emails = [GuerrillaEmail(driver, e) for e in driver.find_elements_by_xpath("//tr[contains(@class, 'mail_row')]")]
            self.unread = [GuerrillaEmail(driver, e) for e in driver.find_elements_by_xpath("//tr[contains(@class, 'email_unread')]")]
        except NoSuchElementException:
            log(ERROR, "GM - No email elements on the page; failed to find inbox!")
            raise GuerrillaMailError

    def refresh(self):
        """Refresh the inbox object, remove any old emails add new ones.

           This must be run whilst on the GuerrillaMail tab. It will remove any
           deleted/timed out emails, update the read/unread status of emails and
           update to include any new emails that have been recieved.
        """
        log(INFO, "Refreshing GuerrillaInbox object.")
        try:
            del(self.emails)
            del(self.unread)
            self.emails = [GuerrillaEmail(self._driver, e) for e in self._driver.find_elements_by_xpath("//tr[contains(@class, 'mail_row')]")]
            self.unread = [GuerrillaEmail(self._driver, e) for e in self._driver.find_elements_by_xpath("//tr[contains(@class, 'email_unread')]")]
        except NoSuchElementException:
            log(ERROR, "GM - No email elements on page; failed to find inbox!")
            raise GuerrillaMailError

    def delete_email(self, email):
        """Delete a GuerillaMail email.

           This must be run whilst on the GuerrillaMail tab. It will remove the
           email from the emails and unread lists.
            - 'email' should be a GuerrillaEmail object to be deleted.
        """
        log(INFO, "Deleting %s." % email)
        email._delete()
        try:
            self.emails.remove(email)
            self.unread.remove(email)
        except ValueError:
            pass
        time.sleep(2)

    def get_by_time(self, timestamp):
        """Get any emails with a timestamp matching that specified.

            - 'timestamp' should be a string of the format 'HH:MM:SS'.
        """
        matches = [e for e in self.emails if e.time == timestamp]
        return matches

    def get_by_subject(self, subject, unread=False):
        """Get any emails containing 'subject' in the subject line.

           This function does not perform exact matching because the browser cannot
           be guaranteed not to add or remove whitespace from the subject line.
            - 'subject' should be a string to be matched.
            - 'unread' is an optional flag to only return unread emails with a
              matching subject line.
        """
        if unread:
            matches = [e for e in self.unread if subject in e.subject]
        else:
            matches = [e for e in self.emails if subject in e.subject]
        return matches

    def wait_for_email(self, wait_dur, refresh_time=11, cycles=10):
        """Wait for emails to be received, then refresh inbox object.

           This function pauses for 'wait_dur' amount of time, then waits for up
           to 'refresh_time' for new emails to arrive. If none arrive; it waits
           twice as long the next time, three times the third time etc. It will
           do this looping 'cycles' many times.
            - 'wait_dur' indicates how long to pause before waiting for emails.
            - 'refresh_time' should be the refresh period of the email service,
              or however long to wait in cycles.
            - 'cycles' is how many times to loop before aborting, remembering that
              the overall wait duration gets longer nonlinearly as cycles increases.
        """
        total_wait = wait_dur
        log(INFO, "Waiting for email.")
        time.sleep(wait_dur)
        for i in range(1, cycles + 1):
            try:
                total_wait += refresh_time * i
                wait_for_xpath_element(self._driver, "//div[contains(@class,'status_alert') and contains(text(), 'New Mail')]", refresh_time*i)
                time.sleep(wait_dur)
                log(INFO, "Email(s) received!")
                self.refresh()
                return
            except TimeoutException:
                if i == 1:  # I.e. wait for first refresh_time to be safe,
                    self.refresh()  # Then if have unread emails, use those.
                    if len(self.unread) > 0:
                        log(INFO, "Waited for %s+%s seconds, no new mail but have unread emails: use these!" % (wait_dur, total_wait - wait_dur))
                        return
                if i != cycles:
                    log(INFO, "Waited for %s+%s seconds, no email! Increment wait duration." % (wait_dur, total_wait - wait_dur))
                else:
                    log(ERROR, "Waited for %s seconds. Stopped waiting!" % total_wait)
                    raise


class GuerrillaEmail():
    """A class to abstract away GuerrillaMail emails.

       These should not be generated by hand, but managed by a GuerrillaInbox object,
       which will store a list of them. It contains the subject, sender, excerpt and
       timestamp; and functions to view the message, save an image of the message,
       save the HTML of the message and close the message.
    """

    def __init__(self, driver, row_element):
        """Create a new GuerrillaEmail object; not reccommended to run this by hand."""
        self._driver = driver
        self._row_element = row_element
        try:
            self.sender_element = row_element.find_element_by_xpath("./td[@class='td2']")
            self.sender = str(self.sender_element.text).lstrip().rstrip()
            self.subject_element = row_element.find_element_by_xpath("./td[@class='td3']")
            self.subject = str(self.subject_element.text).lstrip().rstrip()
            self.excerpt_element = self.subject_element.find_element_by_xpath("./span[@class='email-excerpt']")
            self.excerpt = str(self.excerpt_element.text).lstrip().rstrip()
            self.time_element = row_element.find_element_by_xpath("./td[@class='td4']")
            self.time = str(self.time_element.text).lstrip().rstrip()
        except NoSuchElementException:
            log(ERROR, "GM - Can't created email object. Can't find elements required!")
            raise GuerrillaMailError

    def __str__(self):
        """A useful string representation of the email."""
        return "<Email from '%s' at '%s'>" % (self.sender, self.time)

    def __repr__(self):
        """Set Python's representation to be the string form for easier viewing."""
        return str(self)

    def _delete(self):
        """Delete the email. Do not run by hand, but use GuerrillaInobx.delete(email)."""
        self.close()
        self._select()
        del_button = self._driver.find_element_by_id("del_button")
        del_button.click()
        time.sleep(2)

    def _select(self):
        """Tick the checkbox next to the email, required for deletion.

           Take care when doing this by hand; the email will be deleted if any other
           email is deleted!"""
        try:
            tickbox = self._row_element.find_element_by_xpath("./td[@class='td1']/input")
        except NoSuchElementException:
            log(ERROR, "GM - Couldn't find email element!")
            raise GuerrillaMailError
        if not tickbox.is_selected():
            tickbox.click()
        time.sleep(1)

    def view(self, images=True):
        """Open an email.

           Useful for then running 'get_email_body_element' for checking the content
           of an email. Take care to run 'close()' afterwards to ensure the email
           is not accidentally left open!
           The email container will be resized to fit the whole of the recieved email.
            - 'images' is an optional boolean argument to view images when opening the
              email.
        """
        log(INFO, "Viewing %s" % self)
        try:
            self.sender_element.click()
            time.sleep(2)
            if images:
                show_images = self._driver.find_element_by_id("display_images")
                show_images.click()
                body = self._driver.find_element_by_xpath("//div[@class='email_body']")
                height = body.size['height'] + 125
                self._driver.execute_script("document.getElementsByClassName('email')[0].style.height = '%spx';" % height)
                time.sleep(2)
        except NoSuchElementException:
            log(ERROR, "GM - Can't view email; can't find elements required!")
            raise GuerrillaMailError

    def image(self, fname=None):
        """Save a png image of the email.

           If the optional 'fname' string is specified, save to this filename,
           where '.png' is automatically appended.
        """
        log(INFO, "Imaging %s." % self)
        if fname is None:
            fname = (self.subject + "_" + self.time).lstrip().replace(" ", "_").replace(":", "")
            fname = re.sub(_SAFENAMECHARS, '', fname)
        self.view()
        try:
            email = self._driver.find_element_by_xpath("//div[@class='email']")
            image_div(self._driver, fname, email)
        except NoSuchElementException:
            log(ERROR, "GM - Can't image email; can't find required elements!")
            raise GuerrillaMailError
        self.close()

    def get_email_body_element(self):
        """Return the body WebDriver element of the email, useful for checking content."""
        return self._driver.find_element_by_xpath("//div[@class='email_body']")

    def save_html_body(self, fname=None):
        """Save the HTML of the email body.

           If the optional 'fname' string is specified, save to this filename,
           where '.html' is automatically appended.
        """
        log(INFO, "Saving HTML of %s." % self)
        if fname is None:
            fname = (self.subject + "_" + self.time).lstrip().replace(" ", "_").replace(":", "")
        fname = re.sub(_SAFENAMECHARS, '', fname) + ".html"
        self.view()
        try:
            body_element = self.get_email_body_element()
            body_html = str(body_element.get_attribute('innerHTML'))
            with open(fname, "w") as f:
                f.write(body_html)
        except NoSuchElementException:
            log(ERROR, "Can't save email html body; can't access elements required!")
            raise GuerrillaMailError
        self.close()

    def close(self):
        """Close the email and returns to the inbox.

           Run this after 'view()' to avoid errors.
        """
        try:
            close_button = self._driver.find_element_by_id("back_to_inbox_link")
            log(INFO, "Closing %s." % self)
            close_button.click()
            time.sleep(2)
        except (NoSuchElementException, ElementNotVisibleException):
            pass
