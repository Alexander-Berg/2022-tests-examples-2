# pylint: disable=too-many-lines,redefined-outer-name

import pytest

from tests_uantifraud import utils


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 1.0,
            'threshold': 50,
            'action': 'disable',
            'notify': True,
        },
        'eda_check': {
            'default': {
                'ratio': 1.0,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
            'test_rule1': {
                'ratio': 0.1,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
        },
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:unknown_verdict:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '7',
    ],
)
async def test_auto_fallback_base(taxi_uantifraud, mongodb, stq):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert not raw['enabled']


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 0.2,
            'threshold': 50,
            'action': 'disable',
            'notify': True,
        },
        'other_type': {
            'default': {
                'ratio': 1.0,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
            'test_rule1': {
                'ratio': 1.0,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
        },
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '50',
    ],
)
async def test_auto_fallback_default_rule_type_config(
        taxi_uantifraud, mongodb, stq,
):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert not raw['enabled']


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 1.0,
            'threshold': 50,
            'action': 'disable',
            'notify': True,
        },
        'eda_check': {
            'default': {
                'ratio': 0.2,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
            'other_rule': {
                'ratio': 1.0,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
        },
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '50',
    ],
)
async def test_auto_fallback_default_rule_name_config(
        taxi_uantifraud, mongodb, stq,
):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert not raw['enabled']


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 1.0,
            'threshold': 50,
            'action': 'disable',
            'notify': True,
        },
        'eda_check': {
            'default': {
                'ratio': 1.0,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
            'test_rule1': {
                'ratio': 0.1,
                'threshold': 75,
                'action': 'disable',
                'notify': True,
            },
        },
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:1569920401',
        'test_rule1:triggered',
        '70',
    ],
)
async def test_auto_fallback_threshold(taxi_uantifraud, mongodb, stq):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert raw['enabled']


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 0.00001,
            'threshold': 1,
            'action': 'nothing',
            'notify': True,
        },
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '70',
    ],
)
async def test_auto_fallback_autodisable_config(taxi_uantifraud, mongodb, stq):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert raw['enabled']


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 0.00001,
            'threshold': 1,
            'action': 'disable',
            'notify': True,
        },
        'eda_check': {
            'default': {
                'ratio': 0.00001,
                'threshold': 1,
                'action': 'disable',
                'notify': True,
            },
            'test_rule4': {
                'ratio': 0.00001,
                'threshold': 1,
                'action': 'to_test_mode',
                'notify': True,
            },
            'test_rule55': {
                'ratio': 0.00001,
                'threshold': 1,
                'action': 'to_test_mode',
                'notify': True,
            },
        },
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule2:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule2:triggered:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule3:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule4:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule4:triggered:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule55:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule55:triggered:1569920401',
        '70',
    ],
)
async def test_disabled_rules_send_notifications(taxi_uantifraud, stq):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    assert stq.antifraud_notifications_sending.times_called == 2
    first_call = stq.antifraud_notifications_sending.next_call()
    del first_call['kwargs']['log_extra']
    second_call = stq.antifraud_notifications_sending.next_call()
    del second_call['kwargs']['log_extra']
    assert utils.unordered_lists_are_equal(
        [first_call['kwargs'], second_call['kwargs']],
        [
            {
                'chat_id': 'some_chat',
                'text': 'Rule eda_check::test_rule1 is disabled!',
                'bot_id': 'some_bot',
            },
            {
                'chat_id': 'some_chat',
                'text': 'Rule eda_check::test_rule55 is moved to test mode!',
                'bot_id': 'some_bot',
            },
        ],
    )


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 0.00001,
            'threshold': 1,
            'action': 'disable',
            'notify': False,
        },
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule2:total:1569920401',
        '70',
    ],
)
async def test_disabled_rules_send_metrics_notify_disable(
        taxi_uantifraud, stq,
):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )

    assert not stq.antifraud_notifications_sending.has_calls


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 1.0,
            'threshold': 50,
            'action': 'disable',
            'notify': True,
        },
        'eda_check': {
            'default': {
                'ratio': 1.0,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
            'test_rule1': {
                'ratio': 0.1,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
        },
    },
    AFS_RULES_AUTO_FALLBACKS_SETTINGS={
        'default': {'period': 1000, 'consider_time': 2000},
        'eda_check': {'period': 30000, 'consider_time': 60000},
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165339',
        'test_rule1:total:1569920341',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '7',
    ],
)
async def test_auto_fallback_few_hash_keys(taxi_uantifraud, mongodb):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert raw['enabled']


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 1.0,
            'threshold': 50,
            'action': 'disable',
            'notify': True,
        },
        'eda_check': {
            'default': {
                'ratio': 1.0,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
            'test_rule1': {
                'ratio': 0.1,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
        },
    },
    AFS_RULES_AUTO_FALLBACKS_SETTINGS={
        'default': {'period': 1000, 'consider_time': 2000},
        'eda_check': {'period': 30000, 'consider_time': 60000},
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165338',
        'test_rule1:total:1569920281',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165339',
        'test_rule1:total:1569920340',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '7',
    ],
)
async def test_auto_fallback_few_hash_keys_test_key_time(
        taxi_uantifraud, mongodb, stq,
):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert not raw['enabled']


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 1.0,
            'threshold': 50,
            'action': 'disable',
            'notify': True,
        },
        'eda_check': {
            'default': {
                'ratio': 1.0,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
            'test_rule1': {
                'ratio': 0.1,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
        },
        'antifake': {
            'default': {
                'ratio': 1.0,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
            'test_rule2': {
                'ratio': 0.1,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
            'test_rule3': {
                'ratio': 0.2,
                'threshold': 50,
                'action': 'disable',
                'notify': True,
            },
        },
    },
    AFS_RULES_AUTO_FALLBACKS_SETTINGS={
        'default': {'period': 1000, 'consider_time': 2000},
        'eda_check': {'period': 30000, 'consider_time': 60000},
        'antifake': {'period': 500, 'consider_time': 1000},
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '7',
    ],
    ['set', 'js:antifake:rules_auto_fallback:last_time', '1569920400'],
    [
        'hset',
        'js:antifake:rules_auto_fallback:1569920400',
        'last_time',
        '15699204002',
    ],
    [
        'hset',
        'js:antifake:rules_auto_fallback:1569920400',
        'test_rule2:total:15699204001',
        '70',
    ],
    [
        'hset',
        'js:antifake:rules_auto_fallback:1569920400',
        'test_rule2:triggered:15699204001',
        '7',
    ],
    [
        'hset',
        'js:antifake:rules_auto_fallback:1569920400',
        'test_rule3:total:15699204002',
        '70',
    ],
    [
        'hset',
        'js:antifake:rules_auto_fallback:1569920400',
        'test_rule3:triggered:15699204002',
        '7',
    ],
)
@pytest.mark.parametrize(
    'enable_eda_check,enable_antifake,rules_enabled',
    [
        (True, False, [False, True, True]),
        (True, True, [False, False, True]),
        (False, True, [True, False, True]),
    ],
)
async def test_auto_fallback_multi(
        taxi_uantifraud,
        mongodb,
        enable_eda_check,
        enable_antifake,
        rules_enabled,
        stq,
):
    if enable_eda_check:
        await taxi_uantifraud.run_periodic_task(
            'check_and_disable_bad_rules_eda_check',
        )
    if enable_antifake:
        await taxi_uantifraud.run_periodic_task(
            'check_and_disable_bad_rules_antifake',
        )

    for i, rule_enabled in enumerate(rules_enabled):
        if rule_enabled:
            continue
        assert (
            mongodb.antifraud_rules.find_one(
                {'_id': 'test_rule' + str(i + 1)},
            )['enabled']
            == rule_enabled
        )


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 1.0,
            'threshold': 50,
            'action': 'disable',
            'notify': True,
        },
        'eda_check': {
            'default': {
                'ratio': 1.0,
                'threshold': 50,
                'action': 'to_test_mode',
                'notify': True,
            },
            'test_rule1': {
                'ratio': 0.1,
                'threshold': 50,
                'action': 'to_test_mode',
                'notify': True,
            },
        },
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:unknown_verdict:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '7',
    ],
)
async def test_auto_fallback_action_test_mode(taxi_uantifraud, mongodb, stq):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert raw['enabled'] and raw['test']

    assert stq.antifraud_notifications_sending.times_called == 1
    assert utils.dict_contains_sub_dict(
        stq.antifraud_notifications_sending.next_call()['kwargs'],
        {
            'chat_id': 'some_chat',
            'text': 'Rule eda_check::test_rule1 is moved to test mode!',
            'bot_id': 'some_bot',
        },
    )


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 1.0,
            'threshold': 50,
            'action': 'disable',
            'notify': True,
        },
        'eda_check': {
            'default': {
                'ratio': 1.0,
                'threshold': 50,
                'action': 'nothing',
                'notify': True,
            },
            'test_rule1': {
                'ratio': 0.1,
                'threshold': 50,
                'action': 'nothing',
                'notify': True,
            },
        },
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:unknown_verdict:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '7',
    ],
)
async def test_auto_fallback_action_nothing(taxi_uantifraud, mongodb, stq):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert raw['enabled'] and not raw['test']

    assert stq.antifraud_notifications_sending.times_called == 1
    assert utils.dict_contains_sub_dict(
        stq.antifraud_notifications_sending.next_call()['kwargs'],
        {
            'chat_id': 'some_chat',
            'text': 'Rule eda_check::test_rule1 is triggering too often!',
            'bot_id': 'some_bot',
        },
    )


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 0.1,
            'threshold': 50,
            'action': 'nothing',
            'notify': True,
        },
    },
    AFS_RULES_AUTO_FALLBACK_NOTIFICATION_SETTINGS={
        'default': [
            {'chat_id': 'some_chat1', 'bot_id': 'some_bot1'},
            {'chat_id': 'some_chat2', 'bot_id': 'some_bot2'},
        ],
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:unknown_verdict:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '7',
    ],
)
async def test_auto_fallback_send_few_alerts(taxi_uantifraud, mongodb, stq):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert raw['enabled'] and not raw['test']

    assert stq.antifraud_notifications_sending.times_called == 2
    assert utils.unordered_lists_are_equal(
        [
            utils.del_fields_from_dict(
                stq.antifraud_notifications_sending.next_call()['kwargs'],
                'log_extra',
            )
            for _ in range(2)
        ],
        [
            {
                'chat_id': 'some_chat1',
                'text': 'Rule eda_check::test_rule1 is triggering too often!',
                'bot_id': 'some_bot1',
            },
            {
                'chat_id': 'some_chat2',
                'text': 'Rule eda_check::test_rule1 is triggering too often!',
                'bot_id': 'some_bot2',
            },
        ],
    )


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 0.1,
            'threshold': 50,
            'action': 'nothing',
            'notify': True,
        },
    },
    AFS_RULES_AUTO_FALLBACK_NOTIFICATION_SETTINGS={
        'default': [
            {'chat_id': 'some_chat1', 'bot_id': 'some_bot1'},
            {'chat_id': 'some_chat2', 'bot_id': 'some_bot2'},
        ],
        'eda_check': {
            'default': [
                {'chat_id': 'some_chat3', 'bot_id': 'some_bot3'},
                {'chat_id': 'some_chat4', 'bot_id': 'some_bot4'},
                {'chat_id': 'some_chat5', 'bot_id': 'some_bot5'},
            ],
        },
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '7',
    ],
)
async def test_auto_fallback_send_alerts_rule_type(
        taxi_uantifraud, mongodb, stq,
):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert raw['enabled'] and not raw['test']

    assert stq.antifraud_notifications_sending.times_called == 3
    assert utils.unordered_lists_are_equal(
        [
            utils.del_fields_from_dict(
                stq.antifraud_notifications_sending.next_call()['kwargs'],
                'log_extra',
            )
            for _ in range(3)
        ],
        [
            {
                'chat_id': 'some_chat3',
                'text': 'Rule eda_check::test_rule1 is triggering too often!',
                'bot_id': 'some_bot3',
            },
            {
                'chat_id': 'some_chat4',
                'text': 'Rule eda_check::test_rule1 is triggering too often!',
                'bot_id': 'some_bot4',
            },
            {
                'chat_id': 'some_chat5',
                'text': 'Rule eda_check::test_rule1 is triggering too often!',
                'bot_id': 'some_bot5',
            },
        ],
    )


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 0.1,
            'threshold': 50,
            'action': 'nothing',
            'notify': True,
        },
    },
    AFS_RULES_AUTO_FALLBACK_NOTIFICATION_SETTINGS={
        'default': [
            {'chat_id': 'some_chat1', 'bot_id': 'some_bot1'},
            {'chat_id': 'some_chat2', 'bot_id': 'some_bot2'},
        ],
        'eda_check': {
            'default': [
                {'chat_id': 'some_chat3', 'bot_id': 'some_bot3'},
                {'chat_id': 'some_chat4', 'bot_id': 'some_bot4'},
                {'chat_id': 'some_chat5', 'bot_id': 'some_bot5'},
            ],
            'test_rule1': [{'chat_id': 'some_chat10', 'bot_id': 'some_bot10'}],
        },
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '7',
    ],
)
async def test_auto_fallback_send_alerts_rule_name(
        taxi_uantifraud, mongodb, stq,
):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert raw['enabled'] and not raw['test']

    assert stq.antifraud_notifications_sending.times_called == 1
    assert utils.dict_contains_sub_dict(
        stq.antifraud_notifications_sending.next_call()['kwargs'],
        {
            'chat_id': 'some_chat10',
            'text': 'Rule eda_check::test_rule1 is triggering too often!',
            'bot_id': 'some_bot10',
        },
    )


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 1.0,
            'threshold': 50,
            'action': 'disable',
            'notify': True,
        },
        'eda_check': {
            'default': {
                'ratio': 1.0,
                'threshold': 50,
                'action': 'nothing',
                'notify': True,
            },
            'test_rule1': {
                'ratio': 0.1,
                'threshold': 50,
                'action': 'nothing',
                'notify': True,
            },
        },
    },
    AFS_RULES_AUTO_FALLBACK_NOTIFICATION_SETTINGS={
        'default': [
            {'bot_id': 'some_bot', 'chat_id': 'some_chat', 'period': 30000},
        ],
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:unknown_verdict:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '7',
    ],
    [
        'set',
        'js:eda_check:rules_auto_fallback:test_rule1:some_chat:'
        'last_notification_time',
        '1569920400',
    ],
)
async def test_auto_fallback_little_interval(taxi_uantifraud, mongodb, stq):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert raw['enabled'] and not raw['test']

    assert stq.antifraud_notifications_sending.times_called == 0


@pytest.mark.config(
    AFS_RULES_AUTO_FALLBACK_ENABLED=True,
    AFS_RULES_AUTO_FALLBACKS_ACTION_SETTINGS={
        'default': {
            'ratio': 1.0,
            'threshold': 50,
            'action': 'disable',
            'notify': True,
        },
        'eda_check': {
            'default': {
                'ratio': 1.0,
                'threshold': 50,
                'action': 'nothing',
                'notify': True,
            },
            'test_rule1': {
                'ratio': 0.1,
                'threshold': 50,
                'action': 'nothing',
                'notify': True,
            },
        },
    },
    AFS_RULES_AUTO_FALLBACK_NOTIFICATION_SETTINGS={
        'default': [
            {'bot_id': 'some_bot', 'chat_id': 'some_chat', 'period': 1000},
        ],
    },
)
@pytest.mark.now('2019-10-01T09:00:08+0000')
@pytest.mark.redis_store(
    ['set', 'js:eda_check:rules_auto_fallback:last_time', '26165340'],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'last_time',
        '1569920401',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:total:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:unknown_verdict:1569920401',
        '70',
    ],
    [
        'hset',
        'js:eda_check:rules_auto_fallback:26165340',
        'test_rule1:triggered:1569920401',
        '7',
    ],
    [
        'set',
        'js:eda_check:rules_auto_fallback:test_rule1:some_chat:'
        'last_notification_time',
        '1569920400',
    ],
)
async def test_auto_fallback_interval_is_bigger_than_period(
        taxi_uantifraud, mongodb, stq,
):
    await taxi_uantifraud.run_periodic_task(
        'check_and_disable_bad_rules_eda_check',
    )
    raw = mongodb.antifraud_rules.find_one('test_rule1')

    assert raw['enabled'] and not raw['test']

    assert stq.antifraud_notifications_sending.times_called == 1
    assert utils.dict_contains_sub_dict(
        stq.antifraud_notifications_sending.next_call()['kwargs'],
        {
            'chat_id': 'some_chat',
            'text': 'Rule eda_check::test_rule1 is triggering too often!',
            'bot_id': 'some_bot',
        },
    )
