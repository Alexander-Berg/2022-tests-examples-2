import time
from screens.base_screen import BaseScreen
from selenium.webdriver.common.by import By


class TicketScreen(BaseScreen):
    APPROVE_IDEA_BUTTON = By.XPATH, "//span[text()='Согласовать идею']/.."
    APPROVE_COMMUNICATION_BUTTON = By.XPATH, '//span[text()="Согласовать коммуникацию"]/..'

    '''
    Interactions
    '''
    def approve_idea(self):
        button = self.wait_for_element(self.APPROVE_IDEA_BUTTON)
        time.sleep(1)
        button.click()
        time.sleep(1)

    def approve_communication(self):
        button = self.wait_for_element(self.APPROVE_COMMUNICATION_BUTTON)
        time.sleep(1)
        button.click()
        time.sleep(1)

    def approve_idea_and_go_back(self):
        self.approve_idea()
        self.close_tab()

    def approve_communication_and_go_back(self):
        self.approve_communication()
        self.close_tab()
        time.sleep(3)
