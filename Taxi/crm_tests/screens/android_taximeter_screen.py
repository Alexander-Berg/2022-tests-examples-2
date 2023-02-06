from selenium.webdriver.common.by import By
from screens.base_mobile_screen import BaseMobileScreen
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import NoSuchElementException


class AndroidTaximeterScreen(BaseMobileScreen):
    CONTINUE_BUTTON = By.ID, 'ru.yandex.taximeter:id/button_sign_up'
    PHONE_INPUT = By.ID, 'ru.yandex.taximeter:id/edit_text_view_input_view'
    LOGIN_BUTTON = By.ID, 'ru.yandex.taximeter:id/button_confirm_phone'
    CONTENT = By.ID, 'ru.yandex.taximeter:id/content_base'
    ERROR_SCREEN = By.ID, 'ru.yandex.taximeter:id/screen_non_fatal_error_recycler_view'
    NEWSFEED_BUTTON = By.ID, 'ru.yandex.taximeter:id/image_view_icon'
    NEWSCARD = By.ID, 'ru.yandex.taximeter:id/news_card'
    NEWSCARD_TITLE = By.ID, 'ru.yandex.taximeter:id/tv_news_title'
    NEWSCARD_BODY = By.ID, 'ru.yandex.taximeter:id/tv_news_body'
    OFFLINE_BUTTON = By.ID, 'ru.yandex.taximeter:id/goOfflineBtnGroup'
    GO_ONLINE_BUTTON = By.ID, 'ru.yandex.taximeter:id/go_online_button'
    ACTION_BUTTON = By.ID, 'ru.yandex.taximeter:id/action_button'
    PARK_ITEM = By.ID, 'ru.yandex.taximeter:id/title'
    PROCEED_BUTTON = By.ID, 'ru.yandex.taximeter:id/primary_action_button'

    def is_logged_in(self):
        try:
            self.wait_for_logged_in()
            return True
        except NoSuchElementException:
            return False

    def wait_for_logged_in(self):
        self.wait_for_element(self.OFFLINE_BUTTON, timeout=30)

    def click_continue(self, timeout=30):
        try:
            continue_button = self.wait_for_element(self.CONTINUE_BUTTON, timeout)
        except NoSuchElementException:
            return
        continue_button.click()

    def click_understand(self, timeout=30):
        try:
            continue_button = self.wait_for_element(self.ACTION_BUTTON, timeout)
        except NoSuchElementException:
            return
        continue_button.click()

    def choose_park(self, park_name='Sea bream', timeout=30):
        try:
            park_item = self.wait_for_element(self.PARK_ITEM, timeout)
            if park_item.text == park_name:
                park_item.click()
                continue_button = self.wait_for_element(self.PROCEED_BUTTON)
                continue_button.click()
            else:
                raise NoSuchElementException
        except NoSuchElementException:
            return

    def input_phone(self, phone):
        self.input_field(self.PHONE_INPUT, phone)

    def click_login(self):
        login_button = self.wait_for_element(self.LOGIN_BUTTON)
        login_button.click()

    def close_debug_drawer(self):
        content = self.wait_for_element(self.CONTENT)
        TouchAction(self.driver).tap(content, 0, 200).perform()

    def touch_screen(self):
        content = self.wait_for_element(self.CONTENT)
        TouchAction(self.driver).tap(content, 200, 200).perform()

    def close_error_screen(self):
        self.wait_for_element(self.ERROR_SCREEN)
        self.driver.back()

    def is_error_screen_present(self):
        return self.is_element_present(self.ERROR_SCREEN)
