from screens.campaign_form_screen import CampaignFormScreen
from selenium.webdriver.common.by import By


class CampaignFormEditScreen(CampaignFormScreen):
    CAMPAIGN_SALT = By.CSS_SELECTOR, 'input[name=salt]'
    SCHEDULE_FIELD = By.XPATH, '//div[@class="react-js-cron"]/../input'

    def __init__(self, driver, url, campaign_id):
        self.driver = driver
        self.url = url + f'/{campaign_id}/edit/'

    '''
    Getters
    '''
    def get_salt(self):
        return self.wait_for_element(self.CAMPAIGN_SALT).text

    '''
    Verify
    '''
    def verify_salt_field_state(self, is_enabled=True):
        salt_field = self.wait_for_element(self.CAMPAIGN_SALT)
        salt_field_state = salt_field.is_enabled()
        assert salt_field_state == is_enabled, f"Wrong state of Salt field. Expected {is_enabled}, got {salt_field_state}"

    def verify_global_control_switch_state(self, is_enabled=True):
        global_control_switch = self.wait_for_element(self.GLOBAL_CONTROL_SWITCH)
        global_control_switch_state = global_control_switch.is_enabled()
        assert global_control_switch_state == is_enabled, \
            f"Wrong state of Global Control switch. Expected {is_enabled}, got {global_control_switch_state}"

    def verify_contacts_politics_switch_state(self, is_enabled=True):
        contacts_politics_switch = self.wait_for_element(self.CONTACTS_POLITICS_SWITCH)
        contacts_politics_switch_state = contacts_politics_switch.is_enabled()
        assert contacts_politics_switch_state == is_enabled, \
            f"Wrong state of Contacts Politics switch. Expected {is_enabled}, got {contacts_politics_switch_state}"

    def verify_discount_message_switch_state(self, is_enabled=True):
        discount_message_switch = self.wait_for_element(self.DISCOUNT_SWITCH)
        discount_message_switch_state = discount_message_switch.is_enabled()
        assert discount_message_switch_state == is_enabled, \
            f"Wrong state of Discount Message switch. Expected {is_enabled}, got {discount_message_switch_state}"

    def verify_efficiency_control_switch_state(self, is_enabled=True):
        efficiency_control_switch = self.wait_for_element(self.EFFICIENCY_CONTROL_SWITCH)
        efficiency_control_switch_state = efficiency_control_switch.is_enabled()
        assert efficiency_control_switch_state == is_enabled, \
            f"Wrong state of Efficiency Control switch. Expected {is_enabled}, got {efficiency_control_switch_state}"

    def verify_campaign_selector_state(self, is_enabled=True):
        campaign_type_inputs = self.wait_for_elements(self.CAMPAIGN_TYPE_INPUT)
        for type_input in campaign_type_inputs:
            assert type_input.is_enabled() == is_enabled, f"Wrong state of input {type_input}."

    def verify_audience_selector_state(self, is_enabled=True):
        audience_inputs = self.wait_for_elements(self.AUDIENCE_INPUT)
        for audience_input in audience_inputs:
            assert audience_input.is_enabled() == is_enabled, f"Wrong state of input {audience_input}."
