import base64
import datetime
import json
import time

import pytest
import yt.yson


def _timestamp(time):
    return int(
        (time - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1),
    )


_NOW = datetime.datetime(2018, 7, 13, 16, 0, 0)
_TIMESTAMP = _timestamp(_NOW)


@pytest.fixture
def mock_personal_driver_licenses_find(mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/find')
    def mock_personal_driver_licenses_find(request):
        request_json = json.loads(request.get_data())
        driver_license_map = {
            'SUPERFRAUDER': '9725109e6e204ce28f67e6e91aaea099',
        }
        driver_license = request_json['value']
        if driver_license in driver_license_map:
            return {
                'id': driver_license_map[driver_license],
                'value': driver_license,
            }

        return mockserver.make_response({}, 404)


@pytest.fixture
def mock_personal_driver_licenses_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def mock_personal_retrieve(request):
        items = json.loads(request.get_data())['items']
        response_items = [
            {'id': i['id'], 'value': i['id'][:-6]}
            for i in items
            if i['id'].endswith('_pd_id')
        ]
        return {'items': response_items}


@pytest.mark.parametrize(
    'request_data',
    [
        {'drivers': [{'udi': ''}]},
        {'drivers': 1},
        {'drivers': []},
        {'drivers': [1]},
        {'drivers': [{'license_personal_ids': ['no_fraud_license1_pd_id']}]},
        {
            'drivers': [
                {
                    'udi': 1,
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                },
            ],
        },
        {'drivers': [{'udi': '', 'licenses': 1}]},
        {'drivers': [{'udi': '', 'license_personal_ids': []}]},
        {'drivers': [{'udi': '', 'license_personal_ids': [1]}]},
    ],
)
def test_invalid_request(
        taxi_antifraud, mock_personal_driver_licenses_retrieve, request_data,
):
    taxi_antifraud.tests_control(now=_NOW, invalidate_caches=True)
    response = taxi_antifraud.post(
        'v1/geo_subvention/check_drivers', request_data,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_data, expected_response_data, expected_mongo',
    [
        (
            {
                'drivers': [
                    {
                        'udi': '',
                        'license_personal_ids': ['no_fraud_license1_pd_id'],
                    },
                ],
            },
            {'drivers': [{'license': 'no_fraud_license1', 'frauder': False}]},
            [
                {
                    'license': 'no_fraud_license1',
                    'found': True,
                    'frauder': False,
                    'rule_id': '',
                    'rule_ids': [],
                    'test_rule_ids': [],
                    'rule_apply': _TIMESTAMP,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'udi': '',
                        'license_personal_ids': ['no_fraud_license1_pd_id'],
                    },
                ],
            },
            {'drivers': [{'license': 'no_fraud_license1', 'frauder': False}]},
            None,
        ),
        (
            {
                'drivers': [
                    {
                        'udi': '',
                        'license_personal_ids': ['no_fraud_license1_pd_id'],
                    },
                ],
            },
            {'drivers': [{'license': 'no_fraud_license1', 'frauder': False}]},
            None,
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'frauder_id',
                        'license_personal_ids': ['license2_pd_id'],
                    },
                ],
            },
            {
                'drivers': [
                    {
                        'license': 'license2',
                        'frauder': True,
                        'rule_id': 'test_rule3',
                    },
                ],
            },
            [
                {
                    'license': 'license2',
                    'found': True,
                    'frauder': True,
                    'rule_id': 'test_rule3',
                    'rule_ids': [
                        'test_rule3',
                        'test_rule22',
                        'test_rule21',
                        'test_rule1',
                    ],
                    'test_rule_ids': [],
                    'rule_apply': _TIMESTAMP,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'fraud_by_license_directly',
                        'license_personal_ids': [
                            'license_for_direct_fraud_pd_id',
                        ],
                    },
                ],
            },
            {
                'drivers': [
                    {
                        'license': 'license_for_direct_fraud',
                        'frauder': True,
                        'rule_id': 'test_rule_direct_fraud',
                    },
                ],
            },
            [
                {
                    'license': 'license_for_direct_fraud',
                    'found': False,
                    'frauder': True,
                    'rule_id': 'test_rule_direct_fraud',
                    'rule_ids': ['test_rule_direct_fraud', 'test_rule1'],
                    'test_rule_ids': [],
                    'rule_apply': _TIMESTAMP,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'fraud_by_license_directly',
                        'license_personal_ids': ['SUPERFRAUDER_pd_id'],
                    },
                ],
            },
            {
                'drivers': [
                    {
                        'license': 'SUPERFRAUDER',
                        'frauder': True,
                        'rule_id': 'test_rule_direct_fraud_personal_id',
                    },
                ],
            },
            [
                {
                    'license': 'SUPERFRAUDER',
                    'found': False,
                    'frauder': True,
                    'rule_id': 'test_rule_direct_fraud_personal_id',
                    'rule_ids': [
                        'test_rule_direct_fraud_personal_id',
                        'test_rule1',
                    ],
                    'test_rule_ids': [],
                    'rule_apply': _TIMESTAMP,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'license_personal_ids': [
                            'geo_booking_subvention_fraud_pd_id',
                        ],
                        'period_end': '2018-06-02T00:00:00+05:00',
                        'rules': [
                            {'day_ride_count': [0], 'day_ride_count_days': 1},
                        ],
                        'subvention': {
                            'amount': '538.0000',
                            'currency': 'RUB',
                        },
                        'udi': '59ce9ae816e5302735c2df91',
                    },
                ],
                'period_end': '2018-06-02T00:00:00+05:00',
            },
            {
                'drivers': [
                    {
                        'license': 'geo_booking_subvention_fraud',
                        'frauder': True,
                        'rule_id': 'test_geo_booking_subvention',
                    },
                ],
            },
            [
                {
                    'license': 'geo_booking_subvention_fraud',
                    'found': False,
                    'frauder': True,
                    'rule_id': 'test_geo_booking_subvention',
                    'rule_ids': ['test_geo_booking_subvention', 'test_rule1'],
                    'test_rule_ids': [],
                    'rule_apply': _TIMESTAMP,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'fraud_by_license_directly',
                        'license_personal_ids': ['SUPERFRAUDER_pd_id'],
                    },
                ],
            },
            {
                'drivers': [
                    {
                        'license': 'SUPERFRAUDER',
                        'frauder': True,
                        'rule_id': 'test_rule_direct_fraud_personal_id',
                    },
                ],
            },
            [
                {
                    'license': 'SUPERFRAUDER',
                    'found': False,
                    'frauder': True,
                    'rule_id': 'test_rule_direct_fraud_personal_id',
                    'rule_ids': [
                        'test_rule_direct_fraud_personal_id',
                        'test_rule1',
                    ],
                    'test_rule_ids': [],
                    'rule_apply': _TIMESTAMP,
                },
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    AFS_SUBVENTION_RULES_FETCH_LICENSE_PERSONAL_ID_FROM_PERSONAL=True,
)
def test_check_drivers_base(
        taxi_antifraud,
        db,
        testpoint,
        mock_personal_driver_licenses_find,
        mock_personal_driver_licenses_retrieve,
        request_data,
        expected_response_data,
        expected_mongo,
):
    taxi_antifraud.tests_control(now=_NOW, invalidate_caches=True)
    _test_check_drivers_impl(
        taxi_antifraud,
        db,
        testpoint,
        request_data,
        expected_response_data,
        expected_mongo,
    )


@pytest.mark.parametrize(
    'udi, license, expected_rule',
    [
        ('fraud_udi', 'no_fraud_license_pd_id', 'fraud_udi'),
        ('no_fraud_udi', 'fraud_license_pd_id', 'fraud_license'),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_rules='drivers_udi_license')
def test_check_drivers_udi_license(
        taxi_antifraud,
        mock_personal_driver_licenses_retrieve,
        udi,
        license,
        expected_rule,
):
    request_data = {
        'drivers': [
            {
                'udi': udi,
                'license_personal_ids': [license],
                'rules': [{'day_ride_count_days': 7, 'day_ride_count': [60]}],
            },
        ],
        'period_end': '2016-12-14T00:00:00+0000',
    }
    response = taxi_antifraud.post(
        'v1/geo_subvention/check_drivers', request_data,
    )
    assert response.status_code == 200

    data = response.json()
    drivers = data['drivers']
    assert len(drivers) == 1

    driver = drivers[0]
    rule_id = driver['rule_id']
    assert rule_id == expected_rule


@pytest.mark.config(
    AFS_RULES_LOG_CONFIG={'enabled': True},
    AFS_RULES_PARAMS_FILTER_CONFIG={
        '__default__': {
            'udi': {'args': False, 'logs': True},
            'driver_license': {'args': True, 'logs': True},
        },
    },
    AFS_RULES_PARAMS_FILTER_ENABLED=True,
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_rules='filter')
def test_check_drivers_pass_params(
        taxi_antifraud, mock_personal_driver_licenses_retrieve,
):

    request_data = {
        'drivers': [
            {
                'udi': 'some_udi',
                'license_personal_ids': ['fraud_license_pd_id'],
                'rules': [{'day_ride_count_days': 7, 'day_ride_count': [60]}],
            },
        ],
        'period_end': '2016-12-14T00:00:00+0000',
    }
    response = taxi_antifraud.post(
        'v1/geo_subvention/check_drivers', request_data,
    )
    assert response.status_code == 200

    data = response.json()
    drivers = data['drivers']
    assert len(drivers) == 1

    driver = drivers[0]
    assert driver['frauder'] is True


@pytest.mark.parametrize(
    'request_data, expected_response_data, expected_mongo',
    [
        (
            {
                'drivers': [
                    {
                        'udi': '',
                        'license_personal_ids': [
                            'license11_pd_id',
                            'license12_pd_id',
                        ],
                    },
                    {'udi': '', 'license_personal_ids': ['license21_pd_id']},
                    {'udi': '', 'license_personal_ids': ['license31_pd_id']},
                ],
            },
            {
                'drivers': [
                    {'license': 'license11', 'frauder': False},
                    {'license': 'license12', 'frauder': False},
                    {
                        'license': 'license21',
                        'frauder': True,
                        'rule_id': 'test_rule_license21_15_2',
                    },
                    {
                        'license': 'license31',
                        'frauder': True,
                        'rule_id': 'test_rule_license31_1',
                    },
                ],
            },
            [
                {
                    'license': 'license11',
                    'found': True,
                    'frauder': False,
                    'rule_id': '',
                    'rule_ids': [],
                    'test_rule_ids': [
                        'test_test_rule_license11_1_2',
                        'test_test_rule_license11_1_1',
                    ],
                    'rule_apply': _TIMESTAMP,
                },
                {
                    'license': 'license12',
                    'found': True,
                    'frauder': False,
                    'rule_id': '',
                    'rule_ids': [],
                    'test_rule_ids': ['test_test_rule_license12_1_1'],
                    'rule_apply': _TIMESTAMP,
                },
                {
                    'license': 'license21',
                    'found': True,
                    'frauder': True,
                    'rule_id': 'test_rule_license21_15_2',
                    'rule_ids': [
                        'test_rule_license21_15_2',
                        'test_rule_license21_15_1',
                    ],
                    'test_rule_ids': ['test_test_rule_license21_15'],
                    'rule_apply': _TIMESTAMP,
                },
                {
                    'license': 'license31',
                    'found': True,
                    'frauder': True,
                    'rule_id': 'test_rule_license31_1',
                    'rule_ids': ['test_rule_license31_1'],
                    'test_rule_ids': [],
                    'rule_apply': _TIMESTAMP,
                },
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_rules='test_mode')
def test_check_drivers_test_mode(
        taxi_antifraud,
        db,
        testpoint,
        mock_personal_driver_licenses_retrieve,
        request_data,
        expected_response_data,
        expected_mongo,
):

    taxi_antifraud.tests_control(now=_NOW, invalidate_caches=True)
    _test_check_drivers_impl(
        taxi_antifraud,
        db,
        testpoint,
        request_data,
        expected_response_data,
        expected_mongo,
    )


def _test_check_drivers_impl(
        taxi_antifraud,
        db,
        testpoint,
        request_data,
        expected_response_data,
        expected_mongo,
):

    list = []

    @testpoint('yt_uploads::geo_subvention_results_info')
    def yt_upload(data):
        yt_data = base64.b64decode(data['base64'])
        obj = yt.yson.loads(yt_data, yson_type='list_fragment')

        for element in obj:
            list.append(yt.yson.yson_to_json(element))

    response = taxi_antifraud.post(
        'v1/geo_subvention/check_drivers', request_data,
    )
    assert response.status_code == 200
    assert response.json() == expected_response_data

    if expected_mongo is None:
        return

    for _ in expected_mongo:
        yt_upload.wait_call()

    def _cmp(k):
        return k['license']

    assert sorted(list, key=_cmp) == sorted(expected_mongo, key=_cmp)

    _check_mongo(db, expected_mongo)


def _check_mongo(db, expected_mongo):
    for expected_item in expected_mongo:
        items = db.antifraud_geo_subvention_frauders.find(
            {'license': expected_item['license']},
        )
        for _ in range(20):
            if items.count() == 0:
                time.sleep(0.1)
            else:
                break
        assert items.count() == 1
        item = items[0]
        assert _sanitize(item) == expected_item

    actual_count = db.antifraud_geo_subvention_frauders.count()
    expected_count = len(expected_mongo)
    assert actual_count == expected_count


def _sanitize(item):
    result = {
        key: item[key]
        for key in item
        if key not in ('_id', 'created', 'updated')
    }

    result['rule_apply'] = _timestamp(result['rule_apply'])

    return result
