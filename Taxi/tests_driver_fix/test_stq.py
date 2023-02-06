import json

import pytest

from tests_driver_fix import common


def _get_current_subvention_rule(profile_payment_type_restrictions='online'):
    return (
        """{{
"tariff_zones": ["moscow"],
"status": "enabled",
"start": "2019-01-01T00:00:00.000000+03:00",
"end": "2019-01-10T23:59:00.000000+03:00",
"type": "driver_fix",
"is_personal": false,
"taxirate": "TAXIRATE-01",
"subvention_rule_id": "subvention_rule_id",
"cursor": "cursor",
"tags": ["driver-fix_tags"],
"time_zone": {{"id": "Europe/Moscow", "offset": "+03:00"}},
"currency": "RUB",
"updated": "2019-01-01T00:00:00.000000+00:00",
"visible_to_driver": true,
"week_days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
"hours": [],
"log": [],
"geoareas": ["msk-driver-fix-poly"],
"tariff_classes": ["econom"],
"profile_payment_type_restrictions": "{pt}",
"profile_tariff_classes": ["econom", "business"],
"rates": [
    {{"week_day": "mon", "start": "00:00", "rate_per_minute": "5.0"}},
    {{"week_day": "mon", "start": "05:00", "rate_per_minute": "5.5"}},
    {{"week_day": "mon", "start": "13:00", "rate_per_minute": "6.0"}},
    {{"week_day": "tue", "start": "01:02", "rate_per_minute": "4.8"}},
    {{"week_day": "wed", "start": "12:00", "rate_per_minute": "4.5"}},
    {{"week_day": "thu", "start": "12:00", "rate_per_minute": "4.5"}},
    {{"week_day": "fri", "start": "12:00", "rate_per_minute": "4.5"}},
    {{"week_day": "sat", "start": "12:00", "rate_per_minute": "4.5"}},
    {{"week_day": "sun", "start": "12:00", "rate_per_minute": "4.5"}}
],
"commission_rate_if_fraud": "90.90"
}}""".format(
            pt=profile_payment_type_restrictions,
        )
    )


def _mode_info(request, current_mode, mode_settings):
    assert request.args['driver_profile_id'] == 'driver_uuid'
    assert request.args['park_id'] == 'park_id_0'
    if current_mode:
        result = {
            'mode': {
                'name': current_mode,
                'started_at': '2019-05-01T08:00:00+0300',
            },
        }
        if mode_settings:
            result['mode']['features'] = [
                {'name': 'driver_fix', 'settings': mode_settings},
                {'name': 'reposition'},
            ]
        return result
    return {
        'mode': {'name': 'orders', 'started_at': '1970-01-01T00:00:00+0000'},
    }


@pytest.mark.config(DRIVER_FIX_STQ_ENABLED={'enabled': False})
async def test_stq_disabled(stq, stq_runner):
    kwargs = {
        'park_id': 'park_id_0',
        'driver_profile_id': 'driver_uuid',
        'reschedule_ms': 2000,
        'mode_settings': (
            '{"rule_id": "id", "shift_close_time": "00:00:00+03:00"}'
        ),
        'check_settings': f"""{{
                "check_settings": {{
                    "check_type": "subvention_rule",
                    "subvention_rule_data": {_get_current_subvention_rule()}
                }}
            }}""",
    }
    await stq_runner.driver_fix.call(
        task_id='sample_task', args=[1, 2, 3], kwargs=kwargs,
    )
    assert stq.driver_fix.times_called == 0


@pytest.mark.now('2019-05-01T09:00:00+0000')
@pytest.mark.config(
    DRIVER_FIX_STQ_ENABLED={'enabled': True},
    DRIVER_FIX_STQ_SIMILAR_RULE_RESET_ON_FAIL=True,
    DRIVER_FIX_STQ_SUBVENTION_RULE_USE_PAYMENT_TYPE_RESTRICITONS=True,
)
@pytest.mark.parametrize(
    'rescheduled, current_mode, mode_settings, current_rule_data,'
    'intask_rule_data, new_rule_present, mode_set_response_code,'
    'mode_reset_response_code',
    (
        (
            False,
            None,
            None,
            None,
            _get_current_subvention_rule(),
            False,
            None,
            None,
        ),
        (
            False,
            'orders',
            None,
            None,
            _get_current_subvention_rule(),
            False,
            None,
            None,
        ),
        (
            False,
            'driver_fix',
            {'rule_id': 'another_id', 'shift_close_time': '00:00:00+03:00'},
            None,
            _get_current_subvention_rule(),
            False,
            None,
            None,
        ),
        (
            False,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            None,
            _get_current_subvention_rule(),
            False,
            None,
            200,
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            None,
            _get_current_subvention_rule(),
            False,
            None,
            400,
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            None,
            _get_current_subvention_rule(),
            False,
            None,
            500,
        ),
        (
            False,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            {'status': 'disabled'},
            _get_current_subvention_rule(),
            False,
            None,
            200,
        ),
        (
            False,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            {'status': 'disabled'},
            _get_current_subvention_rule(),
            True,
            200,
            None,
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            {'status': 'disabled'},
            _get_current_subvention_rule(),
            True,
            500,
            None,
        ),
        (
            False,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            {'end': '2019-05-01T11:00:00.000000+03:00'},
            _get_current_subvention_rule(),
            False,
            None,
            200,
        ),
        (
            False,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            {'end': '2019-05-01T11:00:00.000000+03:00'},
            _get_current_subvention_rule(),
            True,
            200,
            None,
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            {'end': '2019-05-01T11:00:00.000000+03:00'},
            _get_current_subvention_rule(),
            True,
            500,
            None,
        ),
        (
            False,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            {'end': '2019-05-01T11:00:00.000000+03:00'},
            _get_current_subvention_rule(),
            True,
            400,  # no chance to subscribe, trying to reset mode
            200,  # reset mode succeded, finishing
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            {'end': '2019-05-01T11:00:00.000000+03:00'},
            _get_current_subvention_rule(),
            True,
            400,  # no chance to subscribe, trying to reset mode
            500,  # reset mode failed, let's try to reshedule
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            {'end': '2019-05-01T11:00:00.000000+03:00'},
            _get_current_subvention_rule(),
            True,
            400,  # no chance to subscribe, trying to reset mode
            400,  # reset mode unable, let's try to reshedule
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            {'end': '2019-05-01T13:00:00.000000+03:00'},
            _get_current_subvention_rule(),
            False,
            None,
            None,
        ),
        (
            False,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            {'end': '2019-05-01T11:00:00.000000+03:00'},
            _get_current_subvention_rule(
                profile_payment_type_restrictions='any',
            ),
            True,
            200,
            None,
        ),
    ),
)
async def test_subvention_rule(
        mockserver,
        stq,
        stq_runner,
        taxi_config,
        rescheduled,
        current_mode,
        mode_settings,
        current_rule_data,
        intask_rule_data,
        new_rule_present,
        mode_set_response_code,
        mode_reset_response_code,
):
    if current_mode:
        data = {
            'driver': {'park_id': 'park_id_0', 'driver_id': 'uuid'},
            'mode': current_mode,
        }
        if mode_settings:
            data['settings'] = mode_settings

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/set')
    def _driver_mode_subscription_mode_set(request):
        data = json.loads(request.get_data())
        assert data['driver_profile_id'] == 'driver_uuid'
        assert data['park_id'] == 'park_id_0'
        assert data['mode_id'] == 'driver_fix'
        settings = data['mode_settings']
        assert settings['rule_id'] == 'new_id'
        assert (
            settings['shift_close_time'] == mode_settings['shift_close_time']
        )
        if mode_set_response_code and mode_set_response_code != 200:
            return mockserver.make_response(
                json={'code': 'some_code', 'message': 'some_message'},
                status=mode_set_response_code,
            )
        return {
            'active_mode': 'driver_fix',
            'active_mode_type': 'driver_fix',
            'active_since': '2019-05-01T12:00:00+0300',
        }

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/reset')
    def _driver_mode_subscription_mode_reset(request):
        data = json.loads(request.get_data())
        assert data['driver_profile_id'] == 'driver_uuid'
        assert data['park_id'] == 'park_id_0'
        assert data['reason'] == 'driver_fix_expired'
        if mode_reset_response_code and mode_reset_response_code != 200:
            return mockserver.make_response(
                json={'code': 'some_code', 'message': 'some_message'},
                status=mode_reset_response_code,
            )
        return {
            'active_mode': 'orders',
            'active_mode_type': 'orders',
            'active_since': '2019-05-01T09:00:00+0000',
        }

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _driver_mode_subscription_mode_info(request):
        return _mode_info(request, current_mode, mode_settings)

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _billing_subventions_rules_select(request):
        data = json.loads(request.get_data())
        if 'rule_ids' in data:
            # get current rule:
            assert 'subvention_rule_id' in data['rule_ids']
            if current_rule_data is not None:
                current_rule = dict(common.DEFAULT_DRIVER_FIX_RULE)
                current_rule.update(current_rule_data)
                return {'subventions': [current_rule]}
        else:
            rule = common.DEFAULT_DRIVER_FIX_RULE
            assert data['tariff_zone'] == rule['tariff_zones'][0]
            assert (
                data['profile_tariff_classes']
                == rule['profile_tariff_classes']
            )
            assert (
                data['payment_type_restrictions']
                == rule['profile_payment_type_restrictions']
            )
            assert data['types'] == [rule['type']]
            assert data['status'] == 'enabled'
            assert data['profile_tags'] == rule['tags']
            assert data['is_personal'] == rule['is_personal']
            time_range = data['time_range']
            assert time_range['start'] == '2019-05-01T09:00:00+00:00'
            assert time_range['end'] == '2019-05-01T09:00:01+00:00'
            if new_rule_present:
                new_rule = dict(common.DEFAULT_DRIVER_FIX_RULE)
                new_rule['subvention_rule_id'] = 'new_id'
                new_rule['start'] = '2019-05-01T09:00:00+00:00'
                new_rule['end'] = '2019-05-01T10:00:00+00:00'
                return {'subventions': [new_rule]}
        return {'subventions': []}

    kwargs = {
        'park_id': 'park_id_0',
        'driver_profile_id': 'driver_uuid',
        'reschedule_ms': 2000,
        'mode_settings': """{
            "rule_id": "subvention_rule_id",
            "shift_close_time": "00:00:00+03:00"
        }""",
        'check_settings': f"""{{
                "check_settings": {{
                    "check_type": "subvention_rule",
                    "subvention_rule_data": {intask_rule_data}
                }}
            }}""",
    }
    await stq_runner.driver_fix.call(
        task_id='sample_task', args=[1, 2, 3], kwargs=kwargs,
    )
    if rescheduled:
        assert stq.driver_fix.times_called == 1
    else:
        assert stq.driver_fix.times_called == 0

    assert _driver_mode_subscription_mode_info.times_called == 1
    if mode_reset_response_code:
        assert mode_set_response_code == 400 or not new_rule_present
        if mode_reset_response_code == 500:
            assert _driver_mode_subscription_mode_reset.times_called == 3
        else:
            assert _driver_mode_subscription_mode_reset.times_called == 1
    else:
        assert _driver_mode_subscription_mode_reset.times_called == 0


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.config(DRIVER_FIX_STQ_ENABLED={'enabled': True})
@pytest.mark.parametrize(
    'add_tags, remove_tags, tags_fail_on_add',
    (
        ([], [], None),
        (['t1'], [], None),
        (['t1'], [], True),
        (['t1'], [], False),
        ([], ['t1'], None),
        ([], ['t1'], True),
        ([], ['t1'], False),
        (['t1'], ['t2'], None),
        (['t1'], ['t2'], True),
        (['t1'], ['t2'], False),
    ),
)
async def test_online_time_tags(
        mockserver, stq, stq_runner, add_tags, remove_tags, tags_fail_on_add,
):
    add_tags_str = json.dumps(add_tags)
    remove_tags_str = json.dumps(remove_tags)
    kwargs = {
        'park_id': 'park_id_0',
        'driver_profile_id': 'driver_uuid',
        'reschedule_ms': 2000,
        'check_settings': f"""{{
                "check_settings": {{
                    "check_type": "online_time_tags",
                    "add_tags": {add_tags_str},
                    "remove_tags": {remove_tags_str}
                }}
            }}""",
    }
    send_tags_call_count = 0

    @mockserver.json_handler('/tags/v1/upload')
    def _v1_upload(request):
        nonlocal send_tags_call_count
        send_tags_call_count += 1
        data = json.loads(request.get_data())
        assert data['merge_policy'] in ['append', 'remove']
        tags = data['tags']
        if data['merge_policy'] == 'append':
            assert [t['name'] for t in tags] == add_tags
            if tags_fail_on_add:
                return None
        else:
            assert [t['name'] for t in tags] == remove_tags
            if tags_fail_on_add is False:
                return None
        return {'status': 'ok'}

    await stq_runner.driver_fix.call(
        task_id='sample_task', args=[1, 2, 3], kwargs=kwargs,
    )
    if not tags_fail_on_add:
        assert send_tags_call_count == bool(add_tags) + bool(remove_tags)
        assert stq.driver_fix.times_called == (
            (tags_fail_on_add is False) and bool(remove_tags)
        )
    else:
        assert send_tags_call_count == 1
        assert stq.driver_fix.times_called == bool(add_tags)


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.config(DRIVER_FIX_STQ_ENABLED={'enabled': True})
@pytest.mark.parametrize(
    'rescheduled, current_mode, mode_settings, current_tags, required_tags,'
    'mode_set_fails',
    (
        (False, None, None, [], [], False),
        (False, 'orders', None, [], [], False),
        (
            False,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            [],
            [],
            False,
        ),
        (
            False,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            ['another_tag1', 'another_tag2'],
            ['driver-fix_tags'],
            False,
        ),
        (
            False,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            ['another_tag1', 'another_tag2'],
            ['driver-fix_tags', 'driver-fix_tags2'],
            False,
        ),
        (
            False,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            ['another_tag1', 'another_tag2'],
            ['another_tag2', 'driver-fix_tags'],
            False,
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            ['another_tag1', 'another_tag2'],
            ['driver-fix_tags'],
            True,
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            ['another_tag1', 'another_tag2'],
            ['driver-fix_tags', 'driver-fix_tags2'],
            True,
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            ['another_tag1', 'another_tag2'],
            ['another_tag2', 'driver-fix_tags'],
            True,
        ),
        (
            False,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            [],
            ['driver-fix_tags'],
            False,
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            [],
            ['driver-fix_tags'],
            True,
        ),
        (
            False,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            [],
            ['driver-fix_tags', 'driver-fix_tags2'],
            False,
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            [],
            ['driver-fix_tags', 'driver-fix_tags2'],
            True,
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            ['another_tag1', 'driver-fix_tags'],
            ['driver-fix_tags'],
            False,
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            ['another_tag1', 'driver-fix_tags', 'driver-fix_tags2'],
            ['driver-fix_tags', 'driver-fix_tags2'],
            False,
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            ['driver-fix_tags'],
            ['driver-fix_tags'],
            False,
        ),
        (
            True,
            'driver_fix',
            {
                'rule_id': 'subvention_rule_id',
                'shift_close_time': '00:00:00+03:00',
            },
            ['driver-fix_tags', 'driver-fix_tags2'],
            ['driver-fix_tags', 'driver-fix_tags2'],
            False,
        ),
    ),
)
async def test_required_tags(
        mockserver,
        stq,
        stq_runner,
        taxi_config,
        rescheduled,
        current_mode,
        mode_settings,
        current_tags,
        required_tags,
        mode_set_fails,
        driver_tags_mocks,
):
    driver_tags_mocks.set_tags_info('park_id_0', 'driver_uuid', current_tags)

    if current_mode:
        data = {
            'driver': {'park_id': 'park_id_0', 'driver_id': 'uuid'},
            'mode': current_mode,
        }
        if mode_settings:
            data['settings'] = mode_settings

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/set')
    def _driver_mode_subscription_mode_set(request):
        match_count = 0
        for required_tag in required_tags:
            match_count += required_tag in current_tags
        assert match_count != len(required_tags)
        data = json.loads(request.get_data())
        assert data['driver_profile_id'] == 'driver_uuid'
        assert data['park_id'] == 'park_id_0'
        assert data['mode_id'] == 'orders'
        assert 'mode_settings' not in data
        if mode_set_fails:
            return {}
        return {
            'active_mode': 'orders',
            'active_mode_type': 'orders',
            'active_since': '2019-05-01T12:00:00+0300',
        }

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _driver_mode_subscription_mode_info(request):
        return _mode_info(request, current_mode, mode_settings)

    required_tags_str = json.dumps(required_tags)
    kwargs = {
        'park_id': 'park_id_0',
        'driver_profile_id': 'driver_uuid',
        'reschedule_ms': 2000,
        'mode_settings': """{
            "rule_id": "subvention_rule_id",
            "shift_close_time": "00:00:00+03:00"
        }""",
        'check_settings': f"""{{
                "check_settings": {{
                    "check_type": "required_tags",
                    "required_tags": {required_tags_str}
                }}
            }}""",
    }
    await stq_runner.driver_fix.call(
        task_id='sample_task', args=[1, 2, 3], kwargs=kwargs,
    )
    if rescheduled:
        assert stq.driver_fix.times_called == 1
    else:
        assert stq.driver_fix.times_called == 0

    assert driver_tags_mocks.has_calls() == bool(required_tags)

    if required_tags and mode_settings:
        assert _driver_mode_subscription_mode_info.times_called == 1
