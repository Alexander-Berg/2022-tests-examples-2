import allure
import time

from allure_commons.types import AttachmentType
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from screens.base_mobile_screen import BaseMobileScreen


class AndroidGoScreen(BaseMobileScreen):
    GDPR_AGREE_BUTTON = By.ID, 'ru.yandex.taxi.develop:id/gdpr_confirm_done'
    MENU_BUTTON = By.ID, "ru.yandex.taxi.develop:id/menu_button"
    BANNER_VIEW = By.ID, "ru.yandex.taxi.develop:id/banner_pager"
    CLOSE_BANNER = By.ID, "ru.yandex.taxi.develop:id/close"
    ENTER_PHONE_ITEM = By.ID, "ru.yandex.taxi.develop:id/enter_phone"
    ENTER_YANDEX = By.XPATH, "(//android.view.View/android.widget.Button)[2]"
    # LOGIN_FIELD = By.ID, "passp-field-login"
    LOGIN_FIELD = By.CLASS_NAME, 'android.widget.EditText'
    # PASSWORD_FIELD = By.ID, "passp-field-passwd"
    PASSWORD_FIELD = By.XPATH, "(//android.view.View/android.widget.EditText)[1]"
    # SIGN_IN_BUTTON = By.ID, "passp:sign-in"
    SIGN_IN_BUTTON = By.XPATH, "(//android.view.View/android.widget.Button)[1]"
    ENTER_BUTTON = By.XPATH, "(//android.view.View/android.widget.Button)[2]"
    EXISTING_ACCOUNT_ITEM = By.ID, "ru.yandex.taxi.develop:id/recycler"
    ADD_NEW_ACCOUNT = By.ID, "ru.yandex.taxi.develop:id/button_other_account_multiple_mode"
    USER_ITEM_IN_MENU = By.ID, "ru.yandex.taxi.develop:id/auth"
    CHANGE_ADDRESS = By.ID, "ru.yandex.taxi.develop:id/nearest_change_address_button"
    INPUT_ADDRESS = By.ID, "ru.yandex.taxi.develop:id/component_list_item_input"
    ADDRESS_SUGGESTIONS = By.ID, "ru.yandex.taxi.develop:id/center"

    def gdpr_accept(self):
        try:
            btn = self.wait_for_element(self.GDPR_AGREE_BUTTON, timeout=60)
            btn.click()
            self.wait_for_element_to_disappear(self.GDPR_AGREE_BUTTON, timeout=60)
        except Exception:
            pass

    def set_location(self, latitude=37, longitude=56):
        self.driver.set_location(latitude, longitude)
        time.sleep(15)

    def open_menu(self):
        btn = self.wait_for_element(self.MENU_BUTTON, timeout=30)
        btn.click()

    def close_banner(self):
        try:
            self.wait_for_element(self.BANNER_VIEW, timeout=30)  # wait for banner
            sc = self.get_screenshot()
            allure.attach(sc, 'banner_opened', AttachmentType.PNG)
            close_banner = self.wait_for_element(self.CLOSE_BANNER)
            close_banner.click()
            time.sleep(5)
        except Exception:
            pass

    def choose_enter_phone(self):
        btn = self.wait_for_element(self.ENTER_PHONE_ITEM, timeout=30)
        btn.click()

    def choose_enter_through_yandex_id(self):
        btn = self.wait_for_element(self.ENTER_YANDEX, timeout=30)
        btn.click()

    def input_login(self, email):
        time.sleep(5)
        self.wait_for_element(self.LOGIN_FIELD, timeout=30)
        self.input_field(self.LOGIN_FIELD, email)

    def click_sign_in(self):
        btn = self.wait_for_element(self.SIGN_IN_BUTTON, timeout=30)
        btn.click()

    def click_enter(self):
        btn = self.wait_for_element(self.ENTER_BUTTON, timeout=30)
        btn.click()

    def input_password(self, password):
        time.sleep(5)
        self.wait_for_element(self.PASSWORD_FIELD, timeout=30)
        self.input_field(self.PASSWORD_FIELD, password)

    def click_existing_account(self):
        btn = self.wait_for_element(self.EXISTING_ACCOUNT_ITEM, timeout=30)
        btn.click()

    def wait_for_authenticated(self):
        self.wait_for_element_to_be_visible(self.USER_ITEM_IN_MENU, timeout=120)

    def is_user_logged_in(self):
        try:
            self.wait_for_element_to_be_visible(self.USER_ITEM_IN_MENU, timeout=120)
            return True
        except NoSuchElementException:
            return False

    def log_into_yandex_id(self, login, password):
        time.sleep(30)
        sc = self.get_screenshot()
        allure.attach(sc, 'opened_web_yandex_id', AttachmentType.PNG)
        if self.is_element_present(self.ENTER_YANDEX):
            self.choose_enter_through_yandex_id()
            self.attach_allure_screenshot('choose_enter_through_yandex_id')
            self.input_login(login)
            self.click_sign_in()
            self.input_password(password)
            self.click_enter()
            self.attach_allure_screenshot('trying_to_login')
        elif self.is_element_present(self.EXISTING_ACCOUNT_ITEM):
            self.click_existing_account()
            self.attach_allure_screenshot('click_existing_account')
        else:
            # self.wait_for_element(self.ENTER_YANDEX, timeout=1200)
            self.attach_allure_screenshot('No_controls')
            raise Exception("No controls for authorization.")

    def click_change_address(self):
        btn = self.wait_for_element(self.CHANGE_ADDRESS)
        btn.click()
        time.sleep(2)

    def input_address(self, address="Москва-сити"):
        self.wait_for_element(self.INPUT_ADDRESS, timeout=20)
        self.input_field(self.INPUT_ADDRESS, address)
        time.sleep(2)

    def choose_address_suggestion(self):
        time.sleep(3)
        suggestions = self.wait_for_elements(self.ADDRESS_SUGGESTIONS)
        suggestions[0].click()
        time.sleep(2)

    def change_address(self):
        time.sleep(5)
        if self.is_element_present(self.CHANGE_ADDRESS):
            self.click_change_address()
            self.input_address()
            self.choose_address_suggestion()
            time.sleep(20)
            self.attach_allure_screenshot('address_changed')
