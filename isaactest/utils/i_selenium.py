import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
from .log import log, INFO, ERROR


__all__ = ['new_tab', 'change_tab', 'assert_tab', 'close_tab', 'image_div',
           'wait_for_xpath_element', 'wait_for_invisible_xpath', 'save_element_html',
           'AssertTabError']


class AssertTabError(Exception):
    """The error raised by 'assert_tab' if it cannot find the required tab."""
    pass


def new_tab(driver):
    """Open a new tab in the browser and switch to it.

       Gets a new tab in a browser independent way. May fail if the page being
       displayed is not a valid HTML page and has no body element.
        - 'driver' should be a Selenium WebDriver, currently Chrome and Firefox
          are supported.
    """
    if driver.name == 'firefox':
        main_window = driver.current_window_handle  # Hack to make currently displayed tab
        driver.find_element_by_xpath("//body").send_keys(Keys.CONTROL + 't')
        driver.switch_to_window(main_window)  # the same one the driver is focused on!
        time.sleep(1)
    elif driver.name == 'chrome':
        old_handles = set(driver.window_handles)
        driver.find_element_by_xpath("//body").send_keys(Keys.CONTROL + 't')
        new_handles = set(driver.window_handles)
        new = new_handles.difference(old_handles).pop()
        driver.switch_to.window(new)
        time.sleep(1)
    else:
        return
    log(INFO, "Opened new tab.")


def change_tab(driver):
    """Change tabs. Not guaranteed to move to the 'expected' next tab!

       The behavior of this function is browser dependent, and it is recommended
       that 'assert_tab' be used instead.
        - 'driver' should be a Selenium WebDriver, currently Chrome and Firefox
          are supported.
    """
    if driver.name == 'firefox':
        main_window = driver.current_window_handle  # Hack to make currently displayed tab
        driver.find_element_by_xpath("//body").send_keys(Keys.CONTROL + Keys.TAB)
        time.sleep(0.5)
        driver.switch_to_window(main_window)  # the same one the driver is focused on!
        url = driver.current_url
        time.sleep(0.5)
    elif driver.name == 'chrome':
        handles = driver.window_handles
        if len(handles) > 1:
            current_handle = driver.current_window_handle
            pos = handles.index(current_handle) + 1
            pos = pos % len(handles)
            driver.switch_to.window(handles[pos])
            time.sleep(0.5)
            driver.get_screenshot_as_base64()  # Awful hack to make current focused tab the one displayed!
            time.sleep(0.5)
        url = driver.current_url
    else:
        return
    log(INFO, "Changed tab to %s." % url)


def close_tab(driver):
    """Close the current tab. Not guaranteed to move the focus to 'expected' tab.

       The behavior of this function is browser dependent; do not rely on closing
       a tab leaving the focus on the tab to the left unless there is only one tab
       left open. Use 'assert_tab' to move to the tab desired after this function
       is called.
        - 'driver' should be a Selenium Webdriver, currently Chrome and Firefox
          are supported.
    """
    if driver.name == 'firefox':
        main_window = driver.current_window_handle  # Hack to make currently displayed tab
        old_url = driver.current_url
        driver.find_element_by_xpath("//body").send_keys(Keys.CONTROL + 'w')
        time.sleep(0.5)
        driver.switch_to_window(main_window)  # the same one the driver is focused on!
        new_url = driver.current_url
        time.sleep(0.5)
    elif driver.name == 'chrome':
        old_url = driver.current_url
        driver.find_element_by_xpath("//body").send_keys(Keys.CONTROL + 'w')
        time.sleep(0.5)
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(0.5)
        driver.get_screenshot_as_base64()  # Awful hack to make current focused tab the one displayed!
        time.sleep(0.5)
        new_url = driver.current_url
    else:
        return
    log(INFO, "Closed tab %s. Now on %s" % (old_url, new_url))


def assert_tab(driver, url_part):
    """Ensure that the browser is focused on a specific tab. Requires unique urls for each tab!

       This function should be used to ensure the browser is focused on the expected
       tab after closing a tab, and should be used in place of 'change_tab' wherever
       a tab change is required.
        - 'driver' should be a Selenium WebDriver, currently Chrome and Firefox
          are supported.
        - 'url_part' should be a string of the url (or a subsection of it) of the tab
          the driver focus should be moved to if necessary.
    """
    log(INFO, "AssertTab: Changing to tab with url containing '%s'." % url_part)
    urls = [driver.current_url]
    if url_part in urls[0]:
        return
    else:
        while not any(url_part in u for u in urls):
            change_tab(driver)
            time.sleep(1)
            current_url = driver.current_url
            if current_url in urls:
                log(ERROR, "AssertTab: Couldn't reach required tab with url containing '%s'!" % url_part)
                raise AssertTabError("AssertTab: Couldn't reach required tab with url containing '%s'!" % url_part)
            urls.append(current_url)


def wait_for_xpath_element(driver, element, duration=10, visible=True):
    """Wait for an element on the page to become visible.

       Ensure an element on the page is visible before continuing; will raise a
       'TimeoutException' if the element does not become visible before the end
       of the duration.
        - 'driver' should be a Selenium WebDriver.
        - 'element' should be the XPATH of the element to wait for.
        - 'duration' is how long to wait before raising a 'TimeoutException'.
        - 'visible' is an optional boolean flag to ensure the element is visible
          on the page. If it is 'False', then the element only needs to be in the
          code of the page, not necessarily visible or able to be interacted with.
    """
    if visible:
        return WebDriverWait(driver, duration).until(EC.visibility_of_element_located((By.XPATH, element)))
    else:
        return WebDriverWait(driver, duration).until(EC.presence_of_element_located((By.XPATH, element)))


def wait_for_invisible_xpath(driver, element, duration=10):
    """Wait for an element on the page to become invisible.

       Ensure an element on the page is invisble before continuing; will raise a
       'TimeoutException' if the element does not become invisible before the end
       of the duration.
        - 'driver' should be a Selenium WebDriver.
        - 'element' should be the XPATH of the element to wait for.
        - 'duration' is how long to wait before raising a 'TimeoutException'.
    """
    return WebDriverWait(driver, duration).until(EC.invisibility_of_element_located((By.XPATH, element)))


def save_element_html(element, fname):
    """Save the HTML of a WebDriver element to file.

       Get the HTML of an element and save it to file.
        - 'element' should be a WebDriver element.
        - 'fname' should the the string filename to save the HTML to, '.html' is
          automatically appended.
    """
    element_html = str(element.get_attribute('innerHTML'))
    with open(fname, "w") as f:
        f.write(element_html)
    log(INFO, "Saved element HTML as '%s'." % fname)


def image_div(driver, fname, div_element=None):
    """Save a png of the div element specified, or the whole page.

       Save an image of the whole page, unless a 'div_element' is specified, in
       which case attempt to image it.
        - 'driver' should be a Selenium WebDriver.
        - 'fname' should the the string filename to save the png to, '.png' is
          automatically appended.
        - 'div_element' is the WebDriver element to image. Recommended to be a div element,
          since these have reliable heights and widths. If the element has no
          height or width, save the whole screen.
    """
    fname += ".png"
    driver.save_screenshot(fname)
    if div_element is None:
        log(INFO, "Saved image '%s'." % fname)
        return
    div_loc = div_element.location
    div_size = div_element.size
    l, t = int(div_loc['x']), int(div_loc['y'])
    r, b = int(l + div_size['width']), int(t + div_size['height'] - 1)
    if (l == r) or (t == b):
        log(INFO, "Element had no size. Saving whole screen")
        return
    image = Image.open(fname)
    image = image.crop((l, t, r, b))
    image.save(fname)
    log(INFO, "Saved image '%s'." % fname)
