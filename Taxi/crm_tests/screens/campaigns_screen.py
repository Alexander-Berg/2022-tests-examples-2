from screens.base_screen import BaseScreen
from selenium.webdriver.common.by import By


class CampaignsScreen(BaseScreen):
    CREATE_CAMPAIGN_BUTTON = By.CSS_SELECTOR, '[data-testid=menu_item-campaigns_create]'
    FRONTEND_API_TESTING = By.CSS_SELECTOR, '[role="menu"] label:nth-child(2)'
    FRONTEND_API_UNSTABLE = By.CSS_SELECTOR, '[role="menu"] label:nth-child(1)'

    '''
    Waits
    '''

    def wait_for_create_button(self):
        self.wait_for_element(self.CREATE_CAMPAIGN_BUTTON)

    '''
    Interactions
    '''
    def open_campaign_form(self):
        create_campaign_button = self.wait_for_element_to_be_clickable(self.CREATE_CAMPAIGN_BUTTON)
        create_campaign_button.click()

    def set_frontend_api_testing(self):
        testing_api_button = self.wait_for_element_to_be_clickable(self.FRONTEND_API_TESTING)
        testing_api_button.click()

    def set_frontend_api_unstable(self):
        unstable_api_button = self.wait_for_element_to_be_clickable(self.FRONTEND_API_UNSTABLE)
        unstable_api_button.click()
