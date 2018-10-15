import time
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.isaac import submit_login_form
from ..utils.i_selenium import assert_tab, image_div
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

__all__ = ["user_type_specific_menu_links"]


#####
# Test : Access Admin Page As Users
#####
@TestWithDependency("USER_TYPE_SPECIFIC_MENU_LINKS", ["LOGIN", "LOGOUT"])
def user_type_specific_menu_links(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test access to admin page is suitably restricted.

        - 'driver' should be a Selenium WebDriver.
        - 'Users' must be a TestUsers object.
        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
        - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
    """
    assert_tab(driver, ISAAC_WEB)
    driver.get(ISAAC_WEB + "/logout")
    log(INFO, "Logging out any logged in user.")
    time.sleep(WAIT_DUR)

    menu_options_for_all = ['/account', '/boards', '/progress', '/assignments', '/solving_problems', '/support/teacher', '/support/student', '/events']
    menu_options_logged_out = ['/login'] + menu_options_for_all
    menu_options_student = ['/logout'] + menu_options_for_all
    menu_options_teacher = menu_options_student + ['/set_assignments', '/assignment_progress', '/groups']
    menu_options_editor = menu_options_teacher + ['/admin/content_errors', '/admin/stats']
    menu_options_event = menu_options_editor + ['/admin', '/admin/usermanager', '/admin/events']
    menu_options_admin = menu_options_event
    all_menu_options = menu_options_admin + ['/login']
    menu_links_fail = False
    global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
    global_nav.click()
    time.sleep(WAIT_DUR)
    menu_to_check = driver.find_element_by_class_name('dl-nav')
    log(INFO, "Found menu bar")
    for option in menu_options_logged_out:
        try:
            element = WebDriverWait(menu_to_check, 1).until(EC.visibility_of_element_located((By.XPATH, "//a[@href='%s']" % option)))
        except TimeoutException:
            log(INFO, "Logged out user doesnt have %s present" % option)
            image_div(driver, "ERROR_unexpected_missing_menu_link")
            log(ERROR, "Logged out user accessed has a missing menu link; see 'ERROR_unexpected_missing_menu_link.png'!")
            menu_links_fail = True
    unavailable_options = all_menu_options
    for suboption in menu_options_logged_out:
        unavailable_options = list(filter(lambda a: a!= suboption, unavailable_options))
    for badoption in unavailable_options:
        try:
            element = WebDriverWait(menu_to_check, 1).until(EC.visibility_of_element_located((By.XPATH, "//a[@href='%s']" % badoption)))
            image_div(driver, "ERROR_unexpected_menu_link")
            log(ERROR, "Logged out user has an extra %s menu link; see 'ERROR_unexpected_missing_menu_link.png'!" % badoption)
            menu_links_fail = True
        except:
            pass
    log(INFO, "Logged out user has all the required menu links")

    access_cases = [("Student", Users.Student, menu_options_student), ("Teacher", Users.Teacher, menu_options_teacher), ("Content Editor", Users.Editor, menu_options_editor), ("Event Manager", Users.Event, menu_options_event), ("Admin", Users.Admin, menu_options_admin)]
    for i_type, user, menu_options in access_cases:
        driver.get(ISAAC_WEB + "/login")
        log(INFO, "Got '%s'. As '%s', try to use global nav." % (ISAAC_WEB + "/login", i_type))
        time.sleep(WAIT_DUR)
        submit_login_form(driver, user=user, wait_dur=WAIT_DUR)
        time.sleep(WAIT_DUR)
        global_nav = driver.find_element_by_xpath("//button[@ng-click='menuToggle()']")
        global_nav.click()
        time.sleep(WAIT_DUR)
        menu_to_check = driver.find_element_by_class_name('dl-nav')
        for option in menu_options:
            try:
                element = WebDriverWait(menu_to_check, 1).until(EC.visibility_of_element_located((By.XPATH, "//a[@href='%s']" % option)))
            except TimeoutException:
                log(INFO, "%s user doesnt have %s present" % (i_type, option))
                image_div(driver, "ERROR_unexpected_missing_menu_link")
                log(ERROR, "%s user accessed has a missing menu link; see 'ERROR_unexpected_missing_menu_link.png'!" % (i_type))
                menu_links_fail = True
        unavailable_options = all_menu_options
        for suboption in menu_options:
            unavailable_options = list(filter(lambda a: a != suboption, unavailable_options))
        for badoption in unavailable_options:
            try:
                element = WebDriverWait(menu_to_check, 1).until(EC.visibility_of_element_located((By.XPATH, "//a[@href='%s']" % badoption)))
                image_div(driver, "ERROR_unexpected_menu_link")
                log(ERROR,"%s user has an extra %s menu link; see 'ERROR_unexpected_missing_menu_link.png'!" % (i_type, badoption))
                menu_links_fail = True
            except:
                pass
        log(INFO, "%s user has all the required menu links" % (i_type))
        driver.get(ISAAC_WEB + "/logout")
        log(INFO, "Logged out '%s' user." % i_type)
        time.sleep(3)

    if not menu_links_fail:
        log(PASS, "Presented menu options are correct for all users")
        return True
    else:
        return False
