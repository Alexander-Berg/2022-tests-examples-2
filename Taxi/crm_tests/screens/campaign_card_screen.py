import time
from datetime import datetime
from screens.base_screen import BaseScreen
from screens.creative_screen import CreativeScreen
from screens.campaign_form_edit_screen import CampaignFormEditScreen
from screens.groups_settings_screen import GroupsSettingsScreen
from screens.segment_filters_screen import SegmentFiltersScreen
from screens.send_settings_screen import SendSettingsScreen
from screens.ticket_screen import TicketScreen
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


class CampaignCardScreen(BaseScreen):
    CAMPAIGN_TITLE = By.CSS_SELECTOR, '.ant-drawer-title'
    CAMPAIGN_EDIT_BUTTON = By.CSS_SELECTOR, '[data-testid="edit_campaign_button"]'
    SEGMENT_SETTINGS = By.CSS_SELECTOR, '[data-testid="segment_params"]'
    SEGMENT_TOTAL = By.CSS_SELECTOR, '[data-testid="segment_total_count"] [data-testid="description_item_value"]'
    SEGMENT_GLOBAL_CONTROL = By.CSS_SELECTOR, '[data-testid="segment_global_control"] [data-testid="description_item_value"]'
    SEGMENT_CONTROL = By.CSS_SELECTOR, '[data-testid="segment_control"] [data-testid="description_item_value"]'
    SEGMENT_CONTACTS_POLITICS = By.CSS_SELECTOR, '[data-testid="segment_contact_politics"] [data-testid="description_item_value"]'
    SEGMENT_AVAILABLE_TO_SEND = By.CSS_SELECTOR, '[data-testid="segment_available_to_send"] [data-testid="description_item_value"]'
    STATISTICS_TOTAL_SENT = By.CSS_SELECTOR, '[data-testid="stat_total_sent"] [data-testid="description_item_value"]'
    STATISTICS_TOTAL_IN_SEGMENT = By.CSS_SELECTOR, '[data-testid="stat_total_in_segment"] [data-testid="description_item_value"]'
    STATISTICS_TOTAL_ADDITIONAL_INFO = By.CSS_SELECTOR, '//div[@data-testid="stat_total_sent"]/../../..//span'
    STATISTICS_TOTAL_ADDITIONAL_INFO_POPOVER = By.CSS_SELECTOR, 'div.ant-popover-inner[role=tooltip]'
    STATISTICS_CHART_BAR = By.CSS_SELECTOR, 'path.recharts-rectangle'
    GROUPS_SECTION = By.XPATH, '//a[@data-testid="send_settings_link"]/../../../..'
    GROUPS_PART_OF_CARD = By.CSS_SELECTOR, '[data-testid="groups_section"]'
    GROUPS_SETTINGS = By.CSS_SELECTOR, '[data-testid="edit_groups_button"]'
    CREATIVE_SETTINGS = By.CSS_SELECTOR, '[data-testid="edit_creatives_button"]'
    CAMPAIGN_CLOSE_BUTTON = By.CSS_SELECTOR, 'button.ant-btn-dangerous'
    CAMPAIGN_CLONE_BUTTON = By.CSS_SELECTOR, '[data-testid="clone_campaign_button"]'
    SEND_FOR_FINAL_APPROVAL_BUTTON = By.CSS_SELECTOR, '[data-testid="send_for_final_approval_button"]'
    CALCULATE_SEGMENT_BUTTON = By.CSS_SELECTOR, '[data-testid="calculate_segment_button"]'
    CALCULATE_GROUPS_BUTTON = By.CSS_SELECTOR, '[data-testid="calculate_groups_button"]'
    STOP_SEGMENT_CALCULATING = By.CSS_SELECTOR, '[data-testid="stop_segment_calculating_button"]'
    SUMMON_ANALYST = By.CSS_SELECTOR, '[data-testid="summon_analyst_button"]'
    # START_REGULAR_CAMPAIGN = By.CSS_SELECTOR, '[data-testid="start_regular_campaign_button"]'
    START_REGULAR_CAMPAIGN = By.CSS_SELECTOR, '[data-testid="apply_draft_campaign_button"]'
    STOP_REGULAR_CAMPAIGN = By.CSS_SELECTOR, '[data-testid="stop_regular_campaign_button"]'
    CREATE_TICKET_FOR_CREATIVE = By.CSS_SELECTOR, '[data-testid="create_ticket_for_creative_button"]'
    CAMPAIGN_STATUS = By.CSS_SELECTOR, '[data-testid="campaign_status_block"] .ant-alert-message'
    CAMPAIGN_STATUS_DESCRIPTION = By.CSS_SELECTOR, '[data-testid="campaign_status_block"] .ant-alert-description'
    APPROVE_IDEA_LINK = By.XPATH, '//div[contains(@class,"ant-col")]//a[starts-with(@href, "https://st.yandex-team.ru/CRMTESTSERVICEC")]'
    CLOSE_CARD_BUTTON = By.CSS_SELECTOR, '.anticon-close'
    SEND_SETTINGS_LINK = By.CSS_SELECTOR, '[data-testid="send_settings_link"]'
    NOTIFICATION = By.CSS_SELECTOR, '.ant-notification-notice-message'
    CLOSE_NOTIFICATION_BUTTON = By.CSS_SELECTOR, 'svg[data-icon=close]'
    PROGRESS_VALUE = By.CSS_SELECTOR, 'span.ant-progress-text'
    PROGRESS_INDICATOR = By.CSS_SELECTOR, '.ant-progress-bg'
    EMPTY_SEGMENT_IMAGE = By.CSS_SELECTOR, 'div.ant-empty-image'
    EMPTY_SEGMENT_DESCRIPTION = By.CSS_SELECTOR, 'div.ant-empty-description'
    CAMPAIGN_NAME = By.CSS_SELECTOR, '[data-testid="campaign_info_name"] [data-testid="description_item_value"]'
    CAMPAIGN_DESCRIPTION = By.CSS_SELECTOR, '[data-testid="campaign_info_specification"] [data-testid="description_item_value"]'
    CAMPAIGN_TREND = By.CSS_SELECTOR, '[data-testid="campaign_info_trend"] [data-testid="description_item_value"]'
    CAMPAIGN_TYPE = By.CSS_SELECTOR, '[data-testid="campaign_info_type"] [data-testid="description_item_value"]'
    CAMPAIGN_AUDIENCE = By.CSS_SELECTOR, '[data-testid="campaign_info_audience"] [data-testid="description_item_value"]'
    CAMPAIGN_PERIOD = By.CSS_SELECTOR, '[data-testid="campaign_info_regular_period"] [data-testid="description_item_value"]'
    CAMPAIGN_SCHEDULE = By.CSS_SELECTOR, '[data-testid="campaign_info_schedule"] [data-testid="description_item_value"]'
    CAMPAIGN_TICKET = By.CSS_SELECTOR, '[data-testid="campaign_info_ticket"] [data-testid="description_item_value"]'
    CAMPAIGN_TICKET_LINK = By.CSS_SELECTOR, '[data-testid="campaign_info_ticket"] [data-testid="description_item_value"] a'
    CAMPAIGN_AUTHOR = By.CSS_SELECTOR, '[data-testid="campaign_info_author"] [data-testid="description_item_value"]'
    CAMPAIGN_SALT = By.CSS_SELECTOR, '[data-testid="campaign_info_salt"] [data-testid="description_item_value"]'
    CAMPAIGN_CREATED = By.CSS_SELECTOR, '[data-testid="campaign_info_created_at"] [data-testid="description_item_value"]'
    CAMPAIGN_UPDATED = By.CSS_SELECTOR, '[data-testid="campaign_info_updated_at"] [data-testid="description_item_value"]'
    CAMPAIGN_GLOBAL_CONTROL = By.CSS_SELECTOR, '[data-testid="campaign_info_global_control"] [data-testid="description_item_value"]'
    CAMPAIGN_DISCOUNT_MESSAGE = By.CSS_SELECTOR, '[data-testid="campaign_info_discount"] [data-testid="description_item_value"]'
    CAMPAIGN_CONTACT_POLITICS = By.CSS_SELECTOR, '[data-testid="campaign_info_com_politic"] [data-testid="description_item_value"]'
    CAMPAIGN_EFFICIENCY_CONTROL = By.CSS_SELECTOR, '[data-testid="campaign_info_efficiency"] [data-testid="description_item_value"]'
    CAMPAIGN_CREATIVE_TICKET = By.CSS_SELECTOR, '[data-testid="campaign_info_creative_ticket"] [data-testid="description_item_value"]'
    CAMPAIGN_CREATIVE_TICKET_LINK = By.CSS_SELECTOR, '[data-testid="campaign_info_creative_ticket"] [data-testid="description_item_value"] a'
    CAMPAIGN_ACTUAL_PERIOD = By.CSS_SELECTOR, '[data-testid="campaign_info_actual_period"] [data-testid="description_item_value"]'
    CAMPAIGN_TEST_USERS = By.CSS_SELECTOR, '[data-testid="campaign_info_test_users"] [data-testid="description_item_value"]'
    CITIES_AGGLOMERATION_DIV = By.CSS_SELECTOR, '[data-testid="cities_agglomerations_block"]'
    STARTS_STATISTICS_DIV = By.CSS_SELECTOR, '[data-testid="campagn_regular_stats_block"]'
    CAMPAIGN_RESULTS = By.CSS_SELECTOR, '[data-testid="campaign_results_block"]'
    LOCALES_DIV = By.CSS_SELECTOR, '[data-testid="locales_block"]'
    SHOW_MORE_CITIES = By.CSS_SELECTOR, '[data-testid="cities_agglomerations_block"] [data-testid="show_more_hide_button"]'
    SHOW_MORE_LOCALES = By.CSS_SELECTOR, '[data-testid="locales_block"] [data-testid="show_more_hide_button"]'
    CLOSE_CAMPAIGN_POPOVER = By.CSS_SELECTOR, '.ant-popconfirm'
    CLOSE_CAMPAIGN_POPOVER_NO = By.XPATH, '//div[@class="ant-popover-inner-content"]//button[not(contains(@class, "ant-btn-primary"))]'
    CLOSE_CAMPAIGN_POPOVER_YES = By.XPATH, '//div[@class="ant-popover-inner-content"]//button[contains(@class, "ant-btn-primary")]'
    GROUPS_SETTINGS_SECTION = By.CSS_SELECTOR, '[data-testid="groups_configurating_section"]'
    FINISHED_GROUPS_SECTION = By.CSS_SELECTOR, '[data-testid="groups_finished_section"]'
    GROUPS_TABLE_ROW = By.XPATH, '//td//*[text()="{}"]/../..'
    SHOW_SKIPPED_GROUPS = By.CSS_SELECTOR, '[data-testid="skipped_groups_label"]'
    FIRST_COLUMN_VALUE = By.XPATH, './/tbody/tr/td[1]'
    ADDITIONAL_INFO_GROUP = By.CSS_SELECTOR, '[data-testid="group_table_additional_info_button"]'
    ADDITIONAL_INFO_GROUP_POPOVER = By.CSS_SELECTOR, 'div.ant-popover-inner[role=tooltip]'

    def __init__(self, driver, url, campaign_id):
        self.driver = driver
        self.base_url = url
        self.url = self.base_url + f'/{campaign_id}'

    '''
    Navigation
    '''
    def go_to_segment_settings(self):
        segment_edit_button = self.wait_for_element_to_be_clickable(self.SEGMENT_SETTINGS)
        segment_edit_button.click()
        campaign_id = self.get_campaign_id()
        segment_settings = SegmentFiltersScreen(self.driver, self.base_url, campaign_id)
        segment_settings.wait_for_segment_filters_open()
        return segment_settings

    def go_to_groups_settings(self):
        edit_button = self.wait_for_element(self.GROUPS_SETTINGS)
        edit_button.click()
        campaign_id = self.get_campaign_id()
        groups_settings = GroupsSettingsScreen(self.driver, self.base_url, campaign_id)
        groups_settings.wait_for_groups_settings_screen_open()
        return groups_settings

    def go_to_creative_settings(self):
        edit_button = self.wait_for_element(self.CREATIVE_SETTINGS)
        edit_button.click()
        campaign_id = self.get_campaign_id()
        creative_screen = CreativeScreen(self.driver, self.base_url, campaign_id)
        creative_screen.wait_for_creative_screen_open()
        return creative_screen

    def go_to_send_settings(self):
        send_settings_link = self.wait_for_element(self.SEND_SETTINGS_LINK)
        send_settings_link.click()
        campaign_id = self.get_campaign_id()
        send_settings = SendSettingsScreen(self.driver, self.base_url, campaign_id)
        send_settings.wait_for_send_settings_open()
        time.sleep(3)
        return send_settings

    def go_to_edit_campaign(self):
        edit_campaign_button = self.wait_for_element(self.CAMPAIGN_EDIT_BUTTON)
        edit_campaign_button.click()
        campaign_id = self.get_campaign_id()
        edit_campaign = CampaignFormEditScreen(self.driver, self.base_url, campaign_id)
        edit_campaign.wait_for_campaign_form_open()
        return edit_campaign

    '''
    Waits
    '''
    def wait_for_status(self, status, timeout=1800):
        try:
            self.wait_for_text(self.CAMPAIGN_STATUS, status, timeout)
        except NoSuchElementException:
            raise AssertionError(f'Cannot find status "{status}" on campaign card. Waited for {timeout} seconds.')

    def wait_for_card_open(self):
        self.wait_for_element(self.CAMPAIGN_TITLE)

    def wait_for_notification_to_disappear(self):
        # time.sleep(0.5)
        # self.wait_for_element_to_be_visible(self.NOTIFICATION)
        self.wait_for_element_to_disappear(self.NOTIFICATION)

    '''
    Interactions
    '''
    def click_link_for_idea_approval_ticket(self):
        ticket_link = self.wait_for_element(self.APPROVE_IDEA_LINK)
        ticket_link_url = self.get_campaign_ticket_link()
        ticket_link.click()
        new_window = self.driver.window_handles[1]
        self.driver.switch_to.window(new_window)
        ticket_screen = TicketScreen(self.driver, ticket_link_url)
        return ticket_screen

    def click_calculate_segment(self):
        calculate_button = self.wait_for_element(self.CALCULATE_SEGMENT_BUTTON)
        calculate_button.click()

    def stop_calculations(self):
        stop_button = self.wait_for_element(self.STOP_SEGMENT_CALCULATING)
        stop_button.click()

    def open_close_campaign_popover(self):
        close_campaign_button = self.wait_for_element(self.CAMPAIGN_CLOSE_BUTTON)
        close_campaign_button.click()
        self.wait_for_element_to_be_visible(self.CLOSE_CAMPAIGN_POPOVER)

    def click_yes_in_close_campaign_popover(self):
        yes_button = self.wait_for_element_to_be_clickable(self.CLOSE_CAMPAIGN_POPOVER_YES)
        yes_button.click()

    def click_no_in_close_campaign_popover(self):
        no_button = self.wait_for_element(self.CLOSE_CAMPAIGN_POPOVER_NO)
        no_button.click()

    def click_start_regular_campaign(self):
        start_button = self.wait_for_element(self.START_REGULAR_CAMPAIGN)
        start_button.click()
        time.sleep(5)

    def click_calculate_groups(self):
        calculate_button = self.wait_for_element(self.CALCULATE_GROUPS_BUTTON)
        calculate_button.click()

    def close_campaign(self):
        self.open_close_campaign_popover()
        self.click_yes_in_close_campaign_popover()

    def close_notification(self):
        close_button = self.wait_for_element(self.CLOSE_NOTIFICATION_BUTTON)
        close_button.click()

    def send_for_final_approval(self):
        send_button = self.wait_for_element(self.SEND_FOR_FINAL_APPROVAL_BUTTON)
        time.sleep(2)
        send_button.click()
        time.sleep(2)

    def show_skipped_groups(self):
        skipped = self.wait_for_element(self.SHOW_SKIPPED_GROUPS)
        skipped.click()

    '''
    Getters
    '''
    def get_progress(self):
        return int(self.wait_for_element(self.PROGRESS_VALUE).text[:-1])

    def get_progress_indicator_value(self):
        progress_indicator = self.wait_for_element(self.PROGRESS_INDICATOR)
        progress_indicator_style = progress_indicator.get_attribute('style')
        progress_indicator_width = progress_indicator_style.split('; ')[0]
        progress_indicator_value = progress_indicator_width.rstrip('%').split(': ')[1]
        return int(progress_indicator_value)

    def get_status(self):
        return self.wait_for_element(self.CAMPAIGN_STATUS).text

    def get_status_description(self):
        return self.wait_for_element(self.CAMPAIGN_STATUS_DESCRIPTION).text

    def get_campaign_name(self):
        return self.wait_for_element(self.CAMPAIGN_NAME).text

    def get_campaign_description(self):
        return self.wait_for_element(self.CAMPAIGN_DESCRIPTION).text

    def get_campaign_trend(self):
        return self.wait_for_element(self.CAMPAIGN_TREND).text

    def get_campaign_type(self):
        return self.wait_for_element(self.CAMPAIGN_TYPE).text

    def get_campaign_audience(self):
        return self.wait_for_element(self.CAMPAIGN_AUDIENCE).text

    def get_campaign_author(self):
        return self.wait_for_element(self.CAMPAIGN_AUTHOR).text

    def get_campaign_salt(self):
        return self.wait_for_element(self.CAMPAIGN_SALT).text

    def get_campaign_created(self):
        return self.wait_for_element(self.CAMPAIGN_CREATED).text

    def get_campaign_updated(self):
        return self.wait_for_element(self.CAMPAIGN_UPDATED).text

    def get_campaign_schedule(self):
        return self.wait_for_element(self.CAMPAIGN_SCHEDULE).text

    def get_campaign_ticket_link(self):
        return self.wait_for_element(self.CAMPAIGN_TICKET_LINK).get_attribute("href")

    def get_campaign_ticket_id(self):
        return self.wait_for_element(self.CAMPAIGN_TICKET_LINK).text

    def get_campaign_ticket_status(self):
        return self.wait_for_element(self.CAMPAIGN_TICKET).text.split()[1]

    def get_creative_ticket_link(self):
        return self.wait_for_element(self.CAMPAIGN_CREATIVE_TICKET_LINK).get_attribute("href")

    def get_campaign_period(self):
        return self.wait_for_element(self.CAMPAIGN_PERIOD).text

    def get_campaign_period_start(self):
        period = self.wait_for_element(self.CAMPAIGN_PERIOD).text
        period = period.replace('\n', ' ')
        return period.split('  –  ')[0]

    def get_campaign_period_end(self):
        period = self.wait_for_element(self.CAMPAIGN_PERIOD).text
        period = period.replace('\n', ' ')
        return period.split('  –  ')[1]

    def get_campaign_actual_period(self):
        return self.wait_for_element(self.CAMPAIGN_ACTUAL_PERIOD).text

    def get_campaign_actual_period_start(self):
        period = self.wait_for_element(self.CAMPAIGN_ACTUAL_PERIOD).text
        period = period.replace('\n', ' ')
        return period.split('  –  ')[0]

    def get_campaign_actual_period_end(self):
        period = self.wait_for_element(self.CAMPAIGN_ACTUAL_PERIOD).text
        period = period.replace('\n', ' ')
        return period.split('  –  ')[1]

    def get_cities_and_agglomerations(self):
        cities_div = self.wait_for_element(self.CITIES_AGGLOMERATION_DIV)
        if self.is_element_present(self.SHOW_MORE_CITIES):
            self.wait_for_element(self.SHOW_MORE_CITIES).click()
        city_els = cities_div.find_elements(By.CSS_SELECTOR, 'text[type=category]')
        cities = []
        for city_el in city_els:
            cities.append(city_el.text)
        return cities

    def get_locales(self):
        locales_div = self.wait_for_element(self.LOCALES_DIV)
        if self.is_element_present(self.SHOW_MORE_LOCALES):
            self.wait_for_element(self.SHOW_MORE_LOCALES).click()
        locale_els = locales_div.find_elements(By.CSS_SELECTOR, 'text[type=category]')
        locales = []
        for locale_el in locale_els:
            locales.append(locale_el.text)
        return locales

    def get_one_or_two_values_with_braces(self, text, audience):
        if audience == 'driver':
            text_values = ["".join(x.split()) for x in text.rstrip(")").split(" (")]
            value_all, value_unique = map(int, text_values)
            return value_all, value_unique
        if audience == 'user' or 'eats_user' or 'geo_services':
            value_all = int("".join(text.split()))
            return value_all

    def get_segment_total_value(self, audience):
        segment_total_text = self.wait_for_element(self.SEGMENT_TOTAL).text
        return self.get_one_or_two_values_with_braces(segment_total_text, audience)

    def get_segment_global_control_value(self, audience):
        segment_global_control = self.wait_for_element(self.SEGMENT_GLOBAL_CONTROL).text
        return self.get_one_or_two_values_with_braces(segment_global_control, audience)

    def get_segment_control_value(self):
        segment_control_text = self.wait_for_element(self.SEGMENT_CONTROL).text
        segment_control_text_value = segment_control_text.lstrip('≈')
        segment_control = int("".join(segment_control_text_value.split()))
        return segment_control

    def get_one_or_two_values(self, text):
        arr = text.split(" – ")
        arr_l = len(arr)
        if arr_l == 1:
            one_value = int("".join(arr[0].split()))
            return one_value
        elif arr_l == 2:
            value_min = int("".join(arr[0].split()))
            value_max = int("".join(arr[1].split()))
            return value_min, value_max

    def get_contact_politics_value(self):
        contact_politics_text = self.wait_for_element(self.SEGMENT_CONTACTS_POLITICS).text
        return self.get_one_or_two_values(contact_politics_text)

    def get_statistics_total_sent(self):
        total_sent_text = self.wait_for_element(self.STATISTICS_TOTAL_SENT).text
        total_sent = int("".join(total_sent_text.split()))
        return total_sent

    def get_statistics_total_in_segment(self):
        total_in_segment_text = self.wait_for_element(self.STATISTICS_TOTAL_IN_SEGMENT).text
        total_in_segment = int("".join(total_in_segment_text.split()))
        return total_in_segment

    def get_segment_available_to_send(self):
        segment_available_to_send_text = self.wait_for_element(self.SEGMENT_AVAILABLE_TO_SEND).text
        return self.get_one_or_two_values(segment_available_to_send_text)

    def get_group_row(self, group_name):
        method = self.GROUPS_TABLE_ROW[0]
        locator = self.GROUPS_TABLE_ROW[1].format(group_name)
        try:
            rows = self.wait_for_elements((method, locator))
            row_parts = []
            for row in rows:
                tds = row.find_elements_by_css_selector('td')
                for td in tds:
                    row_parts.append(td.text)
            return row_parts  # name, comm_channel, status, total, sent, sent_date, sent_time
        except NoSuchElementException:
            raise NoSuchElementException(f"Cannot find group with name {group_name}")

    def get_groups_names(self):
        groups_section = self.wait_for_element(self.GROUPS_PART_OF_CARD)
        group_names_td = groups_section.find_elements(*self.FIRST_COLUMN_VALUE)
        groups_names = []
        for group_name in group_names_td:
            group_name_text = group_name.text
            if group_name_text.startswith(" Пропущено ("):
                continue
            groups_names.append(group_name_text)
        return groups_names

    def get_group_status(self, group_name):
        group_data = self.get_group_row(group_name)
        return group_data[2]

    def get_group_channel(self, group_name):
        group_data = self.get_group_row(group_name)
        return group_data[1]

    '''
    Checks
    '''
    def is_campaign_global_control_enabled(self):
        campaign_global_control = self.wait_for_element(self.CAMPAIGN_GLOBAL_CONTROL).text
        return False if campaign_global_control == 'Нет' else True

    def is_campaign_discount_message_enabled(self):
        discount_message = self.wait_for_element(self.CAMPAIGN_DISCOUNT_MESSAGE).text
        return False if discount_message == 'Нет' else True

    def is_campaign_contact_politics_enabled(self):
        contact_politics = self.wait_for_element(self.CAMPAIGN_CONTACT_POLITICS).text
        return False if contact_politics == 'Нет' else True

    def is_campaign_efficiency_control_enabled(self):
        efficiency_control = self.wait_for_element(self.CAMPAIGN_EFFICIENCY_CONTROL).text
        return False if efficiency_control == 'Нет' else True

    '''
    Verify
    '''
    def verify_status(self, expected_status):
        actual_status = self.get_status()
        assert actual_status == expected_status, \
            f"Wrong campaign status. Expected {expected_status}, got {actual_status}"

    def verify_status_description(self, expected_status_description):
        actual_status_description = self.get_status_description()
        assert actual_status_description == expected_status_description, \
            f"Wrong campaign status description. Expected {expected_status_description}, got {actual_status_description}"

    def verify_progress(self, expected_progress):
        actual_progress = self.get_progress()
        assert actual_progress == expected_progress, \
            f"Wrong progress of campaign. Expected {expected_progress}, got {actual_progress}"

    def verify_progress_indicator(self, expected_progress):
        actual_progress = self.get_progress_indicator_value()
        assert actual_progress == expected_progress, \
            f"Wrong progress indicator of campaign. Expected {expected_progress}, got {actual_progress}"

    def verify_campaign_name(self, expected_name):
        actual_name = self.get_campaign_name()
        assert actual_name == expected_name, \
            f"Wrong campaign name. Expected {expected_name}, got {actual_name}"

    def verify_campaign_description(self, expected_description):
        actual_description = self.get_campaign_description()
        assert actual_description == expected_description, \
            f"Wrong campaign description. Expected {expected_description}, got {actual_description}"

    def verify_campaign_trend(self, expected_trend):
        actual_trend = self.get_campaign_trend()
        assert actual_trend == expected_trend, f"Wrong campaign trend. Expected {expected_trend}, got {actual_trend}"

    def verify_campaign_type(self, expected_type):
        actual_type = self.get_campaign_type()
        assert actual_type == expected_type, f"Wrong campaign type. Expected {expected_type}, got {actual_type}"

    def verify_campaign_audience(self, expected_audience):
        actual_audience = self.get_campaign_audience()
        assert actual_audience == expected_audience, \
            f"Wrong campaign audience. Expected {expected_audience}, got {actual_audience}"

    def verify_author(self, expected_author):
        actual_author = self.get_campaign_author()
        assert actual_author == expected_author, \
            f"Wrong campaign author. Expected {expected_author}, got {actual_author}"

    def verify_salt(self, expected_salt):
        actual_salt = self.get_campaign_salt()
        assert actual_salt == expected_salt, \
            f"Wrong campaign author. Expected {expected_salt}, got {actual_salt}"

    def verify_global_control_state(self, expected_state):
        actual_state = self.is_campaign_global_control_enabled()
        assert actual_state == expected_state, \
            f"Wrong global control state. Expected {expected_state}, got {actual_state}"

    def verify_contact_politics_state(self, expected_state):
        actual_state = self.is_campaign_contact_politics_enabled()
        assert actual_state == expected_state, \
            f"Wrong contact politics state. Expected {expected_state}, got {actual_state}"

    def verify_efficiency_control_state(self, expected_state):
        actual_state = self.is_campaign_efficiency_control_enabled()
        assert actual_state == expected_state, \
            f"Wrong efficiency control state. Expected {expected_state}, got {actual_state}"

    def verify_discount_message_state(self, expected_state):
        actual_state = self.is_campaign_discount_message_enabled()
        assert actual_state == expected_state, \
            f"Wrong discount message state. Expected {expected_state}, got {actual_state}"

    def verify_created_date(self, expected_created_datetime):
        actual_created = self.get_campaign_created()
        actual_created_datetime = datetime.strptime(actual_created, '%d.%m.%y %H:%M')
        diff = expected_created_datetime - actual_created_datetime
        expected_created = expected_created_datetime.strftime('%d.%m.%y %H:%M')
        seconds = diff.total_seconds()
        assert 0 <= seconds <= 90, \
            f"Wrong Created date. Expected {expected_created}, got {actual_created}. Difference in {seconds} seconds"

    def verify_updated_date(self, expected_updated_datetime):
        actual_updated = self.get_campaign_updated()
        actual_updated_datetime = datetime.strptime(actual_updated, '%d.%m.%y %H:%M')
        diff = expected_updated_datetime - actual_updated_datetime
        seconds = diff.total_seconds()
        expected_updated = expected_updated_datetime.strftime('%d.%m.%y %H:%M')
        assert 0 <= seconds <= 90, \
            f"Wrong Updated date. Expected {expected_updated}, got {actual_updated}. Difference in {seconds} seconds"

    def verify_campaign_ticket(self):
        ticket_link = self.get_campaign_ticket_link()
        assert ticket_link.startswith('https://st.yandex-team.ru/CRMTESTSERVICEC-'), 'Wrong campaign startrack ticket'

    def verify_campaign_ticket_status(self, expected_status):
        actual_status = self.get_campaign_ticket_status()
        assert actual_status == expected_status, \
            f"Wrong ticket status. Expected {expected_status}, got {actual_status}"

    def verify_empty_segment_placeholder(self):
        assert self.is_element_present(self.EMPTY_SEGMENT_IMAGE) and self.is_element_present(self.EMPTY_SEGMENT_DESCRIPTION), \
            "No placeholder for empty segment"

    def verify_creative_ticket(self):
        ticket_link = self.get_creative_ticket_link()
        assert ticket_link.startswith('https://st.yandex-team.ru/CRMTEST-'), \
            'Wrong startrack ticket for campaign creative'

    def verify_create_ticket_for_creative_present(self):
        assert self.is_element_present(self.CREATE_TICKET_FOR_CREATIVE), "No button for creating creative ticket"

    def verify_schedule(self, expected_schedule):
        actual_schedule = self.get_campaign_schedule()
        assert actual_schedule == expected_schedule, \
            f"Wrong schedule. Expected {expected_schedule}, got {actual_schedule}"

    def verify_period_start(self, expected_period_start):
        actual_period_start = self.get_campaign_period_start()
        expected_period_start_datetime = datetime.strptime(expected_period_start, '%d.%m.%Y %H:%M')
        expected_period_start = expected_period_start_datetime.strftime('%d.%m.%y %H:%M')
        assert actual_period_start == expected_period_start, \
            f"Wrong period start. Expected {expected_period_start}, got {actual_period_start}."

    def verify_period_end(self, expected_period_end):
        actual_period_end = self.get_campaign_period_end()
        expected_period_end_datetime = datetime.strptime(expected_period_end, '%d.%m.%Y %H:%M')
        expected_period_end = expected_period_end_datetime.strftime('%d.%m.%y %H:%M')
        assert actual_period_end == expected_period_end, \
            f"Wrong period start. Expected {expected_period_end}, got {actual_period_end}."

    def verify_calculate_segment_button_present(self):
        assert self.is_element_present(self.CALCULATE_SEGMENT_BUTTON), "Button for segment calculating is not present."

    def verify_calculate_segment_button_not_present(self):
        assert self.is_not_element_present(self.CALCULATE_SEGMENT_BUTTON), \
            "Button for segment calculating is present. But it should not"

    def verify_summon_analyst_button_present(self):
        assert self.is_element_present(self.SUMMON_ANALYST), 'Summon analyst button is not present'

    def verify_close_campaign_button_present(self):
        assert self.is_element_present(self.CAMPAIGN_CLOSE_BUTTON), 'Close campaign button is not present'

    def verify_groups_configuration_section_present(self):
        assert self.is_element_present(self.GROUPS_SETTINGS_SECTION), \
            'Groups configuration settings section is not present'

    def verify_stop_calculating_button_present(self):
        assert self.is_element_present(self.STOP_SEGMENT_CALCULATING), 'Stop segment calculating button is not present.'

    def verify_city_from_filter_on_card(self, city):
        assert city in self.get_cities_and_agglomerations(), "No city set in filters on campaign card."

    def verify_locales_graph_present(self):
        assert self.is_element_present(self.LOCALES_DIV), "No locales graph on campaign card"
        assert len(self.get_locales()) > 0, "No locales on graph"

    def verify_segment_total_value(self, audience):
        if audience == 'user' or audience == 'eats_user' or audience == 'geo_services':
            total = self.get_segment_total_value(audience)
            assert total > 0, f"Wrong segment total value: {total}"
        elif audience == 'driver':
            total, unique = self.get_segment_total_value('driver')
            assert total >= unique > 0, f'Wrong segment total value. Total: {total}, unique: {unique}'

    def verify_global_control_value(self, audience):
        if audience == 'user' or audience == 'eats_user'or audience == 'geo_services':
            total = self.get_segment_global_control_value(audience)
            assert total > 0, f"Wrong global control value: {total}"
        elif audience == 'driver':
            total, unique = self.get_segment_global_control_value('driver')
            assert total >= unique > 0, f'Wrong global control value. Total: {total}, unique: {unique}'

    def verify_control_value(self, audience):
        control = self.get_segment_control_value()
        if audience == 'user' or audience == 'eats_user' or audience == 'geo_services':
            total = self.get_segment_total_value(audience)
        elif audience == 'driver':
            total = self.get_segment_total_value(audience)[0]
        assert 0 <= abs(total * 0.1 - control) <= 1, f"Wrong control value: {control}. Total segmnet: {total}"

    def verify_contacts_politics_value(self):
        values = self.get_contact_politics_value()
        if len(values) == 2:
            assert values[1] != 0, f"Contacts politics values: {values[0]} - {values[1]}"

    def verify_available_to_send_value(self, audience):
        values = self.get_segment_available_to_send()
        total = self.get_segment_total_value(audience)
        if len(values) == 2:
            val_min = values[0]
            val_max = values[1]
            assert val_min <= val_max and val_max <= total, \
                f"Wrong values of available to send: {val_min} - {val_max}. Total in segment: {total}"

    def verify_segment_total_value_zero(self, audience):
        if audience == 'user' or audience == 'eats_user' or audience == 'geo_services':
            total = self.get_segment_total_value(audience)
            assert total == 0, f"Wrong segment total value: {total}.  Must be 0"
        elif audience == 'driver':
            total, unique = self.get_segment_total_value('driver')
            assert total >= unique > 0, f'Wrong segment total value. Total: {total}, unique: {unique}. Must be 0'

    def verify_global_control_value_zero(self, audience):
        global_control_values = self.get_segment_global_control_value(audience)
        if audience == 'user' or audience == 'eats_user' or audience == 'geo_services':
            assert global_control_values == 0, f"Global control must be 0, but it is {global_control_values}"
        elif audience == 'driver':
            assert global_control_values[0] == 0 and global_control_values[1] == 0, \
                f"Global control must be 0, but it is {global_control_values[0]} ({global_control_values[1]})"

    def verify_control_value_zero(self, audience):
        if audience == 'user' or audience == 'eats_user' or audience == 'geo_services':
            total = self.get_segment_total_value(audience)
            assert total == 0, f"Wrong segment total value: {total}. Must be 0."
        elif audience == 'driver':
            total, unique = self.get_segment_total_value('driver')
            assert total == unique == 0, f'Wrong segment total value. Total: {total}, unique: {unique}. Must be 0'

    def verify_groups_section_is_not_displayed(self):
        assert self.is_not_element_present(self.GROUPS_SECTION), "Groups section is present on card, but it should not"

    def verify_groups_section_is_displayed(self):
        assert self.is_element_present(self.GROUPS_SECTION), "Groups section is not present on card, but it should"

    def verify_start_statistics_present(self):
        assert self.is_element_present(self.STARTS_STATISTICS_DIV), "No starts statistics."

    def verify_groups_names(self, expected_groups_names):
        actual_groups_names = self.get_groups_names()
        actual_len = len(actual_groups_names)
        expected_len = len(expected_groups_names)
        assert actual_len == expected_len, f"We have {actual_len} groups, but expected {expected_len}"
        for eg in expected_groups_names:
            assert eg in actual_groups_names, f"Expect group with name '{eg}' in {actual_groups_names}"

    def verify_group_status(self, group_name, group_status):
        actual_group_status = self.get_group_status(group_name)
        assert actual_group_status == group_status, \
            f"Expected status '{group_status}' for group {group_name}, but got '{actual_group_status}'"

    def verify_group_channel(self, group_name, group_channel):
        actual_group_channel = self.get_group_channel(group_name)
        assert actual_group_channel == group_channel, \
            f"Expected channe; '{group_channel}' for group {group_name}, but got '{actual_group_channel}'"
