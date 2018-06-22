import time
import random
from ..utils.log import log, INFO, ERROR, PASS
from ..utils.i_selenium import assert_tab, wait_for_invisible_xpath, wait_for_xpath_element
from ..utils.isaac import submit_login_form
from ..tests import TestWithDependency
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoAlertPresentException
from selenium.webdriver.support.ui import Select

__all__ = ['board_builder']


def check_all_results(driver, assertion, failure_message_formatter, allow_empty=False):
    question_results = driver.find_elements_by_xpath("//ul[@class='no-bullet results-list ng-scope']//li")
    if not allow_empty:
        assert len(question_results), 'No question results found for assertion with message:\n{}'.format(failure_message_formatter('""'))
    for question_result in question_results:
        assert assertion(question_result), failure_message_formatter(question_result.text)


@TestWithDependency('BOARD_BUILDER')
def board_builder(driver, Users, ISAAC_WEB, WAIT_DUR, **kwargs):
    try:
        random_id = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890') for _ in range(8))

        log(INFO, "Log in as an admin user and go to page")
        assert_tab(driver, ISAAC_WEB)
        driver.get(ISAAC_WEB + '/logout')
        driver.get(ISAAC_WEB + '/game_builder')
        assert submit_login_form(driver, user=Users.Admin, wait_dur=WAIT_DUR), "Can't access User Admin; can't continue testing!"

        log(INFO, "Test subject field filtering")
        subject_field = Select(driver.find_element_by_xpath('//select[@ng-model="questionSearchSubject"]'))

        subject_field.select_by_visible_text('Mathematics')
        time.sleep(WAIT_DUR)
        check_all_results(driver,
                          lambda question_result: 'maths' in question_result.text.lower(),
                          lambda question_result_text: '"maths" was not found in "{}"'.format(question_result_text.lower()))

        subject_field.select_by_visible_text('Physics')
        time.sleep(WAIT_DUR)
        check_all_results(driver,
                          lambda question_result: 'physics' in question_result.text.lower(),
                          lambda question_result_text: '"physics" was not found in "{}"'.format(question_result_text.lower()))

        log(INFO, "Test level field filtering")
        level_field = Select(driver.find_element_by_xpath('//select[@ng-model="questionSearchLevel"]'))
        level_field.select_by_visible_text('2')
        time.sleep(WAIT_DUR)
        check_all_results(driver,
                          lambda question_result: 'level 2' in question_result.text.lower(),
                          lambda question_result_text: '"level 2" was not found in "{}"'.format(question_result_text.lower()))

        log(INFO, "Test query field filtering")
        query_field = driver.find_element_by_xpath('//input[@ng-model="questionSearchText"]')
        query_field.send_keys('toboggan')
        time.sleep(WAIT_DUR)
        check_all_results(driver,
                          lambda question_result: 'toboggan' in question_result.text.lower(),
                          lambda question_result_text: '"toboggan" was not found in "{}"'.format(question_result_text.lower()))

        log(INFO, "Check book links work")
        mastering_physics_link = driver.find_element_by_xpath('//a[text() = "Pre-University Physics"]')
        mastering_physics_link.click()
        time.sleep(WAIT_DUR)
        check_all_results(driver,
                          lambda question_result: all(keyword in question_result.text.lower() for keyword in ['physics', 'physics_skills_14']),
                          lambda question_result_text: '"physics" or "physics_skills_14" was not found in "{}"'.format(question_result_text.lower()))

        mastering_chemistry_link = driver.find_element_by_xpath('//a[text() = "Physical Chemistry"]')
        mastering_chemistry_link.click()
        time.sleep(WAIT_DUR)
        check_all_results(driver,
                          lambda question_result: all(keyword in question_result.text.lower() for keyword in ['chemistry', 'chemistry_16']),
                          lambda question_result_text: '"chemistry" or "chemistry_16" was not found in "{}"'.format(question_result_text.lower()))

        log(INFO, "Build a board")
        question_checkboxes = driver.find_elements_by_xpath("//ul[@class='no-bullet results-list ng-scope']//li//input[@type='checkbox' and @ng-model='enabledQuestions[question.id]']")
        for i in range(10):
            element = question_checkboxes[i]
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()
        try:
            wait_for_xpath_element(driver, "//h4[text() = 'Too Many Questions']", 5)
            log(ERROR, "Did not expect error message to be displayed!")
            return False
        except TimeoutException:
            pass  # Exception occurs only if no error message shown.

        log(INFO, "Try to tick an eleventh checkbox")
        question_checkboxes[10].click()
        try:
            wait_for_xpath_element(driver, "//h4[text() = 'Too Many Questions']", 5)
        except TimeoutException:
            log(ERROR, 'Too Many Questions error not displayed before timeout')
            return False
        wait_for_invisible_xpath(driver, "//h4[text() = 'Too Many Questions']")  # Wait while exception toast is in view

        log(INFO, "Remove one question")
        question_checkboxes[9].click()

        log(INFO, "Try to add two other questions")
        for i in [10, 11]:
            element = question_checkboxes[i]
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()
        try:
            wait_for_xpath_element(driver, "//h4[text() = 'Too Many Questions']", 5)
        except TimeoutException:
            log(ERROR, 'Too Many Questions error not displayed before timeout')
            return False
        wait_for_invisible_xpath(driver, "//h4[text() = 'Too Many Questions']")  # Wait while exception toast is in view

        log(INFO, "Set title")
        title_field = driver.find_element_by_xpath('//input[@ng-model="currentGameBoard.title"]')
        title_field.send_keys('Test Board')

        log(INFO, "Set ID")
        id_field = driver.find_element_by_xpath('//input[@ng-model="currentGameBoard.id"]')
        id_field.send_keys(random_id)

        log(INFO, "Make a wild card selection")
        wildcard_field = Select(driver.find_element_by_xpath('//select[@ng-model="userSelectedBoardWildCardId"]'))
        wildcard_field.select_by_visible_text('About Us')
        time.sleep(WAIT_DUR)
        about_us_hex = driver.find_elements_by_xpath('//div[@class="ru-hex-home-title" and text() = "About Us"]')
        assert len(about_us_hex), 'Not able to see chosen wildcard'

        log(INFO, "Save the board")
        save_button = driver.find_element_by_xpath('//button[@type="submit" and text() = "Save this board"]')
        save_button.click()
        time.sleep(WAIT_DUR)
        try:
            alert = driver.switch_to.alert
            assert 'save' in alert.text, 'Alert text did not contain "save"'
            alert.accept()
        except NoAlertPresentException as e:
            log(ERROR, 'Save alert not present (1)')
            return False

        log(INFO, "Use a URL to populate board builder fields")
        time.sleep(WAIT_DUR)
        driver.get(ISAAC_WEB + '/game_builder?query="physics_skills_14"&subject=physics&level=any&sort=title')
        subject_field = Select(driver.find_element_by_xpath('//select[@ng-model="questionSearchSubject"]'))
        level_field = Select(driver.find_element_by_xpath('//select[@ng-model="questionSearchLevel"]'))
        query_field = driver.find_element_by_xpath('//input[@ng-model="questionSearchText"]')
        time.sleep(WAIT_DUR)
        question_results_text = [question_result.text for question_result in driver.find_elements_by_xpath("//ul[@class='no-bullet results-list ng-scope']//li")]
        assert subject_field.first_selected_option.text == 'Physics', 'Subject field value "{}" does not match expected "{}"'.format(subject_field.first_selected_option.text, 'Physics')
        assert level_field.first_selected_option.text == 'Any', 'Level field value "{}" does not match expected "{}"'.format(level_field.first_selected_option.text, 'Any')
        assert query_field.get_attribute('value') == '"physics_skills_14"', 'Query field value "{}" does not match expected "{}"'.format(query_field.get_attribute('value'), '"physics_skills_14"')
        assert question_results_text == sorted(question_results_text), 'Question results were not sorted as was expected\n{}'.format(question_results_text)

        log(INFO, "Try to save board with a pre-existing ID")
        title_field = driver.find_element_by_xpath('//input[@ng-model="currentGameBoard.title"]')
        title_field.send_keys('Test Duplicate ID Board')
        question_checkboxes = driver.find_elements_by_xpath("//ul[@class='no-bullet results-list ng-scope']//li//input[@type='checkbox' and @ng-model='enabledQuestions[question.id]']")
        question_checkboxes[0].click()
        id_field = driver.find_element_by_xpath('//input[@ng-model="currentGameBoard.id"]')
        id_field.send_keys(random_id)  # Re-use ID used earlier
        save_button = driver.find_element_by_xpath('//button[@type="submit" and text() = "Save this board"]')
        save_button.click()
        try:
            alert = driver.switch_to.alert
            assert 'save' in alert.text, 'Alert text did not contain "save"'
            alert.accept()
            wait_for_xpath_element(driver, '//h4[text() = "Save Operation Failed"]', 5)
        except NoAlertPresentException as e:
            log(ERROR, 'Save alert not present (1)')
            return False
        except TimeoutException:
            log(ERROR, 'Error not displayed when expected after saving with same ID')
            return False
        wait_for_invisible_xpath(driver, "//h4[text() = 'Too Many Questions']")  # Wait while exception toast is in view

        log(PASS, "Board builder functions as expected.")
        return True

    except AssertionError as e:
        log(ERROR, "Asserton Error: {}".format(e))
        return False
    except NoSuchElementException as e:
        log(ERROR, "No Such Element Exception: {}".format(e))
        return False
