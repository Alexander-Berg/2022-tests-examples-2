from screens.base_screen import BaseScreen
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class GroupsSettingsScreen(BaseScreen):
    ADD_GROUP_BUTTON = By.CSS_SELECTOR, '[data-testid="add_group_button"]'
    BACK_BUTTON = By.CSS_SELECTOR, '[data-testid="back_button"]'
    SAVE_AND_CALCULATE_BUTTON = By.CSS_SELECTOR, '[data-testid="save_and_calc_groups_button"]'
    SAVE_BUTTON = By.CSS_SELECTOR, '[data-testid="save_groups_button"]'
    GROUP_NAME_FIELD = By.CSS_SELECTOR, '[id^="groups_"][id$="_name"]'
    CITIES_FIELD = By.CSS_SELECTOR, '[id^="groups_"][id$="_cities"]'
    LOCALES_FIELD = By.CSS_SELECTOR, '[id^="groups_"][id$="_locales"]'
    MINUS_BUTTON = By.CSS_SELECTOR, '.ant-btn-circle'
    GROUP_LIMIT_FIELD = By.CSS_SELECTOR, '[id^="groups_"][id$="_limit"]'
    MODE_LABEL = By.CSS_SELECTOR, 'label[for=mode]'
    CONTROL_LABEL = By.CSS_SELECTOR, 'label[for=control]'

    def __init__(self, driver, url, campaign_id):
        self.driver = driver
        self.url = url + f'/{campaign_id}/groups'

    '''
    Waits
    '''
    def wait_for_groups_settings_screen_open(self):
        self.wait_for_element_to_be_visible(self.CONTROL_LABEL)
        self.wait_for_element_to_be_visible(self.MODE_LABEL)

    '''
    Interactions
    '''
    def fill_in_group_settings(self, title, cities, locales, limit, group_number=0):
        group_names = self.wait_for_elements(self.GROUP_NAME_FIELD)
        limits = self.wait_for_elements(self.GROUP_LIMIT_FIELD)
        try:
            group_name_field = group_names[group_number]
            group_name_field.send_keys(title)
            limit_field = limits[group_number]
            self.clear_limit_field(limit_field)
            limit_field.send_keys(limit)
        except IndexError:
            raise NoSuchElementException(f"No group with index {group_number}")
        # пока без заполнения городов и локалей

    def clear_limit_field(self, el):
        limit_field_value = "".join(el.get_attribute("value").split("&nbsp;"))
        l = len(limit_field_value)
        for l in range(l):
            el.send_keys(Keys.BACKSPACE)
        el.clear()

    def add_group(self):
        add_button = self.wait_for_element(self.ADD_GROUP_BUTTON)
        add_button.click()

    def click_save_and_calculate_button(self):
        save_and_calculate_button = self.wait_for_element(self.SAVE_AND_CALCULATE_BUTTON)
        save_and_calculate_button.click()
        self.wait_for_element_to_disappear(self.SAVE_AND_CALCULATE_BUTTON)

    def click_save_button(self):
        save_button = self.wait_for_element(self.SAVE_BUTTON)
        save_button.click()
        self.wait_for_element_to_disappear(self.SAVE_BUTTON)
