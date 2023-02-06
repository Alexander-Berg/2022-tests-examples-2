import time
from screens.base_screen import BaseScreen
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


class SendSettingsScreen(BaseScreen):
    TEST_USERS_INPUT = By.CSS_SELECTOR, 'input#test_users'
    GROUP_EDIT = By.CSS_SELECTOR, 'svg[data-icon=edit]'
    GROUP_CHECKBOX = By.CSS_SELECTOR, '.ant-checkbox-input'
    GROUP_CARD = By.CSS_SELECTOR, '.ant-card'
    GROUP_TEST = By.CSS_SELECTOR, 'svg[data-icon=right-square]'
    GROUP_SEND = By.CSS_SELECTOR, 'svg[data-icon=send]'
    CANCEL_EDIT_GROUP = By.CSS_SELECTOR, 'svg[data-icon=close]'
    ACCEPT_EDIT_GROUP = By.CSS_SELECTOR, 'svg[data-icon=check]'
    FIELD_WITH_DROPDOWN = By.CSS_SELECTOR, '.ant-select-selector'
    DROPDOWN = By.CSS_SELECTOR, '.ant-select-dropdown'
    NEWSFEED_ID_FIELD = By.CSS_SELECTOR, '[data-testid="feed_id_input"]'
    EXISTING_ID_LINK = By.XPATH, '//div/a[starts-with(@href, "https://tariff-editor.taxi.tst.yandex-team.ru")]'
    CREATE_NEW_ID_LINK = By.CSS_SELECTOR, '[data-testid="create_feed_link"]'
    DROPDOWN_ITEM = By.CSS_SELECTOR, '.ant-select-dropdown .ant-select-item'
    NEWSFEED_POPOVER = By.CSS_SELECTOR, '.ant-popover-inner-content'
    COPY_NEWSFEED_BUTTON = By.XPATH, '//input[@value="copy"]/../..'
    NEW_NEWSFEED_BUTTON = By.XPATH, '//input[@value="new"]/../..'
    CREATE_NEWSFEED_BUTTON = By.CSS_SELECTOR, '[data-testid="create_feed_button"]'
    DAYS_TO_SHOW_FIELD = By.CSS_SELECTOR, 'input[name=days_count]'
    CHOOSE_TIME_TO_END = By.CSS_SELECTOR, 'input[name=time_until]'
    TIME_PICKER_OK_BUTTON = By.CSS_SELECTOR, '.ant-picker-ok button'
    TIME_PICKER_PANEL = By.CSS_SELECTOR, '.ant-picker-panel'
    NOTIFICATION_CONTENT = By.CSS_SELECTOR, 'textarea[name=content]'
    TEST_BUTTON = By.CSS_SELECTOR, '[data-testid="group_settings_test_button"]'
    STOP_TEST_BUTTON = By.CSS_SELECTOR, '[data-testid="group_settings_stop_test_send_button"]'
    SEND_FOR_FINAL_APPROVAL_BUTTON = By.CSS_SELECTOR, '[data-testid="group_settings_submit_for_approval_button"]'
    BACK_BUTTON = By.CSS_SELECTOR, '[data-testid="group_settings_back_link"]'
    SEND_OR_SCHEDULE_BUTTON = By.CSS_SELECTOR, '[data-testid="group_settings_send_button"]'
    FINAL_SEND_POPOVER = By.CSS_SELECTOR, '.ant-popconfirm'
    FINAL_SEND_POPOVER_NO = By.XPATH, '//button[contains(@class, "ant-btn-sm") and not(contains(@class, "ant-btn-primary"))]'  # By.XPATH, '//button/span[text()="Нет"]'
    FINAL_SEND_POPOVER_YES = By.CSS_SELECTOR, '.ant-btn-sm.ant-btn-primary'  # By.XPATH, '//button/span[text()="Да"]'
    HEADER = By.CSS_SELECTOR, 'header'
    CLOSE_NOTIFICATION_BUTTON = By.CSS_SELECTOR, 'svg[data-icon=close]'
    SCHEDULE_TAB = By.CSS_SELECTOR, 'div.ant-tabs-tab:nth-child(3)'
    TEST_USERS_TAB = By.CSS_SELECTOR, 'div.ant-tabs-tab:nth-child(1)'
    SCHEDULE_INPUT = By.XPATH, '//input[@type="text"]'
    EFFICIENCY_START_DATE = By.XPATH, '(//div[@name="efficiency_date_range"]//input)[1]'
    EFFICIENCY_END_DATE = By.XPATH, '(//div[@name="efficiency_date_range"]//input)[2]'
    DATE_PICKER_OK_BUTTON = By.CSS_SELECTOR, '.ant-picker-ok button'
    SAVE_SCHEDULE_BUTTON = By.CSS_SELECTOR, '[data-testid="save_schedule_button"]'
    CLEAR_SCHEDULE_BUTTON = By.CSS_SELECTOR, 'button.react-js-cron-clear-button'

    def __init__(self, driver, url, campaign_id):
        self.driver = driver
        self.url = url + f'/{campaign_id}/send-settings'

    '''
    Waits
    '''
    def wait_for_send_settings_open(self):
        self.wait_for_element_to_be_visible(self.TEST_USERS_INPUT)

    def wait_for_popover(self):
        self.wait_for_element_to_be_visible(self.FINAL_SEND_POPOVER)

    '''
    Getters
    '''
    def get_group_with_name(self, name):
        groups = self.wait_for_elements(self.GROUP_CARD)
        for group in groups:
            if name in group.text:
                return group
        raise NoSuchElementException(f"No group with name {name}")

    '''
    Interactions
    '''
    def edit_group_with_name(self, group_name):
        group = self.get_group_with_name(group_name)
        self.edit_group(group)

    def test_group_with_name(self, group_name):
        time.sleep(1)
        group = self.get_group_with_name(group_name)
        send_button = group.find_element(*self.GROUP_TEST)
        send_button.click()

    def edit_group(self, group_el):
        edit_button = group_el.find_element(*self.GROUP_EDIT)
        edit_button.click()

    def choose_channel(self, group_el, channel):
        channel_selector = group_el.find_element(*self.FIELD_WITH_DROPDOWN)
        channel_selector.click()
        self.wait_for_element(self.DROPDOWN)
        time.sleep(0.5)
        dropdown_items = self.wait_for_elements(self.DROPDOWN_ITEM)
        for item in dropdown_items:
            if item.text == channel:
                item.click()
                return
        raise NoSuchElementException(f"No such channel {channel}")

    def choose_creative(self, group_el, creative_name):
        creative_selector = group_el.find_element(*self.FIELD_WITH_DROPDOWN)
        creative_selector.click()
        self.wait_for_element(self.DROPDOWN)
        time.sleep(0.5)
        dropdown_items = self.wait_for_elements(self.DROPDOWN_ITEM)
        for item in dropdown_items:
            if item.text == creative_name:
                item.click()
                return
        raise NoSuchElementException(f"No such creative {creative_name}")

    def set_newsfeed_id_copy(self, newsfeed_id):
        time.sleep(0.5)
        newsfeed_id_link = self.wait_for_element(self.CREATE_NEW_ID_LINK)
        newsfeed_id_link.click()
        self.wait_for_element_to_be_visible(self.NEWSFEED_POPOVER)
        copy_newsfeed = self.wait_for_element(self.COPY_NEWSFEED_BUTTON)
        copy_newsfeed.click()
        self.input_field(self.NEWSFEED_ID_FIELD, newsfeed_id)
        create_button = self.wait_for_element(self.CREATE_NEWSFEED_BUTTON)
        create_button.click()

    def set_days_to_show(self, days_to_show):
        days_to_show_field = self.wait_for_element(self.DAYS_TO_SHOW_FIELD)
        self.clear_value(days_to_show_field)
        self.input_field(self.DAYS_TO_SHOW_FIELD, days_to_show)

    def set_time_to_end(self, time_to_end):
        time_to_end_field = self.wait_for_element(self.CHOOSE_TIME_TO_END)
        time_to_end_field.click()
        self.clear_value(time_to_end_field)
        self.input_field(self.CHOOSE_TIME_TO_END, time_to_end)
        self.wait_for_element(self.TIME_PICKER_OK_BUTTON).click()
        self.wait_for_element_to_disappear(self.TIME_PICKER_PANEL)

    def set_notification_content(self, content):
        content_field = self.wait_for_element(self.NOTIFICATION_CONTENT)
        self.clear_value(content_field)
        self.input_field(self.NOTIFICATION_CONTENT, content)

    def accept_group_settings(self):
        accept_button = self.wait_for_element(self.ACCEPT_EDIT_GROUP)
        accept_button.click()

    def set_newsfeed_settings(self, group_name, newsfeed_id=None, days_to_show=1, time_to_end="23:59"):
        group = self.get_group_with_name(group_name)
        self.edit_group(group)
        self.choose_channel(group, "Лента")
        if newsfeed_id:
            self.set_newsfeed_id_copy(newsfeed_id)
        else:
            raise NotImplementedError
        self.set_days_to_show(days_to_show)
        self.set_time_to_end(time_to_end)
        self.accept_group_settings()

    def set_no_send_settings(self, group_name):
        group = self.get_group_with_name(group_name)
        self.edit_group(group)
        self.choose_channel(group, "НЕ ОТПРАВЛЯТЬ")
        self.accept_group_settings()

    def set_promo_notification_settings(self, group_name, content, days_to_show=1, time_to_end="23:59"):
        group = self.get_group_with_name(group_name)
        self.edit_group(group)
        self.choose_channel(group, "PROMO_NOTIFICATION")
        self.set_notification_content(content)
        self.set_days_to_show(days_to_show)
        self.set_time_to_end(time_to_end)
        self.accept_group_settings()

    def set_push_settings(self, audience, group_name, content, title=None, link=None, comm_start=None,
                          comm_end=None, code=None, button_name=None, system_push=True, delayed_send=False):
        group = self.get_group_with_name(group_name)
        self.edit_group(group)
        self.choose_channel(group, "PUSH")
        if audience == 'User' or audience == 'EatsUser' or audience == 'Driver' or audience == 'LavkaUser' or audience == 'GeoServices':
            # TODO: сделать заполнение всех полей для разных аудиторий.
            pass
        else:
            raise NameError(f"No such audience: {audience}")
        self.set_notification_content(content)
        self.accept_group_settings()

    def set_creative(self, group_name, creative_name):
        group = self.get_group_with_name(group_name)
        self.edit_group(group)
        self.choose_creative(group, creative_name)
        self.accept_group_settings()

    def select_test_users(self, test_user):
        test_users_field = self.wait_for_element(self.TEST_USERS_INPUT)
        test_users_field.click()
        self.wait_for_element_to_be_visible(self.DROPDOWN)
        self.input_field(self.TEST_USERS_INPUT, test_user)
        items = self.wait_for_elements(self.DROPDOWN_ITEM)
        for item in items:
            if item.text == test_user:
                item.click()
                self.wait_for_element(self.HEADER).click()
                return
        raise NoSuchElementException("No such test user")

    def click_test_groups_button(self):
        test_groups_button = self.wait_for_element(self.TEST_BUTTON)
        test_groups_button.click()

    def click_send_for_final_approval_button(self):
        send_for_final_approval_button = self.wait_for_element(self.SEND_FOR_FINAL_APPROVAL_BUTTON)
        send_for_final_approval_button.click()

    def click_back_button(self):
        back_button = self.wait_for_element(self.BACK_BUTTON)
        back_button.click()

    def close_notification(self):
        close_button = self.wait_for_element(self.CLOSE_NOTIFICATION_BUTTON)
        close_button.click()

    def click_checkbox_for_group(self, group_name):
        group = self.get_group_with_name(group_name)
        checkbox = group.find_element(*self.GROUP_CHECKBOX)
        checkbox.click()
        time.sleep(1)

    def click_send_or_schedule_button(self):
        button = self.wait_for_element(self.SEND_OR_SCHEDULE_BUTTON)
        button.click()

    def click_yes_in_popover(self):
        self.wait_for_popover()
        yes_button = self.wait_for_element(self.FINAL_SEND_POPOVER_YES)
        yes_button.click()

    def click_no_in_popover(self):
        self.wait_for_popover()
        yes_button = self.wait_for_element(self.FINAL_SEND_POPOVER_NO)
        yes_button.click()

    def open_schedule_tab(self):
        schedule_tab = self.wait_for_element(self.SCHEDULE_TAB)
        schedule_tab.click()

    def open_test_user_tab(self):
        test_users_tab = self.wait_for_element(self.TEST_USERS_TAB)
        test_users_tab.click()

    def input_cron_schedule(self, cron_str):
        self.click_clear_schedule()
        self.input_field(self.SCHEDULE_INPUT, cron_str)

    def input_cron_schedule_and_save(self, cron_str):
        self.input_cron_schedule(cron_str)
        self.click_save_schedule()

    def click_save_schedule(self):
        save_button = self.wait_for_element(self.SAVE_SCHEDULE_BUTTON)
        save_button.click()

    def click_clear_schedule(self):
        clear_button = self.wait_for_element(self.CLEAR_SCHEDULE_BUTTON)
        clear_button.click()

    def input_date(self, date_time, field):
        time.sleep(0.5)
        if field == 'start':
            start_date_field = self.wait_for_element(self.EFFICIENCY_START_DATE)
            start_date_field.click()
            self.clear_value(start_date_field)
            self.input_field(self.EFFICIENCY_START_DATE, date_time)
            self.wait_for_element(self.DATE_PICKER_OK_BUTTON).click()
        if field == 'end':
            end_date_field = self.wait_for_element(self.EFFICIENCY_END_DATE)
            end_date_field.click()
            self.clear_value(end_date_field)
            self.input_field(self.EFFICIENCY_END_DATE, date_time)
            self.wait_for_element(self.DATE_PICKER_OK_BUTTON).click()
