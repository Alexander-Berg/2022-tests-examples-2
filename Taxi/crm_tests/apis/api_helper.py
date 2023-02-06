import datetime
import time
import random
import requests


def create_file_to_upload(file_in, file_out, param):
    with open(file_in) as f_in:
        lines_cleaned = []
        lines = f_in.readlines()
        for line in lines:
            lines_cleaned.append(line.rstrip('\n'))

    with open(file_out, "w") as f_out:
        f_out.write(f"{lines_cleaned[0]},{param}\n")
        for i, line in enumerate(lines_cleaned[1:]):
            f_out.write(f"{line},{param}{i}\n")


class ApiHelper:
    def __init__(self, api_url, session, startrack_url, startrack_session):
        self.api_url = api_url
        self.session = session
        self.startrack_url = startrack_url
        self.startrack_session = startrack_session

    def get_campaign_state(self, campaign_id):
        campaign = self.session.get(self.api_url + f'/v1/campaigns/item?id={campaign_id}')
        campaign_json = campaign.json()
        return campaign_json['state']

    def wait_while_state(self, campaign_id, state, n=180, timeout=10):
        campaign_state = self.get_campaign_state(campaign_id)
        assert campaign_state == state, f"Campaign is not is state '{state}'"
        total_secs = n * timeout
        while campaign_state == state and n >= 0:
            time.sleep(timeout)
            n -= 1
            campaign_state = self.get_campaign_state(campaign_id)
            assert campaign_state not in ["SEGMENT_ERROR", "GROUPS_ERROR", "SENDING_ERROR", "VERIFY_ERROR"], \
                f"Campaign in state {campaign_state}"
        if n < 0:
            raise TimeoutError(f"Campaign is still in state: '{state}'. Waited for {total_secs} seconds.")

    def wait_for_state(self, campaign_id, expected_state, n=90, timeout=10):
        campaign_state = self.get_campaign_state(campaign_id)
        total_secs = n * timeout
        while campaign_state != expected_state and n >= 0:
            time.sleep(timeout)
            n -= 1
            campaign_state = self.get_campaign_state(campaign_id)
            assert campaign_state not in ["SEGMENT_ERROR", "GROUPS_ERROR", "SENDING_ERROR", "VERIFY_ERROR"], \
                f"Campaign in state '{campaign_state}'."
        if n < 0:
            raise TimeoutError(f"Campaign is still not in state: '{expected_state}'. Waited for {total_secs} seconds. "
                               f"Current state is {campaign_state}")

    def verify_campaign_state(self, campaign_id, expected_state):
        actual_state = self.get_campaign_state(campaign_id)
        assert actual_state == expected_state, \
            f"Wrong state of campaign. Got '{actual_state}', expected '{expected_state}'"

    # возвращает true, если не проскочили текущий статус
    # возвращает false, сли перешли к следующему статусу (проскочили один)
    # падает по assert, если статус другой
    def check_status_skip(self, campaign_id, expected_state, next_state):
        actual_state = self.get_campaign_state(campaign_id)
        if actual_state == expected_state:
            return True
        elif actual_state == next_state:
            return False
        else:
            AssertionError(f"Wrong state of campaign. Got '{actual_state}', expected '{expected_state} or {next_state}'")

    def get_campaigns_list(self, author):
        payload = {"offset": 0, "limit": 100, "owner": author, "trend": ""}
        campaigns = self.session.post(self.api_url + "/v1/campaigns/list", json=payload)
        return campaigns.json()

    def delete_campaign(self, campaign_id):
        try:
            self.session.delete(self.api_url + f'/v1/internal/campaign/clear?id={campaign_id}')
            print(f"Кампания {campaign_id} удалена.")
        except requests.exceptions.HTTPError as e:
            print(f"{e.response} при попытке удалить {campaign_id}")

    def terminate_campaign(self, campaign_id):
        try:
            self.session.post(self.api_url + f'/v1/regular-campaigns/stop/?campaign_id={campaign_id}')
        except requests.exceptions.HTTPError as e:
            print(f"{e.response} при попытке остановить {campaign_id}")

    def stop_regular_campaign(self, campaign_id):
        # остановить регулярку, если она запущена
        try:
            self.session.post(self.api_url + f'/v1/regular-campaigns/stop/?campaign_id={campaign_id}')
            print(f"Запущенная регулярная кампания id={campaign_id}. Остановили.")
        except requests.exceptions.HTTPError as e:
            print(f"{e.response} при попытке остановить {campaign_id}")

    def terminate_segmenting(self, campaign_id):
        try:
            self.session.post(self.api_url + f'/v1/terminate/segmenting/?id={campaign_id}')
        except requests.exceptions.HTTPError as e:
            print(f"{e.response} при попытке остановить{campaign_id}")

    def terminate(self, campaign_id, campaign_type, campaign_state):
        if campaign_state == "SEGMENT_CALCULATING":
            self.terminate_segmenting(campaign_id)
        elif campaign_state in ["VERIFY_PROCESSING", "SCHEDULED", "SENDING_PROCESSING", "EFFICIENCY_ANALYSIS"]\
                and campaign_type == "oneshot":
            self.terminate_campaign(campaign_id)

    def get_campaign_params(self, campaign):
        campaign_id = campaign['id']
        campaign_name = campaign['name']
        campaign_type = campaign['campaign_type']
        campaign_state = campaign['state']
        try:
            is_campaign_active = campaign['is_active']
        except KeyError:
            is_campaign_active = False

        # костыли ради питона 3.6.9 на новом агенте
        first, second = campaign['created_at'].split("+")
        second = second.replace(":", "")
        campaign_created = "+".join([first, second])
        campaign_created_dt = datetime.datetime.strptime(campaign_created, '%Y-%m-%dT%H:%M:%S.%f%z')

        return campaign_id, campaign_name, campaign_type, campaign_state, is_campaign_active, campaign_created_dt

    def is_terminate_state(self, campaign_state):
        return True if campaign_state not in ["SEGMENT_CALCULATING", "VERIFY_PROCESSING", "SCHEDULED",
                                              "SENDING_PROCESSING", "EFFICIENCY_ANALYSIS", "GROUPS_CALCULATING",
                                              "SEGMENT_CANCELLING"] else False

    def can_terminate(self, campaign_type, campaign_state):
        if (campaign_state == "SEGMENT_CALCULATING") or (
                campaign_state in ["VERIFY_PROCESSING", "SCHEDULED", "SENDING_PROCESSING", "EFFICIENCY_ANALYSIS"]
                and campaign_type == "oneshot"):
            return True
        else:
            return False

    def can_stop(self, campaign_type, is_campaign_active):
        return True if (campaign_type == "regular") and is_campaign_active else False

    def open_campaign_list(self):
        self.session.get(self.api_url + '/v1/config')  # get config
        self.session.get(self.api_url + '/v1/dictionaries/campaign_types')  # get campaign_types
        self.session.get(self.api_url + '/v1/dictionaries/audiences')  # get audiences
        list_payload = {"offset": 0, "limit": 50, "owner": "", "trend": ""}
        self.session.post(self.api_url + '/v1/campaigns/list', json=list_payload)  # get campaigns_list
        self.session.get(self.api_url + '/v1/dictionaries/ticket_states')  # get ticket_states

    def get_segment_versions_for_audience(self, audience):
        self.session.get(self.api_url + f'/v1/quicksegment/versions?audience={audience}')  # segment_versions

    def get_channels_for_audience(self, audience):
        channels = self.session.get(self.api_url + f'/v1/dictionaries/channels?entity={audience}')
        return channels

    def create_campaign(self, audience, campaign_type, campaign_name, start, end, efficiency=False, com_politic=False,
                        segment_version="1", global_control=True):
        if campaign_type == "oneshot":
            if audience == "Driver":
                campaign_payload = {
                    "campaign_type": campaign_type,
                    "discount": False,
                    "global_control": global_control,
                    "efficiency": efficiency,
                    "trend": "tariff_and_money",
                    "com_politic": com_politic,
                    "qs_schema_version": segment_version,
                    "entity": audience,
                    "name": campaign_name,
                    "specification": "test campaign description",
                    "kind": "tariff_in_city",
                    "subkind": "econom",
                    "efficiency_start_time": start,
                    "efficiency_stop_time": end
                }
            elif audience == "User":
                campaign_payload = {
                    "campaign_type": campaign_type,
                    "discount": False,
                    "global_control": global_control,
                    "efficiency": efficiency,
                    "trend": "technical_comm",
                    "com_politic": com_politic,
                    "qs_schema_version": segment_version,
                    "entity": audience,
                    "name": campaign_name,
                    "specification": "test campaign description",
                    "efficiency_start_time": start,
                    "efficiency_stop_time": end
                }
            elif audience == "LavkaUser":
                campaign_payload = {
                    "campaign_type": campaign_type,
                    "discount": False,
                    "global_control": global_control,
                    "efficiency": efficiency,
                    "trend": "lavka_marketing",
                    "com_politic": com_politic,
                    "qs_schema_version": segment_version,
                    "entity": audience,
                    "name": campaign_name,
                    "specification": "test campaign description",
                    "efficiency_start_time": start,
                    "efficiency_stop_time": end
                }
            elif audience == "Geo":
                campaign_payload = {
                    "campaign_type": campaign_type,
                    "discount": False,
                    "global_control": global_control,
                    "efficiency": efficiency,
                    "trend": "geo",
                    "com_politic": com_politic,
                    "qs_schema_version": segment_version,
                    "entity": audience,
                    "name": campaign_name,
                    "specification": "test campaign description",
                    "efficiency_start_time": start,
                    "efficiency_stop_time": end
                }
            else:
                campaign_payload = {"campaign_type": campaign_type,
                                    "discount": False,
                                    "global_control": global_control,
                                    "efficiency": efficiency,
                                    "trend": "eda",
                                    "com_politic": com_politic,
                                    "qs_schema_version": segment_version,
                                    "entity": audience,
                                    "name": campaign_name,
                                    "specification": "test campaign description",
                                    "efficiency_start_time": start,
                                    "efficiency_stop_time": end
                                    }
        elif campaign_type == "regular":
            if audience == "Driver":
                campaign_payload = {
                    "campaign_type": campaign_type,
                    "discount": False,
                    "global_control": global_control,
                    "efficiency": efficiency,
                    "trend": "tariff_and_money",
                    "com_politic": com_politic,
                    "qs_schema_version": segment_version,
                    "entity": audience,
                    "name": campaign_name,
                    "specification": "test campaign description",
                    "kind": "tariff_in_city",
                    "subkind": "econom",
                    "schedule": "0 12 * * *",
                    "regular_start_time": start,
                    "regular_stop_time": end
                }
            elif audience == "User":
                campaign_payload = {
                    "campaign_type": campaign_type,
                    "discount": False,
                    "global_control": global_control,
                    "efficiency": efficiency,
                    "trend": "technical_comm",
                    "com_politic": com_politic,
                    "qs_schema_version": segment_version,
                    "entity": audience,
                    "name": campaign_name,
                    "specification": "test campaign description",
                    "schedule": "0 12 * * *",
                    "regular_start_time": start,
                    "regular_stop_time": end
                }
            elif audience == "LavkaUser":
                campaign_payload = {
                    "campaign_type": campaign_type,
                    "discount": False,
                    "global_control": global_control,
                    "efficiency": efficiency,
                    "trend": "lavka_tech",
                    "com_politic": com_politic,
                    "qs_schema_version": segment_version,
                    "entity": audience,
                    "name": campaign_name,
                    "specification": "test campaign description",
                    "schedule": "0 12 * * *",
                    "regular_start_time": start,
                    "regular_stop_time": end
                }
            elif audience == "Geo":
                campaign_payload = {
                    "campaign_type": campaign_type,
                    "discount": False,
                    "global_control": global_control,
                    "efficiency": efficiency,
                    "trend": "geo",
                    "com_politic": com_politic,
                    "qs_schema_version": segment_version,
                    "entity": audience,
                    "name": campaign_name,
                    "specification": "test campaign description",
                    "schedule": "0 12 * * *",
                    "regular_start_time": start,
                    "regular_stop_time": end
                }
            else:
                campaign_payload = {"campaign_type": campaign_type,
                                    "discount": False,
                                    "global_control": global_control,
                                    "efficiency": efficiency,
                                    "trend": "eda",
                                    "com_politic": com_politic,
                                    "qs_schema_version": segment_version,
                                    "entity": audience,
                                    "name": campaign_name,
                                    "specification": "test campaign description",
                                    "schedule": "0 12 * * *",
                                    "regular_start_time": start,
                                    "regular_stop_time": end
                                    }
        campaign = self.session.post(self.api_url + '/v1/campaigns/item', json=campaign_payload)
        campaign_json = campaign.json()
        campaign_id = campaign_json["id"]
        if audience == "Driver":
            # Создание тикета на креатив
            self.session.post(self.api_url + f'/v1/process/creative?id={campaign_id}')  # creative_ticket
            # TODO добавить проверку на комментарии, кнопки и призывы в тикете
            # creative_ticket_id = creative_ticket.json()["data"]
        return campaign

    def get_campaign(self, campaign_id):
        return self.session.get(self.api_url + f'/v1/campaigns/item?id={campaign_id}')

    def get_campaign_ticket_id(self, campaign_id):
        campaign = self.get_campaign(campaign_id)
        campaign_json = campaign.json()
        return campaign_json["ticket"]

    def get_campaign_results(self, campaign_id):
        return self.session.get(self.api_url + f'/v2/campaigns/results?campaign_id={campaign_id}')

    def get_campaign_stats(self, campaign_id):
        return self.session.get(self.api_url + f'/v1/campaigns/stat/?id={campaign_id}')

    def get_regular_campaign_stats(self, campaign_id):
        return self.session.get(self.api_url + f'/v1/regular-campaigns/stat/?campaign_id={campaign_id}')

    def get_segment_data(self, campaign_id):
        self.session.get(self.api_url + f'/v1/quicksegment/input-schema?campaign_id={campaign_id}')  # segment_filters
        self.session.get(self.api_url + f'/v1/campaigns/filters?id={campaign_id}')  # campaign_filters
        self.session.get(self.api_url + f'/v1/dictionaries/hierarchy_countries')  # hierarchy_countries

    def set_segment(self, campaign_id, audience, segment_type):
        if audience == "Driver":
            self.session.get(self.api_url + f'/v1/dictionaries/hierarchy_zones')  # hierarchy_zones
            if segment_type == "2KK":
                filters_payload = '[{"fieldId":"country","value":["br_russia"]},' \
                                  '{"fieldId":"node_id","value":[]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"executor_type","value":["driver"]},' \
                                  '{"fieldId":"app","value":"taximeter"},' \
                                  '{"fieldId":"communicated_days","value": 90},' \
                                  '{"fieldId":"newcomer","value":"exclude"}]'
            elif segment_type == "300K":
                filters_payload = '[{"fieldId":"country","value":["br_russia"]},' \
                                  '{"fieldId":"node_id","value":["br_moscow","br_saintpetersburg","br_ekaterinburg"]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"executor_type","value":["driver"]},' \
                                  '{"fieldId":"app","value":"taximeter"},' \
                                  '{"fieldId":"communicated_days","value": 90},' \
                                  '{"fieldId":"newcomer","value":"exclude"}]'
            elif segment_type == "200K":
                filters_payload = '[{"fieldId":"country","value":["br_russia"]}' \
                                  ',{"fieldId":"node_id","value":["br_moscow"]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"executor_type","value":["driver"]},' \
                                  '{"fieldId":"app","value":"taximeter"},' \
                                  '{"fieldId":"communicated_days","value": 90},' \
                                  '{"fieldId":"newcomer","value":"exclude"}]'
            elif segment_type == "100K":
                filters_payload = '[{"fieldId":"country","value":["br_russia"]},' \
                                  '{"fieldId":"node_id","value":["br_saintpetersburg","br_ekaterinburg"]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"executor_type","value":["driver"]},' \
                                  '{"fieldId":"app","value":"taximeter"},' \
                                  '{"fieldId":"communicated_days","value": 90},' \
                                  '{"fieldId":"newcomer","value":"exclude"}]'
            else:
                filters_payload = '[{"fieldId":"country","value":["br_russia"]}' \
                                  ',{"fieldId":"node_id","value":["br_moscow"]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"executor_type","value":["driver"]},' \
                                  '{"fieldId":"app","value":"taximeter"},' \
                                  '{"fieldId":"communicated_days","value": 90},' \
                                  '{"fieldId":"newcomer","value":"exclude"}]'
        elif audience == "User":
            self.session.get(self.api_url + f'/v1/dictionaries/hierarchy_agglomerations')  # hierarchy_agglomerations
            self.session.get(self.api_url + f'/v1/dictionaries/hierarchy_agglomerations?countries=br_russia')  # hierarchy_agglomerations_country
            if segment_type == "2KK":
                filters_payload = '[{"fieldId":"country","value":["br_russia"]},' \
                                  '{"fieldId":"city","value":["br_saintpetersburg"]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"brand","value":"yandex"},' \
                                  '{"fieldId":"active_taxi","value":"off"},' \
                                  '{"fieldId":"communicated_days","value": 90}]'
            elif segment_type == "300K":
                filters_payload = '[{"fieldId":"country","value":["br_russia"]},' \
                                  '{"fieldId":"city","value":["br_sochi"]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"brand","value":"yandex"},' \
                                  '{"fieldId":"active_taxi","value":"off"},' \
                                  '{"fieldId":"communicated_days","value": 90}]'

            elif segment_type == "200K":
                filters_payload = '[{"fieldId":"country","value":["br_russia"]},' \
                                  '{"fieldId":"city","value":["br_kaliningrad"]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"brand","value":"yandex"},' \
                                  '{"fieldId":"active_taxi","value":"off"},' \
                                  '{"fieldId":"communicated_days","value": 90}]'
            elif segment_type == "100K":
                filters_payload = '[{"fieldId":"country","value":["br_russia"]},' \
                                  '{"fieldId":"city","value":["br_tula"]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"brand","value":"yandex"},' \
                                  '{"fieldId":"active_taxi","value":"off"},' \
                                  '{"fieldId":"communicated_days","value": 90}]'
            else:
                filters_payload = '[{"fieldId":"country","value":["br_russia"]},' \
                                  '{"fieldId":"city","value":["br_moscow"]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"brand","value":"yandex"},' \
                                  '{"fieldId":"active_taxi","value":"off"},' \
                                  '{"fieldId":"communicated_days","value": 90}]'
        elif audience == "LavkaUser":
            self.session.get(self.api_url + f'/v1/dictionaries/hierarchy_agglomerations')  # hierarchy_agglomerations
            self.session.get(self.api_url + f'/v1/dictionaries/hierarchy_agglomerations?countries=br_russia')  # hierarchy_agglomerations_country
            if segment_type == "100K":
                filters_payload = '[{"fieldId":"country","value":["br_russia"]},' \
                                  '{"fieldId":"city","value":["br_nizhny_novgorod","br_ekaterinburg","br_perm"]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"brand","value":"lavka"},' \
                                  '{"fieldId":"active_taxi","value":"active"},' \
                                  '{"fieldId":"active_taxi_interval","value":"12_weeks"},' \
                                  '{"fieldId":"communicated_days","value": 90}]'
            else:
                filters_payload = '[{"fieldId":"country","value": ["br_russia"]},' \
                                  '{"fieldId":"city","value":[]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"brand","value":"lavka"},' \
                                  '{"fieldId":"active_taxi","value":"active"},' \
                                  '{"fieldId":"active_taxi_interval","value":"12_weeks"},' \
                                  '{"fieldId":"communicated_days","value": 90}]'
        elif audience == "Geo":
            self.session.get(self.api_url + f'/v1/dictionaries/hierarchy_agglomerations')  # hierarchy_agglomerations
            self.session.get(self.api_url + f'/v1/dictionaries/hierarchy_agglomerations?countries=br_russia')  # hierarchy_agglomerations_country
            if segment_type == "100K":
                filters_payload = '[{"fieldId":"country","value":["br_russia"]},' \
                                  '{"fieldId":"city","value":["br_kazan", "br_ekaterinburg", "br_perm"]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"communicated_days","value": 90}]'
            else:
                filters_payload = '[{"fieldId":"country","value":["br_russia"]},' \
                                  '{"fieldId":"city","value":["br_saintpetersburg_adm"]},' \
                                  '{"fieldId":"city_exclude","value":[]},' \
                                  '{"fieldId":"communicated_days","value": 90}]'
        else:  # EatsUser
            self.session.get(self.api_url + f'/v1/dictionaries/hierarchy_agglomerations')  # hierarchy_agglomerations
            self.session.get(self.api_url + f'/v1/dictionaries/hierarchy_agglomerations?countries=br_russia')  # hierarchy_agglomerations_country
            if segment_type == "300K":
                filters_payload = '[{"fieldId":"f_country","value":["br_russia"]},' \
                                  '{"fieldId":"f_city","value":["br_kazan","br_ekaterinburg"]},' \
                                  '{"fieldId":"f_city_exclude","value":[]}]'
            else:
                filters_payload = '[{"fieldId":"country","value":["br_russia"]},' \
                                  '{"fieldId":"city","value":["br_moscow"]},' \
                                  '{"fieldId":"city_exclude","value":[]}]'
        self.session.put(self.api_url + f'/v1/campaigns/filters?id={campaign_id}', data=filters_payload)  # filters_put

    def start_segment_calculations(self, campaign_id):
        self.session.post(self.api_url + f'/v1/process/segment?id={campaign_id}')  # segment_post

    def get_segment_stats(self, campaign_id):
        return self.session.get(self.api_url + f'/v1/campaigns/stat?id={campaign_id}')

    def set_groups(self, campaign_id, test_groups, mode="Filter", control=10):
        # TODO cделать для остальных modes, кроме Filter

        groups = [{"name": "Default", "state": "NEW", "limit": 0, "cities": [], "locales": []}]
        for test_group in test_groups:
            new_group = {"name": test_group["name"],
                         "state": "NEW",
                         "limit": test_group["limit"],
                         "cities": [],
                         "locales": []
                         }
            groups.append(new_group)

        groups_payload = {"mode": mode,
                          "control": control,
                          "groups": groups
                          }

        self.session.post(self.api_url + f'/v1/campaigns/groups/item?id={campaign_id}', json=groups_payload)  # create_groups

    def get_groups(self, campaign_id):
        return self.session.get(self.api_url + f'/v1/campaigns/groups/item?id={campaign_id}')

    def start_groups_calculating(self, campaign_id):
        self.session.post(self.api_url + f'/v1/process/groups?id={campaign_id}')  # process_groups

    def get_group_id(self, campaign_id, group_name):
        groups_info = self.get_groups(campaign_id)
        groups = groups_info.json()["groups"]
        for group in groups:
            if group["name"] == group_name:
                group_id = int(group["id"])
        assert group_id is not None, "There is no group with that name"
        return group_id

    def get_all_groups_id(self, campaign_id):
        groups_info = self.get_groups(campaign_id)
        groups = groups_info.json()["groups"]
        groups_id = []
        for group in groups:
            # по умолчанию не считаем основную группу, так как мы ее не отправляем
            if group['name'] != 'Default':
                groups_id.append(group['id'])
        return groups_id

    def send_groups(self, campaign_id, groups_names):
        groups_ids = []
        for group_name in groups_names:
            group_id = self.get_group_id(campaign_id, group_name)
            groups_ids.append(group_id)
        send_groups_payload = {"group_ids": groups_ids, "final": True}
        self.session.post(self.api_url + f'/v1/process/send?id={campaign_id}', json=send_groups_payload)  # send_groups

    def verify_groups(self, campaign_id, group_names, audience, test_users, test_drivers, test_geo_users):
        group_ids = []
        for group_name in group_names:
            group_id = self.get_group_id(campaign_id, group_name)
            group_ids.append(group_id)
        if audience == "Driver":
            test_data = '['
            for test_driver in test_drivers:
                test_data = test_data + f'"{test_driver}",'
            test_data = test_data[:-1] + ']'
        elif audience == "User" or audience == "EatsUser" or audience == "LavkaUser":
            test_data = '['
            for test_user in test_users:
                test_data = test_data + f'"{test_user}",'
            test_data = test_data[:-1] + ']'
        elif audience == "Geo":
            test_data = '['
            for test_geo in test_geo_users:
                test_data = test_data + f'"{test_geo}",'
            test_data = test_data[:-1] + ']'
        self.session.put(self.api_url + f'/v1/campaigns/test_users?id={campaign_id}', data=test_data)  # put_test_users
        groups_to_test = '['
        for group_id in group_ids:
            groups_to_test = groups_to_test + f'{group_id},'
        groups_to_test = groups_to_test[:-1] + ']'
        self.session.post(self.api_url + f'/v1/process/verify?id={campaign_id}', data=groups_to_test)  # verify_group

    def save_schedule(self, campaign_id, start, end, schedule):
        schedule_payload = {
            "efficiency_start_time": start,
            "efficiency_stop_time": end,
            "schedule": schedule
        }
        self.session.put(self.api_url + f'/v1/campaigns/schedule?id={campaign_id}', json=schedule_payload)  # save_schedule

    def start_regular_campaign(self, campaign_id):
        # start_campaign = self.session.post(self.api_url + f'/v1/regular-campaigns/start/?campaign_id={campaign_id}')
        self.session.post(self.api_url + f'/v1/campaigns/apply_draft/?campaign_id={campaign_id}')  # start_campaign

    def approve_idea_in_ticket(self, ticket_id):
        # TODO добавить проверку на комментарии, кнопки и призывы в тикете
        self.startrack_session.get(self.startrack_url + f"/issues/{ticket_id}/transitions")  # workflow_statuses
        self.startrack_session.post(self.startrack_url + f"/issues/{ticket_id}/transitions/inProgress/_execute")

    def summon_approver(self, campaign_id):
        # TODO добавить проверку на комментарии, кнопки и призывы в тикете
        self.session.post(self.api_url + f'/v1/process/summon_approver?id={campaign_id}')

    def approve_sending(self, ticket_id):
        self.startrack_session.post(
            self.startrack_url + f"/issues/{ticket_id}/transitions/agreed/_execute")
        # workflow_statuses = startrack_session.get(startrack_url + f"/issues/{ticket_id}/transitions")

    def verify_com_policy(self, stats_json, is_com_politics, campaign_id, group_ids, audience):
        # Для водителей политика контактов всегда отключена.
        # Для пользователей - независимо от того вкл/выкл, политика все равно не пустая. И даже blocked будет ненулевым.
        policy_stats = stats_json["policy"]
        if audience == "Driver":
            assert policy_stats == {}, "Not empty policy"
        else:
            assert policy_stats != {}, "Empty policy"
            groups_info = self.get_groups(campaign_id)
            groups = groups_info.json()["groups"]
            for group in groups:
                if group['id'] in group_ids:
                    group_channel = group['channel']
                    group_channel = (audience + '_' + group_channel).lower().replace('.', '_')
                    assert group_channel in policy_stats.keys(), f"Channel {group_channel} is not in policy statistics"
                    channel_stat = policy_stats[group_channel]
                    blocked_size = channel_stat['blocked_size']
                    total_size = stats_json['size']
                    assert blocked_size <= total_size, f"Policy blocked is {blocked_size}, but total size is {total_size}"

    def verify_general_segment_stat(self, stats_json, audience, segment_version, is_global_control, control=10):
        total_size = stats_json["size"]
        total_global_control = stats_json["global_control"]
        total_control = stats_json["control"]
        if audience == "Driver":
            total_unique_drivers = stats_json["unique_drivers"]
            total_global_control_unique_drivers = stats_json["global_control_unique_drivers"]
        if segment_version == '1':  # тестовый сегмент
            assert total_size < 10, f"Expected less than 10 users in test segment, but got {total_size}"
            assert total_global_control == 0, f"Expected empty global control for test segment, but got {total_global_control}"
            if audience == "Driver":
                assert total_unique_drivers < 10, f"Expected less than 10 unique drivers in test segment, but got {total_unique_drivers}"
                assert total_global_control_unique_drivers == 0, f"Expected empty global control for unique drivers for test segment, but got {total_global_control}"
        else:
            assert total_size > 100000  # считаем что в сегменте (не-тестовом), который создается по умолчанию, более 100 000 водителей/пользователей
            if audience == "Driver":
                assert total_unique_drivers <= total_size, f"Total drivers: {total_size}, total unique drivers: {total_unique_drivers}"
            if is_global_control:
                assert total_global_control < total_size, f"Global control is greater than total size of segment"
                if audience == "Driver":
                    total_global_control_unique_drivers <= total_global_control, \
                    f"Global control: {total_global_control}, " \
                    f"global control for unique drivers: {total_global_control_unique_drivers}"
            else:
                assert total_global_control == 0
        assert total_control == control, f"Expected control in test segment: {control}, but got {total_control}"

    def get_columns(self, campaign_id):
        # все колонки сегмента, поля для выгрузки шаблона
        coloumns = self.session.get(self.api_url + f'/v1/process/extra_data/columns/?id={campaign_id}')
        columns = list(coloumns.json())
        return columns

    def get_placeholders(self, campaign_id):
        # доступные сейчас параметры персонализации
        placeholders = self.session.get(self.api_url + f'/v1/process/extra_data/placeholders/?id={campaign_id}')
        placeholders = list(placeholders.json())
        return placeholders

    def get_path_to_extradata(self, api_type, campaign_id, column):
        smth = {"path": f'//home/taxi/testing/features/crm-admin/segments/{api_type}/cmp_{campaign_id}_extra_data',
                "key_column": f'{column}'}

        self.session.post(self.api_url + f'/v1/process/extra_data/path/?id={campaign_id}', json=smth)

    def download_file(self, campaign_id, column, filename, fileformat):
        fileweb = self.session.get(
            self.api_url + f'/v1/process/extra_data/csv?id={campaign_id}&column={column}&format={fileformat}')
        with open(filename, 'w') as f:
            f.write(fileweb.text)

    def send_file(self, campaign_id, filename):
        # загрузить файл в crm
        with open(filename, 'rb') as f:
            self.session.post(self.api_url + f'/v1/process/extra_data/csv/?id={campaign_id}', files={"file": f})

    def count_groups_amount(self, campaign_id, groups_id, count=0):
        # узнать кол-во коммуникаций на отправку в группе
        response = self.get_groups(campaign_id)
        groups = response.json()['groups']
        for group in groups:
            if group['id'] in groups_id:
                # все коммуникации в группе
                count += group['limit']
        return count

    def check_logs_experiments(self, comms, campaign_id, group_id):
        groups = self.get_groups(campaign_id)
        control_percent = groups.json()['control']
        campaign = self.get_campaign(campaign_id)
        global_control = campaign.json()['global_control']

        # делаем словарь для удобства
        amount = {}
        for row in comms:
            if row[0] == '0_global_control':
                row[0] = '0_global'

            try:
                amount[row[0]] += int(row[2])
            except KeyError:
                amount[row[0]] = int(row[2])

            # проверяем, что для контролей стоит значение control, для отправок - testing
            # закоментировано, потому что сейчас это не пишется в логи
            # if campaign.json()['entity'] != "User":
            #     if (row[0] == '0_control') or (row[0] == '0_global'):
            #         assert row[1] == ['control']
            #     else:
            #         assert row[1] == ['testing']

        # считаем сумму отправок в рамках кампании (из crm-admin)
        group_limit = {}

        groups_info = self.get_groups(campaign_id)
        groups = groups_info.json()["groups"]
        for group in groups:
            if group['id'] == group_id:
                # group_channel = group['channel']
                group_limit[group['id']] = int(group['computed']['total'])

        assert sum(group_limit.values()) == sum(amount.values()), f"The actual and expected amount do not match. " \
                                                                  f"Expected:{sum(group_limit.values())}. " \
                                                                  f"Actual {sum(amount.values())}"

        # если глобальный контроль true, то он есть в логах
        # глобальный контроль должен быть 5 процентов по умолчанию
        if global_control:
            # для маленьких групп не считаем доли
            if sum(group_limit.values()) > 20:
                assert ('0_global' in amount) and amount['0_global'], f"There is no global control comms, but it should be"
                global_percent_fact = amount['0_global'] / sum(group_limit.values())
                if round(global_percent_fact, 2) * 100 != 5:
                    assert abs(round(global_percent_fact, 2) * 100 - 5) < 3, f"Incorrect percentage of global control. " \
                                                                             f"Percentage of global control is  " \
                                                                             f"not equal to 5, it's " \
                                                                             f"{round(global_percent_fact, 2) * 100}."
        # раскоментить после того, как будет готов TAXICRMDEV - 1671
        # else:
        #     assert not ('0_global' in amount)

        # если локальный контроль не ноль, то он есть в логах
        # проверка, что ожидаемое кол-во локального контроля и фактическое равны
        if control_percent:
            # для маленьких групп не считаем доли
            if sum(group_limit.values()) > 20:
                assert ('0_control' in amount) and amount['0_control'], f"There is no control comms, but they should be"
                control_percent_fact = amount['0_control'] / sum(group_limit.values())
                if round(control_percent_fact, 2) * 100 != int(groups_info.json()["control"]):
                    assert (round(control_percent_fact, 2) * 100 - int(groups_info.json()["control"]) < 3), \
                        f"Incorrect percentage of control. Percentage {round(control_percent_fact, 2) * 100} " \
                        f"of control is not equal to expected value {int(groups_info.json()['control'])}."
        # раскоментить после того, как будет готов TAXICRMDEV - 1671
        # else:
        #     assert not ('0_control' in amount)

            # округление до двух единиц фактической доли контролей, так как разбиение примерное

    def create_creatives(self, campaign_id, name, audience, channel, text_content=""):

        params = {}

        if audience == "Driver":
            if channel == "PUSH":
                params.update({"channel_name": "driver_push", "content": text_content, "code": 1300, "need_notification": True})
            elif channel == "SMS":
                params.update({"channel_name": "driver_sms", "content": text_content, "intent": "taxicrm_drivers", "sender": "taxi"})
            else:
                # TODO: сделать настройки для остальных водительских каналов
                pass

        elif audience == "User":
            if channel == "PUSH":
                params.update({"channel_name": "user_push", "content": text_content})
            elif channel == "SMS":
                params.update({"channel_name": "user_sms", "content": text_content, "intent": "taxicrm_users", "sender": "go"})
            elif channel == "promo.fs":
                params.update(
                    {"channel_name": "user_promo_fs", "content": "f55edb902b0a4176b15c9b4722aad942", "days_count": 1, "time_until": "23:59"})
            elif channel == "promo.notification":
                params.update(
                    {"channel_name": "user_promo_notification", "content": "db9bb0145fdc4fe0a8a38a83338251b1", "days_count": 1, "time_until": "23:59"})
            elif channel == "promo.card":
                params.update(
                    {"channel_name": "user_promo_card", "content": "80c17bd0d7824ab0ab4e2dc80ffc6e52", "days_count": 1, "time_until": "23:59"})

        elif audience == "EatsUser":
            if channel == "PUSH":
                params.update(
                    {"channel_name": "eatsuser_push", "content": text_content})
            elif channel == "SMS":
                params.update({"channel_name": "eatsuser_sms", "content": text_content, "sender": "eda", "intent": "taxicrm_eda_users_retail"})

        elif audience == "LavkaUser":
            if channel == "PUSH":
                params.update(
                    {"channel_name": "lavkauser_push", "content": text_content})
            elif channel == "SMS":
                params.update(
                    {"channel_name": "lavkauser_sms", "content": text_content, "intent": "grocery_admin_preset_message", "sender": "lavka"})
            elif channel == "promo.fs":
                params.update(
                    {"channel_name": "lavkauser_promo_fs", "content": "f55edb902b0a4176b15c9b4722aad942", "days_count": 1, "time_until": "23:59"})
            elif channel == "promo.notification":
                params.update(
                    {"channel_name": "lavkauser_promo_notification", "content": "db9bb0145fdc4fe0a8a38a83338251b1", "days_count": 1, "time_until": "23:59"})
            elif channel == "promo.card":
                params.update(
                    {"channel_name": "lavkauser_promo_card", "content": "80c17bd0d7824ab0ab4e2dc80ffc6e52", "days_count": 1, "time_until": "23:59"})

        elif audience == "Geo":
            if channel == "PUSH":
                params.update(
                    {"channel_name": "geo_push", "content": text_content})
            else:
                pass

        creatives_settings = {"name": name, "params": params}
        return self.session.post(self.api_url + f'/v1/creatives/?campaign_id={campaign_id}', json=creatives_settings)

    def set_group_send_settings(self, campaign_id, group_name, creative_id, efficiency):
        group_id = self.get_group_id(campaign_id, group_name)

        start = datetime.datetime.now(datetime.timezone.utc)
        start_date = start.strftime('%Y-%m-%d')
        start_time = start.strftime('%H:%M')
        end = start + datetime.timedelta(hours=5)
        end_date = end.strftime('%Y-%m-%d')
        end_time = end.strftime('%H:%M')

        group_send_settings = {"id": group_id, "creative_id": creative_id}

        if efficiency:
            group_send_settings.update(
                {"efficiency_date": [start_date, end_date], "efficiency_time": [start_time, end_time]})

        all_groups_send_settings = [group_send_settings]
        self.session.put(self.api_url + f'/v2/campaigns/groups/item?id={campaign_id}', json=all_groups_send_settings)  # set_group_send_settings

    def setup_creatives(self, campaign_id, channel, audience, groups_count, comm_text):
        creatives_list = []
        if channel == "random":
            available_channels = self.channels_for_audience(audience)

            # веса для рандома выбора каналов (у SMS вес ниже других, чтобы он реже выбирался)
            channels_weight = []
            for i, channel in enumerate(available_channels):
                channels_weight.append(10)
                if channel == "SMS":
                    channels_weight[i] -= 5

            for i in range(groups_count):
                random_channel = random.choices(available_channels, channels_weight)[0]
                creative_info = self.create_creatives(campaign_id, f"{random_channel}. креатив", audience,
                                                      random_channel, comm_text)
                creatives_list.append(creative_info.json())
        else:
            for i in range(groups_count):
                creative_info = self.create_creatives(campaign_id, f"{channel}. креатив", audience, channel,
                                                      comm_text)
                creatives_list.append(creative_info.json())
        return creatives_list

    def channels_for_audience(self, audience):
        # возвращает список поддерживаемых каналов для аудитории
        unsupported_channels = ['LEGACYWALL', 'DEVNULL']
        channels_for_audience = self.get_channels_for_audience(audience)
        channels = []
        for channel in channels_for_audience.json():
            if not (channel['value'] in unsupported_channels):
                channels.append(channel['value'])
        return channels

    # может оно не нужно?
    # def channels_list(self, channel, audience):
    #     # возвращает список поддерживаемых каналов для аудитории
    #     # или список из одного канала, если канал передан в параметрах кампании
    #     channels_list = []
    #     if channel == "random":
    #         channels_list = self.channels_for_audience(audience)
    #     else:
    #         channels_list.append(channel)
    #     return channels_list
