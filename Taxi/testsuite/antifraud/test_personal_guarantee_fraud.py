import datetime
import json

import pytest


HANDLER_URL = '/daily_guarantee_subvention/check_drivers'
NOW = datetime.datetime(2018, 3, 5, 18, 0, 0)


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
    'request_body, expected_error',
    [
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'license_personal_ids': [
                            'crazy_driver11_pd_id',
                            'crazy_driver12_pd_id',
                        ],
                        'rules': [
                            {'day_ride_count': [60], 'day_ride_count_days': 7},
                            {'day_ride_count': [30], 'day_ride_count_days': 1},
                        ],
                    },
                    {
                        'udi': 'crazy_driver2',
                        'license_personal_ids': [
                            'crazy_driver21_pd_id',
                            'crazy_driver22_pd_id',
                        ],
                        'rules': [
                            {
                                'day_ride_count': [60, 90],
                                'day_ride_count_days': 7,
                            },
                            {
                                'day_ride_count': [30, 60],
                                'day_ride_count_days': 1,
                            },
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            None,
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'license_personal_ids': ['crazy_driver11_pd_id'],
                        'rules': [
                            {'day_ride_count': [60], 'day_ride_count_days': 7},
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00Z',
            },
            None,
        ),
        ({'period_end': '2018-03-04T00:00:00+0000'}, 'no drivers'),
        (
            {'drivers': 'ololo', 'period_end': '2018-03-04T00:00:00+0000'},
            'invalid drivers',
        ),
        (
            {'drivers': [], 'period_end': '2018-03-04T00:00:00+0000'},
            'drivers is empty',
        ),
        (
            {
                'drivers': [
                    {
                        'license_personal_ids': ['crazy_driver11_pd_id'],
                        'rules': [
                            {'day_ride_count': [60], 'day_ride_count_days': 7},
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            'no udi',
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'rules': [
                            {'day_ride_count': [60], 'day_ride_count_days': 7},
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            'no license_personal_ids',
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'license_personal_ids': [],
                        'rules': [
                            {'day_ride_count': [60], 'day_ride_count_days': 7},
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            'license_personal_ids is empty',
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'license_personal_ids': ['crazy_driver11_pd_id'],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            'no rules',
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'license_personal_ids': ['crazy_driver11_pd_id'],
                        'rules': [],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            'rules is empty',
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'license_personal_ids': [100500],
                        'rules': [
                            {'day_ride_count': [60], 'day_ride_count_days': 7},
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            'invalid license_personal_ids',
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'license_personal_ids': ['crazy_driver11_pd_id'],
                        'rules': [{'day_ride_count_days': 7}],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            'no day_ride_count',
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'license_personal_ids': ['crazy_driver11_pd_id'],
                        'rules': [
                            {'day_ride_count': [], 'day_ride_count_days': 7},
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            'day_ride_count is empty',
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'license_personal_ids': ['crazy_driver11_pd_id'],
                        'rules': [
                            {'day_ride_count': [0], 'day_ride_count_days': 7},
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            'invalid day_ride_count',
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'license_personal_ids': ['crazy_driver11_pd_id'],
                        'rules': [{'day_ride_count': [60]}],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            'no day_ride_count_days',
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'license_personal_ids': ['crazy_driver11_pd_id'],
                        'rules': [
                            {'day_ride_count': [60], 'day_ride_count_days': 0},
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            'invalid day_ride_count_days',
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'license_personal_ids': ['crazy_driver11_pd_id'],
                        'rules': [
                            {'day_ride_count': [60], 'day_ride_count_days': 7},
                        ],
                    },
                ],
                'period_end': '2018-03-03T00:00:00+0000',
            },
            None,
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'crazy_driver1',
                        'license_personal_ids': ['crazy_driver11_pd_id'],
                        'rules': [
                            {'day_ride_count': [60], 'day_ride_count_days': 7},
                        ],
                    },
                ],
                'period_end': '2018-03-05T00:00:00+0000',
            },
            None,
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
def test_fetch_request(
        taxi_antifraud,
        db,
        mock_personal_driver_licenses_retrieve,
        request_body,
        expected_error,
):
    response = taxi_antifraud.post(HANDLER_URL, request_body)
    if expected_error:
        assert response.status_code == 400
        assert response.json()['error']['text'] == expected_error
    else:
        assert response.status_code == 200


@pytest.mark.parametrize(
    'request_body, expected_response_status_code, '
    'expected_response_body, expected_mongo',
    [
        (
            {
                'drivers': [
                    {
                        'udi': 'some_udi',
                        'license_personal_ids': ['nonfrauder_pd_id'],
                        'rules': [
                            {'day_ride_count': [60], 'day_ride_count_days': 7},
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            200,
            {
                'drivers': [
                    {'license': 'nonfrauder', 'found': True, 'frauder': False},
                ],
            },
            [
                {
                    'license': 'nonfrauder',
                    'total_rides_count': 60,
                    'due_period_days': 7,
                    'checked': True,
                    'frauder': False,
                    'frauder_rules': [],
                    'frauder_test_rules': [],
                    'checking_time': NOW,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'some_udi',
                        'license_personal_ids': ['some_license_pd_id'],
                        'rules': [
                            {
                                'day_ride_count': [777],
                                'day_ride_count_days': 30,
                            },
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            200,
            {
                'drivers': [
                    {
                        'license': 'some_license',
                        'found': True,
                        'frauder': True,
                        'rule_id': 'test_fraud_rides',
                    },
                ],
            },
            [
                {
                    'license': 'some_license',
                    'total_rides_count': 777,
                    'due_period_days': 30,
                    'checked': True,
                    'frauder': True,
                    'frauder_rules': ['test_fraud_rides'],
                    'frauder_test_rules': [],
                    'checking_time': NOW,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'some_udi',
                        'license_personal_ids': ['fraud_license_pd_id'],
                        'rules': [
                            {
                                'day_ride_count': [60],
                                'day_ride_count_days': 30,
                            },
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            200,
            {
                'drivers': [
                    {
                        'license': 'fraud_license',
                        'found': True,
                        'frauder': True,
                        'rule_id': 'test_fraud_license',
                    },
                ],
            },
            [
                {
                    'license': 'fraud_license',
                    'total_rides_count': 60,
                    'due_period_days': 30,
                    'checked': True,
                    'frauder': True,
                    'frauder_rules': ['test_fraud_license'],
                    'frauder_test_rules': [],
                    'checking_time': NOW,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'udi': 'some_udi',
                        'license_personal_ids': ['SUPERFRAUDER_pd_id'],
                        'rules': [
                            {
                                'day_ride_count': [60],
                                'day_ride_count_days': 30,
                            },
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            200,
            {
                'drivers': [
                    {
                        'license': 'SUPERFRAUDER',
                        'found': True,
                        'frauder': True,
                        'rule_id': 'test_fraud_license_personal_id',
                    },
                ],
            },
            [
                {
                    'license': 'SUPERFRAUDER',
                    'total_rides_count': 60,
                    'due_period_days': 30,
                    'checked': True,
                    'frauder': True,
                    'frauder_rules': ['test_fraud_license_personal_id'],
                    'frauder_test_rules': [],
                    'checking_time': NOW,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'license_personal_ids': [
                            'daily_guarantee_subvention_fraud_pd_id',
                        ],
                        'period_end': '2018-06-02T00:00:00+00:00',
                        'rules': [
                            {'day_ride_count': [13], 'day_ride_count_days': 1},
                        ],
                        'subvention': {'amount': '40.0000', 'currency': 'GHS'},
                        'udi': '5ea9daea8fe28d5ce408755e',
                    },
                ],
                'period_end': '2018-06-02T00:00:00+00:00',
            },
            200,
            {
                'drivers': [
                    {
                        'license': 'daily_guarantee_subvention_fraud',
                        'found': True,
                        'frauder': True,
                        'rule_id': 'test_daily_guarantee_subvention',
                    },
                ],
            },
            [
                {
                    'license': 'daily_guarantee_subvention_fraud',
                    'total_rides_count': 13,
                    'due_period_days': 1,
                    'checked': True,
                    'frauder': True,
                    'frauder_rules': ['test_daily_guarantee_subvention'],
                    'frauder_test_rules': [],
                    'checking_time': NOW,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'license_personal_ids': [
                            'daily_guarantee_subvention_fraud_pd_id',
                        ],
                        'period_end': '2021-01-01T09:00:00+00:00',
                        'rules': [
                            {'day_ride_count': [13], 'day_ride_count_days': 1},
                        ],
                        'subvention': {'amount': '40.0000', 'currency': 'GHS'},
                        'udi': '5ea9daea8fe28d5ce408755e',
                    },
                ],
                'period_end': '2021-02-02T12:00:00+00:00',
            },
            200,
            {
                'drivers': [
                    {
                        'license': 'daily_guarantee_subvention_fraud',
                        'found': True,
                        'frauder': True,
                        'rule_id': 'test_daily_guarantee_subvention',
                    },
                ],
            },
            [
                {
                    'license': 'daily_guarantee_subvention_fraud',
                    'total_rides_count': 13,
                    'due_period_days': 1,
                    'checked': True,
                    'frauder': True,
                    'frauder_rules': [
                        'test_daily_guarantee_subvention',
                        'test_period_end',
                    ],
                    'frauder_test_rules': [],
                    'checking_time': NOW,
                },
            ],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(
    antifraud_rules='generic',
    antifraud_entity_list='generic',
    antifraud_entity_item='generic',
)
@pytest.mark.config(
    AFS_SUBVENTION_RULES_FETCH_LICENSE_PERSONAL_ID_FROM_PERSONAL=True,
)
def test_handler(
        taxi_antifraud,
        db,
        testpoint,
        mock_personal_driver_licenses_find,
        mock_personal_driver_licenses_retrieve,
        request_body,
        expected_response_status_code,
        expected_response_body,
        expected_mongo,
):
    @testpoint('after_mongo_recording')
    def after_mongo_recording(_):
        pass

    response = taxi_antifraud.post(HANDLER_URL, request_body)

    if expected_response_status_code:
        assert response.status_code == expected_response_status_code
    if expected_response_body:
        assert response.json() == expected_response_body
    if expected_mongo:
        after_mongo_recording.wait_call()
        _check_mongo(db, expected_mongo)


@pytest.mark.parametrize(
    'request_data, response_data',
    [
        (
            {
                'drivers': [
                    {
                        'udi': 'bad_driver',
                        'license_personal_ids': ['1_pd_id'],
                        'rules': [
                            {'day_ride_count': [66], 'day_ride_count_days': 6},
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            {
                'drivers': [
                    {
                        'license': '1',
                        'found': True,
                        'frauder': True,
                        'rule_id': 'test_rule_driver_id',
                    },
                ],
            },
        ),
        (
            {
                'drivers': [
                    {
                        'udi': '1',
                        'license_personal_ids': [
                            '1_pd_id',
                            'bad_license_pd_id',
                        ],
                        'rules': [
                            {'day_ride_count': [66], 'day_ride_count_days': 6},
                        ],
                    },
                ],
                'period_end': '2018-03-04T00:00:00+0000',
            },
            {
                'drivers': [
                    {'license': '1', 'found': True, 'frauder': False},
                    {
                        'license': 'bad_license',
                        'found': True,
                        'frauder': True,
                        'rule_id': 'test_rule_driver_license',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(AFS_PERSONAL_GUARANTEE_CUSTOM_DATAMARTS_ENABLED=True)
def test_custom_datamarts(
        taxi_antifraud,
        mock_personal_driver_licenses_retrieve,
        request_data,
        response_data,
):
    result = taxi_antifraud.post(HANDLER_URL, request_data)

    assert result.status_code == 200
    assert result.json() == response_data


def _enable_rules(db, rules):
    db.antifraud_rules.update(
        {'_id': {'$in': rules}}, {'$set': {'enabled': True}}, multi=True,
    )


def _check_mongo(db, expected_mongo):
    actual_count = db.antifraud_personal_guarantee_fraud_checks.count()
    expected_count = len(expected_mongo)
    assert actual_count == expected_count

    for expected_item in expected_mongo:
        items = list(
            db.antifraud_personal_guarantee_fraud_checks.find(
                {
                    'license': expected_item['license'],
                    'total_rides_count': expected_item['total_rides_count'],
                    'due_period_days': expected_item['due_period_days'],
                },
            ),
        )
        assert len(items) == 1
        item = items[0]
        assert _without_nondeterministic_fields(item) == expected_item


def _without_nondeterministic_fields(item):
    return {
        key: item[key]
        for key in item
        if key not in ('_id', 'created', 'updated')
    }
