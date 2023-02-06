import datetime
import json
import time

import pytest


_NOW = datetime.datetime(2018, 7, 13, 16, 0, 0)


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


@pytest.mark.parametrize('processor', [False, True])
@pytest.mark.parametrize(
    'request_data',
    [
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [60]},
                    ],
                },
            ],
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [60]},
                    ],
                },
            ],
            'period_end': True,
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [60]},
                    ],
                },
            ],
            'period_end': 'azaza',
        },
        {'period_end': '2016-12-14T00:00:00+0000'},
        {'drivers': 1, 'period_end': '2016-12-14T00:00:00+0000'},
        {'drivers': [], 'period_end': '2016-12-14T00:00:00+0000'},
        {'drivers': [1], 'period_end': '2016-12-14T00:00:00+0000'},
        {
            'drivers': [
                {
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [60]},
                    ],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [60]},
                    ],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': 1,
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [60]},
                    ],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'licenses': 1,
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [60]},
                    ],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': [],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [60]},
                    ],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': [1],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [60]},
                    ],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': 1,
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': [],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': [1],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': [{'day_ride_count': [60]}],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': [{'day_ride_count_days': 7}],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': [
                        {
                            'day_ride_count_days': 'azaza',
                            'day_ride_count': [60],
                        },
                    ],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': 'azaza'},
                    ],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': []},
                    ],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
        {
            'drivers': [
                {
                    'udi': '',
                    'license_personal_ids': ['no_fraud_license1_pd_id'],
                    'rules': [
                        {
                            'day_ride_count_days': 7,
                            'day_ride_count': ['azaza'],
                        },
                    ],
                },
            ],
            'period_end': '2016-12-14T00:00:00+0000',
        },
    ],
)
def test_invalid_request(
        taxi_antifraud,
        mock_personal_driver_licenses_retrieve,
        request_data,
        processor,
        config,
):
    config.set_values({'AFS_PERSONAL_SUBVENTION_PROCESSOR_ENABLED': processor})
    taxi_antifraud.tests_control(now=_NOW, invalidate_caches=True)
    response = taxi_antifraud.post(
        'personal_subvention/check_drivers', request_data,
    )
    assert response.status_code == 400


@pytest.mark.parametrize('processor', [True])
@pytest.mark.parametrize(
    'request_data, expected_response_data, expected_mongo',
    [
        (
            {
                'drivers': [
                    {
                        'udi': '',
                        'license_personal_ids': ['no_fraud_license1_pd_id'],
                        'rules': [
                            {'day_ride_count_days': 7, 'day_ride_count': [60]},
                        ],
                    },
                ],
                'period_end': '2016-12-14T00:00:00+0000',
            },
            {
                'drivers': [
                    {
                        'license': 'no_fraud_license1',
                        'found': True,
                        'frauder': False,
                    },
                ],
            },
            [
                {
                    'license': 'no_fraud_license1',
                    'day_ride_count_days': 7,
                    'day_ride_count': [60],
                    'found': True,
                    'frauder': False,
                    'rule_id': '',
                    'rule_ids': [],
                    'test_rule_ids': [],
                    'rule_apply': _NOW,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'udi': '',
                        'license_personal_ids': ['no_fraud_license2_pd_id'],
                        'rules': [
                            {'day_ride_count_days': 7, 'day_ride_count': [60]},
                        ],
                    },
                ],
                'period_end': '2016-12-14T00:00:00+0000',
            },
            {
                'drivers': [
                    {
                        'license': 'no_fraud_license2',
                        'found': True,
                        'frauder': False,
                    },
                ],
            },
            None,
        ),
        (
            {
                'drivers': [
                    {
                        'udi': '',
                        'license_personal_ids': ['no_fraud_license1_pd_id'],
                        'rules': [
                            {'day_ride_count_days': 7, 'day_ride_count': [60]},
                        ],
                    },
                ],
                'period_end': '2016-12-14T02:59:59+0300',
            },
            {
                'drivers': [
                    {
                        'license': 'no_fraud_license1',
                        'found': True,
                        'frauder': False,
                    },
                ],
            },
            None,
        ),
        (
            {
                'drivers': [
                    {
                        'udi': '',
                        'license_personal_ids': ['no_fraud_license1_pd_id'],
                        'rules': [
                            {
                                'day_ride_count_days': 15,
                                'day_ride_count': [60],
                            },
                        ],
                    },
                ],
                'period_end': '2016-12-14T00:00:00+0000',
            },
            {
                'drivers': [
                    {
                        'license': 'no_fraud_license1',
                        'found': True,
                        'frauder': False,
                    },
                ],
            },
            None,
        ),
        (
            {
                'drivers': [
                    {
                        'udi': '',
                        'license_personal_ids': ['fraud_license_pd_id'],
                        'rules': [
                            {'day_ride_count_days': 1, 'day_ride_count': [30]},
                        ],
                    },
                ],
                'period_end': '2016-12-14T00:00:00+0000',
            },
            {
                'drivers': [
                    {
                        'license': 'fraud_license',
                        'found': True,
                        'frauder': True,
                        'rule_id': 'fraud_license_rule',
                    },
                ],
            },
            [
                {
                    'license': 'fraud_license',
                    'day_ride_count_days': 1,
                    'day_ride_count': [30],
                    'found': True,
                    'frauder': True,
                    'rule_id': 'fraud_license_rule',
                    'rule_ids': ['fraud_license_rule'],
                    'test_rule_ids': [],
                    'rule_apply': _NOW,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'udi': '',
                        'license_personal_ids': ['SUPERFRAUDER_pd_id'],
                        'rules': [
                            {'day_ride_count_days': 1, 'day_ride_count': [30]},
                        ],
                    },
                ],
                'period_end': '2016-12-14T00:00:00+0000',
            },
            {
                'drivers': [
                    {
                        'license': 'SUPERFRAUDER',
                        'found': True,
                        'frauder': True,
                        'rule_id': 'fraud_license_personal_id_rule',
                    },
                ],
            },
            [
                {
                    'license': 'SUPERFRAUDER',
                    'day_ride_count_days': 1,
                    'day_ride_count': [30],
                    'found': True,
                    'frauder': True,
                    'rule_id': 'fraud_license_personal_id_rule',
                    'rule_ids': ['fraud_license_personal_id_rule'],
                    'test_rule_ids': [],
                    'rule_apply': _NOW,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'udi': '',
                        'license_personal_ids': [
                            'fraud_subvention_license_pd_id',
                        ],
                        'rules': [
                            {'day_ride_count_days': 1, 'day_ride_count': [30]},
                        ],
                        'subvention': {'amount': '100.500', 'currency': 'RUB'},
                    },
                ],
                'period_end': '2016-12-14T00:00:00+0000',
            },
            {
                'drivers': [
                    {
                        'license': 'fraud_subvention_license',
                        'found': True,
                        'frauder': True,
                        'rule_id': 'fraud_subvention_rule',
                    },
                ],
            },
            [
                {
                    'license': 'fraud_subvention_license',
                    'day_ride_count_days': 1,
                    'day_ride_count': [30],
                    'found': True,
                    'frauder': True,
                    'rule_id': 'fraud_subvention_rule',
                    'rule_ids': ['fraud_subvention_rule'],
                    'test_rule_ids': [],
                    'rule_apply': _NOW,
                },
            ],
        ),
        (
            {
                'drivers': [
                    {
                        'udi': '',
                        'license_personal_ids': [
                            'fraud_subvention_license_pd_id',
                        ],
                        'rules': [
                            {'day_ride_count_days': 1, 'day_ride_count': [30]},
                        ],
                        'subvention': {'amount': '100.500', 'currency': 'RUB'},
                        'period_end': '2021-10-01T10:30:00+0000',
                    },
                ],
                'period_end': '2016-12-14T00:00:00+0000',
            },
            {
                'drivers': [
                    {
                        'license': 'fraud_subvention_license',
                        'found': True,
                        'frauder': True,
                        'rule_id': 'fraud_subvention_rule',
                    },
                ],
            },
            [
                {
                    'license': 'fraud_subvention_license',
                    'day_ride_count_days': 1,
                    'day_ride_count': [30],
                    'found': True,
                    'frauder': True,
                    'rule_id': 'fraud_subvention_rule',
                    'rule_ids': ['fraud_subvention_rule', 'period_end_rule'],
                    'test_rule_ids': [],
                    'rule_apply': _NOW,
                },
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(
    antifraud_rules='generic', antifraud_subvention_frauders='generic',
)
@pytest.mark.config(
    AFS_SUBVENTION_RULES_FETCH_LICENSE_PERSONAL_ID_FROM_PERSONAL=True,
)
def test_check_drivers_base(
        taxi_antifraud,
        db,
        mock_personal_driver_licenses_find,
        mock_personal_driver_licenses_retrieve,
        request_data,
        expected_response_data,
        expected_mongo,
        processor,
        config,
):
    config.set_values({'AFS_PERSONAL_SUBVENTION_PROCESSOR_ENABLED': processor})
    taxi_antifraud.tests_control(now=_NOW, invalidate_caches=True)
    _test_check_drivers_impl(
        taxi_antifraud,
        db,
        request_data,
        expected_response_data,
        expected_mongo,
    )


@pytest.mark.parametrize('processor', [False, True])
@pytest.mark.parametrize(
    'request_data, expected_response_data, expected_mongo',
    [
        (
            {
                'drivers': [
                    {
                        'udi': '',
                        'license_personal_ids': ['license11_pd_id'],
                        'rules': [
                            {'day_ride_count_days': 1, 'day_ride_count': [30]},
                        ],
                    },
                ],
                'period_end': '2016-12-14T00:00:00+0000',
            },
            {
                'drivers': [
                    {'license': 'license11', 'found': True, 'frauder': False},
                ],
            },
            [
                {
                    'license': 'license11',
                    'day_ride_count_days': 1,
                    'day_ride_count': [30],
                    'found': True,
                    'frauder': False,
                    'rule_id': '',
                    'rule_ids': [],
                    'test_rule_ids': ['test_rule_license11_1'],
                    'rule_apply': _NOW,
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
        mock_personal_driver_licenses_retrieve,
        request_data,
        expected_response_data,
        expected_mongo,
        processor,
        config,
):
    config.set_values({'AFS_PERSONAL_SUBVENTION_PROCESSOR_ENABLED': processor})
    taxi_antifraud.tests_control(now=_NOW, invalidate_caches=True)
    _test_check_drivers_impl(
        taxi_antifraud,
        db,
        request_data,
        expected_response_data,
        expected_mongo,
    )


def _test_check_drivers_impl(
        taxi_antifraud,
        db,
        request_data,
        expected_response_data,
        expected_mongo,
):
    response = taxi_antifraud.post(
        'personal_subvention/check_drivers', request_data,
    )
    assert response.status_code == 200
    assert response.json() == expected_response_data
    _check_mongo(db, expected_mongo)


def _check_mongo(db, expected_mongo):
    if expected_mongo is None:
        return

    for expected_item in expected_mongo:
        items = db.antifraud_personal_subvention_frauders.find(
            {
                'license': expected_item['license'],
                'day_ride_count_days': expected_item['day_ride_count_days'],
            },
        )
        for _ in range(20):
            if items.count() == 0:
                time.sleep(0.1)
            else:
                break
        assert items.count() == 1
        item = items[0]
        assert _without_id_and_dttm_fields(item) == expected_item

    actual_count = db.antifraud_personal_subvention_frauders.count()
    expected_count = len(expected_mongo)
    assert actual_count == expected_count


def _without_id_and_dttm_fields(item):
    return {
        key: item[key]
        for key in item
        if key not in ('_id', 'created', 'updated')
    }
