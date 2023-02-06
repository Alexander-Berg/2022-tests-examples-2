# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import datetime

from driver_work_modes_plugins import *  # noqa: F403 F401
import pytest

from tests_driver_work_modes import utils


@pytest.fixture
def driver_profiles(mockserver, load_json):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_retrieve(request):
        profiles = load_json('driver_profiles.json')
        target_driver_ids = request.json.get('id_in_set', None)

        data = {x['park_driver_profile_id']: x for x in profiles}
        assert len(data) == len(profiles)

        return {
            'profiles': [
                {
                    'park_driver_profile_id': park_driver_id,
                    **data.get(park_driver_id, {}),
                }
                for park_driver_id in target_driver_ids
            ],
        }

    return _mock_retrieve


@pytest.fixture
def driver_orders(mockserver):
    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    def mock_parks_orders_list(request):
        assert request.json['limit'] == 1

        driver_id = request.json['query']['park']['driver_profile']['id']

        response_order = {}
        latest_date = datetime.datetime(1, 1, 1)
        request_at_datetime = datetime.datetime.strptime(
            request.json['query']['park']['order']['booked_at']['to'],
            '%Y-%m-%dT%H:%M:%S+00:00',
        )

        for order in utils.RESULT_ORDERS:
            if (
                    'driver_profile' in order
                    and 'id' in order['driver_profile']
                    and order['driver_profile']['id'] == driver_id
                    and 'booked_at' in order
            ):
                order_datetime = datetime.datetime.strptime(
                    order['booked_at'], '%Y-%m-%dT%H:%M:%S+00:00',
                )
                if request_at_datetime > order_datetime > latest_date:
                    response_order = order
                    latest_date = order_datetime

        return {
            'orders': [response_order] if response_order else [],
            'limit': 1,
        }

    return mock_parks_orders_list
