import datetime
import json

import pytest


def _make_change_block_reason_experiment(clauses):
    ret = {
        'name': (
            'afs_v1_subventions_check_change_block_reason_test_goal_subvention'
        ),
        'consumers': ['afs/v1_subventions_check'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [],
    }
    for claus in clauses:
        ret['clauses'].append(
            {
                'predicate': {'init': {'predicates': []}, 'type': 'all_of'},
                'value': {'reason': claus['reason']},
            },
        )
        for k, v in claus['predicates'].items():
            ret['clauses'][-1]['predicate']['init']['predicates'].append(
                {
                    'init': {'arg_name': k, 'arg_type': 'string', 'value': v},
                    'type': 'eq',
                },
            )
    return ret


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


@pytest.mark.now('2019-01-09T22:00:00+0000')
@pytest.mark.config(
    AFS_BILLING_SUBVENTION_ALWAYS_HOLD=False,
    AFS_BILLING_SUBVENTION_FORCE_PAY_NON_POSITIVE_SUBVENTIONS=True,
    AFS_SUBVENTION_RULE_RESULT_EXP_ENABLED=True,
    AFS_SUBVENTIONS_CHECK_RTXARON_ENABLED=True,
)
@pytest.mark.experiments3(
    **_make_change_block_reason_experiment(
        [
            {
                'predicates': {
                    'rule_id': 'test_goal_subvention',
                    'billing_id': '1000',
                },
                'reason': 'new_custom_reason1',
            },
            {
                'predicates': {'billing_id': '1006'},
                'reason': 'new_custom_reason2',
            },
        ],
    ),
)
def test_subventions_check_base(
        taxi_antifraud,
        testpoint,
        db,
        mock_personal_driver_licenses_retrieve,
        mockserver,
):
    @testpoint('save_subvention_check_info')
    def after_update_stats(_):
        pass

    _REQUEST = {
        'items': [
            {
                'type': 'order',
                'billing_id': '1',
                'data': {
                    'order': {
                        'order_id': '101',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Moscow',
                        'due': '2019-01-10T00:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'moscow',
                    },
                },
            },
            {
                'type': 'order',
                'billing_id': '2',
                'data': {
                    'order': {
                        'order_id': '102',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Moscow',
                        'due': '2019-01-09T20:59:59+0000',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'moscow',
                    },
                },
            },
            {
                'type': 'order',
                'billing_id': '3',
                'data': {
                    'order': {
                        'order_id': '103',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Moscow',
                        'due': '2019-01-09T21:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'moscow',
                    },
                },
            },
            {
                'type': 'order',
                'billing_id': '4',
                'data': {
                    'order': {
                        'order_id': '104',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Accra',
                        'due': '2019-01-09T20:59:59+0000',
                        'time_zone': 'Africa/Accra',
                        'zone': 'ghana',
                    },
                },
            },
            {
                'type': 'order',
                'billing_id': '5',
                'data': {
                    'order': {
                        'order_id': '105',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Accra',
                        'due': '2019-01-09T21:00:00+0000',
                        'time_zone': 'Africa/Accra',
                        'zone': 'ghana',
                    },
                },
            },
            {
                'type': 'order',
                'billing_id': '6',
                'data': {
                    'order': {
                        'order_id': '106',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Vladivostok',
                        'due': '2019-01-09T20:59:59+0000',
                        'time_zone': 'Asia/Vladivostok',
                        'zone': 'vladivostok',
                    },
                },
            },
            {
                'type': 'order',
                'billing_id': '7',
                'data': {
                    'order': {
                        'order_id': '107',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Vladivostok',
                        'due': '2019-01-09T21:00:00+0000',
                        'time_zone': 'Asia/Vladivostok',
                        'zone': 'vladivostok',
                    },
                },
            },
            {
                'type': 'order',
                'billing_id': '8',
                'data': {
                    'order': {
                        'order_id': '108',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Accra',
                        'due': '2019-01-05T00:00:00+0000',
                        'time_zone': 'Africa/Accra',
                        'zone': 'accra',
                    },
                },
            },
            {
                'type': 'order',
                'billing_id': '9',
                'data': {
                    'order': {
                        'order_id': '109',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Vladivostok',
                        'due': '2019-01-05T00:00:00+0000',
                        'time_zone': 'Asia/Vladivostok',
                        'zone': 'vladivostok',
                    },
                },
            },
            {
                'type': 'order',
                'billing_id': '10',
                'data': {
                    'order': {
                        'order_id': '110',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Reutov',
                        'due': '2019-01-10T00:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'reutov',
                    },
                },
            },
            {
                'type': 'order',
                'billing_id': '11',
                'data': {
                    'order': {
                        'order_id': '111',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Reutov',
                        'due': '2019-01-09T23:59:59+0000',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'reutov',
                    },
                },
            },
            {
                'type': 'goal',
                'billing_id': '100',
                'data': {
                    'driver': {
                        'udi': '',
                        'license_personal_ids': ['lic1_pd_id'],
                        'rules': [
                            {'day_ride_count_days': 7, 'day_ride_count': [20]},
                        ],
                    },
                    'period_end': '2019-01-10T09:00:00+1000',
                    'time_zone': 'Asia/Vladivostok',
                },
            },
            {
                'type': 'goal',
                'billing_id': '101',
                'data': {
                    'driver': {
                        'udi': '',
                        'license_personal_ids': ['lic1_pd_id'],
                        'rules': [
                            {'day_ride_count_days': 7, 'day_ride_count': [20]},
                        ],
                    },
                    'period_end': '2019-01-10T00:00:00+1000',
                    'time_zone': 'Asia/Vladivostok',
                },
            },
            {
                'type': 'goal',
                'billing_id': '102',
                'data': {
                    'driver': {
                        'udi': '',
                        'license_personal_ids': ['lic1_pd_id'],
                        'rules': [
                            {'day_ride_count_days': 7, 'day_ride_count': [20]},
                        ],
                    },
                    'period_end': '2019-01-10T00:00:00+0000',
                    'time_zone': 'Africa/Accra',
                },
            },
            {
                'type': 'goal',
                'billing_id': '103',
                'data': {
                    'driver': {
                        'udi': '',
                        'license_personal_ids': ['lic1_pd_id'],
                        'rules': [
                            {'day_ride_count_days': 7, 'day_ride_count': [20]},
                        ],
                    },
                    'period_end': '2019-01-05T00:00:00+0000',
                    'time_zone': 'Africa/Accra',
                },
            },
            {
                'type': 'goal',
                'billing_id': '104',
                'data': {
                    'driver': {
                        'udi': 'hold_udi1',
                        'license_personal_ids': ['hold_lic1_pd_id'],
                        'rules': [
                            {'day_ride_count_days': 7, 'day_ride_count': [20]},
                        ],
                    },
                    'period_end': '2019-01-08T00:00:00+0000',
                    'time_zone': 'Africa/Accra',
                },
            },
            {
                'type': 'order',
                'billing_id': '500',
                'data': {
                    'order': {
                        'order_id': 'subvention_order_id',
                        'license_personal_id': 'subvention_license_pd_id',
                        'city': 'Moscow',
                        'due': '2018-01-10T00:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'moscow',
                    },
                    'subvention': {'amount': '100.500', 'currency': 'RUB'},
                },
            },
            {
                'type': 'goal',
                'billing_id': '1000',
                'data': {
                    'driver': {
                        'udi': '5aafab5fe342c7944bb1549d',
                        'license_personal_ids': [
                            'goal_subvention_fraud_pd_id',
                        ],
                        'rules': [
                            {'day_ride_count_days': 1, 'day_ride_count': [2]},
                        ],
                    },
                    'period_end': '2018-05-31T00:00:00+03:00',
                    'time_zone': 'Europe/Moscow',
                    'subvention': {'amount': '150.000', 'currency': 'RUB'},
                },
            },
            {
                'type': 'daily_guarantee',
                'billing_id': '1001',
                'data': {
                    'driver': {
                        'udi': '5ea9daea8fe28d5ce408755e',
                        'license_personal_ids': [
                            'daily_guarantee_subvention_fraud_pd_id',
                        ],
                        'rules': [
                            {'day_ride_count_days': 1, 'day_ride_count': [13]},
                        ],
                    },
                    'period_end': '2018-06-02T00:00:00+00:00',
                    'time_zone': 'Africa/Accra',
                    'subvention': {'amount': '40.0000', 'currency': 'GHS'},
                },
            },
            {
                'type': 'geo_booking',
                'billing_id': '1002',
                'data': {
                    'driver': {
                        'udi': '59ce9ae816e5302735c2df91',
                        'license_personal_ids': [
                            'geo_booking_subvention_fraud_pd_id',
                        ],
                        'rules': [
                            {'day_ride_count_days': 1, 'day_ride_count': [0]},
                        ],
                    },
                    'period_end': '2018-06-02T00:00:00+05:00',
                    'time_zone': 'Asia/Yekaterinburg',
                    'subvention': {'amount': '538.0000', 'currency': 'RUB'},
                },
            },
            {
                'type': 'driver_fix',
                'billing_id': '1003',
                'data': {
                    'driver': {
                        'udi': '5d3f128c8fe28d5ce45d8af0',
                        'license_personal_ids': [
                            'driver_fix_subvention_fraud_pd_id',
                        ],
                    },
                    'period_end': '2018-06-02T09:25:45+00:00',
                    'time_zone': 'Europe/Moscow',
                    'payment': '0',
                    'guarantee': '837.3953',
                    'currency': 'RUB',
                    'subvention': {'amount': '837.3953', 'currency': 'RUB'},
                },
            },
            {
                'type': 'driver_fix',
                'billing_id': '1005',
                'data': {
                    'driver': {
                        'udi': '5d3f128c8fe28d5ce45d8af0',
                        'license_personal_ids': [
                            'driver_fix_subvention_fraud_pd_id',
                        ],
                    },
                    'period_end': '2018-06-02T09:25:45+00:00',
                    'time_zone': 'Europe/Moscow',
                    'payment': '0',
                    'guarantee': '837.3953',
                    'currency': 'RUB',
                    'subvention': {'amount': '837.3953', 'currency': 'RUB'},
                },
            },
            {
                'type': 'geo_booking',
                'billing_id': '1006',
                'data': {
                    'driver': {
                        'udi': '59ce9ae816e5302735c2df91',
                        'license_personal_ids': [
                            'geo_booking_subvention_fraud2_pd_id',
                        ],
                        'rules': [
                            {'day_ride_count_days': 1, 'day_ride_count': [0]},
                        ],
                    },
                    'period_end': '2018-06-02T00:00:00+05:00',
                    'time_zone': 'Asia/Yekaterinburg',
                    'subvention': {'amount': '538.0000', 'currency': 'RUB'},
                },
            },
            {
                'type': 'daily_guarantee',
                'billing_id': '1007',
                'data': {
                    'driver': {
                        'udi': '5ea9daea8fe28d5ce408755e',
                        'license_personal_ids': [
                            'daily_guarantee_subvention_fraud2_pd_id',
                        ],
                        'rules': [
                            {'day_ride_count_days': 1, 'day_ride_count': [13]},
                        ],
                    },
                    'period_end': '2018-06-02T00:00:00+00:00',
                    'time_zone': 'Africa/Accra',
                    'subvention': {'amount': '40.0000', 'currency': 'GHS'},
                },
            },
            {
                'type': 'goal',
                'billing_id': '1008',
                'data': {
                    'driver': {
                        'udi': '5aafab5fe342c7944bb1549d',
                        'license_personal_ids': [
                            'goal_subvention_fraud2_pd_id',
                        ],
                        'rules': [
                            {'day_ride_count_days': 1, 'day_ride_count': [2]},
                        ],
                    },
                    'period_end': '2018-05-31T00:00:00+03:00',
                    'time_zone': 'Europe/Moscow',
                    'subvention': {'amount': '150.000', 'currency': 'RUB'},
                },
            },
            {
                'type': 'personal',
                'billing_id': '1009',
                'data': {
                    'driver': {
                        'udi': '5aafab5fe342c7944bb1549d',
                        'license_personal_ids': [
                            'personal_subvention_fraud_pd_id',
                        ],
                        'rules': [
                            {'day_ride_count_days': 1, 'day_ride_count': [2]},
                        ],
                    },
                    'period_end': '2018-05-31T00:00:00+03:00',
                    'time_zone': 'Europe/Moscow',
                    'subvention': {'amount': '150.000', 'currency': 'RUB'},
                },
            },
            {
                'type': 'order',
                'billing_id': '1010',
                'data': {
                    'order': {
                        'order_id': '111',
                        'license_personal_id': 'order_subvention_fraud_pd_id',
                        'city': 'Reutov',
                        'due': '2019-01-07T07:11:00+0000',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'perm',
                    },
                },
            },
            {
                'type': 'driver_fix',
                'billing_id': '1011',
                'data': {
                    'driver': {
                        'udi': '5d3f128c8fe28d5ce45d8af0',
                        'license_personal_ids': [
                            'driver_fix_subvention_fraud_pd_id',
                        ],
                    },
                    'period_end': '2018-06-02T09:25:45+00:00',
                    'time_zone': 'Europe/Moscow',
                    'payment': '0',
                    'guarantee': '837.3953',
                    'currency': 'RUB',
                    'subvention': {'amount': '0.0000', 'currency': 'RUB'},
                },
            },
            {
                'type': 'driver_fix',
                'billing_id': '1012',
                'data': {
                    'driver': {
                        'udi': '5d3f128c8fe28d5ce45d8af0',
                        'license_personal_ids': [
                            'driver_fix_subvention_fraud_pd_id',
                        ],
                    },
                    'period_end': '2018-06-02T09:25:45+00:00',
                    'time_zone': 'Europe/Moscow',
                    'payment': '0',
                    'guarantee': '837.3953',
                    'currency': 'RUB',
                    'subvention': {'amount': '-100.0000', 'currency': 'RUB'},
                },
            },
            {
                'type': 'driver_fix',
                'billing_id': '1013',
                'data': {
                    'driver': {
                        'udi': '5d8b88f5b8e3f879689112cd',
                        'license_personal_ids': [
                            'e897fba4003d41c1815d520139e04ce5',
                        ],
                    },
                    'period_end': '2021-05-27T13:01:00+00:00',
                    'time_zone': 'Europe/Moscow',
                    'payment': '0',
                    'guarantee': '837.3953',
                    'currency': 'RUB',
                    'subvention': {'amount': '100.0000', 'currency': 'RUB'},
                },
            },
            {
                'type': 'driver_fix',
                'billing_id': '1014',
                'data': {
                    'driver': {
                        'udi': '5d8b88f5b8e3f879689112cd',
                        'license_personal_ids': [
                            'e897fba4003d41c1815d520139e04ce5',
                        ],
                    },
                    'period_end': '2021-05-27T13:01:00+00:00',
                    'time_zone': 'Europe/Moscow',
                    'payment': '0',
                    'guarantee': '837.3953',
                    'currency': 'RUB',
                    'subvention': {'amount': '100.0000', 'currency': 'RUB'},
                },
            },
        ],
    }

    def _convert_to_rt_xaron_format(billing_id, data):
        result = {'billing_id': billing_id}
        if 'order' in data:
            order = data['order']
            result['driver_license_personal_id'] = order['license_personal_id']
            for field in ('order_id', 'city', 'due', 'zone', 'time_zone'):
                result[field] = order[field]
        if 'subvention' in data:
            subvention = data['subvention']
            result['subvention_amount'] = subvention['amount']
            result['subvention_currency'] = subvention['currency']
        return result

    rt_xaron_requests = {
        e['billing_id']: _convert_to_rt_xaron_format(
            e['billing_id'], e['data'],
        )
        for e in _REQUEST['items']
        if e['type'] == 'order' and e['billing_id'] != '1010'
    }

    assert len(rt_xaron_requests) == 12

    @mockserver.json_handler('/rt_xaron_base/taxi/subventions/single-ride')
    def _rt_xaron(request):
        billing_id = request.json['billing_id']
        assert request.headers['Expect'] == ''
        assert request.json == rt_xaron_requests.pop(billing_id)
        return {
            'jsonrpc': '2.0',
            'id': 1,
            'result': [
                {
                    'source': 'antifraud',
                    'subsource': 'rtxaron',
                    'entity': 'driver_uuid',
                    'key': '',
                    'name': 'taxi_free_trips',
                    'value': True,
                },
            ],
        }

    response = taxi_antifraud.post('v1/subventions/check', json=_REQUEST)

    expected_statuses = {
        '1': {'action': 'pay'},
        '2': {'action': 'pay'},
        '3': {'action': 'pay'},
        '4': {'action': 'pay'},
        '5': {'action': 'pay'},
        '6': {'action': 'pay'},
        '7': {'action': 'pay'},
        '8': {'action': 'pay'},
        '9': {'action': 'pay'},
        '10': {'action': 'delay', 'till': '2019-01-11T01:00:00+00:00'},
        '11': {'action': 'pay'},
        '100': {'action': 'delay', 'till': '2019-01-11T01:00:00+00:00'},
        '101': {'action': 'delay', 'till': '2019-01-10T01:00:00+00:00'},
        '102': {'action': 'delay', 'till': '2019-01-11T01:00:00+00:00'},
        '103': {'action': 'pay'},
        '104': {'action': 'pay'},
        '500': {'action': 'pay'},
        '1000': {'action': 'block'},
        '1001': {'action': 'block'},
        '1002': {'action': 'block'},
        '1003': {'action': 'block'},
        '1005': {'action': 'block'},
        '1006': {'action': 'block'},
        '1007': {'action': 'block'},
        '1008': {'action': 'block'},
        '1009': {'action': 'block'},
        '1010': {'action': 'block'},
        '1011': {'action': 'pay'},
        '1012': {'action': 'pay'},
        '1013': {'action': 'pay'},
        '1014': {'action': 'block'},
    }

    expected_db_records = {
        '1': {
            'subvention_type': 'order',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'order': {
                    'city': 'Moscow',
                    'due': '2019-01-10T00:00:00+0000',
                    'license_personal_id': 'lic1_pd_id',
                    'order_id': '101',
                    'time_zone': 'Europe/Moscow',
                    'zone': 'moscow',
                },
            },
            'check_after': datetime.datetime(2019, 1, 11, 1, 0),
            'proc_status': 'check_later',
        },
        '2': {
            'subvention_type': 'order',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'order': {
                    'city': 'Moscow',
                    'due': '2019-01-09T20:59:59+0000',
                    'license_personal_id': 'lic1_pd_id',
                    'order_id': '102',
                    'time_zone': 'Europe/Moscow',
                    'zone': 'moscow',
                },
            },
            'check_after': datetime.datetime(2019, 1, 10, 1, 0),
            'proc_status': 'check_later',
        },
        '3': {
            'subvention_type': 'order',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'order': {
                    'city': 'Moscow',
                    'due': '2019-01-09T21:00:00+0000',
                    'license_personal_id': 'lic1_pd_id',
                    'order_id': '103',
                    'time_zone': 'Europe/Moscow',
                    'zone': 'moscow',
                },
            },
            'check_after': datetime.datetime(2019, 1, 11, 1, 0),
            'proc_status': 'check_later',
        },
        '4': {
            'subvention_type': 'order',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'order': {
                    'city': 'Accra',
                    'due': '2019-01-09T20:59:59+0000',
                    'license_personal_id': 'lic1_pd_id',
                    'order_id': '104',
                    'time_zone': 'Africa/Accra',
                    'zone': 'ghana',
                },
            },
            'check_after': datetime.datetime(2019, 1, 10, 1, 0),
            'proc_status': 'check_later',
        },
        '5': {
            'subvention_type': 'order',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'order': {
                    'city': 'Accra',
                    'due': '2019-01-09T21:00:00+0000',
                    'license_personal_id': 'lic1_pd_id',
                    'order_id': '105',
                    'time_zone': 'Africa/Accra',
                    'zone': 'ghana',
                },
            },
            'check_after': datetime.datetime(2019, 1, 11, 1, 0),
            'proc_status': 'check_later',
        },
        '6': {
            'subvention_type': 'order',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'order': {
                    'city': 'Vladivostok',
                    'due': '2019-01-09T20:59:59+0000',
                    'license_personal_id': 'lic1_pd_id',
                    'order_id': '106',
                    'time_zone': 'Asia/Vladivostok',
                    'zone': 'vladivostok',
                },
            },
            'check_after': datetime.datetime(2019, 1, 10, 1, 0),
            'proc_status': 'check_later',
        },
        '7': {
            'subvention_type': 'order',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'order': {
                    'city': 'Vladivostok',
                    'due': '2019-01-09T21:00:00+0000',
                    'license_personal_id': 'lic1_pd_id',
                    'order_id': '107',
                    'time_zone': 'Asia/Vladivostok',
                    'zone': 'vladivostok',
                },
            },
            'check_after': datetime.datetime(2019, 1, 11, 1, 0),
            'proc_status': 'check_later',
        },
        '8': {
            'subvention_type': 'order',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'order': {
                    'city': 'Accra',
                    'due': '2019-01-05T00:00:00+0000',
                    'license_personal_id': 'lic1_pd_id',
                    'order_id': '108',
                    'time_zone': 'Africa/Accra',
                    'zone': 'accra',
                },
            },
            'check_after': datetime.datetime(2019, 1, 6, 1, 0),
            'proc_status': 'check_later',
        },
        '9': {
            'subvention_type': 'order',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'order': {
                    'city': 'Vladivostok',
                    'due': '2019-01-05T00:00:00+0000',
                    'license_personal_id': 'lic1_pd_id',
                    'order_id': '109',
                    'time_zone': 'Asia/Vladivostok',
                    'zone': 'vladivostok',
                },
            },
            'check_after': datetime.datetime(2019, 1, 6, 1, 0),
            'proc_status': 'check_later',
        },
        '10': {
            'subvention_type': 'order',
            'statuses': [
                {
                    'payment_status': 'delay',
                    'till': datetime.datetime(2019, 1, 11, 1, 0),
                },
            ],
            'billing_request': {
                'order': {
                    'order_id': '110',
                    'license_personal_id': 'lic1_pd_id',
                    'city': 'Reutov',
                    'due': '2019-01-10T00:00:00+0000',
                    'time_zone': 'Europe/Moscow',
                    'zone': 'reutov',
                },
            },
            'proc_status': 'complete',
        },
        '11': {
            'subvention_type': 'order',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'order': {
                    'city': 'Reutov',
                    'due': '2019-01-09T23:59:59+0000',
                    'license_personal_id': 'lic1_pd_id',
                    'order_id': '111',
                    'time_zone': 'Europe/Moscow',
                    'zone': 'reutov',
                },
            },
            'check_after': datetime.datetime(2019, 1, 11, 1, 0),
            'proc_status': 'check_later',
        },
        '100': {
            'subvention_type': 'goal',
            'statuses': [
                {
                    'payment_status': 'delay',
                    'till': datetime.datetime(2019, 1, 11, 1, 0),
                },
            ],
            'billing_request': {
                'driver': {
                    'udi': '',
                    'license_personal_ids': ['lic1_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [20]},
                    ],
                },
                'period_end': '2019-01-10T09:00:00+1000',
                'time_zone': 'Asia/Vladivostok',
            },
            'proc_status': 'complete',
        },
        '101': {
            'subvention_type': 'goal',
            'statuses': [
                {
                    'payment_status': 'delay',
                    'till': datetime.datetime(2019, 1, 10, 1, 0),
                },
            ],
            'billing_request': {
                'driver': {
                    'udi': '',
                    'license_personal_ids': ['lic1_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [20]},
                    ],
                },
                'period_end': '2019-01-10T00:00:00+1000',
                'time_zone': 'Asia/Vladivostok',
            },
            'proc_status': 'complete',
        },
        '102': {
            'subvention_type': 'goal',
            'statuses': [
                {
                    'payment_status': 'delay',
                    'till': datetime.datetime(2019, 1, 11, 1, 0),
                },
            ],
            'billing_request': {
                'driver': {
                    'udi': '',
                    'license_personal_ids': ['lic1_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [20]},
                    ],
                },
                'period_end': '2019-01-10T00:00:00+0000',
                'time_zone': 'Africa/Accra',
            },
            'proc_status': 'complete',
        },
        '103': {
            'subvention_type': 'goal',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'driver': {
                    'udi': '',
                    'license_personal_ids': ['lic1_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [20]},
                    ],
                },
                'period_end': '2019-01-05T00:00:00+0000',
                'time_zone': 'Africa/Accra',
            },
            'proc_status': 'complete',
        },
        '104': {
            'subvention_type': 'goal',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'driver': {
                    'udi': 'hold_udi1',
                    'license_personal_ids': ['hold_lic1_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 7, 'day_ride_count': [20]},
                    ],
                },
                'period_end': '2019-01-08T00:00:00+0000',
                'time_zone': 'Africa/Accra',
            },
            'proc_status': 'complete',
        },
        '500': {
            'subvention_type': 'order',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'order': {
                    'city': 'Moscow',
                    'due': '2018-01-10T00:00:00+0000',
                    'license_personal_id': 'subvention_license_pd_id',
                    'order_id': 'subvention_order_id',
                    'time_zone': 'Europe/Moscow',
                    'zone': 'moscow',
                },
                'subvention': {'amount': '100.500', 'currency': 'RUB'},
            },
            'check_after': datetime.datetime(2018, 1, 11, 1, 0),
            'proc_status': 'check_later',
        },
        '1000': {
            'subvention_type': 'goal',
            'statuses': [
                {
                    'additional_params': {'rule_id': 'new_custom_reason1'},
                    'payment_status': 'block',
                },
            ],
            'billing_request': {
                'driver': {
                    'udi': '5aafab5fe342c7944bb1549d',
                    'license_personal_ids': ['goal_subvention_fraud_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 1, 'day_ride_count': [2]},
                    ],
                },
                'period_end': '2018-05-31T00:00:00+03:00',
                'time_zone': 'Europe/Moscow',
                'subvention': {'amount': '150.000', 'currency': 'RUB'},
            },
            'proc_status': 'complete',
        },
        '1001': {
            'subvention_type': 'daily_guarantee',
            'statuses': [
                {
                    'additional_params': {
                        'rule_id': 'test_daily_guarantee_subvention',
                    },
                    'payment_status': 'block',
                },
            ],
            'billing_request': {
                'driver': {
                    'udi': '5ea9daea8fe28d5ce408755e',
                    'license_personal_ids': [
                        'daily_guarantee_subvention_fraud_pd_id',
                    ],
                    'rules': [
                        {'day_ride_count_days': 1, 'day_ride_count': [13]},
                    ],
                },
                'period_end': '2018-06-02T00:00:00+00:00',
                'time_zone': 'Africa/Accra',
                'subvention': {'amount': '40.0000', 'currency': 'GHS'},
            },
            'proc_status': 'complete',
        },
        '1002': {
            'subvention_type': 'geo_booking',
            'statuses': [
                {
                    'additional_params': {
                        'rule_id': 'test_geo_booking_subvention',
                    },
                    'payment_status': 'block',
                },
            ],
            'billing_request': {
                'driver': {
                    'udi': '59ce9ae816e5302735c2df91',
                    'license_personal_ids': [
                        'geo_booking_subvention_fraud_pd_id',
                    ],
                    'rules': [
                        {'day_ride_count_days': 1, 'day_ride_count': [0]},
                    ],
                },
                'period_end': '2018-06-02T00:00:00+05:00',
                'time_zone': 'Asia/Yekaterinburg',
                'subvention': {'amount': '538.0000', 'currency': 'RUB'},
            },
            'proc_status': 'complete',
        },
        '1003': {
            'subvention_type': 'driver_fix',
            'statuses': [
                {
                    'additional_params': {
                        'rule_id': 'test_driver_fix_subvention',
                    },
                    'payment_status': 'block',
                },
            ],
            'billing_request': {
                'currency': 'RUB',
                'driver': {
                    'license_personal_ids': [
                        'driver_fix_subvention_fraud_pd_id',
                    ],
                    'udi': '5d3f128c8fe28d5ce45d8af0',
                },
                'guarantee': '837.3953',
                'payment': '0',
                'period_end': '2018-06-02T09:25:45+00:00',
                'subvention': {'amount': '837.3953', 'currency': 'RUB'},
                'time_zone': 'Europe/Moscow',
            },
            'proc_status': 'complete',
        },
        '1005': {
            'subvention_type': 'driver_fix',
            'statuses': [
                {
                    'additional_params': {
                        'rule_id': 'test_driver_fix_subvention',
                    },
                    'payment_status': 'block',
                },
            ],
            'billing_request': {
                'currency': 'RUB',
                'driver': {
                    'license_personal_ids': [
                        'driver_fix_subvention_fraud_pd_id',
                    ],
                    'udi': '5d3f128c8fe28d5ce45d8af0',
                },
                'guarantee': '837.3953',
                'payment': '0',
                'period_end': '2018-06-02T09:25:45+00:00',
                'subvention': {'amount': '837.3953', 'currency': 'RUB'},
                'time_zone': 'Europe/Moscow',
            },
            'proc_status': 'complete',
        },
        '1006': {
            'subvention_type': 'geo_booking',
            'statuses': [
                {
                    'additional_params': {'rule_id': 'new_custom_reason2'},
                    'payment_status': 'block',
                },
            ],
            'billing_request': {
                'driver': {
                    'udi': '59ce9ae816e5302735c2df91',
                    'license_personal_ids': [
                        'geo_booking_subvention_fraud2_pd_id',
                    ],
                    'rules': [
                        {'day_ride_count_days': 1, 'day_ride_count': [0]},
                    ],
                },
                'period_end': '2018-06-02T00:00:00+05:00',
                'time_zone': 'Asia/Yekaterinburg',
                'subvention': {'amount': '538.0000', 'currency': 'RUB'},
            },
            'proc_status': 'complete',
        },
        '1007': {
            'subvention_type': 'daily_guarantee',
            'statuses': [
                {
                    'additional_params': {
                        'rule_id': 'test_daily_guarantee_subvention2',
                    },
                    'payment_status': 'block',
                },
            ],
            'billing_request': {
                'driver': {
                    'udi': '5ea9daea8fe28d5ce408755e',
                    'license_personal_ids': [
                        'daily_guarantee_subvention_fraud2_pd_id',
                    ],
                    'rules': [
                        {'day_ride_count_days': 1, 'day_ride_count': [13]},
                    ],
                },
                'period_end': '2018-06-02T00:00:00+00:00',
                'time_zone': 'Africa/Accra',
                'subvention': {'amount': '40.0000', 'currency': 'GHS'},
            },
            'proc_status': 'complete',
        },
        '1008': {
            'subvention_type': 'goal',
            'statuses': [
                {
                    'additional_params': {'rule_id': 'test_goal_subvention2'},
                    'payment_status': 'block',
                },
            ],
            'billing_request': {
                'driver': {
                    'udi': '5aafab5fe342c7944bb1549d',
                    'license_personal_ids': ['goal_subvention_fraud2_pd_id'],
                    'rules': [
                        {'day_ride_count_days': 1, 'day_ride_count': [2]},
                    ],
                },
                'period_end': '2018-05-31T00:00:00+03:00',
                'time_zone': 'Europe/Moscow',
                'subvention': {'amount': '150.000', 'currency': 'RUB'},
            },
            'proc_status': 'complete',
        },
        '1009': {
            'subvention_type': 'personal',
            'statuses': [
                {
                    'additional_params': {
                        'rule_id': 'test_personal_subvention',
                    },
                    'payment_status': 'block',
                },
            ],
            'billing_request': {
                'driver': {
                    'udi': '5aafab5fe342c7944bb1549d',
                    'license_personal_ids': [
                        'personal_subvention_fraud_pd_id',
                    ],
                    'rules': [
                        {'day_ride_count_days': 1, 'day_ride_count': [2]},
                    ],
                },
                'period_end': '2018-05-31T00:00:00+03:00',
                'time_zone': 'Europe/Moscow',
                'subvention': {'amount': '150.000', 'currency': 'RUB'},
            },
            'proc_status': 'complete',
        },
        '1010': {
            'subvention_type': 'order',
            'statuses': [
                {
                    'payment_status': 'pay',
                    'antifraud_id': 'afs_id/100500',
                    'created': datetime.datetime(2019, 1, 1, 22, 0),
                },
                {
                    'payment_status': 'block',
                    'additional_params': {'rule_id': 'test_order_subvention'},
                },
            ],
            'billing_request': {
                'order': {
                    'city': 'Reutov',
                    'due': '2019-01-01T23:59:59+0000',
                    'license_personal_id': 'order_subvention_fraud_pd_id',
                    'order_id': '111',
                    'time_zone': 'Europe/Moscow',
                    'zone': 'perm',
                },
            },
            'check_after': datetime.datetime(2019, 1, 6, 2, 0),
            'proc_status': 'complete',
        },
        '1011': {
            'subvention_type': 'driver_fix',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'currency': 'RUB',
                'driver': {
                    'license_personal_ids': [
                        'driver_fix_subvention_fraud_pd_id',
                    ],
                    'udi': '5d3f128c8fe28d5ce45d8af0',
                },
                'guarantee': '837.3953',
                'payment': '0',
                'period_end': '2018-06-02T09:25:45+00:00',
                'subvention': {'amount': '0.0000', 'currency': 'RUB'},
                'time_zone': 'Europe/Moscow',
            },
            'proc_status': 'complete',
        },
        '1012': {
            'subvention_type': 'driver_fix',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'currency': 'RUB',
                'driver': {
                    'license_personal_ids': [
                        'driver_fix_subvention_fraud_pd_id',
                    ],
                    'udi': '5d3f128c8fe28d5ce45d8af0',
                },
                'guarantee': '837.3953',
                'payment': '0',
                'period_end': '2018-06-02T09:25:45+00:00',
                'subvention': {'amount': '-100.0000', 'currency': 'RUB'},
                'time_zone': 'Europe/Moscow',
            },
            'proc_status': 'complete',
        },
        '1013': {
            'subvention_type': 'driver_fix',
            'statuses': [{'payment_status': 'pay'}],
            'billing_request': {
                'currency': 'RUB',
                'driver': {
                    'license_personal_ids': [
                        'e897fba4003d41c1815d520139e04ce5',
                    ],
                    'udi': '5d8b88f5b8e3f879689112cd',
                },
                'guarantee': '8199.0330',
                'payment': '0',
                'period_end': '2021-05-27T13:01:00+00:00',
                'subvention': {'amount': '100.0000', 'currency': 'RUB'},
                'time_zone': 'Europe/Moscow',
            },
            'proc_status': 'complete',
        },
        '1014': {
            'subvention_type': 'driver_fix',
            'statuses': [{'payment_status': 'block'}],
            'billing_request': {
                'currency': 'RUB',
                'driver': {
                    'license_personal_ids': [
                        'e897fba4003d41c1815d520139e04ce5',
                    ],
                    'udi': '5d8b88f5b8e3f879689112cd',
                },
                'guarantee': '8199.0330',
                'payment': '0',
                'period_end': '2021-05-27T13:01:00+00:00',
                'subvention': {'amount': '100.0000', 'currency': 'RUB'},
                'time_zone': 'Europe/Moscow',
            },
            'proc_status': 'complete',
        },
    }

    assert response.status_code == 200

    response_json = json.loads(response.text)
    check_statuses = {
        record['billing_id']: record for record in response_json['items']
    }

    assert len({v['antifraud_id'] for v in check_statuses.values()}) == len(
        expected_statuses,
    )
    assert len(check_statuses) == len(expected_statuses)

    after_update_stats.wait_call()

    records = {
        record['billing_id']: record
        for record in db.antifraud_subventions_check_status.find()
    }
    assert len(records) == len(expected_statuses)

    for k, v in expected_statuses.items():
        till = v.get('till')

        assert check_statuses[k]['action'] == v['action'], 'key: {}'.format(k)
        assert check_statuses[k].get('till') == till

        assert records[k]['subvention_type'] == (
            expected_db_records[k]['subvention_type']
        )
        assert records[k]['proc_status'] == (
            expected_db_records[k]['proc_status']
        )
        assert records[k].get('billing_request') == (
            expected_db_records[k].get('billing_request')
        ), 'k = {}'.format(k)
        assert records[k].get('check_after') == (
            expected_db_records[k].get('check_after')
        )
        statuses = records[k]['statuses']
        for actual_status, expected_status in zip(
                statuses, expected_db_records[k]['statuses'],
        ):
            assert actual_status['payment_status'] == (
                expected_status['payment_status']
            )
            if till is not None:
                assert actual_status['additional_params']['till'] == (
                    expected_status['till']
                )
            if 'additional_params' in expected_status:
                assert 'additional_params' in actual_status
                assert (
                    expected_status['additional_params']['rule_id']
                    == actual_status['additional_params']['rule_id']
                )

    assert len(rt_xaron_requests) == 0


@pytest.mark.now('2019-01-09T22:00:00+0000')
@pytest.mark.config(AFS_BILLING_SUBVENTION_ALWAYS_HOLD=False)
def test_subventions_check_idempotent(
        taxi_antifraud, mock_personal_driver_licenses_retrieve, testpoint, db,
):
    @testpoint('save_subvention_check_info')
    def after_update_stats(_):
        pass

    _REQUEST = {
        'items': [
            {
                'type': 'order',
                'billing_id': '1',
                'data': {
                    'order': {
                        'order_id': '101',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Moscow',
                        'due': '2019-01-10T00:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'moscow',
                    },
                },
            },
        ],
    }

    _EXPECTED_RESPONSE = {'billing_id': '1', 'action': 'pay'}

    _EXPECTED_DB_RECORD = {
        'billing_id': '1',
        'statuses': [
            {
                'payment_status': 'pay',
                'created': datetime.datetime(2019, 1, 9, 22, 0),
            },
        ],
        'subvention_type': 'order',
        'proc_status': 'check_later',
        'check_after': datetime.datetime(2019, 1, 11, 1, 0),
        'billing_request': _REQUEST['items'][0]['data'],
        'created': datetime.datetime(2019, 1, 9, 22, 0),
    }

    def _make_request(req):
        resp = taxi_antifraud.post('v1/subventions/check', json=req)
        after_update_stats.wait_call()
        assert resp.status_code == 200
        resp_json = json.loads(resp.text)
        return {k: v for k, v in resp_json['items'][0].items()}

    def _fetch_record(billing_id):
        return db.antifraud_subventions_check_status.find_one(
            {'billing_id': billing_id},
        )

    def _check(status, second=False):
        assert _EXPECTED_RESPONSE == {
            k: v for k, v in status.items() if second or k != 'antifraud_id'
        }

        record = _fetch_record('1')
        assert (
            {k: v for k, v in _EXPECTED_DB_RECORD.items() if k != 'statuses'}
            == {
                k: v
                for k, v in record.items()
                if k not in ['_id', 'statuses', 'updated']
            }
        )
        assert sorted(_EXPECTED_DB_RECORD['statuses']) == sorted(
            [
                {
                    k: v
                    for k, v in status.items()
                    if second or k != 'antifraud_id'
                }
                for status in record['statuses']
            ],
        )

    check_status = _make_request(_REQUEST)
    _check(check_status)

    _EXPECTED_RESPONSE['antifraud_id'] = check_status['antifraud_id']
    _EXPECTED_DB_RECORD['statuses'][0]['antifraud_id'] = check_status[
        'antifraud_id'
    ]

    check_status = _make_request(_REQUEST)
    _check(check_status, second=True)


@pytest.mark.now('2019-01-11T01:00:00+0000')
@pytest.mark.config(AFS_BILLING_SUBVENTION_DEFERRED_CHECK=True)
def test_billing_delay_subvention_checker(
        taxi_antifraud,
        mock_personal_driver_licenses_retrieve,
        mockserver,
        testpoint,
        db,
):
    @testpoint('after_bulk_check')
    def after_bulk_check(_):
        db.antifraud_subventions_check_status.delete_many({})

    @mockserver.json_handler('/antifraud/v1/subventions/check')
    def mock_afs(request):
        _REQUEST = {
            'doc_id/444140570019': {
                'type': 'order',
                'billing_id': 'doc_id/444140570019',
                'data': {
                    'order': {
                        'order_id': '101',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Moscow',
                        'due': '2019-01-10T00:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'moscow',
                    },
                },
            },
            'doc_id/449061040127': {
                'type': 'order',
                'billing_id': 'doc_id/449061040127',
                'data': {
                    'order': {
                        'order_id': '102',
                        'license_personal_id': 'lic1_pd_id',
                        'city': 'Moscow',
                        'due': '2019-01-10T00:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'moscow',
                    },
                },
            },
            'doc_id/459809850054': {
                'type': 'order',
                'billing_id': 'doc_id/459809850054',
                'data': {
                    'order': {
                        'order_id': '103',
                        'license_personal_id': 'lic3_pd_id',
                        'city': 'Moscow',
                        'due': '2019-01-10T00:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'moscow',
                    },
                },
            },
            'doc_id/123': {
                'type': 'order',
                'billing_id': 'doc_id/123',
                'data': {
                    'order': {
                        'order_id': '104',
                        'license_personal_id': 'lic4_pd_id',
                        'city': 'Moscow',
                        'due': '2019-01-10T00:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'moscow',
                    },
                },
            },
        }
        _RESPONSE = {
            'doc_id/444140570019': {
                'billing_id': 'doc_id/444140570019',
                'antifraud_id': 'afs_id/100500',
                'action': 'pay',
            },
            'doc_id/449061040127': {
                'billing_id': 'doc_id/449061040127',
                'antifraud_id': 'afs_id/100501',
                'action': 'block',
            },
            'doc_id/459809850054': {
                'billing_id': 'doc_id/459809850054',
                'antifraud_id': 'afs_id/100502',
                'action': 'pay',
            },
            'doc_id/123': {
                'billing_id': 'doc_id/123',
                'antifraud_id': 'afs_id/123',
                'action': 'block',
                'reason': {'id': 'block_rule1'},
            },
        }

        data = json.loads(request.get_data())
        assert len(data) == 1
        assert len(data['items']) == 4
        for item in data['items']:
            billing_id = item['billing_id']
            assert item == _REQUEST[billing_id]
        return {
            'items': [_RESPONSE[item['billing_id']] for item in data['items']],
        }

    requests_to_billing = []

    @mockserver.json_handler('/billing_orders/v1/antifraud')
    def mock_billing(request):
        _REQUEST = {
            'doc_id/449061040127': {
                'order_event_ref': 'doc_id/449061040127_afs_id/100501_block',
                'type': 'antifraud/action',
                'data': {
                    'billing_request_id': 'doc_id/449061040127',
                    'antifraud_response_id': 'afs_id/100501',
                    'action': 'block',
                    'decision_time': '2019-01-11T01:00:00+00:00',
                },
            },
            'doc_id/123': {
                'order_event_ref': 'doc_id/123_afs_id/123_block',
                'type': 'antifraud/action',
                'data': {
                    'billing_request_id': 'doc_id/123',
                    'antifraud_response_id': 'afs_id/123',
                    'action': 'block',
                    'decision_time': '2019-01-11T01:00:00+00:00',
                    'reason': {'id': 'block_rule1'},
                },
            },
        }
        _RESPONSE = {
            'doc_id/449061040127': {'doc': {'id': 1001}},
            'doc_id/123': {'doc': {'id': 1002}},
        }

        data = json.loads(request.get_data())
        requests_to_billing.append(data)
        billing_id = data['data']['billing_request_id']
        assert data == _REQUEST[billing_id]
        return _RESPONSE[billing_id]

    taxi_antifraud.run_workers(['billing_delay_subvention_checker'])

    mock_afs.wait_call()
    mock_billing.wait_call()
    after_bulk_check.wait_call()

    assert sorted(requests_to_billing, key=lambda k: k['order_event_ref']) == [
        {
            'data': {
                'action': 'block',
                'antifraud_response_id': 'afs_id/123',
                'billing_request_id': 'doc_id/123',
                'decision_time': '2019-01-11T01:00:00+00:00',
                'reason': {'id': 'block_rule1'},
            },
            'order_event_ref': 'doc_id/123_afs_id/123_block',
            'type': 'antifraud/action',
        },
        {
            'data': {
                'action': 'block',
                'antifraud_response_id': 'afs_id/100501',
                'billing_request_id': 'doc_id/449061040127',
                'decision_time': '2019-01-11T01:00:00+00:00',
            },
            'order_event_ref': 'doc_id/449061040127_afs_id/100501_block',
            'type': 'antifraud/action',
        },
    ]


@pytest.mark.parametrize(
    'license_personal_id,action,rule_id',
    [
        ('lic1_pd_id', 'block', 'test_rule1'),
        ('lic2_pd_id', 'pay', None),
        ('lic3_pd_id', 'block', 'test_fraud_subvention1'),
    ],
)
@pytest.mark.now('2019-01-11T01:00:00+0000')
def test_subventions_billing_check_later(
        taxi_antifraud,
        mock_personal_driver_licenses_retrieve,
        testpoint,
        db,
        now,
        license_personal_id,
        action,
        rule_id,
):
    @testpoint('save_subvention_check_info')
    def after_update_stats(_):
        pass

    def _make_request(input):
        resp = taxi_antifraud.post('v1/subventions/check', json=input)
        after_update_stats.wait_call()
        assert resp.status_code == 200
        return json.loads(resp.text)['items'][0]

    def _make_second_status():
        status = {
            'antifraud_id': antifraud_id,
            'payment_status': action,
            'created': datetime.datetime(2019, 1, 11, 2, 0),
        }
        if rule_id is not None:
            status['additional_params'] = {'rule_id': rule_id}
        return status

    _REQUEST = {
        'items': [
            {
                'type': 'order',
                'billing_id': 'doc_id/444140570019',
                'data': {
                    'order': {
                        'order_id': '101',
                        'license_personal_id': license_personal_id,
                        'city': 'Moscow',
                        'due': '2019-01-10T00:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                        'zone': 'moscow',
                    },
                    'subvention': {'amount': '100.500', 'currency': 'RUB'},
                },
            },
        ],
    }

    antifraud_id = None

    for _ in range(2):
        resp_json = _make_request(_REQUEST)

        assert resp_json['billing_id'] == 'doc_id/444140570019'
        assert resp_json['action'] == 'pay'
        if antifraud_id is not None:
            assert resp_json['antifraud_id'] == antifraud_id
        antifraud_id = resp_json['antifraud_id']

    record = db.antifraud_subventions_check_status.find_one(
        {'billing_id': 'doc_id/444140570019'},
    )
    assert record['proc_status'] == 'check_later'
    assert len(record['statuses']) == 1
    assert record['statuses'][0]['payment_status'] == 'pay'

    taxi_antifraud.tests_control(
        now + datetime.timedelta(hours=1), invalidate_caches=False,
    )

    resp_json = _make_request(_REQUEST)
    assert resp_json['billing_id'] == 'doc_id/444140570019'
    assert resp_json['action'] == action
    assert resp_json['antifraud_id'] != antifraud_id
    if rule_id is not None:
        assert resp_json['reason']['id'] == rule_id

    antifraud_id = resp_json['antifraud_id']

    fraud_record = db.antifraud_subventions_check_status.find_one(
        {'billing_id': 'doc_id/444140570019'},
    )

    assert fraud_record['billing_id'] == 'doc_id/444140570019'
    assert fraud_record['proc_status'] == 'complete'
    assert fraud_record['statuses'] == [
        {
            'antifraud_id': 'afs_id/100500',
            'payment_status': 'pay',
            'created': datetime.datetime(2019, 1, 9, 22, 0),
        },
        _make_second_status(),
    ]


@pytest.mark.parametrize(
    'billing_id,due,action,dt',
    [
        (
            'doc/1',
            '2018-03-25T20:59:59.000000+00:00',
            'pay',
            datetime.datetime(2018, 3, 25, 21, 30, 0),
        ),
        (
            'doc/2',
            '2018-03-25T21:00:00.000000+00:00',
            'delay',
            datetime.datetime(2018, 3, 25, 21, 30, 0),
        ),
        (
            'doc/3',
            '2018-03-25T21:00:00.000000+00:00',
            'delay',
            datetime.datetime(2018, 3, 27, 0, 0, 0),
        ),
        (
            'doc/4',
            '2018-03-25T21:00:00.000000+00:00',
            'pay',
            datetime.datetime(2018, 3, 27, 1, 0, 0),
        ),
        (
            'doc/5',
            '2018-10-03T19:30:00.000000+00:00',
            'delay',
            datetime.datetime(2018, 10, 3, 19, 0, 0),
        ),
        (
            'doc/6',
            '2018-10-03T19:30:00.000000+00:00',
            'delay',
            datetime.datetime(2018, 10, 4, 0, 54, 59),
        ),
        (
            'doc/6',
            '2018-10-03T19:30:00.000000+00:00',
            'pay',
            datetime.datetime(2018, 10, 4, 0, 55, 0),
        ),
        (
            'doc/7',
            '2018-10-03T19:30:01.000000+00:00',
            'pay',
            datetime.datetime(2018, 10, 3, 19, 0, 0),
        ),
        (
            'doc/10',
            '2019-08-08T06:00:00.000000+00:00',
            'pay',
            datetime.datetime(2019, 8, 8, 16, 30, 0),
        ),
    ],
)
@pytest.mark.config(AFS_BILLING_SUBVENTION_ALWAYS_HOLD=False)
def test_v1_subventions_check_hold(
        taxi_antifraud,
        mock_personal_driver_licenses_retrieve,
        billing_id,
        due,
        action,
        dt,
):
    _REQUEST = {
        'items': [
            {
                'type': 'order',
                'billing_id': billing_id,
                'data': {
                    'order': {
                        'order_id': 'e315c93736ec1f47932180b3080506ce',
                        'license_personal_id': '5223182651_pd_id',
                        'city': 'Dzerzhinsk',
                        'zone': 'dzerzhinsk',
                        'time_zone': 'Europe/Moscow',
                        'due': due,
                    },
                },
            },
        ],
    }

    if dt is not None:
        taxi_antifraud.tests_control(dt, invalidate_caches=False)

    resp = taxi_antifraud.post('v1/subventions/check', json=_REQUEST)
    assert resp.status_code == 200
    assert json.loads(resp.text)['items'][0]['action'] == action


def check_blocked_checks_db_content(
        taxi_antifraud, testpoint, db, request_content, expected_db_content,
):
    @testpoint('save_subvention_check_info')
    def after_update_stats(_):
        pass

    response = taxi_antifraud.post(
        'v1/subventions/check', json=request_content,
    )

    assert response.status_code == 200

    after_update_stats.wait_call()

    records = {
        record['billing_id']: {
            'billing_id': record['billing_id'],
            'billing_request': record['billing_request'],
            'created': record['created'],
            'proc_status': record['proc_status'],
            'statuses': [
                {
                    'created': status['created'],
                    'payment_status': status['payment_status'],
                }
                for status in record['statuses']
            ],
            'subvention_type': record['subvention_type'],
        }
        for record in db.antifraud_subventions_check_status_only_blocked.find()
    }

    assert records == expected_db_content


@pytest.mark.now('2019-01-09T22:00:00+0000')
@pytest.mark.config(
    AFS_BILLING_SUBVENTION_ALWAYS_HOLD=False,
    AFS_SAVE_BLOCKED_SUBVENTION_CHECK_INFO=True,
)
@pytest.mark.parametrize(
    'request_content,expected_db_content',
    [
        (
            {
                'items': [
                    {
                        'type': 'driver_fix',
                        'billing_id': 'new_billing_id',
                        'data': {
                            'currency': 'RUB',
                            'driver': {
                                'license_personal_ids': [
                                    'definitely_frauder_pd_id',
                                ],
                                'udi': '5bf65ce6254e5eb96a531235',
                            },
                            'guarantee': '80.0000',
                            'payment': '0',
                            'period_end': '2019-01-08T20:00:00+0000',
                            'time_zone': 'Europe/Moscow',
                        },
                    },
                ],
            },
            {
                'new_billing_id': {
                    'billing_id': 'new_billing_id',
                    'billing_request': {
                        'currency': 'RUB',
                        'driver': {
                            'license_personal_ids': [
                                'definitely_frauder_pd_id',
                            ],
                            'udi': '5bf65ce6254e5eb96a531235',
                        },
                        'guarantee': '80.0000',
                        'payment': '0',
                        'period_end': '2019-01-08T20:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                    },
                    'created': datetime.datetime(2019, 1, 9, 22, 0),
                    'proc_status': 'complete',
                    'statuses': [
                        {
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'block',
                        },
                    ],
                    'subvention_type': 'driver_fix',
                },
                'old_billing_id': {
                    'billing_id': 'old_billing_id',
                    'billing_request': {
                        'currency': 'RUB',
                        'driver': {
                            'license_personal_ids': [
                                'definitely_frauder_pd_id',
                            ],
                            'udi': '5bf65ce6254e5eb96a531235',
                        },
                        'guarantee': '80.0000',
                        'payment': '0',
                        'period_end': '2019-01-08T20:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                    },
                    'created': datetime.datetime(2019, 1, 9, 22, 0),
                    'proc_status': 'check_later',
                    'statuses': [
                        {
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'pay',
                        },
                    ],
                    'subvention_type': 'driver_fix',
                },
            },
        ),
    ],
)
def test_subventions_check_status_only_blocked_insert_block(
        taxi_antifraud,
        mock_personal_driver_licenses_retrieve,
        testpoint,
        db,
        request_content,
        expected_db_content,
):
    check_blocked_checks_db_content(
        taxi_antifraud, testpoint, db, request_content, expected_db_content,
    )


@pytest.mark.now('2019-01-09T22:00:00+0000')
@pytest.mark.config(
    AFS_BILLING_SUBVENTION_ALWAYS_HOLD=False,
    AFS_SAVE_BLOCKED_SUBVENTION_CHECK_INFO=True,
)
@pytest.mark.parametrize(
    'request_content,expected_db_content',
    [
        (
            {
                'items': [
                    {
                        'type': 'driver_fix',
                        'billing_id': 'old_billing_id',
                        'data': {
                            'currency': 'RUB',
                            'driver': {
                                'license_personal_ids': [
                                    'definitely_frauder_pd_id',
                                ],
                                'udi': '5bf65ce6254e5eb96a531235',
                            },
                            'guarantee': '80.0000',
                            'payment': '0',
                            'period_end': '2019-01-08T20:00:00+0000',
                            'time_zone': 'Europe/Moscow',
                        },
                    },
                ],
            },
            {
                'old_billing_id': {
                    'billing_id': 'old_billing_id',
                    'billing_request': {
                        'currency': 'RUB',
                        'driver': {
                            'license_personal_ids': [
                                'definitely_frauder_pd_id',
                            ],
                            'udi': '5bf65ce6254e5eb96a531235',
                        },
                        'guarantee': '80.0000',
                        'payment': '0',
                        'period_end': '2019-01-08T20:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                    },
                    'created': datetime.datetime(2019, 1, 9, 22, 0),
                    'proc_status': 'complete',
                    'statuses': [
                        {
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'pay',
                        },
                        {
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'block',
                        },
                    ],
                    'subvention_type': 'driver_fix',
                },
            },
        ),
    ],
)
def test_subventions_check_status_only_blocked_update_block_in_db(
        taxi_antifraud,
        mock_personal_driver_licenses_retrieve,
        testpoint,
        db,
        request_content,
        expected_db_content,
):
    check_blocked_checks_db_content(
        taxi_antifraud, testpoint, db, request_content, expected_db_content,
    )


@pytest.mark.now('2019-01-09T22:00:00+0000')
@pytest.mark.config(
    AFS_BILLING_SUBVENTION_ALWAYS_HOLD=False,
    AFS_SAVE_BLOCKED_SUBVENTION_CHECK_INFO=True,
)
@pytest.mark.parametrize(
    'request_content,expected_db_content',
    [
        (
            {
                'items': [
                    {
                        'type': 'driver_fix',
                        'billing_id': 'new_billing_id',
                        'data': {
                            'currency': 'RUB',
                            'driver': {
                                'license_personal_ids': [
                                    'normal_driver_pd_id',
                                ],
                                'udi': '5bf65ce6254e5eb96a531235',
                            },
                            'guarantee': '80.0000',
                            'payment': '0',
                            'period_end': '2019-01-08T20:00:00+0000',
                            'time_zone': 'Europe/Moscow',
                        },
                    },
                ],
            },
            {
                'old_billing_id': {
                    'billing_id': 'old_billing_id',
                    'billing_request': {
                        'currency': 'RUB',
                        'driver': {
                            'license_personal_ids': [
                                'definitely_frauder_pd_id',
                            ],
                            'udi': '5bf65ce6254e5eb96a531235',
                        },
                        'guarantee': '80.0000',
                        'payment': '0',
                        'period_end': '2019-01-08T20:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                    },
                    'created': datetime.datetime(2019, 1, 9, 22, 0),
                    'proc_status': 'check_later',
                    'statuses': [
                        {
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'pay',
                        },
                    ],
                    'subvention_type': 'driver_fix',
                },
            },
        ),
    ],
)
def test_subventions_check_status_only_blocked_ignore_not_block(
        taxi_antifraud,
        mock_personal_driver_licenses_retrieve,
        testpoint,
        db,
        request_content,
        expected_db_content,
):
    check_blocked_checks_db_content(
        taxi_antifraud, testpoint, db, request_content, expected_db_content,
    )


@pytest.mark.now('2019-01-09T22:00:00+0000')
@pytest.mark.config(
    AFS_BILLING_SUBVENTION_ALWAYS_HOLD=False,
    AFS_SAVE_BLOCKED_SUBVENTION_CHECK_INFO=False,
)
@pytest.mark.parametrize(
    'request_content,expected_db_content',
    [
        (
            {
                'items': [
                    {
                        'type': 'driver_fix',
                        'billing_id': 'new_billing_id',
                        'data': {
                            'currency': 'RUB',
                            'driver': {
                                'license_personal_ids': [
                                    'definitely_frauder_pd_id',
                                ],
                                'udi': '5bf65ce6254e5eb96a531235',
                            },
                            'guarantee': '80.0000',
                            'payment': '0',
                            'period_end': '2019-01-08T20:00:00+0000',
                            'time_zone': 'Europe/Moscow',
                        },
                    },
                ],
            },
            {
                'old_billing_id': {
                    'billing_id': 'old_billing_id',
                    'billing_request': {
                        'currency': 'RUB',
                        'driver': {
                            'license_personal_ids': [
                                'definitely_frauder_pd_id',
                            ],
                            'udi': '5bf65ce6254e5eb96a531235',
                        },
                        'guarantee': '80.0000',
                        'payment': '0',
                        'period_end': '2019-01-08T20:00:00+0000',
                        'time_zone': 'Europe/Moscow',
                    },
                    'created': datetime.datetime(2019, 1, 9, 22, 0),
                    'proc_status': 'check_later',
                    'statuses': [
                        {
                            'created': datetime.datetime(2019, 1, 9, 22, 0),
                            'payment_status': 'pay',
                        },
                    ],
                    'subvention_type': 'driver_fix',
                },
            },
        ),
    ],
)
def test_subventions_check_status_only_blocked_ignore_with_disabled_flag(
        taxi_antifraud,
        mock_personal_driver_licenses_retrieve,
        testpoint,
        db,
        request_content,
        expected_db_content,
):
    check_blocked_checks_db_content(
        taxi_antifraud, testpoint, db, request_content, expected_db_content,
    )


@pytest.mark.now('2019-01-09T23:00:00+0000')
@pytest.mark.config(AFS_BILLING_SUBVENTION_ALWAYS_HOLD=False)
def test_subventions_check_order_subvention(
        taxi_antifraud, mock_personal_driver_licenses_retrieve, db,
):
    taxi_antifraud.post(
        'v1/subventions/check',
        json={
            'items': [
                {
                    'type': 'order',
                    'billing_id': '500',
                    'data': {
                        'order': {
                            'order_id': 'subvention_order_id',
                            'license_personal_id': 'subvention_license_pd_id',
                            'city': 'Moscow',
                            'due': '2018-01-10T00:00:00+0000',
                            'time_zone': 'Europe/Moscow',
                            'zone': 'moscow',
                        },
                        'subvention': {'amount': '100.500', 'currency': 'RUB'},
                    },
                },
            ],
        },
    )
    record = db.antifraud_subventions_check_status.find_one(
        {'billing_id': '500'},
    )
    status = record['statuses'][1]
    assert status['payment_status'] == 'block'
    assert status['additional_params']['rule_id'] == 'test_fraud_subvention'


def _test_subventions_check_exp_change_delay(
        taxi_antifraud, expected_response,
):
    response = taxi_antifraud.post(
        'v1/subventions/check',
        json={
            'items': [
                {
                    'type': 'goal',
                    'billing_id': '100',
                    'data': {
                        'driver': {
                            'udi': 'udi0',
                            'license_personal_ids': ['lic_pd_id0'],
                            'rules': [
                                {
                                    'day_ride_count_days': 7,
                                    'day_ride_count': [20],
                                },
                            ],
                        },
                        'period_end': '2022-02-10T00:00:00+0000',
                        'time_zone': 'Africa/Accra',
                    },
                },
                {
                    'type': 'goal',
                    'billing_id': '101',
                    'data': {
                        'driver': {
                            'udi': 'udi1',
                            'license_personal_ids': ['lic_pd_id1'],
                            'rules': [
                                {
                                    'day_ride_count_days': 7,
                                    'day_ride_count': [20],
                                },
                            ],
                        },
                        'period_end': '2022-02-10T00:00:00+0000',
                        'time_zone': 'Europe/London',
                    },
                },
                {
                    'type': 'goal',
                    'billing_id': '102',
                    'data': {
                        'driver': {
                            'udi': 'udi2',
                            'license_personal_ids': ['lic_pd_id2'],
                            'rules': [
                                {
                                    'day_ride_count_days': 7,
                                    'day_ride_count': [20],
                                },
                            ],
                        },
                        'period_end': '2022-02-10T00:00:00+0200',
                        'time_zone': 'Europe/Kaliningrad',
                    },
                },
                {
                    'type': 'goal',
                    'billing_id': '103',
                    'data': {
                        'driver': {
                            'udi': 'udi3',
                            'license_personal_ids': ['lic_pd_id3'],
                            'rules': [
                                {
                                    'day_ride_count_days': 7,
                                    'day_ride_count': [20],
                                },
                            ],
                        },
                        'period_end': '2022-02-10T00:00:00+0300',
                        'time_zone': 'Europe/Moscow',
                    },
                },
                {
                    'type': 'goal',
                    'billing_id': '104',
                    'data': {
                        'driver': {
                            'udi': 'udi4',
                            'license_personal_ids': ['lic_pd_id4'],
                            'rules': [
                                {
                                    'day_ride_count_days': 7,
                                    'day_ride_count': [20],
                                },
                            ],
                        },
                        'period_end': '2022-02-10T00:00:00+0400',
                        'time_zone': 'Europe/Samara',
                    },
                },
                {
                    'type': 'goal',
                    'billing_id': '105',
                    'data': {
                        'driver': {
                            'udi': 'udi5',
                            'license_personal_ids': ['lic_pd_id5'],
                            'rules': [
                                {
                                    'day_ride_count_days': 7,
                                    'day_ride_count': [20],
                                },
                            ],
                        },
                        'period_end': '2022-02-10T00:00:00+1000',
                        'time_zone': 'Asia/Vladivostok',
                    },
                },
                {
                    'type': 'goal',
                    'billing_id': '106',
                    'data': {
                        'driver': {
                            'udi': 'udi6',
                            'license_personal_ids': ['lic_pd_id6'],
                            'rules': [
                                {
                                    'day_ride_count_days': 7,
                                    'day_ride_count': [20],
                                },
                            ],
                        },
                        'period_end': '2022-02-10T00:00:00+0000',
                        'time_zone': 'Africa/Abidjan',
                    },
                },
            ],
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    for elem in resp_json['items']:
        del elem['antifraud_id']
    assert resp_json == expected_response


@pytest.mark.now('2022-02-09T20:00:00+0300')
@pytest.mark.experiments3(
    name='afs_v1_subventions_check_change_check_tp',
    match={'predicate': {'type': 'true'}, 'enabled': True},
    consumers=['afs/v1_subventions_check'],
    clauses=[
        {
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'subvention_type',
                                'arg_type': 'string',
                                'value': 'goal',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'set': ['Africa/Abidjan'],
                                'arg_name': 'time_zone',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {'goal': {'enabled': True, 'delay': 8}},
        },
        {
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'subvention_type',
                                'arg_type': 'string',
                                'value': 'goal',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'set': [
                                    'Europe/London',
                                    'Europe/Kaliningrad',
                                    'Europe/Moscow',
                                    'Europe/Samara',
                                    'Asia/Vladivostok',
                                ],
                                'arg_name': 'time_zone',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {'goal': {'enabled': True}},
        },
    ],
)
def test_subventions_check_exp_change_delay_on(
        taxi_antifraud, mock_personal_driver_licenses_retrieve, db,
):
    _test_subventions_check_exp_change_delay(
        taxi_antifraud,
        {
            'items': [
                {
                    'action': 'delay',
                    'billing_id': '100',
                    'till': '2022-02-11T01:00:00+00:00',
                },
                {
                    'action': 'delay',
                    'billing_id': '101',
                    'till': '2022-02-12T01:00:00+00:00',
                },
                {
                    'action': 'delay',
                    'billing_id': '102',
                    'till': '2022-02-12T01:00:00+00:00',
                },
                {
                    'action': 'delay',
                    'billing_id': '103',
                    'till': '2022-02-11T01:00:00+00:00',
                },
                {
                    'action': 'delay',
                    'billing_id': '104',
                    'till': '2022-02-11T01:00:00+00:00',
                },
                {
                    'action': 'delay',
                    'billing_id': '105',
                    'till': '2022-02-11T01:00:00+00:00',
                },
                {
                    'action': 'delay',
                    'billing_id': '106',
                    'till': '2022-02-12T05:00:00+00:00',
                },
            ],
        },
    )


@pytest.mark.now('2022-02-09T20:00:00+0300')
def test_subventions_check_exp_change_delay_off(
        taxi_antifraud, mock_personal_driver_licenses_retrieve, db,
):
    _test_subventions_check_exp_change_delay(
        taxi_antifraud,
        {
            'items': [
                {
                    'action': 'delay',
                    'billing_id': '100',
                    'till': '2022-02-11T01:00:00+00:00',
                },
                {
                    'action': 'delay',
                    'billing_id': '101',
                    'till': '2022-02-11T01:00:00+00:00',
                },
                {
                    'action': 'delay',
                    'billing_id': '102',
                    'till': '2022-02-11T01:00:00+00:00',
                },
                {
                    'action': 'delay',
                    'billing_id': '103',
                    'till': '2022-02-11T01:00:00+00:00',
                },
                {
                    'action': 'delay',
                    'billing_id': '104',
                    'till': '2022-02-10T01:00:00+00:00',
                },
                {
                    'action': 'delay',
                    'billing_id': '105',
                    'till': '2022-02-10T01:00:00+00:00',
                },
                {
                    'action': 'delay',
                    'billing_id': '106',
                    'till': '2022-02-11T01:00:00+00:00',
                },
            ],
        },
    )
