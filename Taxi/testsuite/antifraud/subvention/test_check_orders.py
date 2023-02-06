import json

import pytest

ENABLED_RULES = [
    'test_city_info',
    'test_fraud_driver_license_personal_id',
    'test_fraud_license',
    'test_hold',
    'test_due',
    'test_order_id',
    'test_order_fraud_license',
    'test_rule_black_license',
    'test_rule_black_license_hold',
    'test_rule_test',
    'test_bad_rule1',
    'test_bad_rule2',
    'test_bad_rule3',
    'test_bad_rule_js1',
    'test_bad_rule_js2',
    'test_bad_rule_js3',
    'test_bad_rule_js4',
    'test_bad_rule_js5',
    'test_city',
    'test_no_city',
    'test_calc_time',
    'test_no_stat',
    'test_fraud_subvention',
]


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


@pytest.mark.noshuffledb(reason='Flaky, see TAXIBACKEND-15383')
@pytest.mark.parametrize(
    'order,enabled_rules,rules,test_rules,' 'expected_response',
    [
        (
            {
                'order_id': 'some_order_id',
                'license_personal_id': 'fraud_license_pd_id',
                'city': 'Taxiville',
                'subvention': {'amount': '100.500', 'currency': 'RUB'},
                'zone': 'ekb',
            },
            ENABLED_RULES,
            ['test_fraud_license', 'test_fraud_subvention'],
            {'test_rule_test'},
            {
                'found': True,
                'frauder': True,
                'rule_id': 'test_fraud_license',
                'confidence': 900001,
            },
        ),
        (
            {
                'order_id': 'some_order_id',
                'license_personal_id': 'fraud_license_pd_id',
                'city': 'Taxiville',
                'hold': True,
                'zone': 'ekb',
            },
            ENABLED_RULES,
            ['test_fraud_license', 'test_hold'],
            {'test_rule_test'},
            {
                'found': True,
                'frauder': True,
                'rule_id': 'test_fraud_license',
                'confidence': 900001,
            },
        ),
        (
            {
                'order_id': 'some_order_id',
                'license_personal_id': 'some_license_pd_id',
                'city': 'Taxiville',
                'hold': True,
                'zone': 'ekb',
            },
            ENABLED_RULES,
            ['test_hold'],
            {'test_rule_test'},
            {
                'found': True,
                'frauder': True,
                'rule_id': 'test_hold',
                'confidence': 200001,
            },
        ),
        (
            {
                'order_id': 'some_order_id',
                'license_personal_id': 'some_license_pd_id',
                'city': 'Taxiville',
                'due': '2016-12-13T05:33:13+0000',
                'zone': 'ekb',
            },
            ENABLED_RULES,
            ['test_due'],
            {'test_rule_test'},
            {
                'found': True,
                'frauder': True,
                'rule_id': 'test_due',
                'confidence': 300001,
            },
        ),
        (
            {
                'order_id': 'fraud_order_id',
                'license_personal_id': 'some_license_pd_id',
                'city': 'Taxiville',
                'zone': 'ekb',
            },
            ENABLED_RULES,
            ['test_order_id'],
            {'test_rule_test'},
            {
                'found': True,
                'frauder': True,
                'rule_id': 'test_order_id',
                'confidence': 900001,
            },
        ),
        (
            {
                'order_id': 'some_order_id',
                'license_personal_id': 'order_fraud_license_pd_id',
                'city': 'Taxiville',
                'zone': 'ekb',
            },
            ENABLED_RULES,
            ['test_order_fraud_license'],
            {'test_rule_test'},
            {
                'found': True,
                'frauder': True,
                'rule_id': 'test_order_fraud_license',
                'confidence': 900001,
            },
        ),
        (
            {
                'order_id': 'some_order_id',
                'license_personal_id': 'SUPERFRAUDER_pd_id',
                'city': 'Taxiville',
                'zone': 'ekb',
            },
            ENABLED_RULES,
            ['test_fraud_driver_license_personal_id'],
            {'test_rule_test'},
            {
                'found': True,
                'frauder': True,
                'rule_id': 'test_fraud_driver_license_personal_id',
                'confidence': 900001,
            },
        ),
        (
            {
                'order_id': 'some_order_id',
                'license_personal_id': 'order_fraud_license_pd_id',
                'city': 'Taxiville',
                'zone': 'perm',
            },
            ENABLED_RULES,
            ['test_order_fraud_license'],
            {'test_rule_test'},
            {
                'found': True,
                'frauder': True,
                'rule_id': 'test_order_fraud_license',
                'confidence': 900001,
            },
        ),
    ],
)
@pytest.mark.now('2016-12-15T01:01:13+0000')
@pytest.mark.config(
    AFS_SUBVENTION_PROCESSOR_ENABLED=True,
    AFS_SUBVENTION_RULES_FETCH_LICENSE_PERSONAL_ID_FROM_PERSONAL=True,
)
@pytest.mark.filldb(antifraud_rules='base')
def test_check_orders_base(
        taxi_antifraud,
        config,
        now,
        db,
        mock_personal_driver_licenses_find,
        mock_personal_driver_licenses_retrieve,
        order,
        enabled_rules,
        rules,
        test_rules,
        expected_response,
):
    _check_impl(**locals())


@pytest.mark.noshuffledb(reason='Flaky, see TAXIBACKEND-15383')
@pytest.mark.parametrize(
    'order,enabled_rules,rules,test_rules,' 'expected_response',
    [
        (
            {
                'order_id': '1005001',
                'license_personal_id': '1005001_pd_id',
                'city': 'Taxiville',
                'hold': True,
                'due': '2016-12-14T02:33:13+0300',
                'zone': 'ekb',
            },
            ['test_city'],
            ['test_city'],
            set(),
            {
                'found': True,
                'frauder': True,
                'rule_id': 'test_city',
                'confidence': 4,
            },
        ),
        (
            {
                'order_id': '1005003',
                'license_personal_id': '1005003_pd_id',
                'city': 'Taxiville',
                'hold': True,
                'due': '2016-12-14T02:33:13+0300',
                'calc_time': 66.6,
                'zone': 'ekb',
            },
            ['test_calc_time'],
            ['test_calc_time'],
            set(),
            {
                'found': True,
                'frauder': True,
                'rule_id': 'test_calc_time',
                'confidence': 5,
            },
        ),
        (
            {
                'order_id': '1005004',
                'license_personal_id': '1005004_pd_id',
                'city': 'Taxiville',
                'hold': True,
                'due': '2016-12-14T02:33:13+0300',
                'zone': 'ekb',
            },
            ['test_no_stat'],
            ['test_no_stat'],
            set(),
            {
                'found': True,
                'frauder': True,
                'rule_id': 'test_no_stat',
                'confidence': 3,
            },
        ),
    ],
)
@pytest.mark.now('2016-12-15T01:01:13+0000')
@pytest.mark.filldb(antifraud_rules='mod')
def test_check_orders_mod(
        taxi_antifraud,
        mock_personal_driver_licenses_retrieve,
        config,
        now,
        db,
        order,
        enabled_rules,
        rules,
        test_rules,
        expected_response,
):
    _check_impl(**locals())


@pytest.mark.parametrize(
    'order,enabled_rules,rules,test_rules,' 'expected_response',
    [
        (
            {
                'order_id': '123',
                'license_personal_id': 'azaza1_pd_id',
                'city': 'Taxiville',
                'hold': True,
                'due': '2016-12-14T02:33:13+0300',
                'zone': 'ekb',
            },
            ['rule_1'],
            ['rule_1'],
            set(),
            {
                'found': True,
                'frauder': True,
                'rule_id': 'rule_1',
                'confidence': 777,
            },
        ),
        (
            {
                'order_id': '12',
                'license_personal_id': 'azaza1_pd_id',
                'city': 'Taxiville',
                'hold': True,
                'due': '2016-12-14T02:33:13+0300',
                'zone': 'ekb',
            },
            ['rule_2'],
            ['rule_2'],
            set(),
            {
                'found': True,
                'frauder': True,
                'rule_id': 'rule_2',
                'confidence': 777,
            },
        ),
    ],
)
@pytest.mark.now('2016-12-15T01:01:13+0000')
@pytest.mark.config(
    AFS_SUBVENTION_CUSTOM_DATAMARTS_ENABLED=True,
    AFS_SUBVENTION_PROCESSOR_ENABLED=True,
)
@pytest.mark.filldb(
    antifraud_custom_datamarts_driver_license='custom_dtms',
    antifraud_custom_datamarts_order_id='custom_dtms',
    antifraud_rules='custom_dtms',
)
def test_check_orders_custom_dtms(
        taxi_antifraud,
        mock_personal_driver_licenses_retrieve,
        config,
        now,
        db,
        order,
        enabled_rules,
        rules,
        test_rules,
        expected_response,
):
    _check_impl(**locals())


def _check_impl(
        taxi_antifraud,
        config,
        now,
        db,
        order,
        enabled_rules,
        rules,
        test_rules,
        expected_response,
        mock_personal_driver_licenses_find=None,
        mock_personal_driver_licenses_retrieve=None,
):
    def check(response, records_count):
        def check_order_info(object):
            assert object['order_id'] == order['order_id']
            if 'license' in order:
                assert object['license'] == order['license']
            else:
                assert object['license'] == order['license_personal_id'][:-6]
            assert object['found'] == expected_response['found']
            if object['found']:
                assert object['frauder'] == expected_response['frauder']
                if object['frauder']:
                    assert object['rule_id'] == (expected_response['rule_id'])
                    assert object['confidence'] == (
                        expected_response['confidence']
                    )

        assert response.status_code == 200
        data = response.json()
        assert 'orders' in data
        assert len(data['orders']) == 1
        response_order = data['orders'][0]
        check_order_info(response_order)
        records = db.antifraud_subvention_frauders.find(
            {'order_id': order['order_id']},
        )
        assert records.count() == records_count
        record = records[0]
        assert set(record['test_rule_ids']) == test_rules
        assert record['rule_ids'] == rules
        assert record['hold'] == order.get('hold', False)
        check_order_info(record)

    def enable_rules():
        db.antifraud_rules.update(
            {'_id': {'$in': enabled_rules}},
            {'$set': {'enabled': True}},
            multi=True,
        )

    enable_rules()
    taxi_antifraud.tests_control(now=now, invalidate_caches=True)

    request = {'orders': [order]}

    check(taxi_antifraud.post('subvention/check_orders', request), 1)

    config.set_values(dict(AFS_SUBVENTION_PROCESSOR_ENABLED=True))
    taxi_antifraud.tests_control(now=now, invalidate_caches=True)

    check(taxi_antifraud.post('subvention/check_orders', request), 2)
