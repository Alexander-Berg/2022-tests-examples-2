import pytest

HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'}

PROJECT_SETTINGS = {
    'default': {'enable_chatterbox': False},
    'calltaxi': {
        'enable_chatterbox': False,
        'events_source': 'wfm',
        'wfm_effrat_domain': 'taxi',
        'main_permission': 'user_calltaxi',
    },
    'ms_support': {
        'enable_chatterbox': False,
        'events_source': 'wfm',
        'wfm_effrat_domain': 'mediaservices',
        'main_permission': 'user_ms',
    },
}


EXPECTED_DATA_1 = {
    'events': [
        {
            'id': '50394',
            'type': 'shift',
            'start': '2021-01-02T07:00:00+0000',
            'end': '2021-01-02T09:00:00+0000',
            'title': 'Смена',
            'full_day': False,
        },
        {
            'id': '29237',
            'type': 'break',
            'start': '2021-01-02T09:00:00+0000',
            'end': '2021-01-02T09:30:00+0000',
            'title': 'Перерыв',
            'full_day': False,
        },
        {
            'id': '50394',
            'type': 'shift',
            'start': '2021-01-02T09:30:00+0000',
            'end': '2021-01-02T13:00:00+0000',
            'title': 'Смена',
            'full_day': False,
        },
        {
            'id': '29238',
            'type': 'break',
            'start': '2021-01-02T13:00:00+0000',
            'end': '2021-01-02T13:30:00+0000',
            'title': 'Обед',
            'full_day': False,
        },
        {
            'id': '50394',
            'type': 'shift',
            'start': '2021-01-02T13:30:00+0000',
            'end': '2021-01-02T14:30:00+0000',
            'title': 'Смена',
            'full_day': False,
        },
        {
            'id': '29239',
            'type': 'break',
            'start': '2021-01-02T14:30:00+0000',
            'end': '2021-01-02T15:00:00+0000',
            'title': 'Перерыв',
            'full_day': False,
        },
        {
            'id': '50394',
            'type': 'shift',
            'start': '2021-01-02T15:00:00+0000',
            'end': '2021-01-02T15:45:00+0000',
            'title': 'Смена',
            'full_day': False,
        },
        {
            'id': '29240',
            'type': 'break',
            'start': '2021-01-02T15:45:00+0000',
            'end': '2021-01-02T16:00:00+0000',
            'title': 'Перерыв',
            'full_day': False,
        },
    ],
}

EXPECTED_DATA_2 = {
    'events': [
        {
            'id': '29238',
            'type': 'break',
            'start': '2021-01-02T13:00:00+0000',
            'end': '2021-01-02T13:30:00+0000',
            'title': 'Обед',
            'full_day': False,
        },
        {
            'id': '50394',
            'type': 'shift',
            'start': '2021-01-02T13:30:00+0000',
            'end': '2021-01-02T14:30:00+0000',
            'title': 'Смена',
            'full_day': False,
        },
        {
            'id': '29239',
            'type': 'break',
            'start': '2021-01-02T14:30:00+0000',
            'end': '2021-01-02T15:00:00+0000',
            'title': 'Перерыв',
            'full_day': False,
        },
        {
            'id': '50394',
            'type': 'shift',
            'start': '2021-01-02T15:00:00+0000',
            'end': '2021-01-02T15:45:00+0000',
            'title': 'Смена',
            'full_day': False,
        },
        {
            'id': '29240',
            'type': 'break',
            'start': '2021-01-02T15:45:00+0000',
            'end': '2021-01-02T16:00:00+0000',
            'title': 'Перерыв',
            'full_day': False,
        },
    ],
}

EXPECTED_DATA_3 = {
    'events': [
        {
            'id': '50394',
            'type': 'shift',
            'start': '2021-01-02T07:00:00+0000',
            'end': '2021-01-02T16:00:00+0000',
            'title': 'Смена',
            'full_day': False,
        },
    ],
}


@pytest.mark.parametrize(
    'body,status,expected_data',
    [
        (
            {
                'from': '2021-01-01T21:00:00Z',
                'to': '2021-01-02T21:00:00Z',
                'login': 'webalex',
            },
            200,
            EXPECTED_DATA_1,
        ),
        (
            {
                'from': '2021-01-02T13:00:00Z',
                'to': '2021-01-02T21:00:00Z',
                'login': 'webalex',
            },
            200,
            EXPECTED_DATA_2,
        ),
        ({'login': 'webalex'}, 400, None),
    ],
)
@pytest.mark.translations(
    agent={
        'title_event_shift': {'ru': 'Смена'},
        'title_event_technical': {'ru': 'Перерыв'},
        'title_event_lunchtime': {'ru': 'Обед'},
    },
)
@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
async def test_user_events_from_and_to(
        web_app_client,
        body,
        status,
        expected_data,
        mock_wfm_operators,
        mock_wfm_timetable,
):

    response = await web_app_client.post('/events', headers=HEADERS, json=body)
    assert response.status == status
    if response.status == 200:
        content = await response.json()
        assert content == expected_data


@pytest.mark.parametrize(
    'body,status,expected_data',
    [
        (
            {
                'from': '2021-01-01T21:00:00Z',
                'to': '2021-01-02T21:00:00Z',
                'login': 'webalex',
            },
            200,
            EXPECTED_DATA_3,
        ),
    ],
)
@pytest.mark.translations(
    agent={
        'title_event_shift': {'ru': 'Смена'},
        'title_event_technical': {'ru': 'Перерыв'},
        'title_event_lunchtime': {'ru': 'Обед'},
    },
)
@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
async def test_user_events_only_shift(
        web_app_client,
        body,
        status,
        expected_data,
        mock_wfm_operators,
        mock_wfm_timetable_onlyshift,
):
    response = await web_app_client.post('/events', headers=HEADERS, json=body)
    assert response.status == status
    if response.status == 200:
        content = await response.json()
        assert content == expected_data


@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
async def test_user_events_fail_v1_operator(
        web_app_client, mock_wfm_operators_fail, mock_wfm_timetable,
):
    body = {
        'from': '2021-01-01T21:00:00Z',
        'to': '2021-01-02T21:00:00Z',
        'login': 'webalex',
    }
    response = await web_app_client.post('/events', headers=HEADERS, json=body)
    assert response.status == 200
    content = await response.json()
    assert content == {'events': []}


@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
async def test_user_events_fail_v1_shifts(
        web_app_client, mock_wfm_operators, mock_wfm_operators_fail,
):
    body = {
        'from': '2021-01-01T21:00:00Z',
        'to': '2021-01-02T21:00:00Z',
        'login': 'webalex',
    }
    response = await web_app_client.post('/events', headers=HEADERS, json=body)
    assert response.status == 200
    content = await response.json()
    assert content == {'events': []}


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': False,
            'events_source': 'hrms',
            'main_permission': 'user_calltaxi',
        },
    },
)
@pytest.mark.parametrize(
    'body,status,expected_data',
    [
        (
            {
                'from': '2020-01-01T00:00:00Z',
                'to': '2020-01-02T00:00:00Z',
                'login': 'webalex',
            },
            200,
            {
                'events': [
                    {
                        'id': '1',
                        'type': 'shift',
                        'start': '2020-01-01T10:00:00+0000',
                        'end': '2020-01-01T11:00:00+0000',
                        'title': 'перерыв',
                        'full_day': False,
                    },
                    {
                        'id': '2',
                        'type': 'shift',
                        'start': '2020-01-01T11:00:00+0000',
                        'end': '2020-01-01T23:00:00+0000',
                        'title': 'работа',
                        'full_day': False,
                    },
                    {
                        'id': '3',
                        'type': 'break',
                        'start': '2020-01-02T09:00:00+0000',
                        'end': '2020-01-02T22:00:00+0000',
                        'title': 'отпуск',
                        'full_day': False,
                    },
                    {
                        'id': '4',
                        'type': 'unspecified',
                        'start': '2020-01-02T21:00:00+0000',
                        'end': '2020-01-03T20:59:59+0000',
                        'title': 'отпуск',
                        'full_day': False,
                    },
                ],
            },
        ),
    ],
)
async def test_hrms_source(
        web_app_client, mock_hrms_events, body, status, expected_data,
):
    response = await web_app_client.post(
        '/events',
        headers={
            'X-Yandex-Login': 'webalex',
            'Accept-Language': 'ru-ru',
            'X-Ya-User-Ticket': 'webalex_ticket',
        },
        json=body,
    )
    assert response.status == status
    content = await response.json()
    assert content == expected_data
