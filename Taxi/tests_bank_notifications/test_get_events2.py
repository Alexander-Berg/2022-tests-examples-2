import pytest

import tests_bank_notifications.defaults as defaults
import tests_bank_notifications.exp3_helpers as exp3_helpers
import tests_bank_notifications.get_events_common as get_events_common


async def test_ok_one_event_with_experiment_and_defaults_group(
        taxi_bank_notifications, mockserver, pgsql, experiments3,
):
    event = get_events_common.insert_events(
        pgsql=pgsql, experiment='test_exp',
    )[0]

    exp_name = 'test_exp'
    exp_value = {'title': defaults.TITLE, 'action': 'dont remove me'}
    experiments3.add_experiment(
        **exp3_helpers.create_experiment(
            name=exp_name,
            consumers=['bank_notifications/events'],
            predicates=[exp3_helpers.create_true_predicate()],
            value=exp_value,
        ),
    )

    await taxi_bank_notifications.invalidate_caches()

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == [
        {
            'title': 'Тестовый заголовок',
            'description': 'Тестовое описание',
            'action': exp_value['action'],
            'event_type': defaults.EVENT_TYPE,
            'event_id': event.event_id,
            'themes': defaults.DEFAULT_THEMES,
            'is_closable': True,
        },
    ]
    assert 'cursor' not in resp_json


async def test_ok_test_no_cursor_if_no_matched_exp(
        taxi_bank_notifications, mockserver, pgsql, experiments3,
):
    exp_name = 'test_exp'
    get_events_common.insert_events(pgsql=pgsql, count=5, experiment=exp_name)

    exp_value = {
        'title': defaults.TITLE,
        'description': defaults.DESCRIPTION,
        'action': 'dont remove me',
    }
    experiments3.add_experiment(
        **exp3_helpers.create_experiment(
            name=exp_name,
            consumers=['bank_notifications/events'],
            predicates=[exp3_helpers.create_false_predicate()],
            value=exp_value,
        ),
    )

    await taxi_bank_notifications.invalidate_caches()

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == []
    assert 'cursor' not in resp_json


async def test_ok_test_get_matched_and_matched_are_the_only(
        taxi_bank_notifications, mockserver, pgsql, experiments3,
):
    exp_name_false = 'false_exp'
    exp_name_true = 'true_exp'
    get_events_common.insert_events(
        pgsql=pgsql, count=2, experiment=exp_name_false,
    )
    expected_events = get_events_common.insert_events(
        pgsql=pgsql, count=3, experiment=exp_name_true,
    )

    exp_value = {
        'title': defaults.TITLE,
        'description': defaults.DESCRIPTION,
        'action': 'dont remove me',
    }
    experiments3.add_experiment(
        **exp3_helpers.create_experiment(
            name=exp_name_false,
            consumers=['bank_notifications/events'],
            predicates=[exp3_helpers.create_false_predicate()],
            value=exp_value,
        ),
    )
    experiments3.add_experiment(
        **exp3_helpers.create_experiment(
            name=exp_name_true,
            consumers=['bank_notifications/events'],
            predicates=[exp3_helpers.create_true_predicate()],
            value=exp_value,
        ),
    )

    await taxi_bank_notifications.invalidate_caches()

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'][0]['event_id'] == expected_events[2].event_id
    assert resp_json['events'][1]['event_id'] == expected_events[1].event_id
    assert resp_json['events'][2]['event_id'] == expected_events[0].event_id
    assert 'cursor' not in resp_json


@pytest.mark.parametrize(
    'themes,button,description',
    [
        (defaults.DEFAULT_THEMES, None, None),
        (
            {
                'dark': {
                    'background': {'color': 'FF765432'},
                    'title_text_color': 'FFAABBCC',
                    'button_theme': {
                        'background': {'color': 'CCBBAA11'},
                        'text_color': 'BBCC2233',
                    },
                    'images': [{'url': 'path/to/image/', 'type': 'SINGLE'}],
                },
                'light': {
                    'background': {'color': 'AF123456'},
                    'title_text_color': '15151515',
                    'button_theme': {
                        'background': {'color': 'BBBB2211'},
                        'text_color': '55667733',
                    },
                    'images': [
                        {'url': 'path/to/image/', 'type': 'CAROUSEL'},
                        {'url': 'path/to/second/image/', 'type': 'CAROUSEL'},
                    ],
                },
            },
            {'text': 'test_description'},
            None,
        ),
        (
            {
                'dark': {
                    'background': {'color': 'FF765432'},
                    'title_text_color': 'FFAABBCC',
                    'description_text_color': 'AFAFAFAF',
                },
                'light': {
                    'background': {'color': 'AF123456'},
                    'title_text_color': '15151515',
                    'description_text_color': 'FFFFAAAA',
                },
            },
            None,
            'test_description',
        ),
    ],
)
async def test_ok_one_event_defaults_group_fulfill(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        taxi_config,
        themes,
        button,
        description,
):
    defaults_group_name = 'test_defaults_group_over'

    defaults_group = {
        'themes': themes,
        'title': defaults.TITLE,
        'priority': defaults.PRIORITY,
        'is_closable': True,
    }

    event = get_events_common.insert_events(
        pgsql, defaults_group=defaults_group_name, description=None,
    )[0]

    expected_event = {
        'title': 'Тестовый заголовок',
        'action': 'test_action',
        'event_type': defaults.EVENT_TYPE,
        'event_id': event.event_id,
        'themes': themes,
        'is_closable': True,
    }

    if button is not None:
        defaults_group['button'] = button
        expected_event['button'] = {'text': 'Тестовое описание'}
    if description is not None:
        defaults_group['description'] = description
        expected_event['description'] = 'Тестовое описание'

    taxi_config.set_values(
        {
            defaults.DEFAULTS_GROUP_CONFIG_NAME: {
                defaults_group_name: defaults_group,
            },
        },
    )

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == [expected_event]
    assert 'cursor' not in resp_json


@pytest.mark.parametrize(
    'exp_is_closable,default_is_closable,expected_is_closable',
    [
        (True, False, False),
        (True, True, True),
        (False, True, True),
        (False, False, False),
    ],
)
async def test_ok_one_event_defaults_group_and_experiments(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        taxi_config,
        experiments3,
        exp_is_closable,
        default_is_closable,
        expected_is_closable,
):
    exp_name = 'test_exp'
    exp_value = {
        'title': defaults.TITLE,
        'description': defaults.DESCRIPTION,
        'action': 'dont remove me',
        'is_closable': exp_is_closable,
    }
    experiments3.add_experiment(
        **exp3_helpers.create_experiment(
            name=exp_name,
            consumers=['bank_notifications/events'],
            predicates=[exp3_helpers.create_true_predicate()],
            value=exp_value,
        ),
    )

    defaults_group_name = 'test_defaults_group_over'

    event = get_events_common.insert_events(
        pgsql,
        defaults_group=defaults_group_name,
        description=None,
        action=None,
        experiment=exp_name,
    )[0]

    taxi_config.set_values(
        {
            defaults.DEFAULTS_GROUP_CONFIG_NAME: {
                defaults_group_name: {
                    'themes': defaults.DEFAULT_THEMES,
                    'title': defaults.TITLE,
                    'priority': defaults.PRIORITY,
                    'is_closable': default_is_closable,
                },
            },
        },
    )

    await taxi_bank_notifications.invalidate_caches()

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == [
        {
            'title': 'Тестовый заголовок',
            'action': exp_value['action'],
            'event_type': defaults.EVENT_TYPE,
            'event_id': event.event_id,
            'themes': defaults.DEFAULT_THEMES,
            'description': 'Тестовое описание',
            'is_closable': expected_is_closable,
        },
    ]
    assert 'cursor' not in resp_json


async def test_ok_one_event_with_experiment_hiding_after_txn(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        experiments3,
        bank_core_statement_mock,
):
    bank_core_statement_mock.set_transaction_count(0)

    get_events_common.insert_events(
        pgsql=pgsql, event_type=defaults.EVENT_TYPE2, experiment='test_exp',
    )

    exp_name = 'test_exp'
    exp_value = {
        'title': defaults.TITLE,
        'description': defaults.DESCRIPTION,
        'action': 'dont remove me',
    }
    experiments3.add_experiment(
        **exp3_helpers.create_experiment(
            name=exp_name,
            consumers=['bank_notifications/events'],
            predicates=[
                exp3_helpers.create_eq_predicate(
                    arg_name='transactions_count', value=0, arg_type='int',
                ),
                exp3_helpers.create_eq_predicate(
                    arg_name='bank_sdk', value=True, arg_type='bool',
                ),
                exp3_helpers.create_gte_predicate(
                    arg_name='sdk_version', value='0.11.0', arg_type='version',
                ),
            ],
            value=exp_value,
        ),
    )

    await taxi_bank_notifications.invalidate_caches()

    headers = get_events_common.default_headers()
    headers[
        'X-Request-Application'
    ] = 'bank_sdk=true,sdk_ver1=0,sdk_ver2=12,sdk_ver3=0'

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(event_type=defaults.EVENT_TYPE2),
        headers=headers,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['events']) == 1

    bank_core_statement_mock.set_transaction_count(1)

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(event_type=defaults.EVENT_TYPE2),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == []


async def test_no_event_with_experiment_if_timeout(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        experiments3,
        bank_core_statement_mock,
):
    bank_core_statement_mock.set_need_timeout(True)

    get_events_common.insert_events(
        pgsql=pgsql, event_type=defaults.EVENT_TYPE2, experiment='test_exp',
    )

    exp_name = 'test_exp'
    exp_value = {
        'title': defaults.TITLE,
        'description': defaults.DESCRIPTION,
        'action': 'dont remove me',
    }
    experiments3.add_experiment(
        **exp3_helpers.create_experiment(
            name=exp_name,
            consumers=['bank_notifications/events'],
            predicates=[
                exp3_helpers.create_all_of_predicate(
                    [
                        exp3_helpers.create_not_null_predicate(
                            arg_name='transactions_count',
                        ),
                        exp3_helpers.create_eq_predicate(
                            arg_name='transactions_count',
                            value=0,
                            arg_type='int',
                        ),
                    ],
                ),
            ],
            value=exp_value,
        ),
    )

    await taxi_bank_notifications.invalidate_caches()

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(event_type=defaults.EVENT_TYPE2),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == []


async def test_no_limit(taxi_bank_notifications, mockserver, pgsql):
    get_events_common.insert_events(
        pgsql=pgsql, event_type=defaults.EVENT_TYPE,
    )

    req_json = get_events_common.default_json()
    req_json.pop('limit')

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=req_json,
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 500


@pytest.mark.config(
    BANK_NOTIFICATIONS_EVENT_TYPES_2={
        defaults.EVENT_TYPE: {'sort_by': 'PRIORITY', 'limit': 3},
    },
)
async def test_no_limit_request(taxi_bank_notifications, mockserver, pgsql):
    get_events_common.insert_events(
        pgsql=pgsql, event_type=defaults.EVENT_TYPE, count=5,
    )

    req_json = get_events_common.default_json()
    req_json.pop('limit')

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=req_json,
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['events']) == 3
    assert 'cursor' not in resp_json


async def test_ok_tanker_keys(taxi_bank_notifications, mockserver, pgsql):
    title_args = {'val1': 'some_arg'}
    description_args = {'val1': 'another_arg'}
    event = get_events_common.insert_events(
        pgsql=pgsql,
        title=defaults.TITLE_WITH_ARG,
        description=defaults.DESCRIPTION_WITH_ARG,
        title_tanker_args=title_args,
        description_tanker_args=description_args,
    )[0]

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == [
        {
            'title': 'Тестовый заголовок ' + title_args['val1'],
            'description': 'Тестовое описание ' + description_args['val1'],
            'action': 'test_action',
            'event_type': defaults.EVENT_TYPE,
            'event_id': event.event_id,
            'themes': defaults.DEFAULT_THEMES,
            'is_closable': True,
        },
    ]
    assert 'cursor' not in resp_json


async def test_empty_payload(taxi_bank_notifications, mockserver, pgsql):
    event = get_events_common.insert_events(pgsql, payload={})[0]

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == [
        {
            'title': 'Тестовый заголовок',
            'description': 'Тестовое описание',
            'action': 'test_action',
            'event_type': defaults.EVENT_TYPE,
            'event_id': event.event_id,
            'themes': defaults.DEFAULT_THEMES,
            'is_closable': True,
        },
    ]
    assert 'cursor' not in resp_json


async def test_ok_payload(taxi_bank_notifications, mockserver, pgsql):
    event = get_events_common.insert_events(pgsql, payload=defaults.PAYLOAD)[0]

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == [
        {
            'title': 'Тестовый заголовок',
            'description': 'Тестовое описание',
            'action': 'test_action',
            'event_type': defaults.EVENT_TYPE,
            'event_id': event.event_id,
            'themes': defaults.DEFAULT_THEMES,
            'is_closable': True,
            'payload': defaults.PAYLOAD,
        },
    ]
    assert 'cursor' not in resp_json


@pytest.mark.parametrize('account_status', ['ANONYMOUS', 'KYC'])
async def test_ok_one_event_account_status(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        experiments3,
        bank_core_client_mock,
        account_status,
):
    bank_core_client_mock.response = {
        'auth_level': account_status,
        'phone_number': '1',
    }

    get_events_common.insert_events(
        pgsql,
        count=1,
        event_type=defaults.EVENT_TYPE,
        experiment='test_account_status',
    )

    experiments3.add_experiment(
        **exp3_helpers.create_experiment(
            name='test_account_status',
            consumers=['bank_notifications/events'],
            predicates=[
                exp3_helpers.create_eq_predicate(
                    arg_name='account_status',
                    value='ANONYMOUS',
                    arg_type='string',
                ),
            ],
            value={
                'title': defaults.TITLE,
                'description': defaults.DESCRIPTION,
                'action': 'dont remove me',
            },
        ),
    )

    await taxi_bank_notifications.invalidate_caches()

    headers = get_events_common.default_headers()

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(event_type=defaults.EVENT_TYPE),
        headers=headers,
    )
    assert response.status_code == 200
    resp_json = response.json()
    if account_status == 'ANONYMOUS':
        assert len(resp_json['events']) == 1
    else:
        assert not resp_json['events']


@pytest.mark.parametrize(
    'apps_response_code,apps_response,exp_arg_name,exp_value,events_len',
    [
        (
            200,
            {'applications': []},
            'has_processing_app_simplified_identification',
            True,
            0,
        ),
        (
            200,
            {'applications': []},
            'has_processing_app_simplified_identification',
            False,
            1,
        ),
        (
            200,
            {
                'applications': [
                    {
                        'type': 'SIMPLIFIED_IDENTIFICATION',
                        'application_id': (
                            '3edc0788-9b03-4f48-8829-e395311c42e1'
                        ),
                        'is_blocking': False,
                    },
                    {
                        'type': 'SIMPLIFIED_IDENTIFICATION_ESIA',
                        'application_id': (
                            '3edc0788-9b03-4f48-8829-e395311c4000'
                        ),
                        'is_blocking': False,
                    },
                    {
                        'type': 'CHANGE_NUMBER',
                        'application_id': (
                            '3edc0788-9b03-4f48-8829-e395311c4001'
                        ),
                        'is_blocking': False,
                    },
                    {
                        'type': 'KYC',
                        'application_id': (
                            '3edc0788-9b03-4f48-8829-e395311c4002'
                        ),
                        'is_blocking': False,
                    },
                    {
                        'type': 'LOAN_REGISTRATION',
                        'application_id': (
                            '3edc0788-9b03-4f48-8829-e395311c4003'
                        ),
                        'is_blocking': False,
                    },
                ],
            },
            'has_processing_app_simplified_identification',
            True,
            1,
        ),
        (
            200,
            {'applications': []},
            'has_processing_app_digital_card_issue',
            True,
            0,
        ),
        (
            200,
            {'applications': []},
            'has_processing_app_digital_card_issue',
            False,
            1,
        ),
        (
            200,
            {
                'applications': [
                    {
                        'type': 'DIGITAL_CARD_ISSUE',
                        'application_id': (
                            '3edc0788-9b03-4f48-8829-e395311c42e1'
                        ),
                        'is_blocking': False,
                    },
                ],
            },
            'has_processing_app_digital_card_issue',
            True,
            1,
        ),
        (400, {}, 'has_processing_app_digital_card_issue', True, 0),
        (404, {}, 'has_processing_app_digital_card_issue', True, 0),
        (500, {}, 'has_processing_app_simplified_identification', True, 0),
        (400, {}, 'has_processing_app_digital_card_issue', False, 1),
        (404, {}, 'has_processing_app_digital_card_issue', False, 1),
        (500, {}, 'has_processing_app_simplified_identification', False, 1),
    ],
)
async def test_experiment_has_apps(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        experiments3,
        bank_applications_mock,
        apps_response_code,
        apps_response,
        exp_arg_name,
        exp_value,
        events_len,
):
    bank_applications_mock.set_http_status_code(apps_response_code)
    bank_applications_mock.set_response(apps_response)

    exp_name = 'test_exp'
    get_events_common.insert_events(pgsql=pgsql, experiment=exp_name)
    experiments3.add_experiment(
        **exp3_helpers.create_experiment(
            name=exp_name,
            consumers=['bank_notifications/events'],
            predicates=[
                exp3_helpers.create_eq_predicate(
                    arg_name=exp_arg_name, value=exp_value, arg_type='bool',
                ),
            ],
            value={
                'title': defaults.TITLE,
                'description': defaults.DESCRIPTION,
            },
        ),
    )

    await taxi_bank_notifications.invalidate_caches()

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['events']) == events_len
    assert 'cursor' not in resp_json
