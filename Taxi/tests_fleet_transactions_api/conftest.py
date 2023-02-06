import json

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from fleet_transactions_api_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(name='driver_profiles')
def _driver_profiles(mockserver, load_json):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_retrieve(request):
        def make_not_found(park_driver_profile_id):
            return {
                'revision': '0_1234567_0',
                'park_driver_id': park_driver_profile_id,
                'park_driver_profile_id': park_driver_profile_id,
            }

        profiles = {
            profile['park_driver_profile_id']: profile
            for profile in load_json('driver_profiles.json')
        }
        ids = json.loads(request.get_data())['id_in_set']
        return {
            'profiles': [profiles.get(id, make_not_found(id)) for id in ids],
        }


class BillingOrdersContext:
    def __init__(self):
        self.sent_event_ats = set()

    def add_event_ats(self, event_ats):
        self.sent_event_ats |= set(event_ats)

    def get_event_ats(self):
        return self.sent_event_ats


@pytest.fixture(name='billing_orders')
def _billing_orders(mockserver, load_json):
    context = BillingOrdersContext()

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def _mock_billing_orders(request):
        data = json.loads(request.get_data())
        orders = data['orders']
        context.add_event_ats(order['event_at'] for order in orders)

        request_topics = [
            order['topic']
            for order in json.loads(request.get_data())['orders']
        ]
        response_json = load_json('orders_response.json')
        response_json['orders'] = [
            order
            for order in response_json['orders']
            if order['topic'] in request_topics
        ]
        return response_json

    return context


class BillingReportsContext:
    def __init__(self):
        self.entries = []
        self.page_size = 2
        self.request_json = {}

    def get_request_subaccounts(self):
        return [acc['sub_account'] for acc in self.request_json['accounts']]


@pytest.fixture(name='billing_reports')
def _billing_reports_context(mockserver, load_json):
    context = BillingReportsContext()

    @mockserver.json_handler('/billing-reports/v2/journal/select')
    def _mock_billing(request):
        """billing paginated response"""
        data = request.json
        assert data['accounts'][0]['currency'] == 'RUB'

        context.request_json = data
        page_number = int(data.get('cursor') or '0')
        all_entries = context.entries
        start = context.page_size * page_number
        end = context.page_size * (page_number + 1)
        page_entries = all_entries[start:end]
        response = {'entries': page_entries}
        if end < len(all_entries):
            response['cursor'] = str(page_number + 1)
        return response

    return context


@pytest.fixture(name='fleet_parks')
def _fleet_parks(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_v1_parks_list(request):
        return {
            'parks': [
                {
                    'city_id': 'Берлин',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'id': '8601e1f8e094424aa70c81b61ffdf01f',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'ru',
                    'login': 'login',
                    'name': 'name',
                },
            ],
        }
