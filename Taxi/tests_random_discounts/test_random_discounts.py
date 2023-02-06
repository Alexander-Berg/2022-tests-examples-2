# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
# pylint: enable=import-error
import pytest

RANDOM_DISCOUNTS_DB_NAME = 'random_discounts'

HEADERS = {
    'X-YaTaxi-UserId': 'yauid_1',
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '4003514353',
    'X-Request-Application': 'app_name=iphone,app_ver1=10,app_ver2=2',
    'X-Request-Language': 'ru',
    'X-YaTaxi-Bound-Uids': '123, 456',
    'X-AppMetrica-DeviceId': 'default_dev_id',
    'X-AppMetrica-UUID': 'qwerty123',
    'X-Idempotency-Token': 'default_idempotency_token',
}

TRANSLATIONS = {
    'uber.random_discounts.dice_msg.active': {'ru': 'lets play'},
    'uber.random_discounts.dice_msg.inactive': {'ru': 'can\'t play'},
    'uber.random_discounts.roll_msg': {'ru': 'while_roll'},
    'uber.random_discounts.roll_unavailable_msg.button_text': {
        'ru': 'button_text_unav_msg',
    },
    'uber.random_discounts.roll_unavailable_msg.title': {
        'ru': 'title_unav_msg',
    },
    'uber.random_discounts.roll_unavailable_msg.description': {
        'ru': 'description_unav_msg',
    },
    'uber.random_discounts.point_b_msg': {'ru': 'point_b_msg'},
    'uber.random_discounts.roll_failure_msg.button_text': {
        'ru': 'fail_button',
    },
    'uber.random_discounts.roll_failure_msg.title': {'ru': 'fail_title'},
    'uber.random_discounts.roll_failure_msg.description': {
        'ru': 'fail_description',
    },
    'uber.random_discounts.roll_success_msg.button_text': {
        'ru': 'success_button',
    },
    'uber.random_discounts.roll_success_msg.title': {'ru': 'success_title'},
    'uber.random_discounts.roll_success_msg.description': {
        'ru': 'success_description',
    },
    'uber.random_discounts.button_info.title': {'ru': 'Заголовок кнопки'},
    'uber.random_discounts.button_info.description': {'ru': 'Описание кнопки'},
}

ACTIVE = 'active'
INACTIVE = 'inactive'
DISABLED = 'disabled'

DEFAULT_UID = 'some_user_id'


def get_expected_messages(msg_type):
    return {
        'button_text': TRANSLATIONS[
            f'uber.random_discounts.{msg_type}.button_text'
        ]['ru'],
        'description': TRANSLATIONS[
            f'uber.random_discounts.{msg_type}.description'
        ]['ru'],
        'title': TRANSLATIONS[f'uber.random_discounts.{msg_type}.title']['ru'],
    }


EXPECTED_RESPONSE = {
    'roll_unavailable_messages': get_expected_messages('roll_unavailable_msg'),
    'is_autoroll': False,
    'need_point_b_for_dice': True,
    'roll_message': TRANSLATIONS['uber.random_discounts.roll_msg']['ru'],
    'point_b_message': TRANSLATIONS['uber.random_discounts.point_b_msg']['ru'],
}

EXPECTED_RUNAWAY_DISCOUNT_FIELDS = {
    'show_runaway_discount': True,
    'expire_at': '2020-01-09T08:05:00+00:00',
    'discount_ttl_min': 5,
    'supported_classes': ['econom', 'business'],
    'button_info': {
        'title_message': TRANSLATIONS[
            'uber.random_discounts.button_info.title'
        ]['ru'],
        'description_message': TRANSLATIONS[
            'uber.random_discounts.button_info.description'
        ]['ru'],
        'background_color': '#666666',
        'clip_color': '#AAAAAA',
    },
}

GET_USER_ROLLS = (
    'SELECT * FROM random_discounts.random_discounts '
    'WHERE yandex_uid = \'{}\''
)


def check_status(resp_body, expected_status, show_runaway_discount=False):
    assert resp_body['status'] == expected_status
    if expected_status == DISABLED:
        assert len(resp_body) == 1
        return

    assert (
        resp_body['dice_message']
        == TRANSLATIONS[f'uber.random_discounts.dice_msg.{expected_status}'][
            'ru'
        ]
    )
    for field, val in EXPECTED_RESPONSE.items():
        assert val == resp_body[field]

    if show_runaway_discount:
        for field, val in EXPECTED_RUNAWAY_DISCOUNT_FIELDS.items():
            assert val == resp_body[field]
    else:
        assert not resp_body.get('show_runaway_discount', False)


# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.now('2020-01-10T09:00:00+0000'),
    pytest.mark.translations(client_messages=TRANSLATIONS),
    pytest.mark.pgsql(
        RANDOM_DISCOUNTS_DB_NAME, files=['pg_random_discounts.sql'],
    ),
]
# pylint: enable=invalid-name


@pytest.mark.experiments3(filename='random_discounts_exp.json')
@pytest.mark.parametrize(
    ['uid', 'device_id', 'bound_uids'],
    [
        pytest.param('active_id', 'no', '123,143', id='by_uid'),
        pytest.param('no', 'active_dev', 'no', id='by_device_id'),
        pytest.param('no', 'no', 'active_id,123', id='by_bound_uids'),
        pytest.param('no', 'no', 'no', id='not_in_bd'),
    ],
)
async def test_status_active(
        taxi_random_discounts, user_api, uid, device_id, bound_uids,
):
    headers = dict(HEADERS)
    headers['X-Yandex-UID'] = uid
    headers['X-AppMetrica-DeviceId'] = device_id
    headers['X-YaTaxi-Bound-Uids'] = bound_uids

    response = await taxi_random_discounts.post(
        '/4.0/random-discounts/v1/status',
        json={'zone': 'moscow'},
        headers=headers,
    )

    assert response.status_code == 200
    check_status(response.json(), ACTIVE)
    assert user_api.mock_user_phones.times_called == 1


@pytest.mark.experiments3(filename='random_discounts_exp.json')
@pytest.mark.parametrize(
    ['uid', 'device_id', 'zone', 'expected_status'],
    [
        pytest.param('inactive_id', 'no', 'moscow', INACTIVE, id='by_uid'),
        pytest.param(
            'no', 'inactive_dev', 'moscow', INACTIVE, id='inactive_device',
        ),
        pytest.param(
            'active_id', 'active_dev', 'spb', DISABLED, id='disabled',
        ),
    ],
)
async def test_status_not_active(
        taxi_random_discounts, user_api, uid, device_id, zone, expected_status,
):

    headers = dict(HEADERS)
    headers['X-Yandex-UID'] = uid
    headers['X-AppMetrica-DeviceId'] = device_id

    response = await taxi_random_discounts.post(
        '/4.0/random-discounts/v1/status',
        json={'zone': zone},
        headers=headers,
    )

    assert response.status_code == 200
    resp_body = response.json()
    if expected_status == INACTIVE:
        check_status(resp_body, expected_status)
        assert user_api.mock_user_phones.times_called == 1
    else:
        assert len(resp_body) == 1
        assert user_api.mock_user_phones.times_called == 0


@pytest.mark.experiments3(filename='random_discounts_exp.json')
@pytest.mark.parametrize(
    ['uid', 'expected_time'],
    [
        pytest.param('inactive_id', 60, id='inactive_time'),
        pytest.param('time_uid', 71, id='round_from_secs'),
    ],
)
async def test_status_inactive_remaining_time(
        taxi_random_discounts, user_api, uid, expected_time,
):
    headers = dict(HEADERS)
    headers['X-Yandex-UID'] = uid

    response = await taxi_random_discounts.post(
        '/4.0/random-discounts/v1/status',
        json={'zone': 'moscow'},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    check_status(body, INACTIVE)
    assert body['next_activation_remaining_time_min'] == expected_time


def check_success(docs, uid):
    assert len(docs) == 1
    doc = docs[0]

    assert doc['random_discount_id'] == 'default_idempotency_token'
    assert doc['yandex_uid'] == uid
    assert doc['device_id'] == 'default_dev_id'
    assert doc['discount_series'] in ['series_id_0', 'series_id_1']
    assert doc['discount_ttl_mins'] in [1234, 777, 10]
    assert doc['discount'] in [11, 22]
    assert doc['discount_limit'] in [111, 222]
    assert doc['coupon_code'] is not None


def check_fail(docs, uid):
    assert len(docs) == 1
    doc = docs[0]

    assert doc['random_discount_id'] == 'default_idempotency_token'
    assert doc['yandex_uid'] == uid
    assert doc['device_id'] == 'default_dev_id'

    assert doc.get('discount_series') is None
    assert doc.get('discount') is None
    assert doc.get('discount_limit') is None
    assert doc.get('discount_ttl_mins') is None


def check_conflict(docs, uid):
    assert len(docs) == 1
    doc = docs[0]

    assert doc['random_discount_id'] == '1'
    assert doc['yandex_uid'] == uid
    assert doc['device_id'] == 'inactive_dev'
    assert doc['discount_series'] == 'coolseries'
    assert doc['discount'] == 30
    assert doc['discount_limit'] == 150
    assert doc['discount_ttl_mins'] == 1440


def check_random_discounts_db(pgsql, uid, roll_status):
    def get_pg_records_as_dicts(sql, db):
        db.execute(sql)
        columns = [desc[0] for desc in db.description]
        records = list(db)
        return [dict(zip(columns, rec)) for rec in records]

    docs = get_pg_records_as_dicts(
        GET_USER_ROLLS.format(uid), pgsql['random_discounts'].cursor(),
    )
    if roll_status == 'conflict':
        check_conflict(docs, uid)
    if roll_status == 'success':
        check_success(docs, uid)
    if roll_status == 'failure':
        check_fail(docs, uid)


@pytest.mark.experiments3(filename='random_discounts_exp.json')
async def test_roll_handle(taxi_random_discounts, user_api, pgsql):
    uid = 'some_user_id'
    headers = dict(HEADERS)
    headers['X-Yandex-UID'] = uid

    response = await taxi_random_discounts.post(
        '/4.0/random-discounts/v1/roll',
        json={'zone': 'moscow'},
        headers=headers,
    )

    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['roll_result'] == 'success'
    assert resp_body['discount'] in [11, 22]
    assert resp_body['result_messages'] == get_expected_messages(
        'roll_success_msg',
    )

    check_status(resp_body['current_status'], INACTIVE)
    check_random_discounts_db(pgsql, uid, resp_body['roll_result'])

    retry = await taxi_random_discounts.post(
        '/4.0/random-discounts/v1/roll',
        json={'zone': 'moscow'},
        headers=headers,
    )
    retry_body = retry.json()
    assert retry_body == resp_body
    check_status(retry_body['current_status'], INACTIVE)
    check_random_discounts_db(pgsql, uid, resp_body['roll_result'])


@pytest.mark.experiments3(filename='random_discounts_exp.json')
async def test_roll_conflict(taxi_random_discounts, user_api, pgsql):
    uid = 'inactive_id'
    headers = dict(HEADERS)
    headers['X-Yandex-UID'] = uid

    response = await taxi_random_discounts.post(
        '/4.0/random-discounts/v1/roll',
        json={'zone': 'moscow'},
        headers=headers,
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['roll_result'] == 'conflict'
    assert 'discount' not in resp_body
    assert resp_body['result_messages'] == get_expected_messages(
        'roll_unavailable_msg',
    )

    check_status(resp_body['current_status'], INACTIVE)
    assert (
        resp_body['current_status']['next_activation_remaining_time_min'] == 60
    )

    check_random_discounts_db(pgsql, uid, resp_body['roll_result'])


@pytest.mark.experiments3(filename='random_discounts_exp.json')
async def test_roll_fail_on_disable(taxi_random_discounts, user_api, pgsql):
    response = await taxi_random_discounts.post(
        '/4.0/random-discounts/v1/roll', json={'zone': 'spb'}, headers=HEADERS,
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['roll_result'] == 'failure'
    assert 'discount' not in resp_body

    check_status(resp_body['current_status'], DISABLED)

    check_random_discounts_db(
        pgsql, HEADERS['X-Yandex-UID'], resp_body['roll_result'],
    )


@pytest.mark.experiments3(filename='random_discounts_exp.json')
@pytest.mark.parametrize(
    'swap_field, expected_dice_message, expected_roll_message',
    [
        (False, 'can\'t play', 'while_roll'),
        (True, 'while_roll', 'can\'t play'),
    ],
)
async def test_swap_fileds(
        taxi_random_discounts,
        user_api,
        pgsql,
        experiments3,
        swap_field,
        expected_dice_message,
        expected_roll_message,
):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='random_discounts_swap_fields',
        consumers=['coupons/random_discounts'],
        clauses=[
            {
                'title': '1',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'version',
                                    'arg_type': 'version',
                                    'value': '11.0.0',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {'enabled': True},
            },
        ],
        default_value=None,
    )
    await taxi_random_discounts.invalidate_caches()

    headers = dict(HEADERS)
    if swap_field:
        headers[
            'X-Request-Application'
        ] = 'app_name=iphone,app_ver1=11,app_ver2=0,app_ver3=0'

    response = await taxi_random_discounts.post(
        '/4.0/random-discounts/v1/roll',
        json={'zone': 'moscow'},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data['current_status']['dice_message'] == expected_dice_message
    assert data['current_status']['roll_message'] == expected_roll_message


def check_roll_success_metric(metric):
    assert metric.value == 1
    labels = metric.labels
    assert labels['sensor'] == 'random_discounts_metrics'
    assert labels['app'] == 'iphone'
    assert labels['zone'] == 'moscow'
    assert labels['coupon_series'] in ['series_id_0', 'series_id_1']
    assert labels['discount'] in ['11', '22']


@pytest.mark.experiments3(filename='random_discounts_exp.json')
async def test_roll_metrics(
        taxi_random_discounts,
        user_api,
        taxi_random_discounts_monitor,
        get_single_metric_by_label_values,
):

    uid = 'some_user_id'
    headers = dict(HEADERS)
    headers['X-Yandex-UID'] = uid

    async with metrics_helpers.MetricsCollector(
            taxi_random_discounts_monitor,
            sensor='random_discounts_metrics',
            labels={'zone': 'moscow'},
    ) as collector:
        response = await taxi_random_discounts.post(
            '/4.0/random-discounts/v1/roll',
            json={'zone': 'moscow'},
            headers=headers,
        )
    assert response.status == 200

    metric = collector.get_single_collected_metric()
    check_roll_success_metric(metric)


async def test_series_duplicates(
        taxi_random_discounts, user_api, pgsql, experiments3, load_json,
):
    exp = load_json('random_discounts_exp.json')
    exp['experiments'][0]['clauses'][0]['value']['discount_settings'][1][
        'discount_series'
    ] = 'series_id_0'
    experiments3.add_experiments_json(exp)
    await taxi_random_discounts.invalidate_caches()

    response = await taxi_random_discounts.post(
        '/4.0/random-discounts/v1/roll',
        json={'zone': 'moscow'},
        headers=HEADERS,
    )

    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['roll_result'] == 'failure'

    check_status(resp_body['current_status'], INACTIVE)

    check_random_discounts_db(
        pgsql, HEADERS['X-Yandex-UID'], resp_body['roll_result'],
    )


@pytest.mark.parametrize(
    ['uid', 'device_id', 'status', 'show_runaway_discount'],
    [
        pytest.param(
            'active_id',
            'active_dev',
            ACTIVE,
            True,
            id='with_runaway_discount_fields',
        ),
        pytest.param(
            'inactive_id',
            'inactive_dev',
            INACTIVE,
            False,
            id='without_runaway_discount_fields',
        ),
    ],
)
@pytest.mark.experiments3(filename='random_discounts_exp_runaway.json')
async def test_runaway_discount_status_handler(
        taxi_random_discounts,
        user_api,
        uid,
        device_id,
        status,
        show_runaway_discount,
):
    headers = dict(HEADERS)
    headers['X-Yandex-UID'] = uid
    headers['X-AppMetrica-DeviceId'] = device_id

    response = await taxi_random_discounts.post(
        '/4.0/random-discounts/v1/status',
        json={'zone': 'moscow'},
        headers=headers,
    )

    assert response.status_code == 200
    check_status(
        response.json(), status, show_runaway_discount=show_runaway_discount,
    )


@pytest.mark.now('2020-01-09T08:00:00+0000')
@pytest.mark.experiments3(filename='random_discounts_exp_runaway.json')
async def test_runaway_discount_roll_handler(
        taxi_random_discounts, user_api, pgsql,
):
    uid = 'some_user_id_1'
    headers = dict(HEADERS)
    headers['X-Yandex-UID'] = uid

    response = await taxi_random_discounts.post(
        '/4.0/random-discounts/v1/roll',
        json={'zone': 'moscow'},
        headers=headers,
    )

    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['roll_result'] == 'success'
    assert resp_body['discount'] in [11, 22]
    assert resp_body['result_messages'] == get_expected_messages(
        'roll_success_msg',
    )

    check_status(resp_body['current_status'], INACTIVE, True)
    check_random_discounts_db(pgsql, uid, 'success')

    status_response = await taxi_random_discounts.post(
        '/4.0/random-discounts/v1/status',
        json={'zone': 'moscow'},
        headers=headers,
    )

    check_status(status_response.json(), INACTIVE, True)


def build_yandex_uid_identity(uid):
    return {'type': 'yandex_uid', 'value': uid}


@pytest.mark.parametrize(
    'yandex_uid', ['full_statistics', 'recent_statistics'],
)
@pytest.mark.parametrize(
    ['user_stat_response', 'user_stat_error', 'expected_status'],
    [
        pytest.param(
            {'response_json': {'data': []}},
            'TimeoutError',
            DISABLED,
            id='statistics timeout',
        ),
        pytest.param(
            {'response_json': {'data': []}},
            'NetworkError',
            DISABLED,
            id='statistics network error',
        ),
        pytest.param(
            {'response_json': {'data': []}},
            None,
            DISABLED,
            id='empty response',
        ),
        pytest.param(
            {'response_params': {'value': 0, 'yandex_uid': DEFAULT_UID}},
            None,
            ACTIVE,
            id='user is newbie',
        ),
        pytest.param(
            {'response_params': {'value': 1, 'yandex_uid': DEFAULT_UID}},
            None,
            DISABLED,
            id='user is not newbie',
        ),
    ],
)
@pytest.mark.now('2020-01-09T08:00:00+0000')
@pytest.mark.experiments3(filename='user_statistics_params.json')
@pytest.mark.experiments3(filename='random_discounts_exp_newbie.json')
@pytest.mark.config(
    CLIENT_USER_STATISTICS_QOS={
        '__default__': {'__default__': {'attempts': 3, 'timeout-ms': 200}},
        'random-discounts': {
            '__default__': {'attempts': 1, 'timeout-ms': 200},
        },
    },
)
async def test_discount_for_newbie(
        taxi_random_discounts,
        user_api,
        mockserver,
        yandex_uid,
        user_stat_response,
        user_stat_error,
        expected_status,
        client_user_statistic,
):
    client_user_statistic.setup(
        response=user_stat_response, error=user_stat_error,
    )

    headers = dict(HEADERS)
    headers['X-Yandex-UID'] = yandex_uid

    response = await taxi_random_discounts.post(
        '/4.0/random-discounts/v1/status',
        json={'zone': 'moscow'},
        headers=headers,
    )

    if yandex_uid == 'full_statistics':
        assert client_user_statistic.mock_v1_orders.times_called == 1
        assert client_user_statistic.mock_v1_recent_orders.times_called == 0
    else:
        assert client_user_statistic.mock_v1_orders.times_called == 0
        assert client_user_statistic.mock_v1_recent_orders.times_called == 1

    assert response.status_code == 200
    check_status(response.json(), expected_status)
