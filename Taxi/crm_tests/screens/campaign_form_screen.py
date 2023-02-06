import time
from screens.base_screen import BaseScreen
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


class CampaignFormScreen(BaseScreen):
    CAMPAIGN_FORM_TITLE = By.CSS_SELECTOR, '.ant-drawer-title'
    CAMPAIGN_TYPE_INPUT = By.CSS_SELECTOR, 'input[name=campaign_type]'
    CAMPAIGN_TYPE_ONESHOT = By.XPATH, '//input[@value="oneshot"]/../../span[2]'
    CAMPAIGN_TYPE_REGULAR = By.XPATH, '//input[@value="regular"]/../../span[2]'
    AUDIENCE_INPUT = By.CSS_SELECTOR, 'input[name=entity]'
    AUDIENCE_DRIVERS = By.XPATH, '//input[@value="Driver"]/../../span[2]'
    AUDIENCE_USERS = By.XPATH, '//input[@value="User"]/../../span[2]'
    AUDIENCE_EATS_USERS = By.XPATH, '//input[@value="EatsUser"]/../../span[2]'
    AUDIENCE_LAVKA_USERS = By.XPATH, '//input[@value="LavkaUser"]/../../span[2]'
    AUDIENCE_GEO = By.XPATH, '//input[@value="Geo"]/../../span[2]'
    CAMPAIGN_NAME = By.CSS_SELECTOR, 'input[name=name]'
    CAMPAIGN_DESCRIPTION = By.CSS_SELECTOR, 'textarea[name=specification]'
    # CAMPAIGN_TREND_FIELD = By.XPATH, '//input[@name="trend"]/../../span'
    CAMPAIGN_TREND_FIELD = By.XPATH, '//input[@id="rc_select_6"]/../..'
    CAMPAIGN_TREND_LIST = By.CSS_SELECTOR, 'ul.ant-cascader-menu'
    CAMPAIGN_TREND_LIST_ITEM = By.CSS_SELECTOR, 'ul.ant-cascader-menu>li'
    ONESHOT_PLANNED_DATE = By.CSS_SELECTOR, 'input[name=planned_start_date]'
    ONESHOT_START_DATE = By.XPATH, '(//div[@name="efficiency_date_range"]//input)[1]'
    ONESHOT_END_DATE = By.XPATH, '(//div[@name="efficiency_date_range"]//input)[2]'
    REGULAR_START_DATE = By.XPATH, '(//div[@name="regular_date_range"]/div/input)[1]'
    REGULAR_END_DATE = By.XPATH, '(//div[@name="regular_date_range"]/div/input)[2]'
    DATE_PICKER_OK_BUTTON = By.CSS_SELECTOR, '.ant-picker-ok button'
    CREATIVE_NEEDED_SWITCH = By.CSS_SELECTOR, 'button[name=creativeTicket]'
    DISCOUNT_SWITCH = By.CSS_SELECTOR, 'button[name=discount]'
    EFFICIENCY_CONTROL_SWITCH = By.CSS_SELECTOR, 'button[name=efficiency]'
    CONTACTS_POLITICS_SWITCH = By.CSS_SELECTOR, 'button[name=com_politic]'
    GLOBAL_CONTROL_SWITCH = By.CSS_SELECTOR, 'button[name=global_control]'
    CREATE_BUTTON = By.CSS_SELECTOR, '.ant-drawer-footer button.ant-btn-primary'
    CANCEL_BUTTON = By.CSS_SELECTOR, '.ant-drawer-footer button.ant-btn-link'
    FILTER_VERSION_INPUT = By.XPATH, '//div[@name="qs_schema_version"]'
    FILTER_VERSION_MENU = By.CSS_SELECTOR, '.rc-virtual-list-holder-inner'
    FILTER_VERSION_ITEM = By.CSS_SELECTOR, '.ant-select-item'

    def __init__(self, driver, url):
        self.driver = driver
        self.base_url = url
        self.url = self.base_url + '/create'

    '''
    Interactions
    '''
    def select_oneshot(self):
        oneshot_button = self.wait_for_element_to_be_visible(self.CAMPAIGN_TYPE_ONESHOT)
        oneshot_button.click()

    def select_regular(self):
        regular_button = self.wait_for_element(self.CAMPAIGN_TYPE_REGULAR)
        regular_button.click()

    def select_drivers(self):
        drivers = self.wait_for_element(self.AUDIENCE_DRIVERS)
        drivers.click()

    def select_users(self):
        users = self.wait_for_element(self.AUDIENCE_USERS)
        users.click()

    def select_eats_users(self):
        eats_users = self.wait_for_element(self.AUDIENCE_EATS_USERS)
        eats_users.click()

    def select_lavka_users(self):
        lavka_users = self.wait_for_element(self.AUDIENCE_LAVKA_USERS)
        lavka_users.click()

    def select_geo_services(self):
        geo_services = self.wait_for_element(self.AUDIENCE_GEO)
        geo_services.click()

    def input_campaign_name(self, camp_name='test'):
        name_input = self.wait_for_element(self.CAMPAIGN_NAME)
        self.clear_value(name_input)
        name_input.send_keys(camp_name)

    def input_description(self, desc='test'):
        description = self.wait_for_element(self.CAMPAIGN_DESCRIPTION)
        description.clear()
        description.send_keys(desc)

    def open_trends(self):
        self.wait_for_element(self.CAMPAIGN_TREND_FIELD).click()

    def choose_trend_category(self, subcategory_name, subcategory_level=0):
        time.sleep(0.5)
        menus = self.wait_for_elements(self.CAMPAIGN_TREND_LIST)
        subcategories = menus[subcategory_level].find_elements(*self.CAMPAIGN_TREND_LIST_ITEM)
        for c in subcategories:
            if c.text == subcategory_name:
                c.click()
                return
        raise NoSuchElementException(f"Can't find category with name '{subcategory_name}'")

    def input_trend(self, trend):
        self.open_trends()
        trend_parts = trend.split(' > ')
        for i, trend_part in enumerate(trend_parts):
            self.choose_trend_category(trend_part, i)

    def input_date(self, date_time, field, campaign_type):
        time.sleep(0.5)
        if field == 'start':
            if campaign_type == 'regular':
                start_date_field = self.wait_for_element(self.REGULAR_START_DATE)
            else:
                start_date_field = self.wait_for_element(self.ONESHOT_START_DATE)
            start_date_field.click()
            self.clear_value(start_date_field)
            if campaign_type == 'regular':
                self.input_field(self.REGULAR_START_DATE, date_time)
            else:
                self.input_field(self.ONESHOT_START_DATE, date_time)
            self.wait_for_element(self.DATE_PICKER_OK_BUTTON).click()
        if field == 'end':
            if campaign_type == 'regular':
                end_date_field = self.wait_for_element(self.REGULAR_END_DATE)
            else:
                end_date_field = self.wait_for_element(self.ONESHOT_END_DATE)
            end_date_field.click()
            self.clear_value(end_date_field)
            if campaign_type == 'regular':
                self.input_field(self.REGULAR_END_DATE, date_time)
            else:
                self.input_field(self.ONESHOT_END_DATE, date_time)
            self.wait_for_element(self.DATE_PICKER_OK_BUTTON).click()

    def click_create(self):
        self.wait_for_element(self.CREATE_BUTTON).click()

    def select_filter_version(self, version=1):
        filters_input = self.wait_for_element(self.FILTER_VERSION_INPUT)
        filters_input.click()
        self.wait_for_element_to_be_visible(self.FILTER_VERSION_MENU)
        items = self.wait_for_elements(self.FILTER_VERSION_ITEM)
        for item in items:
            if int(item.get_attribute("title")) == version:
                item.click()
                return
        raise NoSuchElementException("No such version of filter")

    def global_control_switch_on(self):
        switch = self.wait_for_element(self.GLOBAL_CONTROL_SWITCH)
        if not self.is_switch_on(switch):
            switch.click()

    def global_control_switch_off(self):
        switch = self.wait_for_element(self.GLOBAL_CONTROL_SWITCH)
        if self.is_switch_on(switch):
            switch.click()

    def contacts_politics_switch_on(self):
        switch = self.wait_for_element(self.CONTACTS_POLITICS_SWITCH)
        if not self.is_switch_on(switch):
            switch.click()

    def contacts_politics_switch_off(self):
        switch = self.wait_for_element(self.CONTACTS_POLITICS_SWITCH)
        if self.is_switch_on(switch):
            switch.click()

    def discount_switch_on(self):
        switch = self.wait_for_element(self.DISCOUNT_SWITCH)
        if not self.is_switch_on(switch):
            switch.click()

    def discount_switch_off(self):
        switch = self.wait_for_element(self.DISCOUNT_SWITCH)
        if self.is_switch_on(switch):
            switch.click()

    def efficiency_control_switch_on(self):
        switch = self.wait_for_element(self.EFFICIENCY_CONTROL_SWITCH)
        if not self.is_switch_on(switch):
            switch.click()

    def efficiency_control_switch_off(self):
        switch = self.wait_for_element(self.EFFICIENCY_CONTROL_SWITCH)
        if self.is_switch_on(switch):
            switch.click()

    def creative_needed_switch_on(self):
        switch = self.wait_for_element(self.CREATIVE_NEEDED_SWITCH)
        if not self.is_switch_on(switch):
            switch.click()

    def creative_needed_switch_off(self):
        switch = self.wait_for_element(self.CREATIVE_NEEDED_SWITCH)
        if self.is_switch_on(switch):
            switch.click()

    def create_campaign(self,
                                campaign_type,
                                audience,
                                campaign_name,
                                description,
                                trend,
                                start,
                                end,
                                is_creative_needed=True,
                                contact_politics=True,
                                discount_message=False,
                                efficiency_control=False,
                                filter_version=1):
        self.wait_for_campaign_form_open()
        time.sleep(1)
        if campaign_type == "oneshot":
            self.select_oneshot()
        else:
            self.select_regular()
        if audience == 'Driver':
            self.select_drivers()
            if is_creative_needed:
                self.creative_needed_switch_on()
            else:
                self.creative_needed_switch_off()
        elif audience == 'User':
            self.select_users()
        elif audience == 'EatsUser':
            self.select_eats_users()
        elif audience == 'LavkaUser':
            self.select_lavka_users()
        elif audience == 'GeoServices':
            self.select_geo_services()
        self.input_campaign_fields(campaign_type, audience, campaign_name, description,
                                   trend, start, end, contact_politics,
                                   discount_message, efficiency_control, filter_version)
        self.click_create_and_wait()

    def input_campaign_fields(self,
                                campaign_type,
                                audience,
                                campaign_name,
                                description,
                                trend,
                                start,
                                end,
                                contact_politics=True,
                                discount_message=False,
                                efficiency_control=False,
                                filter_version=1,
                                mode='input'):

        if audience == 'User':
            if contact_politics:
                self.contacts_politics_switch_on()
            else:
                self.contacts_politics_switch_off()
            if discount_message:
                self.discount_switch_on()
            else:
                self.discount_switch_off()
        elif audience == 'EatsUser':
            if contact_politics:
                self.contacts_politics_switch_on()
            else:
                self.contacts_politics_switch_off()
        elif audience == 'GeoServices':
            if contact_politics:
                self.contacts_politics_switch_on()
            else:
                self.contacts_politics_switch_off()
        if campaign_type == 'oneshot':
            if efficiency_control:
                self.efficiency_control_switch_on()
            else:
                self.efficiency_control_switch_off()
        self.input_campaign_name(campaign_name)
        self.input_description(description)
        self.input_trend(trend)
        self.input_date(start, 'start', campaign_type)
        self.input_date(end, 'end', campaign_type)
        self.select_filter_version(filter_version)

    def click_create_and_wait(self):
        self.click_create()
        self.wait_for_campaign_form_close()

    def scroll_form_down(self):
        self.driver.execute_script("document.querySelector('div.ant-drawer-body').scrollTop=500")
        time.sleep(1)

    '''
    Getters
    '''
    def get_name(self):
        return self.wait_for_element(self.CAMPAIGN_NAME).get_attribute('value')

    def get_description(self):
        return self.wait_for_element(self.CAMPAIGN_DESCRIPTION).text

    def get_trend(self):
        return self.wait_for_element(self.CAMPAIGN_TREND_FIELD).text

    def get_start_date(self):
        return self.wait_for_element(self.REGULAR_START_DATE).get_attribute('value')

    def get_end_date(self):
        return self.wait_for_element(self.REGULAR_END_DATE).get_attribute('value')

    def get_filter_version(self):
        return self.wait_for_element(self.FILTER_VERSION_INPUT).text

    '''
    Waits
    '''
    def wait_for_campaign_form_open(self):
        self.wait_for_element_to_be_visible(self.CAMPAIGN_FORM_TITLE)

    def wait_for_campaign_form_close(self):
        self.wait_for_element_to_disappear(self.CAMPAIGN_TYPE_ONESHOT)

    '''
    Checks
    '''
    def is_switch_on(self, switch_el):
        val = switch_el.get_attribute("aria-checked")
        return True if val == 'true' else False

    def is_regular_selected(self):
        regular_button = self.wait_for_element(self.CAMPAIGN_TYPE_REGULAR)
        radio_button = regular_button.find_element(By.XPATH, './../span/input')
        return radio_button.is_selected()

    def is_oneshot_selected(self):
        oneshot_button = self.wait_for_element(self.CAMPAIGN_TYPE_ONESHOT)
        radio_button = oneshot_button.find_element(By.XPATH, './../span/input')
        return radio_button.is_selected()

    def is_drivers_selected(self):
        drivers_button = self.wait_for_element(self.AUDIENCE_DRIVERS)
        radio_button = drivers_button.find_element(By.XPATH, './../span/input')
        return radio_button.is_selected()

    def is_users_selected(self):
        users_button = self.wait_for_element(self.AUDIENCE_USERS)
        radio_button = users_button.find_element(By.XPATH, './../span/input')
        return radio_button.is_selected()

    def is_eats_users_selected(self):
        eats_users_button = self.wait_for_element(self.AUDIENCE_EATS_USERS)
        radio_button = eats_users_button.find_element(By.XPATH, './../span/input')
        return radio_button.is_selected()

    def is_geo_services_selected(self):
        users_button = self.wait_for_element(self.AUDIENCE_GEO)
        radio_button = users_button.find_element(By.XPATH, './../span/input')
        return radio_button.is_selected()

    def is_create_button_enabled(self):
        return self.wait_for_element(self.CREATE_BUTTON).is_enabled()

    def is_name_field_enabled(self):
        return self.wait_for_element(self.CAMPAIGN_NAME).is_enabled()

    def is_description_field_enabled(self):
        return self.wait_for_element(self.CAMPAIGN_DESCRIPTION).is_enabled()

    def is_trend_field_enabled(self):
        trend_field = self.wait_for_element(self.CAMPAIGN_TREND_FIELD)
        trend_field_input = trend_field.find_element(By.XPATH, './/input')
        return trend_field_input.is_enabled()

    def is_start_date_enabled(self):
        if self.is_element_present(self.REGULAR_START_DATE):
            start_date = self.wait_for_element(self.REGULAR_START_DATE)
        else:
            start_date = self.wait_for_element(self.ONESHOT_START_DATE)
        return start_date.is_enabled()

    def is_end_date_enabled(self):
        if self.is_element_present(self.REGULAR_START_DATE):
            end_date = self.wait_for_element(self.REGULAR_END_DATE)
        else:
            end_date = self.wait_for_element(self.ONESHOT_END_DATE)
        return end_date.is_enabled()

    '''
    Verify
    '''
    def verify_campaign_selector_default_state(self):
        assert self.is_oneshot_selected() and not self.is_regular_selected(), "Wrong state of campaign type selector."

    def verify_audience_selector_default_state(self):
        assert not (self.is_drivers_selected() and self.is_eats_users_selected() and self.is_users_selected()) and self.is_geo_services_selected(), \
            "Wrong state of audience selector"

    def verify_create_button(self, is_enabled):
        if is_enabled:
            assert self.is_create_button_enabled(), "Button 'Create' is not enabled"
        else:
            assert not self.is_create_button_enabled(), "Button 'Create' is enabled"

    def verify_name_input(self, is_enabled):
        if is_enabled:
            assert self.is_name_field_enabled(), "Field 'Name' is not enabled"
        else:
            assert not self.is_name_field_enabled(), "Field 'Name' is enabled"

    def verify_description_input(self, is_enabled):
        if is_enabled:
            assert self.is_description_field_enabled(), "Field 'Description' is not enabled"
        else:
            assert not self.is_description_field_enabled(), "Field 'Description' is enabled"

    def verify_trend_field(self, is_enabled):
        if is_enabled:
            assert self.is_trend_field_enabled(), "Field 'Trend' is not enabled"
        else:
            assert not self.is_trend_field_enabled(), "Field 'Trend' is enabled"

    def verify_dates(self, are_enabled):
        if are_enabled:
            assert self.is_start_date_enabled() and self.is_end_date_enabled(), "Campaign dates are not enabled"
        else:
            assert not(self.is_start_date_enabled() and self.is_end_date_enabled()), "Campaign dates are enabled"

    def verify_users_selected(self):
        assert self.is_users_selected(), "Users radio button is not selected"

    def verify_eats_users_selected(self):
        assert self.is_eats_users_selected(), "Eats Users radio button is not selected"

    def verify_drivers_selected(self):
        assert self.is_drivers_selected(), "Drivers radio button is not selected"

    def verify_geo_services_selected(self):
        assert self.is_geo_services_selected(), "Geo Services radio button is not selected"

    def verify_contacts_politics_switch(self, is_on):
        contacts_politics_switch = self.wait_for_element(self.CONTACTS_POLITICS_SWITCH)
        if is_on:
            assert self.is_switch_on(contacts_politics_switch), "Contacts politics switch is off"
        else:
            assert not self.is_switch_on(contacts_politics_switch), "Contacts politics switch is on"

    def verify_global_control_switch(self, is_on):
        global_control_switch = self.wait_for_element(self.GLOBAL_CONTROL_SWITCH)
        if is_on:
            assert self.is_switch_on(global_control_switch), "Global control switch is off"
        else:
            assert not self.is_switch_on(global_control_switch), "Global control switch is on"

    def verify_discount_message_switch(self, is_on):
        discount_message_switch = self.wait_for_element(self.DISCOUNT_SWITCH)
        if is_on:
            assert self.is_switch_on(discount_message_switch), "Discount message switch is off"
        else:
            assert not self.is_switch_on(discount_message_switch), "Discount message switch is on"

    def verify_efficiency_control_switch(self, is_on):
        efficiency_control_switch = self.wait_for_element(self.EFFICIENCY_CONTROL_SWITCH)
        if is_on:
            assert self.is_switch_on(efficiency_control_switch), "Efficiency control switch is off"
        else:
            assert not self.is_switch_on(efficiency_control_switch), "Efficiency control switch is on"

    def verify_creative_needed_switch(self, is_on):
        creative_needed_switch = self.wait_for_element(self.CREATIVE_NEEDED_SWITCH)
        if is_on:
            assert self.is_switch_on(creative_needed_switch), "Creative needed switch is off"
        else:
            assert not self.is_switch_on(creative_needed_switch), "Creative needed switch is on"

    def verify_contacts_politics_switch_visibility(self, is_visible):
        if is_visible:
            assert self.is_element_present(self.CONTACTS_POLITICS_SWITCH)
        else:
            assert self.is_not_element_present(self.CONTACTS_POLITICS_SWITCH, timeout=0.01)

    def verify_global_control_switch_visibility(self, is_visible):
        if is_visible:
            assert self.is_element_present(self.GLOBAL_CONTROL_SWITCH)
        else:
            assert self.is_not_element_present(self.GLOBAL_CONTROL_SWITCH, timeout=0.01)

    def verify_discount_message_switch_visibility(self, is_visible):
        if is_visible:
            assert self.is_element_present(self.DISCOUNT_SWITCH)
        else:
            assert self.is_not_element_present(self.DISCOUNT_SWITCH, timeout=0.01)

    def verify_efficiency_control_switch_visibility(self, is_visible):
        if is_visible:
            assert self.is_element_present(self.EFFICIENCY_CONTROL_SWITCH)
        else:
            assert self.is_not_element_present(self.EFFICIENCY_CONTROL_SWITCH, timeout=0.01)

    def verify_creative_needed_switch_visibility(self, is_visible):
        if is_visible:
            assert self.is_element_present(self.CREATIVE_NEEDED_SWITCH)
        else:
            assert self.is_not_element_present(self.CREATIVE_NEEDED_SWITCH, timeout=0.01)

    def verify_campaign_name(self, expected_name):
        actual_name = self.get_name()
        assert actual_name == expected_name, f'Wrong campaign name. Expected {expected_name}, got {actual_name}'

    def verify_campaign_description(self, expected_description):
        actual_description = self.get_description()
        assert actual_description == expected_description, \
            f'Wrong campaign description. Expected {expected_description}, got {actual_description}'

    def verify_campaign_trend(self, expected_trend):
        actual_trend = self.get_trend()
        assert actual_trend == expected_trend, \
            f'Wrong campaign trend. Expected {expected_trend}, got {actual_trend}'

    def verify_start_date(self, expected_start_date):
        actual_start_date = self.get_start_date()
        assert actual_start_date == expected_start_date, \
            f'Wrong campaign start date. Expected {expected_start_date}, got {actual_start_date}'

    def verify_end_date(self, expected_end_date):
        actual_end_date = self.get_end_date()
        assert actual_end_date == expected_end_date, \
            f'Wrong campaign end date. Expected {expected_end_date}, got {actual_end_date}'
