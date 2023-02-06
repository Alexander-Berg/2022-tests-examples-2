import copy

import pytest

from antifraud import utils
from antifraud.v1.eda import eda_common


def _make_old_response(frauder):
    return {'decision': 'frauder' if frauder else 'not_frauder'}


def test_check_base(taxi_antifraud, testpoint):
    eda_common.check_base(
        taxi_antifraud,
        testpoint,
        'v1/eda/check',
        eda_common.REQUEST_CHECKOUT,
        eda_common.NOT_FRAUDER_RESPONSE,
    )


def test_check_fraud_test(taxi_antifraud, testpoint):
    test_rules_triggered = []

    @testpoint('test_rule_triggered')
    def test_rule_triggered(json):
        test_rules_triggered.append(json['rule'])

    @testpoint('rule_triggered')
    def rule_triggered(_):
        pass

    response = taxi_antifraud.post(
        'v1/eda/check', json=eda_common.REQUEST_CHECKOUT,
    )
    assert response.status_code == 200
    assert response.json() == eda_common.NOT_FRAUDER_RESPONSE

    assert not rule_triggered.has_calls

    assert test_rules_triggered == ['test_fraud_rule1']


@pytest.mark.filldb(antifraud_rules='check_rule_args')
def test_check_fraud(taxi_antifraud, testpoint):
    eda_common.check_fraud(
        taxi_antifraud,
        testpoint,
        'v1/eda/check',
        eda_common.REQUEST_CHECKOUT,
        eda_common.FRAUDER_RESPONSE,
    )


@pytest.mark.config(
    AFS_ENTITY_MAPS={
        'bad_device_id': {
            'device_id_from_config1': 10,
            'device_id_from_config2': 20,
        },
        'key_from_config': {
            'value_from_config1': True,
            'value_from_config2': False,
        },
    },
)
def test_check_entity_map(taxi_antifraud, testpoint):
    @testpoint('first_rule_triggered')
    def first_rule_triggered(_):
        pass

    response = taxi_antifraud.post(
        'v1/eda/check', json=eda_common.REQUEST_CHECKOUT,
    )
    assert response.status_code == 200
    assert response.json() == eda_common.FRAUDER_RESPONSE

    assert first_rule_triggered.wait_call() == {
        '_': {'rule': 'entity_map_fraud_rule1'},
    }


_REDIS_KEY_PREFIX = 'js:eda_check:rules_auto_fallback:'


@pytest.mark.config(
    AFS_FAST_STORE_RULES_AUTO_FALLBACK_METRICS=False,
    AFS_RULES_AUTO_FALLBACK_METRICS_SEND=True,
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
def test_check_redis_metrics(taxi_antifraud, redis_store, now, testpoint):
    @testpoint('after_send_eda_metrics_for_auto_fallback')
    def after_send_metrics(_):
        pass

    response = taxi_antifraud.post(
        'v1/eda/check', json=eda_common.REQUEST_CHECKOUT,
    )
    assert response.status_code == 200

    after_send_metrics.wait_call()

    assert int(
        redis_store.get(_REDIS_KEY_PREFIX + 'last_time'),
    ) == utils.to_timestamp(now, utils.Units.MINUTES)

    redis_hash_key = _REDIS_KEY_PREFIX + str(
        utils.to_timestamp(now, utils.Units.MINUTES),
    )
    assert int(
        redis_store.hget(redis_hash_key, 'last_time'),
    ) == utils.to_timestamp(now, utils.Units.SECONDS)

    assert (
        int(
            redis_store.hget(
                redis_hash_key,
                'not_frauder_rule:total:'
                + str(utils.to_timestamp(now, utils.Units.SECONDS)),
            ),
        )
        == 1
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key,
                'frauder_rule:total:'
                + str(utils.to_timestamp(now, utils.Units.SECONDS)),
            ),
        )
        == 1
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key,
                'frauder_rule:triggered:'
                + str(utils.to_timestamp(now, utils.Units.SECONDS)),
            ),
        )
        == 1
    )


@pytest.mark.config(
    AFS_FAST_STORE_RULES_AUTO_FALLBACK_METRICS=False,
    AFS_RULES_AUTO_FALLBACK_METRICS_SEND=True,
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
def test_check_redis_metrics_multi(
        taxi_antifraud, redis_store, now, testpoint,
):
    @testpoint('after_send_eda_metrics_for_auto_fallback')
    def after_send_metrics(_):
        pass

    repeats = 3
    for _ in range(repeats):
        response = taxi_antifraud.post(
            'v1/eda/check', json=eda_common.REQUEST_CHECKOUT,
        )
        assert response.status_code == 200

    for _ in range(repeats):
        after_send_metrics.wait_call()

    assert int(
        redis_store.get(_REDIS_KEY_PREFIX + 'last_time'),
    ) == utils.to_timestamp(now, utils.Units.MINUTES)

    redis_hash_key = _REDIS_KEY_PREFIX + str(
        utils.to_timestamp(now, utils.Units.MINUTES),
    )
    assert int(
        redis_store.hget(redis_hash_key, 'last_time'),
    ) == utils.to_timestamp(now, utils.Units.SECONDS)

    assert (
        int(
            redis_store.hget(
                redis_hash_key,
                'not_frauder_rule:total:'
                + str(utils.to_timestamp(now, utils.Units.SECONDS)),
            ),
        )
        == repeats
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key,
                'frauder_rule:total:'
                + str(utils.to_timestamp(now, utils.Units.SECONDS)),
            ),
        )
        == repeats
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key,
                'frauder_rule:triggered:'
                + str(utils.to_timestamp(now, utils.Units.SECONDS)),
            ),
        )
        == repeats
    )


@pytest.mark.config(
    AFS_FAST_STORE_RULES_AUTO_FALLBACK_METRICS=False,
    AFS_RULES_AUTO_FALLBACK_METRICS_SEND=True,
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
def test_check_redis_different_time(
        taxi_antifraud, redis_store, now, testpoint,
):
    @testpoint('after_send_eda_metrics_for_auto_fallback')
    def after_send_metrics(_):
        pass

    response = taxi_antifraud.post(
        'v1/eda/check', json=eda_common.REQUEST_CHECKOUT,
    )
    assert response.status_code == 200
    after_send_metrics.wait_call()

    redis_hash_key_old_now = _REDIS_KEY_PREFIX + str(
        utils.to_timestamp(now, utils.Units.MINUTES),
    )

    old_now = now

    now = now.replace(minute=1)
    taxi_antifraud.tests_control(now=now, invalidate_caches=False)

    response = taxi_antifraud.post(
        'v1/eda/check', json=eda_common.REQUEST_CHECKOUT,
    )
    assert response.status_code == 200
    after_send_metrics.wait_call()

    assert int(
        redis_store.get(_REDIS_KEY_PREFIX + 'last_time'),
    ) == utils.to_timestamp(now, utils.Units.MINUTES)
    redis_hash_key_new_now = _REDIS_KEY_PREFIX + str(
        utils.to_timestamp(now, utils.Units.MINUTES),
    )

    assert int(
        redis_store.hget(redis_hash_key_new_now, 'last_time'),
    ) == utils.to_timestamp(now, utils.Units.SECONDS)

    assert (
        int(
            redis_store.hget(
                redis_hash_key_old_now,
                'not_frauder_rule:total:'
                + str(utils.to_timestamp(old_now, utils.Units.SECONDS)),
            ),
        )
        == 1
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key_old_now,
                'frauder_rule:total:'
                + str(utils.to_timestamp(old_now, utils.Units.SECONDS)),
            ),
        )
        == 1
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key_old_now,
                'frauder_rule:triggered:'
                + str(utils.to_timestamp(old_now, utils.Units.SECONDS)),
            ),
        )
        == 1
    )

    assert (
        int(
            redis_store.hget(
                redis_hash_key_new_now,
                'not_frauder_rule:total:'
                + str(utils.to_timestamp(now, utils.Units.SECONDS)),
            ),
        )
        == 1
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key_new_now,
                'frauder_rule:total:'
                + str(utils.to_timestamp(now, utils.Units.SECONDS)),
            ),
        )
        == 1
    )
    assert (
        int(
            redis_store.hget(
                redis_hash_key_new_now,
                'frauder_rule:triggered:'
                + str(utils.to_timestamp(now, utils.Units.SECONDS)),
            ),
        )
        == 1
    )


@pytest.mark.config(
    AFS_FAST_STORE_RULES_AUTO_FALLBACK_METRICS=False,
    AFS_RULES_AUTO_FALLBACK_METRICS_SEND=True,
)
@pytest.mark.redis_store(
    [
        'hset',
        _REDIS_KEY_PREFIX + '26165340',
        'frauder_rule:total:1569920408',
        '45',
    ],
    ['set', _REDIS_KEY_PREFIX + 'last_time', '26165340'],
    ['hset', _REDIS_KEY_PREFIX + '26165340', 'last_time', '1569920408'],
)
@pytest.mark.now('2019-10-01T08:00:08+0000')
def test_check_redis_time_less(taxi_antifraud, redis_store, now, testpoint):
    @testpoint('after_send_eda_metrics_for_auto_fallback')
    def after_send_metrics(_):
        pass

    response = taxi_antifraud.post(
        'v1/eda/check', json=eda_common.REQUEST_CHECKOUT,
    )
    assert response.status_code == 200
    after_send_metrics.wait_call()

    max_hash_time = 26165340
    max_key_time = 1569920408

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


def test_check_new_schema_enabled_new_js_not_frauder(
        taxi_antifraud, testpoint,
):
    eda_common.check_new_schema(
        taxi_antifraud,
        testpoint,
        eda_common.REQUEST_CHECKOUT,
        {'decision': 'not_frauder'},
        {'passed': [{'rule': 'fraud_rule1', 'decision': 'not_frauder'}]},
    )


def test_check_new_schema_enabled_new_js_suspect(taxi_antifraud, testpoint):
    eda_common.check_new_schema(
        taxi_antifraud,
        testpoint,
        eda_common.REQUEST_CHECKOUT,
        {'decision': 'suspect'},
        {'triggered': [{'rule': 'fraud_rule1', 'decision': 'suspect'}]},
    )


def test_check_new_schema_enabled_new_js_frauder(taxi_antifraud, testpoint):
    eda_common.check_new_schema(
        taxi_antifraud,
        testpoint,
        eda_common.REQUEST_CHECKOUT,
        {'decision': 'frauder'},
        {'triggered': [{'rule': 'fraud_rule1', 'decision': 'frauder'}]},
    )


def test_check_new_schema_enabled_chain1(taxi_antifraud, testpoint):
    eda_common.check_new_schema(
        taxi_antifraud,
        testpoint,
        eda_common.REQUEST_CHECKOUT,
        {'decision': 'suspect'},
        {
            'passed': [
                {'rule': 'fraud_rule_not_frauder', 'decision': 'not_frauder'},
            ],
            'triggered': [
                {'rule': 'fraud_rule_suspect', 'decision': 'suspect'},
            ],
        },
    )


def test_check_new_schema_enabled_chain2(taxi_antifraud, testpoint):
    eda_common.check_new_schema(
        taxi_antifraud,
        testpoint,
        eda_common.REQUEST_CHECKOUT,
        {'decision': 'frauder'},
        {
            'passed': [
                {'rule': 'fraud_rule_not_frauder', 'decision': 'not_frauder'},
            ],
            'triggered': [
                {'rule': 'fraud_rule_suspect', 'decision': 'suspect'},
                {'rule': 'fraud_rule_frauder', 'decision': 'frauder'},
            ],
        },
    )


@pytest.mark.config(AFS_EDA_SAVE_REQUEST=True)
def test_check_save_request(taxi_antifraud, testpoint, db, now):
    @testpoint('after_save_request')
    def after_save_request(_):
        pass

    response = taxi_antifraud.post(
        'v1/eda/check', json=eda_common.REQUEST_CHECKOUT,
    )
    assert response.status_code == 200
    assert response.json() == eda_common.NOT_FRAUDER_RESPONSE

    assert after_save_request.wait_call()

    saved_request = db.antifraud_eda_check_requests.find_one(
        {'_id': eda_common.REQUEST_CHECKOUT['order_nr']},
    )

    assert now.replace(microsecond=0) == saved_request['created']

    r = copy.deepcopy(eda_common.REQUEST_CHECKOUT)
    del r['appmetric_device_id']
    del r['appmetric_uuid']

    assert r == saved_request['request']
    assert eda_common.NOT_FRAUDER_RESPONSE == saved_request['response']


@pytest.mark.config(AFS_EDA_SCORE_PHONE=True)
def test_send_phone_to_scoring(taxi_antifraud, mockserver):
    @mockserver.json_handler('/uantifraud/v1/phone_scoring')
    def mock_uantifraud_phone_scoring(request):
        assert request.json == {
            'user_phone': eda_common.REQUEST_CHECKOUT['user_phone'],
        }
        # return {}

    response = taxi_antifraud.post(
        'v1/eda/check', json=eda_common.REQUEST_CHECKOUT,
    )
    assert response.status_code == 200
    assert mock_uantifraud_phone_scoring.wait_call()


@pytest.mark.parametrize(
    'order_nr,rule',
    [
        ('order_nr1', 'fraud_rule1'),
        ('100500', 'default_rule'),
        ('100500100500', 'fraud_rule1'),
        ('-100500', 'fraud_rule1'),
        ('-100500100500', 'fraud_rule1'),
    ],
)
def test_check_auto_entity_map_lazy_access(
        taxi_antifraud, testpoint, order_nr, rule,
):
    @testpoint('first_rule_triggered')
    def first_rule_triggered(_):
        pass

    response = taxi_antifraud.post(
        'v1/eda/check',
        json={**eda_common.REQUEST_CHECKOUT, **{'order_nr': order_nr}},
    )
    assert response.status_code == 200
    assert response.json() == eda_common.FRAUDER_RESPONSE

    assert first_rule_triggered.wait_call() == {'_': {'rule': rule}}
