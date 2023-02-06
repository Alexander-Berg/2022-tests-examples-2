import pytest

import tests_bank_notifications.db_helpers as db_helpers
import tests_bank_notifications.defaults as defaults
import tests_bank_notifications.exp3_helpers as exp3_helpers
import tests_bank_notifications.get_events_common as get_events_common
import tests_bank_notifications.models as models


@pytest.mark.parametrize(
    'header,',
    [
        'X-Yandex-UID',
        'X-Yandex-BUID',
        'X-YaBank-SessionUUID',
        'X-YaBank-PhoneID',
        'X-Ya-User-Ticket',
    ],
)
async def test_unauthorized(
        taxi_bank_notifications, mockserver, pgsql, header,
):
    headers = get_events_common.default_headers()
    headers.pop(header)
    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=headers,
    )
    get_events_common.check_failed_response(response, 401, '401')


async def test_empty_buid(taxi_bank_notifications, mockserver, pgsql):
    headers = get_events_common.default_headers()
    headers['X-Yandex-BUID'] = ''
    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=headers,
    )
    get_events_common.check_failed_response(response, 401, '401')


@pytest.mark.parametrize('field_name', [defaults.EVENT_TYPE_KEY, 'limit'])
async def test_empty_required_field(
        taxi_bank_notifications, mockserver, pgsql, field_name,
):
    req_json = get_events_common.default_json()
    req_json[field_name] = ''
    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=req_json,
        headers=get_events_common.default_headers(),
    )
    get_events_common.check_failed_response(response, 400, '400')


async def test_invalid_event_type(taxi_bank_notifications, mockserver, pgsql):
    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(event_type='invalid'),
        headers=get_events_common.default_headers(),
    )
    get_events_common.check_failed_response(
        response, 400, 'BadRequest', 'invalid event_type \'invalid\'',
    )


@pytest.mark.parametrize('cursor', ['', 'invalid'])
async def test_no_invalid_cursor(
        taxi_bank_notifications, mockserver, pgsql, cursor,
):
    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(cursor=cursor),
        headers=get_events_common.default_headers(),
    )
    get_events_common.check_failed_response(response, 400, 'BadRequest')


async def test_ok_empty(taxi_bank_notifications, mockserver, pgsql):
    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == []
    assert 'cursor' not in resp_json


async def test_ok_one_event(taxi_bank_notifications, mockserver, pgsql):
    event = get_events_common.insert_events(pgsql)[0]

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


async def test_ok_one_all_event(taxi_bank_notifications, mockserver, pgsql):
    event = get_events_common.insert_events(pgsql, bank_uid=defaults.ALL_KEY)[
        0
    ]

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

    headers = get_events_common.default_headers()
    headers['X-Yandex-BUID'] = defaults.BUID2

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=headers,
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


async def test_ok_order(taxi_bank_notifications, mockserver, pgsql):
    events = get_events_common.insert_events(pgsql, count=2)

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['events']) == 2
    assert resp_json['events'][0]['event_id'] == events[1].event_id
    assert resp_json['events'][1]['event_id'] == events[0].event_id


async def test_event_without_title(taxi_bank_notifications, mockserver, pgsql):
    event = models.Event.default(
        event_type=defaults.EVENT_TYPE, title=None, defaults_group='abc',
    )
    db_response = db_helpers.insert_event(pgsql, event)
    assert len(db_response) == 1

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['events'] == []


@pytest.mark.parametrize(
    'action,description,expected_event',
    [
        (
            None,
            None,
            {
                'action': 'test_action',
                'description': 'Тестовое описание',
                'event_type': 'MAIN_SCREEN',
                'title': 'Тестовый заголовок',
                'themes': defaults.DEFAULT_THEMES,
                'is_closable': True,
            },
        ),
        (
            None,
            'description.abc',
            {
                'action': 'test_action',
                'description': 'Тестовое описание ABC',
                'event_type': 'MAIN_SCREEN',
                'title': 'Тестовый заголовок',
                'themes': defaults.DEFAULT_THEMES,
                'is_closable': True,
            },
        ),
        (
            'action 123',
            None,
            {
                'action': 'action 123',
                'description': 'Тестовое описание',
                'event_type': 'MAIN_SCREEN',
                'title': 'Тестовый заголовок',
                'themes': defaults.DEFAULT_THEMES,
                'is_closable': True,
            },
        ),
        (
            'action 123',
            'description.abc',
            {
                'action': 'action 123',
                'description': 'Тестовое описание ABC',
                'event_type': 'MAIN_SCREEN',
                'title': 'Тестовый заголовок',
                'themes': defaults.DEFAULT_THEMES,
                'is_closable': True,
            },
        ),
    ],
)
async def test_no_event_action_description(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        action,
        description,
        expected_event,
):
    event = models.Event.default(
        event_type=defaults.EVENT_TYPE, action=action, description=description,
    )
    db_response = db_helpers.insert_event(pgsql, event)
    assert len(db_response) == 1

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json) == 1
    events = resp_json['events']
    assert len(events) == 1
    event = events[0]
    event_id = event.pop('event_id')
    assert len(event_id) > 1
    assert event == expected_event


async def test_part_marked(taxi_bank_notifications, mockserver, pgsql):
    events = get_events_common.insert_events(pgsql, count=2)
    get_events_common.insert_marks(pgsql, [events[0].event_id])

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['events']) == 1
    assert resp_json['events'][0]['event_id'] == events[1].event_id


async def test_all_marked(taxi_bank_notifications, mockserver, pgsql):
    events = get_events_common.insert_events(pgsql, count=5)
    get_events_common.insert_marks(pgsql, [event.event_id for event in events])

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == []
    assert 'cursor' not in resp_json


async def test_merge_keys(taxi_bank_notifications, mockserver, pgsql):
    events = [
        models.Event.default(
            event_id=defaults.gen_uuid(),
            merge_key='abc',
            merge_status='MERGED',
        ),
        models.Event.default(
            event_id=defaults.gen_uuid(),
            merge_key='abc',
            merge_status='CURRENT',
        ),
        models.Event.default(event_id=defaults.gen_uuid()),
        models.Event.default(
            event_id=defaults.gen_uuid(),
            event_type=defaults.EVENT_TYPE2,
            merge_key='abc',
            merge_status='CURRENT',
        ),
        models.Event.default(
            bank_uid=defaults.BUID2,
            event_id=defaults.gen_uuid(),
            merge_key='abc',
            merge_status='CURRENT',
        ),
    ]
    for event in events:
        db_helpers.insert_event(pgsql, event)
    db_events_buid1 = db_helpers.select_events(pgsql, defaults.BUID)
    assert len(db_events_buid1) == 4
    db_events_buid2 = db_helpers.select_events(pgsql, defaults.BUID2)
    assert len(db_events_buid2) == 1

    # buid=buid1 and event_type=defaults.EVENT_TYPE
    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['events']) == 2
    assert resp_json['events'][0]['event_id'] == events[2].event_id
    assert resp_json['events'][1]['event_id'] == events[1].event_id
    assert 'cursor' not in resp_json

    # buid=buid1 and event_type=defaults.EVENT_TYPE2
    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(defaults.EVENT_TYPE2),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['events']) == 1
    assert resp_json['events'][0]['event_id'] == events[3].event_id
    assert 'cursor' not in resp_json

    # buid=buid2 and event_type=defaults.EVENT_TYPE
    headers = get_events_common.default_headers()
    headers['X-Yandex-BUID'] = defaults.BUID2
    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=headers,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['events']) == 1
    assert resp_json['events'][0]['event_id'] == events[4].event_id
    assert 'cursor' not in resp_json


async def test_no_title_localization(
        taxi_bank_notifications, mockserver, pgsql,
):
    event = models.Event.default(title='abc')
    db_response = db_helpers.insert_event(pgsql, event)
    assert len(db_response) == 1

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == []
    assert 'cursor' not in resp_json


async def test_no_description_and_action(
        taxi_bank_notifications, mockserver, pgsql,
):
    event = models.Event.default(
        defaults_group='test_defaults_group_only_required',
        description=None,
        action=None,
    )
    db_response = db_helpers.insert_event(pgsql, event)
    assert len(db_response) == 1

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
            'event_type': defaults.EVENT_TYPE,
            'event_id': event.event_id,
            'themes': defaults.DEFAULT_THEMES,
            'is_closable': True,
        },
    ]
    assert 'cursor' not in resp_json


async def test_no_description_localized(
        taxi_bank_notifications, mockserver, pgsql,
):
    event = models.Event.default(description='abc')
    db_response = db_helpers.insert_event(pgsql, event)
    assert len(db_response) == 1

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == []
    assert 'cursor' not in resp_json


@pytest.mark.parametrize(
    'locale,title,description',
    [
        ('ru', 'Тестовый заголовок', 'Тестовое описание'),
        ('en', 'Test title', 'Test description'),
        ('abc', 'Тестовый заголовок', 'Тестовое описание'),
        ('', 'Тестовый заголовок', 'Тестовое описание'),
    ],
)
async def test_localization_locale(
        taxi_bank_notifications, mockserver, pgsql, locale, title, description,
):
    event = models.Event.default()
    db_response = db_helpers.insert_event(pgsql, event)
    assert len(db_response) == 1

    headers = get_events_common.default_headers()
    headers['X-Request-Language'] = locale
    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=headers,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == [
        {
            'title': title,
            'description': description,
            'action': 'test_action',
            'event_type': defaults.EVENT_TYPE,
            'event_id': event.event_id,
            'themes': defaults.DEFAULT_THEMES,
            'is_closable': True,
        },
    ]
    assert 'cursor' not in resp_json


def fill_priority_events(pgsql, event_type):
    default_priority_event = models.Event.default(
        event_id=defaults.gen_uuid(), event_type=event_type,
    )
    db_helpers.insert_event(pgsql, default_priority_event)

    big_priority_event = models.Event.default(
        event_id=defaults.gen_uuid(), priority=1000, event_type=event_type,
    )
    db_helpers.insert_event(pgsql, big_priority_event)

    small_priority_event = models.Event.default(
        event_id=defaults.gen_uuid(), priority=10, event_type=event_type,
    )
    db_helpers.insert_event(pgsql, small_priority_event)

    events = get_events_common.insert_events(
        pgsql, count=3, event_type=event_type,
    )
    events.reverse()  # sort in desc order

    sort_by_time = events + [
        small_priority_event,
        big_priority_event,
        default_priority_event,
    ]
    sort_by_priority = (
        [big_priority_event]
        + events
        + [default_priority_event, small_priority_event]
    )
    return sort_by_time, sort_by_priority


@pytest.mark.parametrize(
    'event_type',
    [defaults.EVENT_TYPE, defaults.EVENT_TYPE2, defaults.EVENT_TYPE_BELL],
)
async def test_sorted_events(
        taxi_bank_notifications, mockserver, pgsql, event_type,
):
    events_by_time, events_by_priority = fill_priority_events(
        pgsql, event_type,
    )

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(event_type),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json) == 1
    resp_events = resp_json['events']
    assert len(resp_events) == 6
    if event_type == defaults.EVENT_TYPE_BELL:
        for i, event in enumerate(events_by_time):
            assert resp_events[i]['event_id'] == event.event_id
    else:
        for i, event in enumerate(events_by_priority):
            assert resp_events[i]['event_id'] == event.event_id


@pytest.mark.parametrize(
    'event_type',
    [defaults.EVENT_TYPE, defaults.EVENT_TYPE2, defaults.EVENT_TYPE_BELL],
)
async def test_sorted_events_with_cursor(
        taxi_bank_notifications, mockserver, pgsql, event_type,
):
    events_by_time, events_by_priority = fill_priority_events(
        pgsql, event_type,
    )

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(event_type=event_type, limit=3),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json) == 2
    resp_events = resp_json['events']
    cursor = resp_json['cursor']
    assert len(resp_events) == 3
    if event_type == defaults.EVENT_TYPE_BELL:
        for i, event in enumerate(events_by_time[:3]):
            assert resp_events[i]['event_id'] == event.event_id
    else:
        for i, event in enumerate(events_by_priority[:3]):
            assert resp_events[i]['event_id'] == event.event_id

    response2 = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(
            event_type=event_type, limit=3, cursor=cursor,
        ),
        headers=get_events_common.default_headers(),
    )
    assert response2.status_code == 200
    resp_json2 = response2.json()
    assert len(resp_json2) == 1
    resp_events2 = resp_json2['events']
    assert len(resp_events2) == 3
    if event_type == defaults.EVENT_TYPE_BELL:
        for i, event in enumerate(events_by_time[3:]):
            assert resp_events2[i]['event_id'] == event.event_id
    else:
        for i, event in enumerate(events_by_priority[3:]):
            assert resp_events2[i]['event_id'] == event.event_id


async def test_ok_one_event_with_experiment(
        taxi_bank_notifications, mockserver, pgsql, experiments3,
):
    event = get_events_common.insert_events(
        pgsql=pgsql, experiment='test_exp',
    )[0]

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


@pytest.mark.parametrize(
    'color_theme',
    [defaults.DARK_KEY, defaults.LIGHT_KEY, defaults.SYSTEM_KEY],
)
async def test_header_color_theme(
        taxi_bank_notifications, mockserver, pgsql, experiments3, color_theme,
):
    get_events_common.insert_events(pgsql=pgsql, experiment='test_exp')

    headers = get_events_common.default_headers()
    headers['X-YaBank-ColorTheme'] = color_theme

    theme = {
        'background': {'color': '0123ABFD'},
        'title_text_color': 'DFBA3210',
    }
    exp_name = 'test_exp'
    exp_value = {
        'title': defaults.TITLE,
        'description': defaults.DESCRIPTION,
        'action': 'dont remove me',
        'themes': {'dark': theme, 'light': theme},
    }
    experiments3.add_experiment(
        **exp3_helpers.create_experiment(
            name=exp_name,
            consumers=['bank_notifications/events'],
            predicates=[exp3_helpers.create_true_predicate()],
            value=exp_value,
        ),
    )

    expected_theme = {}

    if color_theme in (defaults.SYSTEM_KEY, defaults.DARK_KEY):
        expected_theme['dark'] = theme
    if color_theme in (defaults.SYSTEM_KEY, defaults.LIGHT_KEY):
        expected_theme['light'] = theme

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=headers,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'][0]['themes'] == expected_theme
    assert 'cursor' not in resp_json


async def test_ok_one_event_with_full_experiment(
        taxi_bank_notifications, mockserver, pgsql, experiments3,
):
    event = get_events_common.insert_events(
        pgsql=pgsql, experiment='test_exp',
    )[0]

    exp_name = 'test_exp'
    theme = {
        'background': {'color': '01ABCDEF'},
        'title_text_color': '01ABCDEF',
        'description_text_color': '01ABCDEF',
        'top_box_text_color': '01ABCDEF',
        'button_theme': {
            'text_color': '01ABCDEF',
            'background': {'color': '01ABCDEF'},
        },
        'images': [{'type': 'SINGLE', 'url': 'yandex.svg'}],
    }
    exp_value = {
        'themes': {'dark': theme, 'light': theme},
        'title': defaults.TITLE,
        'description': defaults.DESCRIPTION,
        'action': 'dont remove me',
        'top_box_text': 'soon_text',
        'button': {'text': 'press_me_text'},
        'is_closable': True,
    }
    experiments3.add_experiment(
        **exp3_helpers.create_experiment(
            name=exp_name,
            consumers=['bank_notifications/events'],
            predicates=[exp3_helpers.create_true_predicate()],
            value=exp_value,
        ),
    )

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['events'] == [
        {
            'themes': {'dark': theme, 'light': theme},
            'title': 'Тестовый заголовок',
            'description': 'Тестовое описание',
            'action': exp_value['action'],
            'event_type': defaults.EVENT_TYPE,
            'event_id': event.event_id,
            'top_box_text': 'скоро',
            'button': {'text': 'Нажми меня!'},
            'is_closable': True,
        },
    ]
    assert 'cursor' not in resp_json


async def test_no_event_with_experiment_marked(
        taxi_bank_notifications, mockserver, pgsql, experiments3,
):
    event = get_events_common.insert_events(
        pgsql=pgsql, experiment='test_exp',
    )[0]
    get_events_common.insert_marks(pgsql, [event.event_id])

    exp_name = 'test_exp'
    exp_value = {
        'title': 'event via exp',
        'description': 'im testing experiment',
        'action': 'dont remove me',
    }
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
    assert resp_json['events'] == []


async def test_no_event_with_experiment_not_in_exp(
        taxi_bank_notifications, mockserver, pgsql, experiments3,
):
    get_events_common.insert_events(pgsql=pgsql, experiment='test_exp')

    exp_name = 'test_exp'
    exp_value = {
        'title': 'event via exp',
        'description': 'im testing experiment',
        'action': 'dont remove me',
    }
    experiments3.add_experiment(
        **exp3_helpers.create_experiment(
            name=exp_name,
            consumers=['bank_notifications/events'],
            predicates=[
                exp3_helpers.create_eq_predicate('buid', defaults.BUID2),
            ],
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


@pytest.mark.parametrize(
    'transactions_count,exp_value,events_len',
    [(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)],
)
async def test_main_screen_event_with_transactions_exp(
        taxi_bank_notifications,
        mockserver,
        pgsql,
        experiments3,
        bank_core_statement_mock,
        transactions_count,
        exp_value,
        events_len,
):
    bank_core_statement_mock.set_transaction_count(transactions_count)

    exp_name = 'test_exp'
    event_type = 'MAIN_SCREEN'
    get_events_common.insert_events(
        pgsql=pgsql, event_type=event_type, experiment=exp_name,
    )
    experiments3.add_experiment(
        **exp3_helpers.create_experiment(
            name=exp_name,
            consumers=['bank_notifications/events'],
            predicates=[
                exp3_helpers.create_eq_predicate(
                    arg_name='transactions_count',
                    value=exp_value,
                    arg_type='int',
                ),
            ],
            value={'title': defaults.TITLE},
        ),
    )

    await taxi_bank_notifications.invalidate_caches()

    response = await taxi_bank_notifications.post(
        '/v1/notifications/v1/get_events',
        json=get_events_common.default_json(event_type=event_type),
        headers=get_events_common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['events']) == events_len
    assert 'cursor' not in resp_json
