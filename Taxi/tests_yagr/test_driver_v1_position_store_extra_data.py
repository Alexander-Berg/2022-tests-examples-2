# pylint: disable=import-error

import datetime
import random

from dap_tools.dap import dap_fixture  # noqa: F401 C5521
import pytest


def check_polling_header(header):
    parts = header.split(', ')
    parts.sort()
    assert parts == [
        'background=1200s',
        'full=600s',
        'idle=1800s',
        'powersaving=1200s',
    ]


@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_extra_data_send_to_logbroker(
        taxi_yagr_adv, dap, redis_store, testpoint, user_agent, app_family,
):
    @testpoint('write-extra-data-to-yt-logger')
    def testpoint_extra_data(data):
        pass

    park_id = 'park1'
    driver_id = 'driver1'
    taxi_yagr_adv = dap.create_driver_wrapper(
        taxi_yagr_adv,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )
    data = {}

    random.seed(42)

    def generate_satellite_item():
        item = {}
        item['elevation'] = random.uniform(0, 5)
        item['azimuth'] = random.randint(0, 300)
        item['cn0'] = random.uniform(0, 5)
        item['constellation'] = random.randint(0, 10)
        item['svid'] = random.randint(0, 10)
        return item

    def generate_wifi_item():
        item = {}
        item['mac'] = '01:23:45:67:AB:CD'
        item['sigstr'] = random.randint(-100, 0)
        return item

    def generate_cell_item():
        item = {}
        item['cell_id'] = random.randint(0, 1000)
        item['country_code'] = 'ru'
        item['lac'] = random.randint(0, 100)
        item['operator_id'] = 'Yandex Mobile'
        item['sigstr'] = random.randint(-100, 0)
        return item

    def generate_items(item_generator):
        items_count = random.randint(2, 3)
        items = []
        for _ in range(items_count):
            item = {}
            unix_ts = int(
                datetime.datetime(
                    2019, 9, 11, 13, 42, random.randint(0, 59),
                ).timestamp()
                * 1000,
            )
            item['unix_timestamp'] = unix_ts
            item['data'] = [
                item_generator() for i in range(random.randint(2, 3))
            ]
            items.append(item)
        return items

    def generate_payload():
        payload = {}
        payload['satellites'] = generate_items(generate_satellite_item)
        payload['wifi'] = generate_items(generate_wifi_item)
        payload['cell'] = generate_items(generate_cell_item)
        return payload

    headers = {'Accept-Language': 'ru'}
    payload = generate_payload()
    response = await taxi_yagr_adv.post(
        '/driver/v1/position/store_extra_data', json=payload, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {}
    check_polling_header(response.headers['X-Polling-Power-Policy'])

    def round_floats(obj):
        significant_digits = 6
        if isinstance(obj, dict):
            for key in obj:
                obj[key] = round_floats(obj[key])
            return obj
        if isinstance(obj, list):
            for i, _ in enumerate(obj):
                obj[i] = round_floats(obj[i])
            return obj
        if isinstance(obj, float):
            return round(obj, significant_digits)
        return obj

    data = await testpoint_extra_data.wait_call()

    # round floats
    round_floats(payload)
    round_floats(data['data']['json'])
    # delete timestamp field which is added by yt-logger
    del data['data']['json']['timestamp']

    # compare
    assert {
        **payload,
        **{'contractor_uuid': driver_id, 'contractor_dbid': park_id},
    } == data['data']['json']


@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_extra_data_send_not_authorized(
        taxi_yagr_adv, redis_store, testpoint, user_agent, app_family,
):
    headers = {
        'User-Agent': user_agent,
        'Accept-Language': 'ru',
        'X-Request-Application-Version': '9.1',
        'X-YaTaxi-Park-Id': '',
        'X-YaTaxi-Driver-Profile-Id': '',
    }
    payload = {}
    payload['contractor_uuid'] = 'driver2'
    payload['contractor_dbid'] = 'park2'
    payload['satellites'] = []
    payload['wifi'] = []
    payload['cell'] = []
    response = await taxi_yagr_adv.post(
        '/driver/v1/position/store_extra_data', json=payload, headers=headers,
    )
    assert response.status_code == 401
