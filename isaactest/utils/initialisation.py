import selenium.webdriver
import time
from .log import log, INFO
from .i_selenium import new_tab
from .isaac import TestUsers, User
from ..emails.guerrillamail import GuerrillaInbox, set_guerrilla_mail_address


def define_users():
    """Set up the TestUser object and add the temporary email address to it."""
    Users = TestUsers.load()
    Guerrilla = User("isaactest@sharklasers.com", "Temp",
                     "Test", "test")
    Users.Guerrilla = Guerrilla
    Users.Guerrilla.new_email = "isaactesttwo@sharklasers.com"
    Users.Guerrilla.new_password = "testing123"
    return Users


def start_selenium(Users, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR, PATH_TO_CHROMEDRIVER=None):
    """Start the Selenium WebDriver of choice.

       Start a Selenium WebDriver then return it and a GuerrillaInbox object. If
       a 'PATH_TO_CHROMEDRIVER' is specified, the WebDriver will be Chrome, otherwise
       Firefox will be used.
        - 'Users' should be the TestUser object returned by
          'isaactest.utils.initialisation.define_users()'.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'GUERRILLAMAIL' is the string URL of GuerrillaMail.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
        - 'PATH_TO_CHROMEDRIVER' is an optional argument telling Python where to
          look for the ChromeDriver executable. If not specified, Firefox will
          be used.
    """
    # Selenium Start-up:
    if PATH_TO_CHROMEDRIVER is not None:
        driver = selenium.webdriver.Chrome(PATH_TO_CHROMEDRIVER)
    else:
        driver = selenium.webdriver.Firefox()
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