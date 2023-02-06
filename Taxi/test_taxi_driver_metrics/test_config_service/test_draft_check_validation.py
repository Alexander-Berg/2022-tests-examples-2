import typing as tp

import pytest


FULL_RULE = {
    'name': 'test_audit_rule4',
    'zone': 'ekb',
    'type': 'tagging',
    'events': [{'topic': 'order', 'name': 'auto_reorder'}],
    'actions': [
        {
            'action': [
                {
                    'type': 'tagging',
                    'merge_policy': 'append',
                    'tags': [{'name': 'audit_tag_you_know', 'ttl': 600}],
                },
                {
                    'type': 'push',
                    'voice_over': True,
                    'code': 100,
                    'keyset': 'taximeter_messages',
                    'tanker_key_template': 'drivercheck.DriverFixWarning1',
                    'fullscreen': True,
                    'ttl': 300,
                },
            ],
        },
    ],
    'additional_params': {
        'events_to_trigger_cnt': '3',
        'events_period_sec': '3600',
    },
    'disabled': True,
    'service_name': 'driver-metrics',
}


def make_rule(**kwargs):
    return {
        **{
            'name': 'test_audit_rule4',
            'zone': 'ekb',
            'type': 'tagging',
            'events': [{'topic': 'order', 'name': 'auto_reorder'}],
            'actions': [
                {
                    'action': [
                        {
                            'type': 'tagging',
                            'merge_policy': 'append',
                            'tags': [
                                {'name': 'audit_tag_you_know', 'ttl': 600},
                            ],
                        },
                        {
                            'type': 'push',
                            'voice_over': True,
                            'code': 100,
                            'keyset': 'taximeter_messages',
                            'tanker_key_template': (
                                'drivercheck.DriverFixWarning1'
                            ),
                            'fullscreen': True,
                            'ttl': 300,
                        },
                    ],
                },
            ],
            'additional_params': {
                'events_to_trigger_cnt': '3',
                'events_period_sec': '3600',
            },
            'disabled': True,
            'service_name': 'driver-metrics',
        },
        **kwargs,
    }


async def check(
        taxi_driver_metrics, draft_check_handler: str, test_request: tp.Dict,
) -> tp.Tuple[int, tp.Dict]:
    result = await taxi_driver_metrics.post(
        draft_check_handler,
        json={'new': test_request},
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )

    return result.status, await result.json()


@pytest.mark.now('2016-12-31T00:00:00')
@pytest.mark.parametrize(
    'test_request, expected_status, expected_response, draft_check_handler',
    [
        pytest.param(
            FULL_RULE, 200, None, '/v1/config/draft/check', id='correct_rule',
        ),
        pytest.param(
            make_rule(
                additional_params={
                    'events_to_trigger_cnt': '3',
                    'events_period_sec': '3600',
                    'expr': 'incorrect python expr ! o.m.g',
                },
            ),
            400,
            {
                'code': 'wrong_data',
                'details': None,
                'message': (
                    'Config includes incorrect expr- incorrect '
                    'python expr ! o.m.g'
                ),
            },
            '/v1/config/draft/check',
            id='wrong_expr_in_global_scope',
        ),
        pytest.param(
            make_rule(
                events=[
                    {
                        'topic': 'order',
                        'name': 'auto_reorder',
                        'expr': 'incorrect python expr ! o.m.g',
                    },
                ],
            ),
            400,
            {
                'code': 'wrong_data',
                'details': None,
                'message': (
                    'Config includes incorrect expr- incorrect '
                    'python expr ! o.m.g'
                ),
            },
            '/v1/config/draft/check',
            id='wrong_expr_in_events',
        ),
        pytest.param(
            make_rule(
                actions=[
                    {
                        'expr': 'incorrect python expr ! o.m.g',
                        'action': [
                            {
                                'type': 'tagging',
                                'merge_policy': 'append',
                                'tags': [
                                    {'name': 'audit_tag_you_know', 'ttl': 600},
                                ],
                            },
                            {
                                'type': 'push',
                                'voice_over': True,
                                'code': 100,
                                'keyset': 'taximeter_messages',
                                'tanker_key_template': (
                                    'drivercheck.DriverFixWarning1'
                                ),
                                'fullscreen': True,
                                'ttl': 300,
                            },
                        ],
                    },
                ],
            ),
            400,
            {
                'code': 'wrong_data',
                'details': None,
                'message': (
                    'Config includes incorrect expr- incorrect '
                    'python expr ! o.m.g'
                ),
            },
            '/v1/config/draft/check',
            id='wrong_expr_in_actions',
        ),
        pytest.param(
            make_rule(
                additional_params={
                    'events_to_trigger_cnt': '3',
                    'events_period_sec': '3600',
                    'tags': 'incorrect python expr ! o.m.g',
                },
            ),
            400,
            {
                'code': 'wrong_data',
                'details': None,
                'message': (
                    'Config includes incorrect bool expression - '
                    '[\'incorrect python expr ! o.m.g\']'
                ),
            },
            '/v1/config/draft/check',
            id='wrong_tags_in_global_scope',
        ),
        pytest.param(
            make_rule(
                events=[
                    {
                        'topic': 'order',
                        'name': 'auto_reorder',
                        'tags': 'incorrect python expr ! o.m.g',
                    },
                ],
            ),
            400,
            {
                'code': 'wrong_data',
                'details': None,
                'message': (
                    'Config includes incorrect bool expression - '
                    '[\'incorrect python expr ! o.m.g\']'
                ),
            },
            '/v1/config/draft/check',
            id='wrong_tags_in_events',
        ),
        pytest.param(
            make_rule(
                actions=[
                    {
                        'tags': 'incorrect python expr ! o.m.g',
                        'action': [
                            {
                                'type': 'tagging',
                                'merge_policy': 'append',
                                'tags': [
                                    {'name': 'audit_tag_you_know', 'ttl': 600},
                                ],
                            },
                            {
                                'type': 'push',
                                'voice_over': True,
                                'code': 100,
                                'keyset': 'taximeter_messages',
                                'tanker_key_template': (
                                    'drivercheck.DriverFixWarning1'
                                ),
                                'fullscreen': True,
                                'ttl': 300,
                            },
                        ],
                    },
                ],
            ),
            400,
            {
                'code': 'wrong_data',
                'details': None,
                'message': (
                    'Config includes incorrect bool expression - '
                    '[\'incorrect python expr ! o.m.g\']'
                ),
            },
            '/v1/config/draft/check',
            id='wrong_tags_in_actions',
        ),
    ],
)
@pytest.mark.translations(
    taximeter_messages={
        'drivercheck.DriverFixWarning1Message': {
            'ru': 'title-ru',
            'fr': 'title-fr-',
            'en': 'title-en-',
        },
        'drivercheck.DriverFixWarning1Title': {
            'ru': 'message-ru-',
            'fr': 'message-fr-',
            'en': 'message-en-',
        },
    },
)
async def test_check_drafts_validation_base(
        taxi_driver_metrics,
        test_request,
        stq3_context,
        expected_status,
        expected_response,
        tags_service_mock,
        mockserver_clickhouse_host,
        draft_check_handler,
):
    tags_service_mock(tag_info={'is_financial': False})

    # Wrong format saving test
    status, body = await check(
        taxi_driver_metrics, draft_check_handler, test_request,
    )

    assert status == expected_status

    if status > 200:
        assert body == expected_response


@pytest.mark.now('2016-12-31T00:00:00')
@pytest.mark.parametrize(
    'test_request, expected_status, expected_response, draft_check_handler',
    [
        pytest.param(
            make_rule(
                actions=[
                    {
                        'action': [
                            {
                                'type': 'chatterbox_chat',
                                'macro_ids': [1, 2, 3],
                            },
                        ],
                    },
                ],
            ),
            400,
            {
                'code': 'actually_protected',
                'details': None,
                'message': (
                    'Rule contains chatterbox action, but not protected'
                ),
            },
            '/v1/config/draft/check',
            id='chatterbox_action_must_be_protected',
        ),
    ],
)
@pytest.mark.translations(
    taximeter_messages={
        'drivercheck.DriverFixWarning1Message': {
            'ru': 'title-ru',
            'fr': 'title-fr-',
            'en': 'title-en-',
        },
        'drivercheck.DriverFixWarning1Title': {
            'ru': 'message-ru-',
            'fr': 'message-fr-',
            'en': 'message-en-',
        },
    },
)
async def test_check_chatterbox_protected(
        taxi_driver_metrics,
        test_request,
        stq3_context,
        expected_status,
        expected_response,
        tags_service_mock,
        mockserver_clickhouse_host,
        draft_check_handler,
):
    tags_service_mock(tag_info={'is_financial': False})

    # Wrong format saving test
    status, body = await check(
        taxi_driver_metrics, draft_check_handler, test_request,
    )

    assert status == expected_status

    if status > 200:
        assert body == expected_response


@pytest.mark.now('2016-12-31T00:00:00')
@pytest.mark.parametrize(
    'test_request, expected_status, expected_response, draft_check_handler',
    [
        pytest.param(
            FULL_RULE,
            400,
            {
                'message': 'Config includes financial tags, but not protected',
                'details': None,
                'code': 'actually_protected',
            },
            '/v1/config/draft/check',
            id='contains_financial_tag',
        ),
    ],
)
@pytest.mark.translations(
    taximeter_messages={
        'drivercheck.DriverFixWarning1Message': {
            'ru': 'title-ru',
            'fr': 'title-fr-',
            'en': 'title-en-',
        },
        'drivercheck.DriverFixWarning1Title': {
            'ru': 'message-ru-',
            'fr': 'message-fr-',
            'en': 'message-en-',
        },
    },
)
async def test_check_financial_tags(
        taxi_driver_metrics,
        test_request,
        stq3_context,
        expected_status,
        expected_response,
        tags_service_mock,
        mockserver_clickhouse_host,
        draft_check_handler,
):
    tags_service_mock(tag_info={'is_financial': True})

    # Wrong format saving test
    status, body = await check(
        taxi_driver_metrics, draft_check_handler, test_request,
    )

    assert status == expected_status

    if status > 200:
        assert body == expected_response


@pytest.mark.now('2016-12-31T00:00:00')
@pytest.mark.parametrize(
    'test_request, expected_status, expected_response, draft_check_handler',
    [
        pytest.param(
            make_rule(
                actions=[
                    {
                        'action': [
                            {
                                'type': 'tagging',
                                'merge_policy': 'append',
                                'tags': [
                                    {'name': 'audit_tag_you_know', 'ttl': 600},
                                ],
                            },
                            {
                                'type': 'push',
                                'voice_over': True,
                                'code': 100,
                                'keyset': 'taximeter_messages',
                                'tanker_key_template': 'drivercheck.Bad',
                                'fullscreen': True,
                                'ttl': 300,
                            },
                        ],
                    },
                ],
            ),
            400,
            {
                'code': 'wrong_data',
                'details': None,
                'message': (
                    'Config includes incorrect tanker keys - '
                    '[\'tanker_key_template: '
                    'drivercheck.Bad, keyset: taximeter_messages\']'
                ),
            },
            '/v1/config/draft/check',
            id='wrong_tanker_key',
        ),
    ],
)
@pytest.mark.translations(
    taximeter_messages={
        'drivercheck.DriverFixWarning1Message': {
            'ru': 'title-ru',
            'fr': 'title-fr-',
            'en': 'title-en-',
        },
        'drivercheck.DriverFixWarning1Title': {
            'ru': 'message-ru-',
            'fr': 'message-fr-',
            'en': 'message-en-',
        },
    },
)
async def test_check_tanker_keys(
        taxi_driver_metrics,
        test_request,
        stq3_context,
        expected_status,
        expected_response,
        tags_service_mock,
        mockserver_clickhouse_host,
        draft_check_handler,
):
    tags_service_mock(tag_info={'is_financial': False})

    # Wrong format saving test
    status, body = await check(
        taxi_driver_metrics, draft_check_handler, test_request,
    )

    assert status == expected_status

    if status > 200:
        assert body == expected_response


@pytest.mark.now('2016-12-31T00:00:00')
@pytest.mark.parametrize(
    'test_request, expected_status, expected_response, draft_check_handler',
    [
        pytest.param(
            {'query': 'SELECT * FROM $order_metrics', 'type': 'fake'},
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for type: \'fake\' must be one of '
                        '[\'loyalty\', \'tagging\', '
                        '\'activity\', \'default\', '
                        '\'communications\', \'query\', '
                        '\'dispatch_length_thresholds\', \'blocking\', '
                        '\'stq_callback\', \'activity_blocking\']'
                    ),
                },
                'message': 'Some parameters are invalid',
            },
            '/v1/config/draft/check',
            id='unknown_action_type',
        ),
        pytest.param(
            {'type': 'activity'},
            400,
            {
                'code': 'wrong_type',
                'details': None,
                'message': (
                    'Config has wrong type activity, '
                    'only RuleType.QUERY allowed'
                ),
            },
            '/v1/config/query/draft/check',
            id='wrong_action_type',
        ),
    ],
)
@pytest.mark.translations(
    taximeter_messages={
        'drivercheck.DriverFixWarning1Message': {
            'ru': 'title-ru',
            'fr': 'title-fr-',
            'en': 'title-en-',
        },
        'drivercheck.DriverFixWarning1Title': {
            'ru': 'message-ru-',
            'fr': 'message-fr-',
            'en': 'message-en-',
        },
    },
)
async def test_check_clickhouse(
        taxi_driver_metrics,
        test_request,
        stq3_context,
        expected_status,
        expected_response,
        tags_service_mock,
        mockserver_clickhouse_host,
        draft_check_handler,
):
    tags_service_mock(tag_info={'is_financial': False})

    # Wrong format saving test
    status, body = await check(
        taxi_driver_metrics, draft_check_handler, test_request,
    )

    assert status == expected_status

    if status > 200:
        assert body == expected_response
