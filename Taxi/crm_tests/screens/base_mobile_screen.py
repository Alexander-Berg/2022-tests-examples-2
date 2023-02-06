import allure
import time

from allure_commons.types import AttachmentType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC


class BaseMobileScreen:
    DISMISS_NOTIFICATIONS = By.ID, 'com.android.systemui:id/dismiss_text'
    CLEAR_NOTIFICATIONS = By.ID, 'com.android.systemui:id/clear_all_button'
    PUSH_TITLE = By.ID, 'android:id/title'
    PUSH_TEXT = By.ID, 'android:id/big_text'
    NOTIFICATION_PANEL = By.ID, 'com.android.systemui:id/notification_stack_scroller'
    NOTIFICATION = By.CLASS_NAME, 'android.widget.FrameLayout'

    def __init__(self, driver):
        self.driver = driver
    '''
    Interactions
    '''

    def input_field(self, locator, text):
        field = self.wait_for_element(locator)
        field.clear()
        field.send_keys(text)

    '''
    Getters
    '''
    def get_element(self, locator):
        return self.driver.find_element(*locator)

    def get_elements(self, locator):
        return self.driver.find_elements(*locator)

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
            self.attach_allure_screenshot(f'no_element_{locator[1]}')
            raise NoSuchElementException(f"Cannot find element {locator}")
        return el

    def wait_for_elements(self, locator, timeout=15):
        try:
            els = WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located(locator))
        except TimeoutException:
            print("Cannot find elements {} {}".format(locator[0], locator[1]))
            self.attach_allure_screenshot(f'no_elements_{locator[1]}')
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
            sc = self.get_screenshot()
            allure.attach(sc, 'no_text', AttachmentType.PNG)
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
            self.attach_allure_screenshot(f'no_element_{locator[1]}')
            raise NoSuchElementException(f"Cannot find element {locator}")
        return el

    def wait_for_element_to_disappear(self, locator, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until_not(EC.visibility_of_element_located(locator))
        except TimeoutException:
            print("Element is still visible")
            self.attach_allure_screenshot(f'still_present_element_{locator[1]}')
            return

    '''
    Screenshots
    '''
    def get_screenshot(self):
        return self.driver.get_screenshot_as_png()

    def attach_allure_screenshot(self, filename):
        sc = self.get_screenshot()
        allure.attach(sc, 'choose_enter_phone', AttachmentType.PNG)

    '''
    Notifications
    '''
    def open_notification_panel(self):
        self.driver.open_notifications()
        time.sleep(3)

    def clear_notifications(self):
        time.sleep(2)
        if self.is_not_element_present(self.CLEAR_NOTIFICATIONS) and self.is_not_element_present(self.DISMISS_NOTIFICATIONS):
            screen_size = self.driver.get_window_size()
            screen_width = screen_size["width"]
            screen_height = screen_size["height"]
            x1 = screen_width / 2
            y1 = screen_height * 0.8
            x2 = screen_width / 2
            y2 = screen_height * 0.2
            tries = 3
            while self.is_not_element_present(self.CLEAR_NOTIFICATIONS) and \
                    self.is_not_element_present(self.DISMISS_NOTIFICATIONS) and tries >= 0:
                if self.is_not_element_present(self.CLEAR_NOTIFICATIONS) and \
                        self.is_not_element_present(self.DISMISS_NOTIFICATIONS):
                    self.driver.swipe(x1, y1, x2, y2, 200)
                    tries -= 1
        if self.is_element_present(self.CLEAR_NOTIFICATIONS):
            clear_button = self.wait_for_element(self.CLEAR_NOTIFICATIONS)
            clear_button.click()
        elif self.is_element_present(self.DISMISS_NOTIFICATIONS):
            dismiss_button = self.wait_for_element(self.DISMISS_NOTIFICATIONS)
            dismiss_button.click()
        else:
            sc = self.get_screenshot()
            allure.attach(sc, 'no_clean_notification_button', AttachmentType.PNG)
            raise NoSuchElementException("Cannot clean notifications.")

    def close_notification_panel(self):
        self.driver.back()

    def get_notification_texts(self):
        notifications = self.driver.find_elements(*self.PUSH_TEXT)
        texts = []
        for n in notifications:
            texts.append(n.text)
        return texts

    def is_expected_text_in_texts(self, expected_text, texts):
        for text in texts:
            if text.startswith(expected_text):
                return True
        return False

    def wait_for_notification_with_text(self, expected_text, match_type="full", timeout=3600):  # подумать какой таймаут поставить
        time.sleep(5)
        initial_timeout = timeout
        notification_texts = self.get_notification_texts()
        timeout_to_check = 10
        if match_type == "starts_with":
            # тут будем проверять что текст нотификации только начинается на заданную строку,
            # так как при тестировании может прийти любая строка из сегмента
            # а в конце expected_text будет стоять цифра, относящаяся к конкретному пользователю
            expected_text = expected_text[:-1]
            while (not self.is_expected_text_in_texts(expected_text, notification_texts)) and (timeout >= 0):
                time.sleep(timeout_to_check)
                timeout -= timeout_to_check
                notification_texts = self.get_notification_texts()
        elif match_type == "full":
            while (expected_text not in notification_texts) and (timeout >= 0):
                time.sleep(timeout_to_check)
                timeout -= timeout_to_check
                notification_texts = self.get_notification_texts()
        if timeout <= 0:
            sc = self.get_screenshot()
            allure.attach(sc, 'no_notification', AttachmentType.PNG)
            raise TimeoutError(f"Waited for notification with: '{expected_text} for {initial_timeout} seconds, "
                               f"but it does not appear.")
