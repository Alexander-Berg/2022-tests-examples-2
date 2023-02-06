import re
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class BaseScreen:
    def __init__(self, driver, url):
        self.driver = driver
        self.url = url

    '''
    Interactions
    '''
    def open(self):
        self.driver.get(self.url)

    def input_field(self, locator, text):
        field = self.wait_for_element(locator)
        field.clear()
        field.send_keys(text)

    def close_tab(self):
        old_window = self.driver.window_handles[0]
        self.driver.close()
        self.driver.switch_to.window(old_window)

    def refresh(self):
        self.driver.refresh()
        time.sleep(5)

    def clear_value(self, field_el):
        text_len = len(field_el.get_attribute("value"))
        field_el.send_keys(Keys.END)
        for l in range(text_len):
            field_el.send_keys(Keys.BACKSPACE)

    def take_screenshot(self, filename):
        file_name = 'screenshot.png'
        self.driver.save_screenshot(file_name)

    '''
    Getters
    '''
    def get_element(self, locator):
        return self.driver.find_element(*locator)

    def get_elements(self, locator):
        return self.driver.find_elements(*locator)

    def get_campaign_id(self):
        current_url = self.driver.current_url
        id = re.compile(r"(\d{4})")
        return int(id.search(current_url).group(0))

    '''
    Checks
    '''
    def is_element_present(self, locator):
        try:
            self.driver.find_element(*locator)
        except NoSuchElementException:
            return False
        return True

    def is_not_element_present(self, locator, timeout=3):
        self.driver.implicitly_wait(0)
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
        except TimeoutException:
            self.driver.implicitly_wait(5)
            return True
        self.driver.implicitly_wait(5)
        return False

    def are_elements_present(self, locator):
        try:
            self.driver.find_elements(*locator)
        except NoSuchElementException:
            return False
        return True

    def is_element_clickable(self, locator, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(*locator))
        except TimeoutException:
            return False
        return True

    def is_not_element_clickable(self, locator, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until_not(EC.element_to_be_clickable(locator))
        except TimeoutException:
            return False
        return True

    '''
    Waits
    '''
    def wait_for_element(self, locator, timeout=15):
        try:
            el = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
        except TimeoutException:
            print("Cannot find element {} {}".format(locator[0], locator[1]))
            raise NoSuchElementException(f"Cannot find element {locator}")
        return el

    def wait_for_elements(self, locator, timeout=15):
        try:
            els = WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located(locator))
        except TimeoutException:
            print("Cannot find elements {} {}".format(locator[0], locator[1]))
            raise NoSuchElementException(f"Cannot find elements {locator}")
        return els

    def wait_for_element_to_be_clickable(self, locator, timeout=15):
        try:
            el = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            print("Cannot find elements {} {}".format(locator[0], locator[1]))
            raise NoSuchElementException(f"Cannot find element {locator}")
        return el

    def wait_for_text(self, locator, text, timeout=15):
        try:
            WebDriverWait(self.driver, timeout).until(EC.text_to_be_present_in_element(locator, text))
        except TimeoutException:
            print("Cannot find elements {} {}".format(locator[0], locator[1]))
            raise NoSuchElementException(f"Cannot find element {locator} with text '{text}'")
        return self.driver.find_element(*locator)

    def wait_for_element_not_to_be_clickable(self, locator, timeout=15):
        try:
            el = WebDriverWait(self.driver, timeout).until_not(EC.element_to_be_clickable(locator))
        except TimeoutException:
            print("Cannot find elements {} {}".format(locator[0], locator[1]))
            return
        return el

    def wait_for_element_to_be_visible(self, locator, timeout=15):
        try:
            el = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            print("Cannot find element {} {}".format(locator[0], locator[1]))
            raise NoSuchElementException(f"Cannot find element {locator}")
        return el

    def wait_for_element_to_disappear(self, locator, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until_not(EC.visibility_of_element_located(locator))
        except TimeoutException:
            print("Element is still visible")
            return
