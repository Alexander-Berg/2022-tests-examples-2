import base64
import datetime
import json

import pytest
import yt.yson

from antifraud import utils


@pytest.fixture
def mock_personal_phones_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def mock_personal_phones_retrieve(request):
        request_json = json.loads(request.get_data())
        phones_map = {
            'f3b46027b6af44ca8c998a111c94e296': '+79169999999',
            '87745c883b8149138c50ef7e454b7857': '+77777777777',
            '7c444af50f37412e993354b056f9e843': '+79031234568',
            '2c225598d99c44b8bd92ffc1db0f524a': '+79091234567',
            'fa29f28a20534d5faf2e9aef15a8102d': '+79123456789',
            'e5d502839c52491790416f0777083435': '+79160000000',
            'dff27ecdb137448c9ac98a709481f799': '+79162991489',
            '07b6badad9464a439507a2c1601031dd': '+79169999998',
            '1c406207f46f42069cdb14a98c78af31': '+79172991489',
            '4a83ce41d92741a4abb388a19d0b4ee7': '+79031234569',
        }
        personal_id = request_json['id']
        if personal_id in phones_map:
            return {'id': personal_id, 'value': phones_map[personal_id]}

        return mockserver.make_response({}, 404)


@pytest.mark.parametrize(
    'input,output,expected_code',
    [
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': 'f3b46027b6af44ca8c998a111c94e296',
                'user_id': 'df6b27dc9b044fbdb5b703ba993a1786',
                'user_phone_id': '54f7632696421984c36931f9',
            },
            {'frauder': True, 'rule_id': 'test_rule2_2'},
            200,
        ),
        (
            {
                'user_personal_phone_id': 'f3b46027b6af44ca8c998a111c94e296',
                'user_id': 'df6b27dc9b044fbdb5b703ba993a1786',
            },
            {},
            400,
        ),
        (
            {
                'user_id': '85f087e6ca1246ba938dc0b4b87658f8',
                'zone': 'moscow',
                'order_id': 'e9103e313d9346d6ae02297dfd62b942',
                'user_phone_id': '54f7632696421984c36931f9',
                'ip': '10.191.239.18',
                'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
                'instance_id': 'cansRALrqnE',
                'application': 'android',
                'mac': '14:dd:a9:a7:7d:6b',
                'yandex_uuid': '8c817929541ab5d8705fb2ffdbbeda0e',
                'metrica_device_id': '990a9ec348f6bb10cd0871bea8b8a890',
                'position': {'lat': 55.7353219, 'lon': 37.6447321},
                'yandex_uid': '4012918528',
                'application_version': '3.51.0',
                'metrica_uuid': '8c817929541ab5d8705fb2ffdbbeda0e',
                'device_id': '91998e8f28d5d48e6ab1decd8622b1648dc73cef',
            },
            {'frauder': True, 'rule_id': 'test_rule3'},
            200,
        ),
        (
            {
                'zone': 'moscow',
                'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
                'user_id': 'a9f602364e92410c8d6202f1795653a4',
                'user_phone_id': '54f7632696421984c36931f9',
                'source': {'lon': 37.6453218823, 'lat': 55.734834939},
                'destinations': [
                    {'lon': 37.623483, 'lat': 55.768024},
                    {'lon': 37.592863, 'lat': 55.735312},
                    {'lon': 37.602371, 'lat': 55.766643},
                ],
            },
            {'frauder': True, 'rule_id': 'test_rule4'},
            200,
        ),
        (
            {
                'zone': 'moscow',
                'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
                'user_id': 'a9f602364e92410c8d6202f1795653a4',
                'user_phone_id': '54f7632696421984c36931f9',
                'user_created': '2018-07-12T05:10:28+0000',
                'launch_updated': '2018-07-12T08:30:03+0000',
            },
            {'frauder': True, 'rule_id': 'test_rule5'},
            200,
        ),
        (
            {
                'zone': 'moscow',
                'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
                'user_id': 'a9f602364e92410c8d6202f1795653a4',
                'user_phone_id': '54f7632696421984c36931f9',
                'real_ip': '2a02:6b8:b010:50a3::18',
            },
            {'frauder': True, 'rule_id': 'test_rule6'},
            200,
        ),
        (
            {
                'zone': 'moscow',
                'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
                'user_id': 'a9f602364e92410c8d6202f1795653a4',
                'user_phone_id': '54f7632696421984c36931f9',
                'order_complete_count': 100,
                'order_total_count': 500,
            },
            {'frauder': True, 'rule_id': 'test_rule7'},
            200,
        ),
        (
            {
                'zone': 'moscow',
                'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
                'user_id': 'a9f602364e92410c8d6202f1795653a4',
                'user_phone_id': '54f7632696421984c36931f9',
                'order_total_count': 500,
            },
            {'frauder': False},
            200,
        ),
        (
            {
                'zone': 'tambov',
                'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
                'user_id': 'a9f602364e92410c8d6202f1795653a4',
                'user_phone_id': '54f7632696421984c36931f9',
                'order_complete_count': 1002,
                'order_total_count': 2003,
            },
            {'frauder': False},
            200,
        ),
        (
            {
                'zone': 'krasnoyarsk',
                'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
                'user_id': 'a9f602364e92410c8d6202f1795653a4',
                'user_phone_id': '54f7632696421984c36931f9',
                'order_total_count': 2003,
            },
            {'frauder': False},
            200,
        ),
        (
            {
                'zone': 'tambov',
                'user_personal_phone_id': '1c406207f46f42069cdb14a98c78af31',
                'user_id': 'a9f602364e92410c8d6202f1795653a4',
                'user_phone_id': '54f7632696421984c36931f9',
                'order_total_count': 2003,
            },
            {'frauder': False},
            200,
        ),
        (
            {
                'zone': 'tambov',
                'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
                'user_id': 'a9f602364e92410c8d6202f1795653a4',
                'user_phone_id': '54f7632696421984c36931f9',
                'order_total_count': 2003,
            },
            {'frauder': True, 'rule_id': 'test_rule9'},
            200,
        ),
        (
            {
                'zone': 'tambov',
                'user_personal_phone_id': 'e5d502839c52491790416f0777083435',
                'user_id': 'a9f602364e92410c8d6202f1795653a4',
                'user_phone_id': '54f7632696421984c36931f9',
                'order_total_count': 2003,
            },
            {'frauder': True, 'rule_id': 'test_rule9'},
            200,
        ),
        (
            {
                'zone': 'spb',
                'user_personal_phone_id': '2c225598d99c44b8bd92ffc1db0f524a',
                'user_id': 'a9f602364e92410c8d6202f1795653a4',
                'user_phone_id': '54f7632696421984c36931f9',
                'order_complete_count': 19,
                'order_total_count': 91,
            },
            {'frauder': False},
            200,
        ),
        (
            {
                'zone': '',
                'user_id': '',
                'user_phone_id': '54f7632696421984c36931f9',
                'comment': 'speed - 300; wait - 1;',
                'extra_user_personal_phone_id': (
                    '4a83ce41d92741a4abb388a19d0b4ee7'
                ),
                'is_multiorder': True,
                'payment_type': 'cash',
            },
            {'frauder': True, 'rule_id': 'test_rule12'},
            200,
        ),
        (
            {
                'zone': 'moscow',
                'user_personal_phone_id': '7c444af50f37412e993354b056f9e843',
                'user_id': 'a9f602364e92410c8d6202f1795653a5',
                'user_phone_id': '54f7632696421984c36931f9',
                'extra_user_personal_phone_id': (
                    '4a83ce41d92741a4abb388a19d0b4ee7'
                ),
            },
            {'frauder': True, 'rule_id': 'test_rule13'},
            200,
        ),
        (
            {
                'zone': 'moscow',
                'user_personal_phone_id': '7c444af50f37412e993354b056f9e843',
                'user_id': 'a9f602364e92410c8d6202f1795653a5',
                'user_phone_id': '54f7632696421984c36931f9',
                'user_agent': (
                    'yandex-taxi/4.40.0.121945 Android/8.1.0 '
                    '(Xiaomi; Redmi 5 Plus)'
                ),
            },
            {'frauder': True, 'rule_id': 'test_rule_user_agent_check'},
            200,
        ),
    ],
)
@pytest.mark.config(AFS_RULES_METRICS=True)
def test_check_fake_base(
        taxi_antifraud,
        mock_personal_phones_retrieve,
        input,
        output,
        expected_code,
):
    def check(response):
        assert response.status_code == expected_code
        if response.status_code == 200:
            data = json.loads(response.text)
            assert data == output

    check(taxi_antifraud.post('client/user/check_fake', json=input))


@pytest.mark.config(
    AFS_RULES_LOG_CONFIG={
        'enabled': True,
        'rule_types': {'antifake': {'yt': 'ALL', 'file': 'ALL'}},
        'rule_overrides': {},
    },
)
@pytest.mark.filldb(
    antifraud_users_orders_aggregates='pass_aggregates',
    antifraud_rules='pass_aggregates',
)
@pytest.mark.parametrize(
    'input,output,expected_code',
    [
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': '87745c883b8149138c50ef7e454b7857',
                'user_id': 'aaaa27dc9b044fbdb5b703ffffffffff',
                'user_phone_id': '54f7632696421984c36931f9',
                'order_id': '0ba165e446cf1af0b3b7e8e0eeaf8c4b',
                'order_complete_count': 664,
                'order_total_count': 797,
            },
            {'frauder': True, 'rule_id': 'test_pass_aggregates'},
            200,
        ),
    ],
)
@pytest.mark.config(
    AFS_RULES_METRICS=True, AFS_ANTIFAKE_LOG_SPECIFIC_FIELDS=True,
)
def test_pass_aggregates(
        taxi_antifraud,
        mock_personal_phones_retrieve,
        input,
        output,
        expected_code,
):
    def check(response):
        assert response.status_code == expected_code
        if response.status_code == 200:
            data = json.loads(response.text)
            assert data == output

    check(taxi_antifraud.post('client/user/check_fake', json=input))


@pytest.mark.parametrize(
    'input,current_time,count',
    [
        (
            {
                'zone': 'moscow',
                'user_personal_phone_id': '7c444af50f37412e993354b056f9e843',
                'user_id': 'a9f602364e92410c8d6202f1795653a5',
                'user_phone_id': '54f7632696421984c36931f9',
            },
            datetime.datetime(2019, 2, 22, 0, 0, 0),
            1,
        ),
        (
            {
                'zone': 'moscow',
                'user_personal_phone_id': '7c444af50f37412e993354b056f9e843',
                'user_id': 'a9f602364e92410c8d6202f1795653a5',
                'user_phone_id': '54f7632696421984c36931f9',
            },
            datetime.datetime(2019, 3, 22, 0, 0, 0),
            7,
        ),
        (
            {
                'zone': 'moscow',
                'user_personal_phone_id': '7c444af50f37412e993354b056f9e843',
                'user_id': 'a9f602364e92410c8d6202f1795653a5',
                'user_phone_id': '54f7632696421984c36931f9',
            },
            datetime.datetime(2019, 1, 22, 0, 0, 0),
            0,
        ),
    ],
)
@pytest.mark.filldb(antifraud_rules='stats')
@pytest.mark.config(AFS_RULES_METRICS=True)
def test_check_fake_rules_stats(
        taxi_antifraud,
        mock_personal_phones_retrieve,
        input,
        current_time,
        count,
):
    taxi_antifraud.tests_control(now=current_time, invalidate_caches=False)

    for _ in range(count):
        taxi_antifraud.post('client/user/check_fake', json=input)

    current_time = current_time.replace(second=59)
    taxi_antifraud.tests_control(now=current_time, invalidate_caches=False)

    stats = json.loads(taxi_antifraud.get('service/statistics').text)

    def check(name, value, zone=''):
        prefix = 'antifraud_rules.'
        if zone != '':
            prefix = prefix + zone + '.'
        prefix = prefix + 'antifake.'
        name = prefix + name
        if value == 0:
            assert name not in stats
        else:
            assert stats[name] == value

    check('js_failed.failed', count)
    check('js_failed.triggered', 0, input['zone'])
    check('js_failed.test.failed', 0)
    check('js_failed.test.triggered', 0, input['zone'])

    check('test_js_failed.failed', 0)
    check('test_js_failed.triggered', 0, input['zone'])
    check('test_js_failed.test.failed', count)
    check('test_js_failed.test.triggered', 0, input['zone'])

    check('js_triggered.failed', 0)
    check('js_triggered.triggered', count, input['zone'])
    check('js_triggered.test.failed', 0)
    check('js_triggered.test.triggered', 0, input['zone'])

    check('test_js_triggered.failed', 0)
    check('test_js_triggered.triggered', 0, input['zone'])
    check('test_js_triggered.test.failed', 0)
    check('test_js_triggered.test.triggered', count, input['zone'])


@pytest.mark.parametrize(
    'real_ip,output',
    [
        ('127.0.0.1', {'frauder': True, 'rule_id': 'test_rule1'}),
        ('176.112.95.255', {'frauder': True, 'rule_id': 'test_rule2'}),
        ('78.82.0.1', {'frauder': True, 'rule_id': 'test_rule5'}),
        (None, {'frauder': True, 'rule_id': 'test_rule6'}),
        ('8.8.8.8', {'frauder': True, 'rule_id': 'test_rule7'}),
        ('9.9.9.9', {'frauder': True, 'rule_id': 'test_rule8'}),
    ],
)
@pytest.mark.config(AFS_ANTIFAKE_LIBGEOBASE_ENABLED=True)
def test_check_geobase(
        taxi_antifraud, mock_personal_phones_retrieve, real_ip, output,
):
    def request():
        input = {
            'user_id': '85f087e6ca1246ba938dc0b4b87658f8',
            'zone': 'moscow',
            'order_id': 'e9103e313d9346d6ae02297dfd62b942',
            'user_phone_id': '54f7632696421984c36931f9',
            'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
            'real_ip': real_ip,
        }
        return taxi_antifraud.post('client/user/check_fake', json=input)

    def check(response):
        assert response.status_code == 200
        data = json.loads(response.text)
        assert data == output

    check(request())


@pytest.mark.parametrize(
    'input,output,expected_code',
    [
        (
            {
                'user_id': '85f087e6ca1246ba938dc0b4b87658f8',
                'zone': 'moscow',
                'order_id': 'e9103e313d9346d6ae02297dfd62b942',
                'user_phone_id': '54f7632696421984c36931f9',
                'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
            },
            {'frauder': True, 'rule_id': 'test_rule1'},
            200,
        ),
    ],
)
@pytest.mark.config(AFS_ANTIFAKE_CUSTOM_DATAMARTS_ENABLED=True)
def test_check_fake_datamarts(
        taxi_antifraud,
        mock_personal_phones_retrieve,
        input,
        output,
        expected_code,
        db,
):
    def check(response):
        assert response.status_code == expected_code
        if response.status_code == 200:
            data = json.loads(response.text)
            assert data == output

    check(taxi_antifraud.post('client/user/check_fake', json=input))


@pytest.mark.parametrize(
    'batches,hour,output',
    [
        (
            [
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 10,
                },
            ],
            1,
            {'frauder': True, 'rule_id': 'test_rule1'},
        ),
        (
            [
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 5,
                },
                {'times': 0},
                {'times': 0},
                {'times': 0},
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 5,
                },
            ],
            2,
            {'frauder': True, 'rule_id': 'test_rule2'},
        ),
        (
            [
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 1,
                },
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 1,
                },
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 1,
                },
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 1,
                },
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 1,
                },
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 1,
                },
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 1,
                },
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 1,
                },
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 1,
                },
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 1,
                },
            ],
            3,
            {'frauder': True, 'rule_id': 'test_rule3'},
        ),
        (
            [{'user_id': 'UID_WITHOUT_METRIC', 'zone': 'moscow', 'times': 10}],
            4,
            {'frauder': True, 'rule_id': 'test_rule4'},
        ),
        (
            [
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 1,
                },
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 1,
                },
            ],
            5,
            {'frauder': False},
        ),
        (
            [
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 9,
                },
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'spb',
                    'times': 9,
                },
            ],
            6,
            {'frauder': False},
        ),
        (
            [
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'spb',
                    'times': 9,
                },
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 1,
                },
                {
                    'user_id': 'UID_WITHOUT_COMMON_PARAMS',
                    'zone': 'moscow',
                    'times': 9,
                },
            ],
            7,
            {'frauder': True, 'rule_id': 'test_rule2'},
        ),
    ],
)
@pytest.mark.config(AFS_USER_ANTIFAKE_PASS_GEOZONE_METRICS=True)
@pytest.mark.now('2020-01-01T00:00:00+0000')
def test_check_fake_realtime_stats(
        taxi_antifraud,
        mock_personal_phones_retrieve,
        batches,
        hour,
        output,
        now,
):
    now = now.replace(hour=hour)
    taxi_antifraud.tests_control(now=now, invalidate_caches=True)

    def request(batch):
        input = {
            'user_id': batch['user_id'],
            'zone': batch['zone'],
            'order_id': 'e9103e313d9346d6ae02297dfd62b942',
            'user_phone_id': '54f7632696421984c36931f9',
            'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
        }
        return taxi_antifraud.post('client/user/check_fake', json=input)

    def check(response):
        assert response.status_code == 200
        data = json.loads(response.text)
        assert data == output

    next_minute = 0

    def sleep_one_minute():
        nonlocal next_minute
        next_now = now.replace(minute=next_minute, second=59)
        next_minute += 1
        taxi_antifraud.tests_control(now=next_now, invalidate_caches=True)

    last_batch = None

    for batch in batches:
        for _ in range(batch['times']):
            request(batch)
            last_batch = batch
        sleep_one_minute()

    check(request(last_batch))


@pytest.mark.parametrize(
    'input,output,expected_code',
    [
        (
            {
                'user_id': '85f087e6ca1246ba938dc0b4b87658f8',
                'zone': 'moscow',
                'order_id': 'e9103e313d9346d6ae02297dfd62b942',
                'user_phone_id': '54f7632696421984c36931f9',
                'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
            },
            {'frauder': True, 'rule_id': 'test_rule1'},
            200,
        ),
    ],
)
def test_own_properties(
        taxi_antifraud,
        mock_personal_phones_retrieve,
        input,
        output,
        expected_code,
):
    def check(response):
        assert response.status_code == expected_code
        if response.status_code == 200:
            data = json.loads(response.text)
            assert data == output

    check(taxi_antifraud.post('client/user/check_fake', json=input))


@pytest.mark.parametrize(
    'input,output,expected_code',
    [
        (
            {
                'user_id': '85f087e6ca1246ba938dc0b4b87658f8',
                'zone': 'moscow',
                'order_id': 'e9103e313d9346d6ae02297dfd62b942',
                'user_phone_id': '54f7632696421984c36931f9',
                'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
            },
            {'frauder': True, 'rule_id': 'test_rule2'},
            200,
        ),
    ],
)
@pytest.mark.config(AFS_USER_ANTIFAKE_PASS_MAP_ENTITIES=True)
def test_passing_exceptions_through_v8(
        taxi_antifraud,
        mock_personal_phones_retrieve,
        input,
        output,
        expected_code,
):
    def check(response):
        assert response.status_code == expected_code
        if response.status_code == 200:
            data = json.loads(response.text)
            assert data == output

    check(taxi_antifraud.post('client/user/check_fake', json=input))


@pytest.mark.parametrize(
    'input,output',
    [
        (
            {
                'user_id': 'some_user_id',
                'zone': 'moscow',
                'order_id': 'some_order_id',
                'user_phone_id': 'user_phone_id_to_find_in_map',
                'user_personal_phone_id': '87745c883b8149138c50ef7e454b7857',
            },
            {'frauder': True, 'rule_id': 'test_rule1'},
        ),
    ],
)
@pytest.mark.config(AFS_PASS_AUTO_MAP_ENTITIES=True)
def test_auto_entity_map(
        taxi_antifraud, mock_personal_phones_retrieve, input, output,
):
    def check(response):
        assert response.status_code == 200
        data = json.loads(response.text)
        assert data == output

    check(taxi_antifraud.post('client/user/check_fake', json=input))


@pytest.mark.parametrize(
    'input,output,expected_code',
    [
        (
            {
                'user_id': '85f087e6ca1246ba938dc0b4b87658f8',
                'zone': 'moscow',
                'order_id': 'e9103e313d9346d6ae02297dfd62b942',
                'user_phone_id': '54f7632696421984c36931f9',
                'user_personal_phone_id': 'dff27ecdb137448c9ac98a709481f799',
            },
            {'frauder': True, 'rule_id': 'test_rule1'},
            200,
        ),
    ],
)
@pytest.mark.config(
    AFS_USER_ANTIFAKE_PASS_GEOZONE_METRICS=True,
    AFS_USER_ANTIFAKE_GEOZONE_PARAMS={'internal': {'frauder': True}},
)
def test_check_fake_geo_config(
        taxi_antifraud,
        mock_personal_phones_retrieve,
        input,
        output,
        expected_code,
):
    def check(response):
        assert response.status_code == expected_code
        if response.status_code == 200:
            data = json.loads(response.text)
            assert data == output

    check(taxi_antifraud.post('client/user/check_fake', json=input))


@pytest.mark.now('2018-10-01T00:00:00+0000')
def test_check_fake_stats(
        taxi_antifraud, testpoint, now, db, mock_personal_phones_retrieve,
):
    @testpoint('after_save_stats')
    def after_save_stats(data):
        assert data == {'name': 'afs_antifake'}

    def proc(frauder_cnt, not_frauder_cnt):
        def check_response(response):
            assert response.status_code == 200

        frauder = {
            'zone': 'reutov',
            'user_personal_phone_id': 'f3b46027b6af44ca8c998a111c94e296',
            'user_id': 'df6b27dc9b044fbdb5b703ba993a1786',
            'user_phone_id': '54f7632696421984c36931f9',
        }
        not_frauder = {
            'zone': 'reutov',
            'user_personal_phone_id': '07b6badad9464a439507a2c1601031dd',
            'user_id': 'df6b27dc9b044fbdb5b703ba993a1786',
            'user_phone_id': '54f7632696421984c36931f9',
        }

        while frauder_cnt or not_frauder_cnt:
            if frauder_cnt:
                check_response(
                    taxi_antifraud.post(
                        'client/user/check_fake', json=frauder,
                    ),
                )
                frauder_cnt -= 1
            if not_frauder_cnt:
                check_response(
                    taxi_antifraud.post(
                        'client/user/check_fake', json=not_frauder,
                    ),
                )
                not_frauder_cnt -= 1

    def check_db(frauder, all, count, created):
        assert count == db.event_stats.count()
        record = db.event_stats.find_one(
            {
                'name': 'afs_antifake',
                'created': created.replace(second=0, microsecond=0),
            },
        )
        assert record is not None
        assert record['detailed']['frauder'] == frauder
        assert record['detailed']['all'] == all
        assert record['detailed']['rule_ids'] == {
            'test_rule2_2': frauder,
            'test_rule2': frauder,
        }
        assert record['detailed']['test_rule_ids'] == {'test_rule_test1': all}

    frauder_count = 2
    not_frauder_count = 3

    proc(frauder_count, not_frauder_count)
    for _ in range(frauder_count + not_frauder_count):
        after_save_stats.wait_call()
    check_db(frauder_count, frauder_count + not_frauder_count, 1, now)

    now = now.replace(second=59)
    taxi_antifraud.tests_control(now=now, invalidate_caches=True)

    proc(frauder_count, not_frauder_count)
    for _ in range(frauder_count + not_frauder_count):
        after_save_stats.wait_call()
    check_db(
        frauder_count * 2, (frauder_count + not_frauder_count) * 2, 1, now,
    )

    now = now.replace(minute=1, second=0)
    taxi_antifraud.tests_control(now=now, invalidate_caches=True)

    proc(frauder_count, not_frauder_count)
    for _ in range(frauder_count + not_frauder_count):
        after_save_stats.wait_call()
    check_db(frauder_count, frauder_count + not_frauder_count, 2, now)


@pytest.mark.parametrize(
    'input,ml_in,ml_out,output,expected_code',
    [
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': 'fa29f28a20534d5faf2e9aef15a8102d',
                'user_id': 'e994415b04442b25fc53a72d36f95e2e',
                'user_phone_id': '54f7632696421984c36931f9',
                'yandex_uid': '745415988',
                'yandex_uid_type': 'portal',
                'device_id': 'ce142d112e152ca0ac6a66d6cfcb493f422a8b71',
                'payment_type': 'corp',
                'ip': '192.168.1.1',
                'requirements_quantity': 5,
                'source': {
                    'country': 'Russia1',
                    'description': 'Nobody knows1',
                    'exact': True,
                    'fullname': 'ulica Pushkina, dom Kolotushkina, 4561',
                    'lon': 135.086173,
                    'lat': 48.468265,
                    'locality': 'Balashiha1',
                    'object_type': 'object',
                    'oid': '56698680',
                    'porchnumber': '15',
                    'premisenumber': '456',
                    'short_text': 'ulica Pushkina, dom Kolotushkina',
                    'thoroughfare': 'Pushkina',
                    'type': 'address',
                    'use_geopoint': False,
                    'metrica_method': 'nomethod',
                    'metrica_action': 'noaction',
                },
                'destinations': [
                    {
                        'country': 'Russia',
                        'description': 'Nobody knows',
                        'exact': True,
                        'fullname': 'ulica Pushkina, dom Kolotushkina, 456',
                        'lon': 135.086173,
                        'lat': 48.468265,
                        'locality': 'Balashiha',
                        'object_type': 'object',
                        'oid': '56698680',
                        'porchnumber': '15',
                        'premisenumber': '456',
                        'short_text': 'ulica Pushkina, dom Kolotushkina',
                        'thoroughfare': 'Pushkina',
                        'type': 'address',
                        'use_geopoint': False,
                        'metrica_method': 'nomethod',
                        'metrica_action': 'noaction',
                    },
                    {
                        'country': 'Russia',
                        'description': 'Couple of words',
                        'exact': False,
                        'fullname': 'ulica 1, dom 1111111, 456',
                        'lon': 138.086173,
                        'lat': 49.468265,
                        'locality': 'Moscow',
                        'object_type': 'object',
                        'oid': '56698683',
                        'porchnumber': '894',
                        'premisenumber': '1111111',
                        'short_text': 'ulica 1, dom 11111111',
                        'thoroughfare': '1',
                        'type': 'address',
                        'use_geopoint': True,
                        'metrica_method': 'nomethod1',
                        'metrica_action': 'noaction1',
                    },
                ],
            },
            {
                'aggregates': {
                    'calc_period': {
                        'begin_at': '2019-02-15T13:50:34+00:00',
                        'end_at': '2019-02-21T13:35:43+00:00',
                    },
                    'cost_of_success_orders': 1666,
                    'destinations_count': 8,
                    'driver_wait_time': 1379,
                    'order_requirements': 0,
                    'orders_expired': 0,
                    'orders_success': 6,
                    'orders_total': 7,
                    'orders_user_cancelled': 1,
                    'plan_order_cost': 1700,
                    'plan_travel_time': 61,
                    'route_stats_calls': 16,
                    'time_between_orders': 330676,
                    'travel_time_of_success_orders': 76,
                },
                'currency': 'RUB',
                'datetime': '2019-02-22T08:00:00+00:00',
                'order_request': {
                    'device_id': 'ce142d112e152ca0ac6a66d6cfcb493f422a8b71',
                    'ip': '192.168.1.1',
                    'user_phone_id': '54f7632696421984c36931f9',
                    'yandex_uid': '745415988',
                    'yandex_uid_type': 'portal',
                    'order_requirements': {},
                    'payment': {'type': 'corp'},
                    'plan_cost': 0,
                    'plan_travel_time': 0,
                    'source': {
                        'country': 'Russia1',
                        'description': 'Nobody knows1',
                        'exact': True,
                        'fullname': 'ulica Pushkina, dom Kolotushkina, 4561',
                        'geopoint': [135.086173, 48.468265],
                        'locality': 'Balashiha1',
                        'object_type': 'object',
                        'oid': '56698680',
                        'porchnumber': '15',
                        'premisenumber': '456',
                        'short_text': 'ulica Pushkina, dom Kolotushkina',
                        'thoroughfare': 'Pushkina',
                        'type': 'address',
                        'use_geopoint': False,
                        'metrica_method': 'nomethod',
                        'metrica_action': 'noaction',
                    },
                    'route_points': [
                        {
                            'country': 'Russia',
                            'description': 'Nobody knows',
                            'exact': True,
                            'fullname': (
                                'ulica Pushkina, dom Kolotushkina, 456'
                            ),
                            'geopoint': [135.086173, 48.468265],
                            'locality': 'Balashiha',
                            'object_type': 'object',
                            'oid': '56698680',
                            'porchnumber': '15',
                            'premisenumber': '456',
                            'short_text': 'ulica Pushkina, dom Kolotushkina',
                            'thoroughfare': 'Pushkina',
                            'type': 'address',
                            'use_geopoint': False,
                            'metrica_method': 'nomethod',
                            'metrica_action': 'noaction',
                        },
                        {
                            'country': 'Russia',
                            'description': 'Couple of words',
                            'exact': False,
                            'fullname': 'ulica 1, dom 1111111, 456',
                            'geopoint': [138.086173, 49.468265],
                            'locality': 'Moscow',
                            'object_type': 'object',
                            'oid': '56698683',
                            'porchnumber': '894',
                            'premisenumber': '1111111',
                            'short_text': 'ulica 1, dom 11111111',
                            'thoroughfare': '1',
                            'type': 'address',
                            'use_geopoint': True,
                            'metrica_method': 'nomethod1',
                            'metrica_action': 'noaction1',
                        },
                    ],
                    'route_stats_calls': 0,
                    'order_requirement_count': 5,
                    'tariff_zone': 'reutov',
                },
            },
            {
                'fake_order_prob': 0.65,
                'fake_order_verdicts': [
                    {'strictness': 'soft', 'verdict': 'not_fake'},
                    {'strictness': 'normal', 'verdict': 'not_fake'},
                    {'strictness': 'hard', 'verdict': 'fake'},
                ],
            },
            {'frauder': True, 'rule_id': 'test_rule_ml1'},
            200,
        ),
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': 'fa29f28a20534d5faf2e9aef15a8102d',
                'user_id': 'e994415b04442b25fc53a72d36f95e2e',
                'user_phone_id': '54f7632696421984c36931f9',
                'yandex_uid': '745415988',
                'yandex_uid_type': 'portal',
                'device_id': 'ce142d112e152ca0ac6a66d6cfcb493f422a8b71',
                'payment_type': 'corp',
                'ip': '192.168.1.1',
                'requirements_quantity': 5,
                'source': {
                    'country': 'Russia1',
                    'description': 'Nobody knows1',
                    'exact': True,
                    'fullname': 'ulica Pushkina, dom Kolotushkina, 4561',
                    'lon': 135.086173,
                    'lat': 48.468265,
                    'locality': 'Balashiha1',
                    'object_type': 'object',
                    'oid': '56698680',
                    'porchnumber': '15',
                    'premisenumber': '456',
                    'short_text': 'ulica Pushkina, dom Kolotushkina',
                    'thoroughfare': 'Pushkina',
                    'type': 'address',
                    'use_geopoint': False,
                    'metrica_method': 'nomethod',
                    'metrica_action': 'noaction',
                },
                'destinations': [
                    {
                        'country': 'Russia',
                        'description': 'Nobody knows',
                        'exact': True,
                        'fullname': 'ulica Pushkina, dom Kolotushkina, 456',
                        'lon': 135.086173,
                        'lat': 48.468265,
                        'locality': 'Balashiha',
                        'object_type': 'object',
                        'oid': '56698680',
                        'porchnumber': '15',
                        'premisenumber': '456',
                        'short_text': 'ulica Pushkina, dom Kolotushkina',
                        'thoroughfare': 'Pushkina',
                        'type': 'address',
                        'use_geopoint': False,
                        'metrica_method': 'nomethod',
                        'metrica_action': 'noaction',
                    },
                    {
                        'country': 'Russia',
                        'description': 'Couple of words',
                        'exact': False,
                        'fullname': 'ulica 1, dom 1111111, 456',
                        'lon': 138.086173,
                        'lat': 49.468265,
                        'locality': 'Moscow',
                        'object_type': 'object',
                        'oid': '56698683',
                        'porchnumber': '894',
                        'premisenumber': '1111111',
                        'short_text': 'ulica 1, dom 11111111',
                        'thoroughfare': '1',
                        'type': 'address',
                        'use_geopoint': True,
                        'metrica_method': 'nomethod1',
                        'metrica_action': 'noaction1',
                    },
                ],
            },
            {
                'aggregates': {
                    'calc_period': {
                        'begin_at': '2019-02-15T13:50:34+00:00',
                        'end_at': '2019-02-21T13:35:43+00:00',
                    },
                    'cost_of_success_orders': 1666,
                    'destinations_count': 8,
                    'driver_wait_time': 1379,
                    'order_requirements': 0,
                    'orders_expired': 0,
                    'orders_success': 6,
                    'orders_total': 7,
                    'orders_user_cancelled': 1,
                    'plan_order_cost': 1700,
                    'plan_travel_time': 61,
                    'route_stats_calls': 16,
                    'time_between_orders': 330676,
                    'travel_time_of_success_orders': 76,
                },
                'currency': 'RUB',
                'datetime': '2019-02-22T08:00:00+00:00',
                'order_request': {
                    'device_id': 'ce142d112e152ca0ac6a66d6cfcb493f422a8b71',
                    'ip': '192.168.1.1',
                    'user_phone_id': '54f7632696421984c36931f9',
                    'yandex_uid': '745415988',
                    'yandex_uid_type': 'portal',
                    'order_requirements': {},
                    'payment': {'type': 'corp'},
                    'plan_cost': 0,
                    'plan_travel_time': 0,
                    'source': {
                        'country': 'Russia1',
                        'description': 'Nobody knows1',
                        'exact': True,
                        'fullname': 'ulica Pushkina, dom Kolotushkina, 4561',
                        'geopoint': [135.086173, 48.468265],
                        'locality': 'Balashiha1',
                        'object_type': 'object',
                        'oid': '56698680',
                        'porchnumber': '15',
                        'premisenumber': '456',
                        'short_text': 'ulica Pushkina, dom Kolotushkina',
                        'thoroughfare': 'Pushkina',
                        'type': 'address',
                        'use_geopoint': False,
                        'metrica_method': 'nomethod',
                        'metrica_action': 'noaction',
                    },
                    'route_points': [
                        {
                            'country': 'Russia',
                            'description': 'Nobody knows',
                            'exact': True,
                            'fullname': (
                                'ulica Pushkina, dom Kolotushkina, 456'
                            ),
                            'geopoint': [135.086173, 48.468265],
                            'locality': 'Balashiha',
                            'object_type': 'object',
                            'oid': '56698680',
                            'porchnumber': '15',
                            'premisenumber': '456',
                            'short_text': 'ulica Pushkina, dom Kolotushkina',
                            'thoroughfare': 'Pushkina',
                            'type': 'address',
                            'use_geopoint': False,
                            'metrica_method': 'nomethod',
                            'metrica_action': 'noaction',
                        },
                        {
                            'country': 'Russia',
                            'description': 'Couple of words',
                            'exact': False,
                            'fullname': 'ulica 1, dom 1111111, 456',
                            'geopoint': [138.086173, 49.468265],
                            'locality': 'Moscow',
                            'object_type': 'object',
                            'oid': '56698683',
                            'porchnumber': '894',
                            'premisenumber': '1111111',
                            'short_text': 'ulica 1, dom 11111111',
                            'thoroughfare': '1',
                            'type': 'address',
                            'use_geopoint': True,
                            'metrica_method': 'nomethod1',
                            'metrica_action': 'noaction1',
                        },
                    ],
                    'route_stats_calls': 0,
                    'order_requirement_count': 5,
                    'tariff_zone': 'reutov',
                },
            },
            {
                'fake_order_prob': 0.0,
                'extra_order_info': [
                    {
                        'id': 'another_ml',
                        'raw_value': 0.65,
                        'values': [
                            {'strictness': 'soft', 'verdict': 'not_fake'},
                            {'strictness': 'normal', 'verdict': 'not_fake'},
                            {'strictness': 'hard', 'verdict': 'fake'},
                        ],
                    },
                ],
                'fake_order_verdicts': [
                    {'strictness': 'soft', 'verdict': 'not_fake'},
                    {'strictness': 'normal', 'verdict': 'not_fake'},
                    {'strictness': 'hard', 'verdict': 'not_fake'},
                ],
            },
            {'frauder': True, 'rule_id': 'test_rule_ml2'},
            200,
        ),
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': 'fa29f28a20534d5faf2e9aef15a8102d',
                'user_id': 'e994415b04442b25fc53a72d36f95e2e',
                'user_phone_id': '54f7632696421984c36931f9',
                'payment_type': 'agent',
                'ip': '192.168.1.1',
                'requirements_quantity': 5,
                'source': {
                    'country': 'Russia1',
                    'description': 'Nobody knows1',
                    'exact': True,
                    'fullname': 'ulica Pushkina, dom Kolotushkina, 4561',
                    'lon': 135.086173,
                    'lat': 48.468265,
                    'locality': 'Balashiha1',
                    'object_type': 'object',
                    'oid': '56698680',
                    'porchnumber': '15',
                    'premisenumber': '456',
                    'short_text': 'ulica Pushkina, dom Kolotushkina',
                    'thoroughfare': 'Pushkina',
                    'type': 'address',
                    'use_geopoint': False,
                    'metrica_method': 'nomethod',
                    'metrica_action': 'noaction',
                },
                'destinations': [
                    {
                        'country': 'Russia',
                        'description': 'Nobody knows',
                        'exact': True,
                        'fullname': 'ulica Pushkina, dom Kolotushkina, 456',
                        'lon': 135.086173,
                        'lat': 48.468265,
                        'locality': 'Balashiha',
                        'object_type': 'object',
                        'oid': '56698680',
                        'porchnumber': '15',
                        'premisenumber': '456',
                        'short_text': 'ulica Pushkina, dom Kolotushkina',
                        'thoroughfare': 'Pushkina',
                        'type': 'address',
                        'use_geopoint': False,
                        'metrica_method': 'nomethod',
                        'metrica_action': 'noaction',
                    },
                    {
                        'country': 'Russia',
                        'description': 'Couple of words',
                        'exact': False,
                        'fullname': 'ulica 1, dom 1111111, 456',
                        'lon': 138.086173,
                        'lat': 49.468265,
                        'locality': 'Moscow',
                        'object_type': 'object',
                        'oid': '56698683',
                        'porchnumber': '894',
                        'premisenumber': '1111111',
                        'short_text': 'ulica 1, dom 11111111',
                        'thoroughfare': '1',
                        'type': 'address',
                        'use_geopoint': True,
                        'metrica_method': 'nomethod1',
                        'metrica_action': 'noaction1',
                    },
                ],
            },
            {
                'aggregates': {
                    'calc_period': {
                        'begin_at': '2019-02-17T10:54:41+00:00',
                        'end_at': '2019-02-21T13:35:43+00:00',
                    },
                    'cost_of_success_orders': 1666,
                    'destinations_count': 8,
                    'driver_wait_time': 1379,
                    'order_requirements': 0,
                    'orders_expired': 0,
                    'orders_success': 6,
                    'orders_total': 7,
                    'orders_user_cancelled': 1,
                    'plan_order_cost': 1700,
                    'plan_travel_time': 61,
                    'route_stats_calls': 16,
                    'time_between_orders': 330676,
                    'travel_time_of_success_orders': 76,
                },
                'currency': 'RUB',
                'datetime': '2019-02-22T08:00:00+00:00',
                'order_request': {
                    'ip': '192.168.1.1',
                    'user_phone_id': '54f7632696421984c36931f9',
                    'order_requirements': {},
                    'payment': {'type': 'agent'},
                    'plan_cost': 0,
                    'plan_travel_time': 0,
                    'source': {
                        'country': 'Russia1',
                        'description': 'Nobody knows1',
                        'exact': True,
                        'fullname': 'ulica Pushkina, dom Kolotushkina, 4561',
                        'geopoint': [135.086173, 48.468265],
                        'locality': 'Balashiha1',
                        'object_type': 'object',
                        'oid': '56698680',
                        'porchnumber': '15',
                        'premisenumber': '456',
                        'short_text': 'ulica Pushkina, dom Kolotushkina',
                        'thoroughfare': 'Pushkina',
                        'type': 'address',
                        'use_geopoint': False,
                        'metrica_method': 'nomethod',
                        'metrica_action': 'noaction',
                    },
                    'route_points': [
                        {
                            'country': 'Russia',
                            'description': 'Nobody knows',
                            'exact': True,
                            'fullname': (
                                'ulica Pushkina, dom Kolotushkina, 456'
                            ),
                            'geopoint': [135.086173, 48.468265],
                            'locality': 'Balashiha',
                            'object_type': 'object',
                            'oid': '56698680',
                            'porchnumber': '15',
                            'premisenumber': '456',
                            'short_text': 'ulica Pushkina, dom Kolotushkina',
                            'thoroughfare': 'Pushkina',
                            'type': 'address',
                            'use_geopoint': False,
                            'metrica_method': 'nomethod',
                            'metrica_action': 'noaction',
                        },
                        {
                            'country': 'Russia',
                            'description': 'Couple of words',
                            'exact': False,
                            'fullname': 'ulica 1, dom 1111111, 456',
                            'geopoint': [138.086173, 49.468265],
                            'locality': 'Moscow',
                            'object_type': 'object',
                            'oid': '56698683',
                            'porchnumber': '894',
                            'premisenumber': '1111111',
                            'short_text': 'ulica 1, dom 11111111',
                            'thoroughfare': '1',
                            'type': 'address',
                            'use_geopoint': True,
                            'metrica_method': 'nomethod1',
                            'metrica_action': 'noaction1',
                        },
                    ],
                    'route_stats_calls': 0,
                    'order_requirement_count': 5,
                    'tariff_zone': 'reutov',
                },
            },
            {
                'fake_order_prob': 0.0,
                'extra_order_info': [
                    {
                        'id': 'another_ml',
                        'raw_value': 0.65,
                        'values': [
                            {'strictness': 'soft', 'verdict': 'not_fake'},
                            {'strictness': 'normal', 'verdict': 'not_fake'},
                            {'strictness': 'hard', 'verdict': 'fake'},
                        ],
                    },
                ],
                'fake_order_verdicts': [
                    {'strictness': 'soft', 'verdict': 'not_fake'},
                    {'strictness': 'normal', 'verdict': 'not_fake'},
                    {'strictness': 'hard', 'verdict': 'not_fake'},
                ],
            },
            {'frauder': True, 'rule_id': 'test_rule_ml2'},
            200,
        ),
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': 'fa29f28a20534d5faf2e9aef15a8102d',
                'user_id': 'e994415b04442b25fc53a72d36f95e2e',
                'user_phone_id': '54f7632696421984c36931f9',
                'payment_type': 'yandex_card',
                'ip': '192.168.1.1',
                'requirements_quantity': 5,
                'source': {
                    'country': 'Russia1',
                    'description': 'Nobody knows1',
                    'exact': True,
                    'fullname': 'ulica Pushkina, dom Kolotushkina, 4561',
                    'lon': 135.086173,
                    'lat': 48.468265,
                    'locality': 'Balashiha1',
                    'object_type': 'object',
                    'oid': '56698680',
                    'porchnumber': '15',
                    'premisenumber': '456',
                    'short_text': 'ulica Pushkina, dom Kolotushkina',
                    'thoroughfare': 'Pushkina',
                    'type': 'address',
                    'use_geopoint': False,
                    'metrica_method': 'nomethod',
                    'metrica_action': 'noaction',
                },
                'destinations': [
                    {
                        'country': 'Russia',
                        'description': 'Nobody knows',
                        'exact': True,
                        'fullname': 'ulica Pushkina, dom Kolotushkina, 456',
                        'lon': 135.086173,
                        'lat': 48.468265,
                        'locality': 'Balashiha',
                        'object_type': 'object',
                        'oid': '56698680',
                        'porchnumber': '15',
                        'premisenumber': '456',
                        'short_text': 'ulica Pushkina, dom Kolotushkina',
                        'thoroughfare': 'Pushkina',
                        'type': 'address',
                        'use_geopoint': False,
                        'metrica_method': 'nomethod',
                        'metrica_action': 'noaction',
                    },
                    {
                        'country': 'Russia',
                        'description': 'Couple of words',
                        'exact': False,
                        'fullname': 'ulica 1, dom 1111111, 456',
                        'lon': 138.086173,
                        'lat': 49.468265,
                        'locality': 'Moscow',
                        'object_type': 'object',
                        'oid': '56698683',
                        'porchnumber': '894',
                        'premisenumber': '1111111',
                        'short_text': 'ulica 1, dom 11111111',
                        'thoroughfare': '1',
                        'type': 'address',
                        'use_geopoint': True,
                        'metrica_method': 'nomethod1',
                        'metrica_action': 'noaction1',
                    },
                ],
            },
            {
                'aggregates': {
                    'calc_period': {
                        'begin_at': '2019-02-17T10:54:41+00:00',
                        'end_at': '2019-02-21T13:35:43+00:00',
                    },
                    'cost_of_success_orders': 1666,
                    'destinations_count': 8,
                    'driver_wait_time': 1379,
                    'order_requirements': 0,
                    'orders_expired': 0,
                    'orders_success': 6,
                    'orders_total': 7,
                    'orders_user_cancelled': 1,
                    'plan_order_cost': 1700,
                    'plan_travel_time': 61,
                    'route_stats_calls': 16,
                    'time_between_orders': 330676,
                    'travel_time_of_success_orders': 76,
                },
                'currency': 'RUB',
                'datetime': '2019-02-22T08:00:00+00:00',
                'order_request': {
                    'ip': '192.168.1.1',
                    'user_phone_id': '54f7632696421984c36931f9',
                    'order_requirements': {},
                    'payment': {'type': 'yandex_card'},
                    'plan_cost': 0,
                    'plan_travel_time': 0,
                    'source': {
                        'country': 'Russia1',
                        'description': 'Nobody knows1',
                        'exact': True,
                        'fullname': 'ulica Pushkina, dom Kolotushkina, 4561',
                        'geopoint': [135.086173, 48.468265],
                        'locality': 'Balashiha1',
                        'object_type': 'object',
                        'oid': '56698680',
                        'porchnumber': '15',
                        'premisenumber': '456',
                        'short_text': 'ulica Pushkina, dom Kolotushkina',
                        'thoroughfare': 'Pushkina',
                        'type': 'address',
                        'use_geopoint': False,
                        'metrica_method': 'nomethod',
                        'metrica_action': 'noaction',
                    },
                    'route_points': [
                        {
                            'country': 'Russia',
                            'description': 'Nobody knows',
                            'exact': True,
                            'fullname': (
                                'ulica Pushkina, dom Kolotushkina, 456'
                            ),
                            'geopoint': [135.086173, 48.468265],
                            'locality': 'Balashiha',
                            'object_type': 'object',
                            'oid': '56698680',
                            'porchnumber': '15',
                            'premisenumber': '456',
                            'short_text': 'ulica Pushkina, dom Kolotushkina',
                            'thoroughfare': 'Pushkina',
                            'type': 'address',
                            'use_geopoint': False,
                            'metrica_method': 'nomethod',
                            'metrica_action': 'noaction',
                        },
                        {
                            'country': 'Russia',
                            'description': 'Couple of words',
                            'exact': False,
                            'fullname': 'ulica 1, dom 1111111, 456',
                            'geopoint': [138.086173, 49.468265],
                            'locality': 'Moscow',
                            'object_type': 'object',
                            'oid': '56698683',
                            'porchnumber': '894',
                            'premisenumber': '1111111',
                            'short_text': 'ulica 1, dom 11111111',
                            'thoroughfare': '1',
                            'type': 'address',
                            'use_geopoint': True,
                            'metrica_method': 'nomethod1',
                            'metrica_action': 'noaction1',
                        },
                    ],
                    'route_stats_calls': 0,
                    'order_requirement_count': 5,
                    'tariff_zone': 'reutov',
                },
            },
            {
                'fake_order_prob': 0.0,
                'extra_order_info': [
                    {
                        'id': 'another_ml',
                        'raw_value': 0.65,
                        'values': [
                            {'strictness': 'soft', 'verdict': 'not_fake'},
                            {'strictness': 'normal', 'verdict': 'not_fake'},
                            {'strictness': 'hard', 'verdict': 'fake'},
                        ],
                    },
                ],
                'fake_order_verdicts': [
                    {'strictness': 'soft', 'verdict': 'not_fake'},
                    {'strictness': 'normal', 'verdict': 'not_fake'},
                    {'strictness': 'hard', 'verdict': 'not_fake'},
                ],
            },
            {'frauder': True, 'rule_id': 'test_rule_ml2'},
            200,
        ),
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': 'fa29f28a20534d5faf2e9aef15a8102d',
                'user_id': 'e994415b04442b25fc53a72d36f95e2e',
                'user_phone_id': '54f7632696421984c36931f9',
                'payment_type': 'sbp',
                'ip': '192.168.1.1',
                'requirements_quantity': 5,
                'source': {
                    'country': 'Russia1',
                    'description': 'Nobody knows1',
                    'exact': True,
                    'fullname': 'ulica Pushkina, dom Kolotushkina, 4561',
                    'lon': 135.086173,
                    'lat': 48.468265,
                    'locality': 'Balashiha1',
                    'object_type': 'object',
                    'oid': '56698680',
                    'porchnumber': '15',
                    'premisenumber': '456',
                    'short_text': 'ulica Pushkina, dom Kolotushkina',
                    'thoroughfare': 'Pushkina',
                    'type': 'address',
                    'use_geopoint': False,
                    'metrica_method': 'nomethod',
                    'metrica_action': 'noaction',
                },
                'destinations': [
                    {
                        'country': 'Russia',
                        'description': 'Nobody knows',
                        'exact': True,
                        'fullname': 'ulica Pushkina, dom Kolotushkina, 456',
                        'lon': 135.086173,
                        'lat': 48.468265,
                        'locality': 'Balashiha',
                        'object_type': 'object',
                        'oid': '56698680',
                        'porchnumber': '15',
                        'premisenumber': '456',
                        'short_text': 'ulica Pushkina, dom Kolotushkina',
                        'thoroughfare': 'Pushkina',
                        'type': 'address',
                        'use_geopoint': False,
                        'metrica_method': 'nomethod',
                        'metrica_action': 'noaction',
                    },
                    {
                        'country': 'Russia',
                        'description': 'Couple of words',
                        'exact': False,
                        'fullname': 'ulica 1, dom 1111111, 456',
                        'lon': 138.086173,
                        'lat': 49.468265,
                        'locality': 'Moscow',
                        'object_type': 'object',
                        'oid': '56698683',
                        'porchnumber': '894',
                        'premisenumber': '1111111',
                        'short_text': 'ulica 1, dom 11111111',
                        'thoroughfare': '1',
                        'type': 'address',
                        'use_geopoint': True,
                        'metrica_method': 'nomethod1',
                        'metrica_action': 'noaction1',
                    },
                ],
            },
            {
                'aggregates': {
                    'calc_period': {
                        'begin_at': '2019-02-17T10:54:41+00:00',
                        'end_at': '2019-02-21T13:35:43+00:00',
                    },
                    'cost_of_success_orders': 1666,
                    'destinations_count': 8,
                    'driver_wait_time': 1379,
                    'order_requirements': 0,
                    'orders_expired': 0,
                    'orders_success': 6,
                    'orders_total': 7,
                    'orders_user_cancelled': 1,
                    'plan_order_cost': 1700,
                    'plan_travel_time': 61,
                    'route_stats_calls': 16,
                    'time_between_orders': 330676,
                    'travel_time_of_success_orders': 76,
                },
                'currency': 'RUB',
                'datetime': '2019-02-22T08:00:00+00:00',
                'order_request': {
                    'ip': '192.168.1.1',
                    'user_phone_id': '54f7632696421984c36931f9',
                    'order_requirements': {},
                    'payment': {'type': 'sbp'},
                    'plan_cost': 0,
                    'plan_travel_time': 0,
                    'source': {
                        'country': 'Russia1',
                        'description': 'Nobody knows1',
                        'exact': True,
                        'fullname': 'ulica Pushkina, dom Kolotushkina, 4561',
                        'geopoint': [135.086173, 48.468265],
                        'locality': 'Balashiha1',
                        'object_type': 'object',
                        'oid': '56698680',
                        'porchnumber': '15',
                        'premisenumber': '456',
                        'short_text': 'ulica Pushkina, dom Kolotushkina',
                        'thoroughfare': 'Pushkina',
                        'type': 'address',
                        'use_geopoint': False,
                        'metrica_method': 'nomethod',
                        'metrica_action': 'noaction',
                    },
                    'route_points': [
                        {
                            'country': 'Russia',
                            'description': 'Nobody knows',
                            'exact': True,
                            'fullname': (
                                'ulica Pushkina, dom Kolotushkina, 456'
                            ),
                            'geopoint': [135.086173, 48.468265],
                            'locality': 'Balashiha',
                            'object_type': 'object',
                            'oid': '56698680',
                            'porchnumber': '15',
                            'premisenumber': '456',
                            'short_text': 'ulica Pushkina, dom Kolotushkina',
                            'thoroughfare': 'Pushkina',
                            'type': 'address',
                            'use_geopoint': False,
                            'metrica_method': 'nomethod',
                            'metrica_action': 'noaction',
                        },
                        {
                            'country': 'Russia',
                            'description': 'Couple of words',
                            'exact': False,
                            'fullname': 'ulica 1, dom 1111111, 456',
                            'geopoint': [138.086173, 49.468265],
                            'locality': 'Moscow',
                            'object_type': 'object',
                            'oid': '56698683',
                            'porchnumber': '894',
                            'premisenumber': '1111111',
                            'short_text': 'ulica 1, dom 11111111',
                            'thoroughfare': '1',
                            'type': 'address',
                            'use_geopoint': True,
                            'metrica_method': 'nomethod1',
                            'metrica_action': 'noaction1',
                        },
                    ],
                    'route_stats_calls': 0,
                    'order_requirement_count': 5,
                    'tariff_zone': 'reutov',
                },
            },
            {
                'fake_order_prob': 0.0,
                'extra_order_info': [
                    {
                        'id': 'another_ml',
                        'raw_value': 0.65,
                        'values': [
                            {'strictness': 'soft', 'verdict': 'not_fake'},
                            {'strictness': 'normal', 'verdict': 'not_fake'},
                            {'strictness': 'hard', 'verdict': 'fake'},
                        ],
                    },
                ],
                'fake_order_verdicts': [
                    {'strictness': 'soft', 'verdict': 'not_fake'},
                    {'strictness': 'normal', 'verdict': 'not_fake'},
                    {'strictness': 'hard', 'verdict': 'not_fake'},
                ],
            },
            {'frauder': True, 'rule_id': 'test_rule_ml2'},
            200,
        ),
    ],
)
@pytest.mark.config(AFS_ANTIFAKE_ML_ENABLED=True)
@pytest.mark.now('2019-02-22T08:00:00+0000')
@pytest.mark.filldb(antifraud_rules='ml', antifraud_users_aggregates='ml')
def test_check_fake_ml(
        taxi_antifraud,
        mockserver,
        mock_personal_phones_retrieve,
        input,
        ml_in,
        ml_out,
        output,
        expected_code,
):
    @mockserver.json_handler('/mlaas/user_order_fakeness')
    def mock_ml(request):
        data = json.loads(request.get_data())
        assert data == ml_in
        return ml_out

    def check(response):
        assert response.status_code == expected_code
        if response.status_code == 200:
            data = json.loads(response.text)
            assert data == output

    check(taxi_antifraud.post('client/user/check_fake', json=input))


@pytest.mark.parametrize(
    'input,laas_in,laas_out,output,expected_code',
    [
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': 'fa29f28a20534d5faf2e9aef15a8102d',
                'user_id': 'e994415b04442b25fc53a72d36f95e2e',
                'user_phone_id': '54f7632696421984c36931f9',
                'yandex_uid': '745415988',
                'yandex_uid_type': 'portal',
                'device_id': 'ce142d112e152ca0ac6a66d6cfcb493f422a8b71',
                'payment_type': 'corp',
                'ip': '192.168.1.1',
                'real_ip': '192.168.1.1',
                'requirements_quantity': 5,
            },
            'service=afs_user_antifake&real_ip=192.168.1.1',
            {
                'region_id': 1,
                'precision': 1,
                'latitude': 2.0,
                'longitude': 2.0,
                'is_user_choice': True,
                'suspected_region_id': 1,
                'city_id': 1,
                'region_by_ip': 1,
                'suspected_region_city': 1,
                'location_accuracy': 1,
                'location_unixtime': 1,
                'suspected_latitude': 1,
                'suspected_longitude': 1,
                'suspected_location_accuracy': 1,
                'suspected_location_unixtime': 1,
                'suspected_precision': 1,
                'probable_regions_reliability': 1,
                'country_id_by_ip': 1,
                'is_anonymous_vpn': True,
                'is_public_proxy': True,
                'is_serp_trusted_net': True,
                'is_tor': True,
                'is_hosting': True,
                'is_gdpr': True,
                'is_mobile': True,
                'is_yandex_net': True,
                'is_yandex_staff': True,
            },
            {'frauder': True, 'rule_id': 'test_rule_laas1'},
            200,
        ),
    ],
)
@pytest.mark.config(
    AFS_ANTIFAKE_LAAS_ENABLED=True, LAAS_CLIENT_TIMEOUT_MS=1000,
)
@pytest.mark.now('2019-02-22T08:00:00+0000')
@pytest.mark.filldb(antifraud_rules='laas')
def test_check_fake_laas(
        taxi_antifraud,
        mockserver,
        config,
        mock_personal_phones_retrieve,
        input,
        laas_in,
        laas_out,
        output,
        expected_code,
):
    config.set_values(dict(LAAS_CLIENT_URL=mockserver.url('laas')))

    @mockserver.json_handler('/laas')
    def mock_laas(request):
        data = request.query_string.decode()
        assert data == laas_in
        return laas_out

    def check(response):
        assert response.status_code == expected_code
        if response.status_code == 200:
            data = json.loads(response.text)
            assert data == output

    check(taxi_antifraud.post('client/user/check_fake', json=input))


@pytest.mark.parametrize(
    'input,laas_in,laas_out,output,expected_code',
    [
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': 'fa29f28a20534d5faf2e9aef15a8102d',
                'user_id': 'e994415b04442b25fc53a72d36f95e2e',
                'user_phone_id': '54f7632696421984c36931f9',
                'yandex_uid': '745415988',
                'yandex_uid_type': 'portal',
                'device_id': 'ce142d112e152ca0ac6a66d6cfcb493f422a8b71',
                'payment_type': 'corp',
                'ip': '176.112.95.255',
                'real_ip': '176.112.95.255',
                'requirements_quantity': 5,
            },
            'service=afs_user_antifake&real_ip=176.112.95.255',
            {
                'region_id': 1,
                'precision': 1,
                'latitude': 2.0,
                'longitude': 2.0,
                'is_user_choice': True,
                'suspected_region_id': 1,
                'city_id': 213,  # Moscow id
                'region_by_ip': 1,
                'suspected_region_city': 1,
                'location_accuracy': 1,
                'location_unixtime': 1,
                'suspected_latitude': 1,
                'suspected_longitude': 1,
                'suspected_location_accuracy': 1,
                'suspected_location_unixtime': 1,
                'suspected_precision': 1,
                'probable_regions_reliability': 1,
                'country_id_by_ip': 225,  # RU id
                'is_anonymous_vpn': True,
                'is_public_proxy': True,
                'is_serp_trusted_net': True,
                'is_tor': True,
                'is_hosting': True,
                'is_gdpr': True,
                'is_mobile': True,
                'is_yandex_net': True,
                'is_yandex_staff': True,
            },
            {'frauder': True, 'rule_id': 'test_rule_laas_and_geobase'},
            200,
        ),
    ],
)
@pytest.mark.config(
    AFS_ANTIFAKE_LAAS_ENABLED=True,
    LAAS_CLIENT_TIMEOUT_MS=1000,
    AFS_ANTIFAKE_LIBGEOBASE_ENABLED=True,
)
@pytest.mark.now('2019-02-22T08:00:00+0000')
@pytest.mark.filldb(antifraud_rules='laas_with_geo')
def test_check_fake_laas_with_geo(
        taxi_antifraud,
        mockserver,
        config,
        mock_personal_phones_retrieve,
        input,
        laas_in,
        laas_out,
        output,
        expected_code,
):
    config.set_values(dict(LAAS_CLIENT_URL=mockserver.url('laas')))

    @mockserver.json_handler('/laas')
    def mock_laas(request):
        data = request.query_string.decode()
        assert data == laas_in
        return laas_out

    def check(response):
        assert response.status_code == expected_code
        if response.status_code == 200:
            data = json.loads(response.text)
            assert data == output

    check(taxi_antifraud.post('client/user/check_fake', json=input))


@pytest.mark.parametrize(
    'input,yt_data,experiments',
    [
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': 'f3b46027b6af44ca8c998a111c94e296',
                'user_id': 'df6b27dc9b044fbdb5b703ba993a1786',
                'user_phone_id': 'some_user_id',
                'order_id': 'some_id',
            },
            {
                'js_params': {
                    'order_id': 'some_id',
                    'user_phone_id': 'some_user_id',
                },
                'time': 1550822400000000000,
                'rules_type': 'antifake',
                'unique_resolutions': [False],
                'rule_resolutions': {
                    'test_log_level': False,
                    'test_log_experiments1': False,
                    'test_log_experiments2': False,
                    'test_log_experiments3': False,
                },
                'test_rule_resolutions': {},
                'logs': {
                    'test_log_level': [
                        {
                            'level': 'INFO',
                            'message': 'reutov',
                            'params': {'level': 'info'},
                        },
                        {
                            'level': 'WARNING',
                            'message': 'reutov',
                            'params': {'level': 'warn'},
                        },
                    ],
                },
                'rule_resolutions_as_output': {
                    'test_log_level': False,
                    'test_log_experiments1': False,
                    'test_log_experiments2': False,
                    'test_log_experiments3': False,
                },
                'experiments': {},
            },
            [],
        ),
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': 'f3b46027b6af44ca8c998a111c94e296',
                'user_id': 'bad_guy',
                'user_phone_id': 'some_user_id',
                'order_id': 'some_id',
            },
            {
                'js_params': {
                    'order_id': 'some_id',
                    'user_phone_id': 'some_user_id',
                },
                'time': 1550822400000000000,
                'rules_type': 'antifake',
                'unique_resolutions': [False, True],
                'rule_resolutions': {
                    'test_log_level': False,
                    'test_log_experiments1': True,
                    'test_log_experiments2': True,
                    'test_log_experiments3': False,
                },
                'test_rule_resolutions': {},
                'logs': {
                    'test_log_level': [
                        {
                            'level': 'INFO',
                            'message': 'reutov',
                            'params': {'level': 'info'},
                        },
                        {
                            'level': 'WARNING',
                            'message': 'reutov',
                            'params': {'level': 'warn'},
                        },
                    ],
                },
                'rule_resolutions_as_output': {
                    'test_log_level': False,
                    'test_log_experiments1': False,
                    'test_log_experiments2': True,
                    'test_log_experiments3': False,
                },
                'experiments': {
                    'disable_rules_for_tests': {
                        'test_log_experiments1': True,
                        'test_log_experiments3': False,
                    },
                    'disable_rules_for_tests_second': {
                        'test_log_experiments1': True,
                    },
                },
            },
            [
                {
                    'name': 'disable_rules_for_tests',
                    'clauses': [
                        {
                            'title': 'disable_test_exp_rule_1&3',
                            'predicate': {
                                'type': 'eq',
                                'init': {
                                    'arg_type': 'string',
                                    'arg_name': 'user_phone_id',
                                    'value': 'some_user_id',
                                },
                            },
                            'value': {
                                'disabled_rules': [
                                    'test_log_experiments1',
                                    'test_log_experiments3',
                                ],
                            },
                        },
                    ],
                },
                {
                    'name': 'disable_rules_for_tests_second',
                    'clauses': [
                        {
                            'title': 'disable_test_exp_rule_1',
                            'predicate': {
                                'type': 'eq',
                                'init': {
                                    'arg_type': 'string',
                                    'arg_name': 'user_phone_id',
                                    'value': 'some_user_id',
                                },
                            },
                            'value': {
                                'disabled_rules': ['test_log_experiments1'],
                            },
                        },
                    ],
                },
            ],
        ),
    ],
)
@pytest.mark.config(
    AFS_RULES_LOG_CONFIG={
        'enabled': True,
        'rule_types': {'antifake': {'yt': 'INFO'}},
    },
    AFS_RULES_PARAMS_FILTER_CONFIG={
        '__default__': {
            'order_id': {'args': True, 'logs': True},
            'user_phone_id': {'args': True, 'logs': True},
        },
    },
)
@pytest.mark.filldb(antifraud_rules='logs')
@pytest.mark.now('2019-02-22T08:00:00+0000')
def test_check_yt(
        taxi_antifraud,
        testpoint,
        mock_personal_phones_retrieve,
        experiments3,
        input,
        yt_data,
        experiments,
):
    for experiment in experiments:
        experiments3.add_experiment(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name=experiment['name'],
            consumers=['afs/antifake'],
            clauses=experiment['clauses'],
        )

    list = []

    @testpoint('yt_uploads::js_logs_info')
    def yt_upload(data):
        yt_data = base64.b64decode(data['base64'])
        obj = yt.yson.loads(yt_data, yson_type='list_fragment')

        for element in obj:
            list.append(yt.yson.yson_to_json(element))

    response = taxi_antifraud.post('client/user/check_fake', input)
    assert response.status_code == 200

    yt_upload.wait_call()
    assert len(list) == 1
    assert list[0] == yt_data


@pytest.mark.parametrize(
    'input,result',
    [
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': 'f3b46027b6af44ca8c998a111c94e296',
                'user_id': 'df6b27dc9b044fbdb5b703ba993a1786',
                'user_phone_id': 'some_user_id',
                'order_id': 'some_id',
                'should_be_undefined': 'defined',
                'should_be_undefined_2': 'defined',
            },
            True,
        ),
    ],
)
@pytest.mark.config(
    AFS_RULES_PARAMS_FILTER_ENABLED=True,
    AFS_RULES_PARAMS_FILTER_CONFIG={
        '__default__': {'should_be_undefined': {'args': True, 'logs': True}},
        '__all__': {
            'zone': {'args': True, 'logs': True},
            'should_be_undefined_2': {'args': True, 'logs': True},
        },
        'rule_types': {
            'antifake': {
                'order_id': {'args': True, 'logs': True},
                'should_be_undefined_2': {'args': False, 'logs': False},
            },
        },
    },
    AFS_RULES_LOG_CONFIG={'enabled': True},
)
@pytest.mark.filldb(antifraud_rules='args_filter')
def test_check_args_filter(
        taxi_antifraud, mock_personal_phones_retrieve, input, result,
):
    response = taxi_antifraud.post('client/user/check_fake', input)

    assert response.status_code == 200
    assert response.json()['frauder'] == result


@pytest.mark.config(AFS_ANTIFAKE_PASS_PROTOCOL_EVENTS=True)
@pytest.mark.redis_store(
    [
        'rpush',
        'v1:events:protocol:base:user1',
        '1547110810000:paymentmethods',
        '1547110805000:expecteddestinations',
        '1547110800000:couponlist',
    ],
    [
        'rpush',
        'v1:events:protocol:base:user2',
        '1547110800000:paymentmethods',
        '1547110805000:expecteddestinations',
        '1547110810000:couponlist',
    ],
)
@pytest.mark.parametrize(
    'user,frauder,rule',
    [('user1', True, 'test_rule1'), ('user2', False, None)],
)
def test_check_protocol_events(
        taxi_antifraud, mock_personal_phones_retrieve, user, frauder, rule,
):
    response = taxi_antifraud.post(
        'client/user/check_fake',
        {
            'zone': 'reutov',
            'user_personal_phone_id': 'f3b46027b6af44ca8c998a111c94e296',
            'user_id': user,
            'user_phone_id': 'some_id',
            'order_id': 'some_id',
        },
    )
    assert response.status_code == 200
    if frauder:
        assert {'frauder': True, 'rule_id': rule} == response.json()
    else:
        assert {'frauder': False} == response.json()


@pytest.mark.config(
    AFS_ANTIFAKE_IDEMPOTENT_FETCH=True, AFS_ANTIFAKE_IDEMPOTENT_STORE=True,
)
@pytest.mark.parametrize(
    'user,order,frauder,rule',
    [
        ('user1', 'order1', False, None),
        ('fraud_user1', 'fraud_order1', True, 'test_rule1'),
    ],
)
def test_check_idempotent_base(
        taxi_antifraud,
        testpoint,
        mock_personal_phones_retrieve,
        user,
        order,
        frauder,
        rule,
):
    @testpoint('after_fetch_idempotent_status')
    def after_fetch_idempotent_status(data):
        pass

    @testpoint('after_store_idempotent_status')
    def after_store_idempotent_status(data):
        pass

    def _make_request():
        return taxi_antifraud.post(
            'client/user/check_fake',
            {
                'zone': 'reutov',
                'user_personal_phone_id': 'f3b46027b6af44ca8c998a111c94e296',
                'user_id': user,
                'user_phone_id': 'user_phone_id1',
                'order_id': order,
            },
        )

    for i in range(5):
        response = _make_request()

        if not i:
            assert after_fetch_idempotent_status.wait_call() == {
                'data': {'found': False, 'frauder': False},
            }
            if frauder:
                assert after_store_idempotent_status.wait_call() == {
                    'data': {'frauder': frauder, 'rule_id': rule},
                }
            else:
                assert after_store_idempotent_status.wait_call() == {
                    'data': {'frauder': frauder},
                }
        else:
            if frauder:
                assert after_fetch_idempotent_status.wait_call() == {
                    'data': {
                        'found': True,
                        'frauder': frauder,
                        'rule_id': rule,
                    },
                }
            else:
                assert after_fetch_idempotent_status.wait_call() == {
                    'data': {'found': True, 'frauder': frauder},
                }

        assert response.status_code == 200

        if frauder:
            assert {'frauder': True, 'rule_id': rule} == response.json()
        else:
            assert {'frauder': False} == response.json()


_REALTIME_METRICS_CANCELS = 'realtime_metrics:cancels:436089'


@pytest.mark.config(
    AFS_USER_ANTIFAKE_PASS_REALTIME_FAKES=True,
    AFS_FAKERS_BY_GEOZONE_REALTIMES_ENABLED=True,
    AFS_RULES_LOG_CONFIG={
        'enabled': True,
        'rule_types': {'antifake': {'yt': 'ALL', 'file': 'ALL'}},
        'rule_overrides': {},
    },
)
@pytest.mark.filldb(antifraud_rules='realtime_fakes')
@pytest.mark.now('2019-10-01T09:00:00+0000')
@pytest.mark.redis_store(
    [
        'hset',
        _REALTIME_METRICS_CANCELS,
        'reutov:card:econom:total:26165339',
        '45',
    ],
    [
        'hset',
        _REALTIME_METRICS_CANCELS,
        'reutov:card:econom:total:26164339',
        '45',
    ],
    [
        'hset',
        _REALTIME_METRICS_CANCELS,
        'retov:card:econom:total:26165339',
        '45',
    ],
    [
        'hset',
        _REALTIME_METRICS_CANCELS,
        'reutov:card:econom:bad_driver_cancels:26165339',
        '45',
    ],
    [
        'hset',
        _REALTIME_METRICS_CANCELS,
        'reutov:cash:econom:total:26165339',
        '45',
    ],
    [
        'hset',
        _REALTIME_METRICS_CANCELS,
        'reutov:card:business:total:26165339',
        '45',
    ],
)
def test_realtime_fakes_metrics(
        taxi_antifraud, now, mock_personal_phones_retrieve,
):
    response = taxi_antifraud.post(
        'client/user/check_fake',
        {
            'zone': 'reutov',
            'user_personal_phone_id': 'f3b46027b6af44ca8c998a111c94e296',
            'user_id': 'user',
            'user_phone_id': 'user_phone_id1',
            'order_id': 'order',
            'payment_type': 'card',
            'tariff_class': 'econom',
            'is_multi_class': False,
        },
    )

    assert response.status_code == 200
    assert {'frauder': True, 'rule_id': 'test_rule_1'} == response.json()


def _check(response, expected_code, output=None):
    assert response.status_code == expected_code
    if response.status_code == 200:
        data = json.loads(response.text)
        assert data == output


@pytest.mark.config(
    AFS_RULES_LOG_CONFIG={
        'enabled': True,
        'rule_types': {'antifake': {'yt': 'ALL', 'file': 'ALL'}},
        'rule_overrides': {},
    },
)
@pytest.mark.filldb(
    antifraud_users_orders_aggregates='pass_daily_aggregates',
    antifraud_rules='pass_daily_aggregates',
)
@pytest.mark.parametrize(
    'input,output,expected_code',
    [
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': '87745c883b8149138c50ef7e454b7857',
                'user_id': 'aaaa27dc9b044fbdb5b703ffffffffff',
                'user_phone_id': '54f7632696421984c36931f9',
                'order_id': '0ba165e446cf1af0b3b7e8e0eeaf8c4b',
                'order_complete_count': 664,
                'order_total_count': 797,
            },
            {'frauder': True, 'rule_id': 'test_pass_aggregates'},
            200,
        ),
    ],
)
def test_pass_daily_aggregates(
        taxi_antifraud,
        mock_personal_phones_retrieve,
        input,
        output,
        expected_code,
):
    _check(
        taxi_antifraud.post('client/user/check_fake', json=input),
        expected_code,
        output,
    )


@pytest.mark.config(
    AFS_RULES_LOG_CONFIG={
        'enabled': True,
        'rule_types': {'antifake': {'yt': 'ALL', 'file': 'ALL'}},
        'rule_overrides': {},
    },
)
@pytest.mark.filldb(
    antifraud_users_aggregates='pass_daily_handlers_aggregates',
    antifraud_rules='pass_daily_handlers_aggregates',
)
@pytest.mark.parametrize(
    'input,output,expected_code',
    [
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': '87745c883b8149138c50ef7e454b7857',
                'user_id': 'aaaa27dc9b044fbdb5b703ffffffffff',
                'user_phone_id': '54f7632696421984c36931f9',
                'order_id': '0ba165e446cf1af0b3b7e8e0eeaf8c4b',
                'order_complete_count': 664,
                'order_total_count': 797,
            },
            {
                'frauder': True,
                'rule_id': 'test_pass_daily_handlers_aggregates',
            },
            200,
        ),
    ],
)
def test_pass_daily_handlers_aggregates(
        taxi_antifraud,
        mock_personal_phones_retrieve,
        input,
        output,
        expected_code,
):
    _check(
        taxi_antifraud.post('client/user/check_fake', json=input),
        expected_code,
        output,
    )


@pytest.mark.config(
    AFS_RULES_LOG_CONFIG={
        'enabled': True,
        'rule_types': {'antifake': {'yt': 'ALL', 'file': 'ALL'}},
        'rule_overrides': {},
    },
)
@pytest.mark.filldb(
    antifraud_users_aggregates='pass_all_handlers_aggregates',
    antifraud_rules='pass_all_handlers_aggregates',
)
@pytest.mark.parametrize(
    'input,output,expected_code',
    [
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': '87745c883b8149138c50ef7e454b7857',
                'user_id': 'aaaa27dc9b044fbdb5b703ffffffffff',
                'user_phone_id': '54f7632696421984c36931f9',
                'order_id': '0ba165e446cf1af0b3b7e8e0eeaf8c4b',
                'order_complete_count': 664,
                'order_total_count': 797,
            },
            {'frauder': True, 'rule_id': 'test_pass_all_handlers_aggregates'},
            200,
        ),
    ],
)
def test_pass_all_handlers_aggregates(
        taxi_antifraud,
        mock_personal_phones_retrieve,
        input,
        output,
        expected_code,
):
    _check(
        taxi_antifraud.post('client/user/check_fake', json=input),
        expected_code,
        output,
    )


@pytest.mark.config(AFS_ANTIFAKE_PASS_SIGNATURE=True)
@pytest.mark.parametrize(
    'input,output,expected_code',
    [
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': '87745c883b8149138c50ef7e454b7857',
                'user_id': 'aaaa27dc9b044fbdb5b703ffffffffff',
                'user_phone_id': '54f7632696421984c36931f9',
            },
            {'frauder': True, 'rule_id': 'test_pass_signature'},
            200,
        ),
    ],
)
def test_pass_device_info(
        taxi_antifraud,
        mock_personal_phones_retrieve,
        input,
        output,
        expected_code,
):
    response = taxi_antifraud.post('client/user/check_fake', json=input)

    assert response.status_code == expected_code
    assert response.json() == output


@pytest.mark.config(TVM_ENABLED=False)
def test_exp3(taxi_antifraud, mock_personal_phones_retrieve, experiments3):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='afs_notify_handler_call_zone_info',
        consumers=['afs/antifake'],
        clauses=[
            {
                'title': 'disable_test_exp_rule_1&2',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_type': 'string',
                        'arg_name': 'user_phone_id',
                        'value': '54f7632696421984c36931f9',
                    },
                },
                'value': {
                    'disabled_rules': ['test_exp_rule1', 'test_exp_rule2'],
                },
            },
        ],
    )

    response = taxi_antifraud.post(
        'client/user/check_fake',
        json={
            'zone': 'reutov',
            'user_personal_phone_id': '87745c883b8149138c50ef7e454b7857',
            'user_id': 'aaaa27dc9b044fbdb5b703ffffffffff',
            'user_phone_id': '54f7632696421984c36931f9',
            'order_id': 'e9103e313d9346d6ae02297dfd62b942',
        },
    )

    assert response.status_code == 200
    assert response.json() == {'frauder': False}


@pytest.mark.parametrize(
    'input,output,expected_code',
    [
        (
            {
                'zone': 'reutov',
                'user_personal_phone_id': 'fa29f28a20534d5faf2e9aef15a8102d',
                'user_id': 'e994415b04442b25fc53a72d36f95e2e',
                'user_phone_id': '54f7632696421984c36931f9',
                'yandex_uid': '745415988',
                'yandex_uid_type': 'portal',
                'device_id': 'ce142d112e152ca0ac6a66d6cfcb493f422a8b71',
                'payment_type': 'corp',
                'ip': '192.168.1.1',
                'real_ip': '192.168.1.1',
                'requirements_quantity': 5,
            },
            {'frauder': True, 'rule_id': 'test_rule_telesign'},
            200,
        ),
    ],
)
@pytest.mark.config(AFS_ANTIFAKE_TELESIGN_ENABLED=True)
def test_check_telesign(
        taxi_antifraud,
        mockserver,
        config,
        mock_personal_phones_retrieve,
        input,
        output,
        expected_code,
):
    def check(response):
        assert response.status_code == expected_code
        if response.status_code == 200:
            data = json.loads(response.text)
            assert data == output

    check(taxi_antifraud.post('client/user/check_fake', json=input))


def _check_dict_is_subdict(d, subdict):
    for key, value in subdict.items():
        assert key in d
        assert value == d[key]


@pytest.mark.parametrize(
    'input,expected_fields,expected_code,frauder',
    [
        (
            {
                'order_id': 'frauder_order',
                'zone': 'reutov',
                'user_personal_phone_id': '87745c883b8149138c50ef7e454b7857',
                'user_id': 'aaaa27dc9b044fbdb5b703ffffffffff',
                'user_phone_id': '54f7632696421984c36931f9',
                'device_id': 'some_device',
                'metrica_device_id': 'some_metrica_id',
                'order_total_count': 2,
                'order_complete_count': 0,
            },
            {
                'device_id': 'some_device',
                'metrica_device_id': 'some_metrica_id',
                'order_id': 'frauder_order',
                'personal_phone_id': '87745c883b8149138c50ef7e454b7857',
                'triggered_rules': ['first_reutov_rule', 'second_reutov_rule'],
                'phone_id': '54f7632696421984c36931f9',
                'total_orders_count': 2,
                'complete_orders_count': 0,
            },
            200,
            True,
        ),
        (
            {
                'order_id': 'not_frauder_order',
                'zone': 'ne_reutov',
                'user_personal_phone_id': '87745c883b8149138c50ef7e454b7857',
                'user_id': 'aaaa27dc9b044fbdb5b703ffffffffff',
                'user_phone_id': '54f7632696421984c36931f9',
            },
            None,
            200,
            False,
        ),
    ],
)
def test_save_triggered_rules_info(
        taxi_antifraud,
        testpoint,
        mock_personal_phones_retrieve,
        input,
        expected_fields,
        db,
        expected_code,
        frauder,
):
    @testpoint('after_store_rules_result')
    def after_store_idempotent_status(data):
        pass

    pre_state = [
        row
        for row in db.antifraud_antifake_triggering.find(
            {'order_id': input['order_id']},
        )
    ]
    assert len(pre_state) == 0

    response = taxi_antifraud.post('client/user/check_fake', json=input)

    assert response.status_code == expected_code
    assert response.json()['frauder'] == frauder

    if expected_fields is not None:
        after_store_idempotent_status.wait_call()
    rows = [
        row
        for row in db.antifraud_antifake_triggering.find(
            {'order_id': input['order_id']},
        )
    ]
    if expected_fields is not None:
        assert len(rows) == 1
        _check_dict_is_subdict(rows[0], expected_fields)
    else:
        assert len(rows) == 0


_REDIS_KEY_PREFIX = 'js:antifake:rules_auto_fallback:'
_REDIS_KEY_TIME_MULTIPLIER = 100


@pytest.mark.parametrize(
    'input',
    [
        {
            'zone': 'reutov',
            'user_personal_phone_id': '87745c883b8149138c50ef7e454b7857',
            'user_id': 'aaaa27dc9b044fbdb5b703ffffffffff',
            'user_phone_id': '54f7632696421984c36931f9',
            'order_id': 'e9103e313d9346d6ae02297dfd62b942',
        },
    ],
)
@pytest.mark.filldb(antifraud_rules='auto_fallbacks_stats')
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.config(
    AFS_ANTIFAKE_FAST_SEND_STATS_FOR_AUTO_FALLBACKS=False,
    AFS_ANTIFAKE_SEND_STATS_FOR_AUTO_FALLBACKS=True,
)
def test_send_rules_stats_for_auto_fallbacks(
        taxi_antifraud,
        testpoint,
        mock_personal_phones_retrieve,
        redis_store,
        now,
        input,
):
    @testpoint('after_send_antifake_metrics_for_auto_fallback')
    def after_send_metrics(_):
        pass

    response = taxi_antifraud.post('client/user/check_fake', json=input)

    assert response.status_code == 200
    after_send_metrics.wait_call()

    assert int(
        redis_store.get(_REDIS_KEY_PREFIX + 'last_time'),
    ) == utils.to_timestamp(now, utils.Units.SECONDS)

    redis_hash_key = _REDIS_KEY_PREFIX + str(
        utils.to_timestamp(now, utils.Units.SECONDS),
    )
    assert (
        int(redis_store.hget(redis_hash_key, 'last_time'))
        == utils.to_timestamp(
            now, utils.Units.MILLISECONDS, _REDIS_KEY_TIME_MULTIPLIER,
        )
    )

    assert (
        int(
            redis_store.hget(
                redis_hash_key,
                'not_frauder_rule:total:'
                + str(
                    utils.to_timestamp(
                        now,
                        utils.Units.MILLISECONDS,
                        _REDIS_KEY_TIME_MULTIPLIER,
                    ),
                ),
            ),
        )
        == 1
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key,
                'frauder_rule:total:'
                + str(
                    utils.to_timestamp(
                        now,
                        utils.Units.MILLISECONDS,
                        _REDIS_KEY_TIME_MULTIPLIER,
                    ),
                ),
            ),
        )
        == 1
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key,
                'frauder_rule:triggered:'
                + str(
                    utils.to_timestamp(
                        now,
                        utils.Units.MILLISECONDS,
                        _REDIS_KEY_TIME_MULTIPLIER,
                    ),
                ),
            ),
        )
        == 1
    )


@pytest.mark.parametrize(
    'input',
    [
        {
            'zone': 'reutov',
            'user_personal_phone_id': '87745c883b8149138c50ef7e454b7857',
            'user_id': 'aaaa27dc9b044fbdb5b703ffffffffff',
            'user_phone_id': '54f7632696421984c36931f9',
            'order_id': 'e9103e313d9346d6ae02297dfd62b942',
        },
    ],
)
@pytest.mark.filldb(antifraud_rules='auto_fallbacks_stats')
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.config(
    AFS_ANTIFAKE_FAST_SEND_STATS_FOR_AUTO_FALLBACKS=False,
    AFS_ANTIFAKE_SEND_STATS_FOR_AUTO_FALLBACKS=True,
)
def test_send_rules_stats_for_auto_fallbacks_multi(
        taxi_antifraud,
        testpoint,
        mock_personal_phones_retrieve,
        redis_store,
        now,
        input,
):
    @testpoint('after_send_antifake_metrics_for_auto_fallback')
    def after_send_metrics(_):
        pass

    repeats = 3

    for _ in range(repeats):
        response = taxi_antifraud.post('client/user/check_fake', json=input)

        assert response.status_code == 200

    for _ in range(repeats):
        after_send_metrics.wait_call()

    assert int(
        redis_store.get(_REDIS_KEY_PREFIX + 'last_time'),
    ) == utils.to_timestamp(now, utils.Units.SECONDS)

    redis_hash_key = _REDIS_KEY_PREFIX + str(
        utils.to_timestamp(now, utils.Units.SECONDS),
    )
    assert (
        int(redis_store.hget(redis_hash_key, 'last_time'))
        == utils.to_timestamp(
            now, utils.Units.MILLISECONDS, _REDIS_KEY_TIME_MULTIPLIER,
        )
    )

    assert (
        int(
            redis_store.hget(
                redis_hash_key,
                'not_frauder_rule:total:'
                + str(
                    utils.to_timestamp(
                        now,
                        utils.Units.MILLISECONDS,
                        _REDIS_KEY_TIME_MULTIPLIER,
                    ),
                ),
            ),
        )
        == repeats
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key,
                'frauder_rule:total:'
                + str(
                    utils.to_timestamp(
                        now,
                        utils.Units.MILLISECONDS,
                        _REDIS_KEY_TIME_MULTIPLIER,
                    ),
                ),
            ),
        )
        == repeats
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key,
                'frauder_rule:triggered:'
                + str(
                    utils.to_timestamp(
                        now,
                        utils.Units.MILLISECONDS,
                        _REDIS_KEY_TIME_MULTIPLIER,
                    ),
                ),
            ),
        )
        == repeats
    )


@pytest.mark.parametrize(
    'input',
    [
        {
            'zone': 'reutov',
            'user_personal_phone_id': '87745c883b8149138c50ef7e454b7857',
            'user_id': 'aaaa27dc9b044fbdb5b703ffffffffff',
            'user_phone_id': '54f7632696421984c36931f9',
            'order_id': 'e9103e313d9346d6ae02297dfd62b942',
        },
    ],
)
@pytest.mark.filldb(antifraud_rules='auto_fallbacks_stats')
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.config(
    AFS_ANTIFAKE_FAST_SEND_STATS_FOR_AUTO_FALLBACKS=False,
    AFS_ANTIFAKE_SEND_STATS_FOR_AUTO_FALLBACKS=True,
)
def test_send_rules_stats_for_auto_fallbacks_different_time(
        taxi_antifraud,
        testpoint,
        mock_personal_phones_retrieve,
        redis_store,
        now,
        input,
):
    @testpoint('after_send_antifake_metrics_for_auto_fallback')
    def after_send_metrics(_):
        pass

    response = taxi_antifraud.post('client/user/check_fake', json=input)

    assert response.status_code == 200
    after_send_metrics.wait_call()

    redis_hash_key_old_now = _REDIS_KEY_PREFIX + str(
        utils.to_timestamp(now, utils.Units.SECONDS),
    )

    old_now = now

    now = now.replace(minute=1)
    taxi_antifraud.tests_control(now=now, invalidate_caches=False)

    response = taxi_antifraud.post('client/user/check_fake', json=input)
    assert response.status_code == 200
    after_send_metrics.wait_call()

    assert int(
        redis_store.get(_REDIS_KEY_PREFIX + 'last_time'),
    ) == utils.to_timestamp(now, utils.Units.SECONDS)
    redis_hash_key_new_now = _REDIS_KEY_PREFIX + str(
        utils.to_timestamp(now, utils.Units.SECONDS),
    )

    assert (
        int(redis_store.hget(redis_hash_key_new_now, 'last_time'))
        == utils.to_timestamp(
            now, utils.Units.MILLISECONDS, _REDIS_KEY_TIME_MULTIPLIER,
        )
    )

    assert (
        int(
            redis_store.hget(
                redis_hash_key_old_now,
                'not_frauder_rule:total:'
                + str(
                    utils.to_timestamp(
                        old_now,
                        utils.Units.MILLISECONDS,
                        _REDIS_KEY_TIME_MULTIPLIER,
                    ),
                ),
            ),
        )
        == 1
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key_old_now,
                'frauder_rule:total:'
                + str(
                    utils.to_timestamp(
                        old_now,
                        utils.Units.MILLISECONDS,
                        _REDIS_KEY_TIME_MULTIPLIER,
                    ),
                ),
            ),
        )
        == 1
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key_old_now,
                'frauder_rule:triggered:'
                + str(
                    utils.to_timestamp(
                        old_now,
                        utils.Units.MILLISECONDS,
                        _REDIS_KEY_TIME_MULTIPLIER,
                    ),
                ),
            ),
        )
        == 1
    )

    assert (
        int(
            redis_store.hget(
                redis_hash_key_new_now,
                'not_frauder_rule:total:'
                + str(
                    utils.to_timestamp(
                        now,
                        utils.Units.MILLISECONDS,
                        _REDIS_KEY_TIME_MULTIPLIER,
                    ),
                ),
            ),
        )
        == 1
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key_new_now,
                'frauder_rule:total:'
                + str(
                    utils.to_timestamp(
                        now,
                        utils.Units.MILLISECONDS,
                        _REDIS_KEY_TIME_MULTIPLIER,
                    ),
                ),
            ),
        )
        == 1
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key_new_now,
                'frauder_rule:triggered:'
                + str(
                    utils.to_timestamp(
                        now,
                        utils.Units.MILLISECONDS,
                        _REDIS_KEY_TIME_MULTIPLIER,
                    ),
                ),
            ),
        )
        == 1
    )


@pytest.mark.parametrize(
    'input',
    [
        {
            'zone': 'reutov',
            'user_personal_phone_id': '87745c883b8149138c50ef7e454b7857',
            'user_id': 'aaaa27dc9b044fbdb5b703ffffffffff',
            'user_phone_id': '54f7632696421984c36931f9',
            'order_id': 'e9103e313d9346d6ae02297dfd62b942',
        },
    ],
)
@pytest.mark.filldb(antifraud_rules='auto_fallbacks_stats')
@pytest.mark.now('2019-10-01T07:00:08+0000')
@pytest.mark.config(
    AFS_ANTIFAKE_FAST_SEND_STATS_FOR_AUTO_FALLBACKS=False,
    AFS_ANTIFAKE_SEND_STATS_FOR_AUTO_FALLBACKS=True,
)
@pytest.mark.redis_store(
    [
        'hset',
        _REDIS_KEY_PREFIX + '1569920408',
        'frauder_rule:total:15699204080',
        '45',
    ],
    ['set', _REDIS_KEY_PREFIX + 'last_time', '1569920408'],
    ['hset', _REDIS_KEY_PREFIX + '1569920408', 'last_time', '15699204080'],
)
def test_send_rules_stats_for_auto_fallbacks_time_less(
        taxi_antifraud,
        testpoint,
        mock_personal_phones_retrieve,
        redis_store,
        input,
):
    @testpoint('after_send_antifake_metrics_for_auto_fallback')
    def after_send_metrics(_):
        pass

    response = taxi_antifraud.post('client/user/check_fake', json=input)

    assert response.status_code == 200
    after_send_metrics.wait_call()

    max_hash_time = 1569920408
    max_key_time = 15699204080

    assert (
        int(redis_store.get(_REDIS_KEY_PREFIX + 'last_time')) == max_hash_time
    )

    redis_hash_key = _REDIS_KEY_PREFIX + str(max_hash_time)
    assert int(redis_store.hget(redis_hash_key, 'last_time')) == max_key_time

    assert (
        int(
            redis_store.hget(
                redis_hash_key, 'not_frauder_rule:total:' + str(max_key_time),
            ),
        )
        == 1
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key, 'frauder_rule:total:' + str(max_key_time),
            ),
        )
        == 46
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key, 'frauder_rule:triggered:' + str(max_key_time),
            ),
        )
        == 1
    )


@pytest.mark.now('2021-06-17T20:11:58+0300')
@pytest.mark.config(AFS_ANTIFAKE_RTXARON_ENABLED=True)
def test_rt_xaron(taxi_antifraud, mock_personal_phones_retrieve, mockserver):
    @mockserver.json_handler('/rt_xaron_base/')
    def mock_personal_phones_retrieve(request):
        assert request.headers['Expect'] == ''
        assert request.json == {
            'created': 1623949918.0,
            'nz': 'reutov',
            'order_id': '3f5a815b45de22caaab9edd4a33c9b87',
            'payment_type': 'googlepay',
            'request_ip': '2a00:1370:810c:9894:5f3:ee3c:bde7:e4f9',
            'source_geopoint': [37.847002, 55.747576],
            'updated': 1623949918.0,
            'user_device_id': 'b4cbe7a3407234d99149daeb42d08ee7',
            'user_id': 'f1550a8410c245929e2b40455e958f32',
            'user_personal_phone_id': 'ed4f680d049e4cabb1c91060635e70c2',
            'user_uid': '162823816',
            'params': {'service': 'rtxaron'},
            'order_application': 'android',
            'plan_transporting_distance_m': 1283.406165599823,
            'order_comment': 'К 3 подъезду',
            'destinations_geopoint': [
                [37.642528, 55.735707],
                [46.023228, 51.536121],
            ],
            'extra_user_personal_phone_id': 'ed693bcf723844f680b16824f70ef486',
            'user_fixed_price': 949.0,
            'driver_fixed_price': 1264.0,
            'is_multiorder': True,
            'user_metrica_device_id': 'b4cbe7a3407234d99149daeb42d08ee7',
            'user_order_complete_count': 1039,
            'user_order_total_count': 1251,
            'position_geopoint': [37.84543228149414, 55.74775314331055],
            'surge': {
                'surcharge_alpha': 0.2,
                'surcharge_beta': 0.8,
                'surge_price': 1.0,
            },
            'request_classes': 'vip',
            'user_agent': 'ru.yandex.ytaxi/650.23.0.188145',
        }
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

    response = taxi_antifraud.post(
        'client/user/check_fake',
        json={
            'fixed_price': {
                'driver_price': 1264.0,
                'price_original': 949.0,
                'price': 949.0,
            },
            'ip': '192.168.1.68',
            'user_phone': '+79162991489',
            'is_multi_class': False,
            'metrica_device_id': 'b4cbe7a3407234d99149daeb42d08ee7',
            'user_created': '2020-04-22T09:33:15+0000',
            'requirements_quantity': 1,
            'destinations': [
                {
                    'metrica_action': 'addressCorrection',
                    'lon': 37.642528,
                    'lat': 55.735707,
                    'type': 'address',
                    'metrica_method': 'suggest',
                },
                {
                    'oid': '121328259779',
                    'lon': 46.023228,
                    'lat': 51.536121,
                    'premisenumber': '80',
                    'type': 'organization',
                    'metrica_method': 'suggest',
                },
            ],
            'user_id': 'f1550a8410c245929e2b40455e958f32',
            'zone': 'reutov',
            'application': 'android',
            'order_complete_count': 1039,
            'source': {
                'metrica_action': 'auto',
                'lon': 37.847002,
                'lat': 55.747576,
                'premisenumber': '1',
                'type': 'address',
                'metrica_method': 'suggest',
            },
            'allowed_tariffs': {
                '__park__': {
                    'cargo': 995.0,
                    'eda': 0.0,
                    'lavka': 0.0,
                    'courier': 333.0,
                    'business': 303.0,
                    'minivan': 669.0,
                    'promo': 0.0,
                    'express': 543.0,
                    'premium_van': 1862.0,
                    'econom': 262.0,
                    'suv': 501.0,
                    'vip': 949.0,
                    'ultimate': 2345.0,
                    'comfortplus': 488.0,
                    'child_tariff': 315.0,
                    'maybach': 2405.0,
                    'cargocorp': 967.0,
                },
            },
            'yandex_uuid': '63f04e36719e479a9d99bcba9c0e3b59',
            'yandex_uid_type': 'portal',
            'payment_type': 'googlepay',
            'launch_updated': '2020-12-02T13:38:56+0000',
            'order_total_count': 1251,
            'real_ip': '2a00:1370:810c:9894:5f3:ee3c:bde7:e4f9',
            'order_id': '3f5a815b45de22caaab9edd4a33c9b87',
            'user_personal_phone_id': 'ed4f680d049e4cabb1c91060635e70c2',
            'mac': '02:00:00:00:00:00',
            'yandex_uid': '162823816',
            'application_version': '4.14.1',
            'device_id': 'b4cbe7a3407234d99149daeb42d08ee7',
            'real_application': 'android',
            'surge': {
                'surcharge_beta': 0.8,
                'surcharge_alpha': 0.2,
                'surge_price': 1.0,
            },
            'instance_id': 'cmDRMMfkOko',
            'user_phone_id': '55a2690b056f5f6f8223bb83',
            'position': {
                'lat': 55.74775314331055,
                'lon': 37.84543228149414,
                'dx': 142,
            },
            'tariff_class': 'vip',
            'metrica_uuid': '63f04e36719e479a9d99bcba9c0e3b59',
            'calc_distance': 1283.406165599823,
            'comment': 'К 3 подъезду',
            'extra_user_personal_phone_id': 'ed693bcf723844f680b16824f70ef486',
            'is_multiorder': True,
            'user_agent': 'ru.yandex.ytaxi/650.23.0.188145',
        },
    )

    assert response.status_code == 200
    assert response.json() == {'frauder': True, 'rule_id': 'test_rt_xaron1'}


@pytest.mark.now('2021-06-17T20:11:58+0300')
@pytest.mark.config(AFS_ANTIFAKE_USER_TAGS_ENABLED=True)
def test_user_tags(taxi_antifraud, mock_personal_phones_retrieve, mockserver):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def mock_user_tags(request):
        assert request.json == {
            'match': [
                {
                    'type': 'personal_phone_id',
                    'value': 'ed4f680d049e4cabb1c91060635e70c2',
                },
            ],
        }
        return {'tags': ['tag1', 'tag2', 'tag3']}

    response = taxi_antifraud.post(
        'client/user/check_fake',
        json={
            'fixed_price': {
                'driver_price': 1264.0,
                'price_original': 949.0,
                'price': 949.0,
            },
            'ip': '192.168.1.68',
            'user_phone': '+79162991489',
            'is_multi_class': False,
            'metrica_device_id': 'b4cbe7a3407234d99149daeb42d08ee7',
            'user_created': '2020-04-22T09:33:15+0000',
            'requirements_quantity': 1,
            'destinations': [
                {
                    'metrica_action': 'addressCorrection',
                    'lon': 37.642528,
                    'lat': 55.735707,
                    'type': 'address',
                    'metrica_method': 'suggest',
                },
            ],
            'user_id': 'f1550a8410c245929e2b40455e958f32',
            'zone': 'reutov',
            'application': 'android',
            'order_complete_count': 1039,
            'source': {
                'metrica_action': 'auto',
                'lon': 37.847002,
                'lat': 55.747576,
                'premisenumber': '1',
                'type': 'address',
                'metrica_method': 'suggest',
            },
            'allowed_tariffs': {
                '__park__': {
                    'cargo': 995.0,
                    'eda': 0.0,
                    'lavka': 0.0,
                    'courier': 333.0,
                    'business': 303.0,
                    'minivan': 669.0,
                    'promo': 0.0,
                    'express': 543.0,
                    'premium_van': 1862.0,
                    'econom': 262.0,
                    'suv': 501.0,
                    'vip': 949.0,
                    'ultimate': 2345.0,
                    'comfortplus': 488.0,
                    'child_tariff': 315.0,
                    'maybach': 2405.0,
                    'cargocorp': 967.0,
                },
            },
            'yandex_uuid': '63f04e36719e479a9d99bcba9c0e3b59',
            'yandex_uid_type': 'portal',
            'payment_type': 'googlepay',
            'launch_updated': '2020-12-02T13:38:56+0000',
            'order_total_count': 1251,
            'real_ip': '2a00:1370:810c:9894:5f3:ee3c:bde7:e4f9',
            'order_id': '3f5a815b45de22caaab9edd4a33c9b87',
            'user_personal_phone_id': 'ed4f680d049e4cabb1c91060635e70c2',
            'mac': '02:00:00:00:00:00',
            'yandex_uid': '162823816',
            'application_version': '4.14.1',
            'device_id': 'b4cbe7a3407234d99149daeb42d08ee7',
            'real_application': 'android',
            'surge': {
                'surcharge_beta': 0.8,
                'surcharge_alpha': 0.2,
                'surge_price': 1.0,
            },
            'instance_id': 'cmDRMMfkOko',
            'user_phone_id': '55a2690b056f5f6f8223bb83',
            'position': {
                'lat': 55.74775314331055,
                'lon': 37.84543228149414,
                'dx': 142,
            },
            'tariff_class': 'vip',
            'metrica_uuid': '63f04e36719e479a9d99bcba9c0e3b59',
        },
    )

    assert response.status_code == 200
    assert response.json() == {'frauder': True, 'rule_id': 'test_user_tags1'}


@pytest.mark.config(AFS_ANTIFAKE_STORE_REASONS=True)
@pytest.mark.filldb(antifraud_rules='return_struct_result')
def test_return_struct_result(taxi_antifraud, testpoint, redis_store):
    @testpoint('after_store_reasons')
    def after_store_reasons(data):
        pass

    response = taxi_antifraud.post(
        'client/user/check_fake',
        json={
            'order_id': 'order_id1',
            'user_id': 'fraud_user1',
            'user_phone_id': (
                'some_user_phone_id1'
            ),  # not required by schema, but really required
            'zone': 'moscow',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'frauder': True, 'rule_id': 'test_rule1'}

    EXPECTED_REASONS = ['test_reason']

    assert after_store_reasons.wait_call() == {'data': EXPECTED_REASONS}
    redis_key = ':'.join(
        ['v1', 'client', 'user', 'antifake', 'r', 'order_id1'],
    )
    assert json.loads(redis_store.get(redis_key)) == EXPECTED_REASONS


@pytest.mark.config(AFS_ANTIFAKE_STORE_REASONS=True)
@pytest.mark.filldb(antifraud_rules='return_struct_result')
def test_fail_struct_result(taxi_antifraud, testpoint):
    @testpoint('fail_parse_rule_result_object')
    def fail_parse_rule_result_object(_):
        pass

    response = taxi_antifraud.post(
        'client/user/check_fake',
        json={
            'order_id': 'order_id1',
            'user_id': 'user_for_fail_response1',
            'user_phone_id': (
                'some_user_phone_id1'
            ),  # not required by schema, but really required
            'zone': 'moscow',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'frauder': False}

    assert fail_parse_rule_result_object.wait_call()
