import time
from screens.base_screen import BaseScreen
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


class CreativeScreen(BaseScreen):
    CREATE_BUTTON = By.CSS_SELECTOR, '[data-testid="create_creative_link"]'
    NAME_FIELD = By.CSS_SELECTOR, 'input[name=name]'
    FIELD_WITH_DROPDOWN = By.CSS_SELECTOR, '.ant-select-selector'
    CHANNEL_SELECTOR = By.CSS_SELECTOR, 'span.ant-select-selection-item'  # By.CSS_SELECTOR, '[name=channel] input'
    DROPDOWN = By.CSS_SELECTOR, '.ant-select-dropdown'
    DROPDOWN_ITEM = By.CSS_SELECTOR, '.ant-select-dropdown .ant-select-item'
    TEXT_INPUT = By.CSS_SELECTOR, '[name="channel_params.content"]'
    PUSH_ID_INPUT = By.CSS_SELECTOR, '[name="channel_params.push_id"]'
    DAYS_TO_SHOW_FIELD = By.CSS_SELECTOR, '[name="channel_params.days_count"]'
    CHOOSE_TIME_TO_END = By.CSS_SELECTOR, '[name="channel_params.time_until"]'
    CREATE_FEED_LINK = By.CSS_SELECTOR, '[data-testid="create_feed_link"]'
    TIME_PICKER_OK_BUTTON = By.CSS_SELECTOR, '.ant-picker-ok button'
    TIME_PICKER_PANEL = By.CSS_SELECTOR, '.ant-picker-panel'
    NEWSFEED_POPOVER = By.CSS_SELECTOR, '.ant-popover-inner-content'
    COPY_NEWSFEED_BUTTON = By.XPATH, '//input[@value="copy"]/../..'
    NEWSFEED_ID_FIELD = By.CSS_SELECTOR, '[data-testid="feed_id_input"]'
    CREATE_NEWSFEED_BUTTON = By.CSS_SELECTOR, '[data-testid="create_feed_button"]'
    SAVE_CREATIVE_BUTTON = By.CSS_SELECTOR, '[data-testid="creative_form_submit_button"]'
    CLOSE_CARD_BUTTON = By.CSS_SELECTOR, 'button.ant-drawer-close'
    CLOSE_NOTIFICATION_BUTTON = By.CSS_SELECTOR, 'span.ant-notification-close-x'
    CAMPAIGN_CARD_LINK = By.CSS_SELECTOR, 'header span a'

    def __init__(self, driver, url, campaign_id):
        self.driver = driver
        self.url = url + f'/{campaign_id}/creatives'

    '''
    Waits
    '''
    def wait_for_creative_screen_open(self):
        self.wait_for_element_to_be_visible(self.CREATE_BUTTON)

    '''
    Interactions
    '''
    def open_campaign_card(self):
        campaign_link = self.wait_for_element(self.CAMPAIGN_CARD_LINK)
        campaign_link.click()

    def click_create(self):
        create_button = self.wait_for_element(self.CREATE_BUTTON)
        create_button.click()

    def click_create_feed_link(self):
        create_button = self.wait_for_element(self.CREATE_FEED_LINK)
        create_button.click()

    def choose_channel(self, channel):
        channel_selector = self.wait_for_element(self.CHANNEL_SELECTOR)
        channel_selector.click()
        self.wait_for_element(self.DROPDOWN)
        time.sleep(0.5)
        dropdown_items = self.wait_for_elements(self.DROPDOWN_ITEM)
        for item in dropdown_items:
            if item.text == channel:
                item.click()
                return
        raise NoSuchElementException(f"No such channel {channel}")

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

    def set_newsfeed_id_copy(self, newsfeed_id):
        time.sleep(0.5)
        newsfeed_id_link = self.wait_for_element(self.CREATE_FEED_LINK)
        newsfeed_id_link.click()
        self.wait_for_element_to_be_visible(self.NEWSFEED_POPOVER)
        copy_newsfeed = self.wait_for_element(self.COPY_NEWSFEED_BUTTON)
        copy_newsfeed.click()
        self.input_field(self.NEWSFEED_ID_FIELD, newsfeed_id)
        create_button = self.wait_for_element(self.CREATE_NEWSFEED_BUTTON)
        create_button.click()

    def set_name(self, name):
        name_field = self.wait_for_element(self.NAME_FIELD)
        self.clear_value(name_field)
        self.input_field(self.NAME_FIELD, name)

    def set_content(self, content):
        content_field = self.wait_for_element(self.TEXT_INPUT)
        self.clear_value(content_field)
        self.input_field(self.TEXT_INPUT, content)

    def set_push_id(self, push_id):
        push_id_field = self.wait_for_element(self.PUSH_ID_INPUT)
        self.clear_value(push_id_field)
        self.input_field(self.PUSH_ID_INPUT, push_id)

    def close_notification(self):
        close_button = self.wait_for_element(self.CLOSE_NOTIFICATION_BUTTON)
        close_button.click()

    def close_creative_card(self):
        close_button = self.wait_for_element(self.CLOSE_CARD_BUTTON)
        close_button.click()

    def save_creative(self):
        save_button = self.wait_for_element(self.SAVE_CREATIVE_BUTTON)
        save_button.click()
        # self.close_notification()
        time.sleep(15)
        self.close_creative_card()

    def set_newsfeed_creative(self, creative_name, newsfeed_id, days_to_show=1, time_to_end="23:59"):
        self.click_create()
        self.set_name(creative_name)
        self.choose_channel("Лента")
        self.set_newsfeed_id_copy(newsfeed_id)
        self.set_days_to_show(days_to_show)
        self.set_time_to_end(time_to_end)
        self.save_creative()

    def set_push_creative(self, creative_name, content):
        self.click_create()
        self.set_name(creative_name)
        self.choose_channel("PUSH")
        self.set_content(content)
        self.save_creative()

    def set_geopush_creative(self, creative_name, content, push_id):
        self.click_create()
        self.set_name(creative_name)
        self.choose_channel("PUSH")
        self.set_content(content)
        self.set_push_id(push_id)
        self.save_creative()

    def set_promo_notification_settings(self, creative_name, content, days_to_show=1, time_to_end="23:59"):
        self.click_create()
        self.set_name(creative_name)
        self.choose_channel("PROMO_NOTIFICATION")
        self.set_content(content)
        self.set_days_to_show(days_to_show)
        self.set_time_to_end(time_to_end)
        self.save_creative()
