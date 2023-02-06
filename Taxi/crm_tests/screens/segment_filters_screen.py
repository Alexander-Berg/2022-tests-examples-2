import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from screens.base_screen import BaseScreen


class SegmentFiltersScreen(BaseScreen):
    COUNTRIES_INPUT = By.XPATH, '(//input[@class="ant-select-selection-search-input"])[1]'
    COUNTRIES_TITLE = By.XPATH, '(//label[@title])[1]'  # By.XPATH, '//div[@name="country"]/../../../..//label'
    CITIES_INPUT = By.XPATH, '(//input[@class="ant-select-selection-search-input"])[2]'
    DROPDOWN = By.CSS_SELECTOR, '.ant-select-dropdown'
    DROPDOWN_ITEM = By.CSS_SELECTOR, '.ant-select-dropdown .ant-select-item'
    BACK_BUTTON = By.CSS_SELECTOR, '[data-testid="filters_form_back_button"]'
    SAVE_BUTTON = By.CSS_SELECTOR, '[data-testid="filters_form_save_button"]'
    SAVE_AND_CALCULATE_BUTTON = By.CSS_SELECTOR, '[data-testid="filters_form_save_and_calc_button"]'
    BRAND_RADIO_BUTTON = By.XPATH, '//input[@name="brand"]'
    ADDITIONAL_ATTRIBUTES = By.CSS_SELECTOR, 'div.ant-collapse-item:nth-child(13)'
    ADDITIONAL_ADVANCED_ATTRIBUTES_CHECKBOX = By.CSS_SELECTOR, 'div.ant-collapse-item:nth-child(13) li.ant-list-item:nth-child(2) input'
    BREAK_SEGMENT_CHECKBOX = By.CSS_SELECTOR, 'div[name="pro_extra_fields"] label:last-child input'

    def __init__(self, driver, url, campaign_id):
        self.driver = driver
        self.url = url + f'/{campaign_id}/filters'
    '''
    Interactions
    '''
    def input_filter_field(self, input_value, field_type):
        locator = ""
        if field_type == 'country':
            locator = self.COUNTRIES_INPUT
        elif field_type == 'city':
            locator = self.CITIES_INPUT
        field_input = self.wait_for_element(locator)
        field_input.click()
        time.sleep(0.5)
        # self.wait_for_element_to_be_visible(self.DROPDOWN)
        self.input_field(locator, input_value)
        menu_items = self.wait_for_elements(self.DROPDOWN_ITEM)
        for menu_item in menu_items:
            if menu_item.text == input_value:
                menu_item.click()
                self.wait_for_element(self.COUNTRIES_TITLE).click()
                return
        raise NoSuchElementException("No such menu item.")

    def click_save_button(self):
        save_button = self.wait_for_element(self.SAVE_BUTTON)
        save_button.click()

    def click_save_and_calculate_button(self):
        save_and_calculate_button = self.wait_for_element(self.SAVE_AND_CALCULATE_BUTTON)
        save_and_calculate_button.click()

    def click_back_button(self):
        back_button = self.wait_for_element(self.BACK_BUTTON)
        back_button.click()

    def select_brand(self, brand_name):
        name_value = {
            "Яндекс Go": "yandex",
            "Uber": "uber",
            "Yango": "yango",
            "Лавка": "lavka",
            "Deli": "yango_deli"
        }
        if brand_name not in name_value.keys():
            raise NoSuchElementException("No such brand in segment filters.")
        brands = self.wait_for_elements(self.BRAND_RADIO_BUTTON)
        for brand in brands:
            if brand.get_attribute("value") == name_value[brand_name]:
                brand.click()
                break

    def click_additional_attributes(self):
        additional_attributes = self.wait_for_element(self.ADDITIONAL_ATTRIBUTES)
        additional_attributes.click()

    def click_additional_advanced_attributes(self):
        additional_advanced_attributes = self.wait_for_element(self.ADDITIONAL_ADVANCED_ATTRIBUTES_CHECKBOX)
        additional_advanced_attributes.click()

    def click_break_segment_checkbox(self):
        break_segment_checkbox = self.wait_for_element(self.BREAK_SEGMENT_CHECKBOX)
        break_segment_checkbox.click()

    def scroll_form(self, height=1000):
        self.driver.execute_script(f"document.querySelector('main.ant-layout-content').scrollTop={height}")
        time.sleep(1)

    def break_default_driver_segment(self):
        self.input_filter_field("Россия", 'country')
        self.input_filter_field('Москва', 'city')
        self.click_additional_attributes()
        self.click_additional_advanced_attributes()
        self.click_break_segment_checkbox()
        self.click_save_and_calculate_button()
        self.wait_for_segment_filter_closed()

    def create_default_driver_segment(self):
        self.input_filter_field("Россия", 'country')
        self.input_filter_field('Москва', 'city')
        self.click_save_and_calculate_button()
        self.wait_for_segment_filter_closed()

    def create_default_eat_user_segment(self):
        self.input_filter_field("Россия", 'country')
        self.input_filter_field('Москва', 'city')
        self.click_save_and_calculate_button()
        self.wait_for_segment_filter_closed()

    def create_default_lavka_user_segment(self):
        self.input_filter_field("Россия", 'country')
        self.input_filter_field('Москва', 'city')
        self.select_brand("Лавка")
        self.click_save_and_calculate_button()
        self.wait_for_segment_filter_closed()

    def create_default_user_segment(self):
        self.input_filter_field("Россия", 'country')
        self.input_filter_field('Москва', 'city')
        self.select_brand("Яндекс Go")
        self.click_save_and_calculate_button()
        self.wait_for_segment_filter_closed()

    def create_default_geo_services_segment(self):
        self.input_filter_field("Россия", 'country')
        self.input_filter_field('Москва', 'city')
        self.click_save_and_calculate_button()
        self.wait_for_segment_filter_closed()

    '''
    Waits
    '''
    def wait_for_segment_filters_open(self):
        self.wait_for_element(self.COUNTRIES_INPUT)
        self.wait_for_element(self.CITIES_INPUT)

    def wait_for_segment_filter_closed(self):
        self.wait_for_element_to_disappear(self.SAVE_AND_CALCULATE_BUTTON)
