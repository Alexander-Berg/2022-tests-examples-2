import pytest

HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-ru'}
HEADERS_HRMS = {
    'X-Yandex-Login': 'agent_hrms',
    'Accept-Language': 'ru-ru',
    'X-Ya-User-Ticket': 'some',
}


PROJECT_SETTINGS = {
    'default': {'enable_chatterbox': False},
    'calltaxi': {
        'enable_chatterbox': False,
        'main_permission': 'user_calltaxi',
        'piecework_tariff': 'call-taxi-unified',
        'piecework_source': 'piecework_calculation',
    },
    'hrms': {
        'enable_chatterbox': False,
        'main_permission': 'user_hrms',
        'piecework_source': 'hrms',
    },
}


@pytest.mark.parametrize(
    'body,status,expected_data',
    [
        (
            {
                'start_date': '2021-01-01',
                'stop_date': '2021-01-16',
                'project': 'calltaxi',
                'country': 'ru',
            },
            200,
            {
                'items': [
                    {
                        'login': 'liambaev',
                        'team': 'first_line_calltaxi',
                        'country': 'ru',
                        'half_time': False,
                    },
                    {
                        'login': 'webalex',
                        'team': 'first_line_calltaxi',
                        'country': 'ru',
                        'half_time': True,
                    },
                ],
            },
        ),
        (
            {
                'start_date': '2021-01-01',
                'stop_date': '2021-01-31',
                'project': 'calltaxi',
                'country': 'by',
            },
            200,
            {'items': []},
        ),
        (
            {
                'start_date': '2021-01-01',
                'stop_date': '2021-01-16',
                'project': 'calltaxi',
            },
            200,
            {
                'items': [
                    {
                        'login': 'liambaev',
                        'team': 'first_line_calltaxi',
                        'country': 'ru',
                        'half_time': False,
                    },
                    {
                        'login': 'webalex',
                        'team': 'first_line_calltaxi',
                        'country': 'ru',
                        'half_time': True,
                    },
                ],
            },
        ),
        (
            {
                'start_date': '2021-01-16',
                'stop_date': '2021-01-31',
                'project': 'calltaxi',
            },
            200,
            {
                'items': [
                    {
                        'login': 'liambaev',
                        'team': 'first_line_calltaxi',
                        'country': 'ru',
                        'half_time': False,
                    },
                    {
                        'login': 'webalex',
                        'team': 'second_line_calltaxi',
                        'country': 'ru',
                        'half_time': True,
                    },
                ],
            },
        ),
        (
            {
                'start_date': '2021-01-01',
                'stop_date': '2021-01-16',
                'project': 'unknown_project',
            },
            409,
            {},
        ),
    ],
)
@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
async def test_piecework_employee(web_app_client, body, status, expected_data):
    response = await web_app_client.post('/piecework/employee', json=body)
    assert response.status == status
    if status == 200:
        content = await response.json()
        assert content == expected_data


@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
@pytest.mark.config(AGENT_USE_PIECEWORK_FOR_RESERVE=True)
@pytest.mark.parametrize(
    'body,headers,status,expected_data',
    [
        (
            {'login': 'a-topalyan'},
            {'X-Yandex-Login': 'a-topalyan', 'Accept-Language': 'ru-ru'},
            200,
            {
                'basic_score': {
                    'current_value': {'value': 10000.0, 'style': 'decimal'},
                    'reserve': {'value': 1234.0, 'style': 'decimal'},
                },
                'benefit': {'value': {'value': 0.5, 'style': 'percent'}},
            },
        ),
        (
            {'login': 'webalexbot'},
            {'X-Yandex-Login': 'webalexbot', 'Accept-Language': 'ru-ru'},
            500,
            {},
        ),
        (
            {'login': 'agent'},
            {'X-Yandex-Login': 'webalexbot', 'Accept-Language': 'ru-ru'},
            403,
            {},
        ),
    ],
)
async def test_piecework_summary(
        web_app_client,
        mock_piecework_response,
        mock_picework_reserve_current,
        body,
        headers,
        status,
        expected_data,
):
    response = await web_app_client.post(
        '/piecework', json=body, headers=headers,
    )
    assert response.status == status
    if status == 200:
        content = await response.json()
        assert content == expected_data


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
            'piecework_source': 'hrms',
        },
    },
)
@pytest.mark.config(AGENT_USE_PIECEWORK_FOR_RESERVE=True)
@pytest.mark.parametrize(
    'body,headers,status,expected_data',
    [
        (
            {'login': 'a-topalyan'},
            {
                'X-Yandex-Login': 'a-topalyan',
                'Accept-Language': 'ru-ru',
                'X-Ya-User-Ticket': 'Ticket',
            },
            200,
            {
                'basic_score': {
                    'current_value': {'value': 447.0, 'style': 'decimal'},
                },
            },
        ),
    ],
)
async def test_piecework_hrms_summary(
        web_app_client,
        mock_hrms_finances_one_person,
        mock_picework_reserve_current,
        body,
        headers,
        status,
        expected_data,
):
    response = await web_app_client.post(
        '/piecework', json=body, headers=headers,
    )
    assert response.status == status
    if status == 200:
        content = await response.json()
        assert content == expected_data


@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
@pytest.mark.config(AGENT_USE_PIECEWORK_FOR_RESERVE=False)
@pytest.mark.parametrize(
    'body,headers,status,expected_data',
    [
        (
            {'login': 'a-topalyan'},
            {'X-Yandex-Login': 'a-topalyan', 'Accept-Language': 'ru-ru'},
            200,
            {
                'basic_score': {
                    'current_value': {'value': 10000.0, 'style': 'decimal'},
                    'reserve': {'value': 1777.0, 'style': 'decimal'},
                },
                'benefit': {'value': {'value': 0.5, 'style': 'percent'}},
            },
        ),
        (
            {'login': 'webalexbot'},
            {'X-Yandex-Login': 'webalexbot', 'Accept-Language': 'ru-ru'},
            500,
            {},
        ),
        (
            {'login': 'agent'},
            {'X-Yandex-Login': 'webalexbot', 'Accept-Language': 'ru-ru'},
            403,
            {},
        ),
    ],
)
async def test_piecework_summary_reserve_compendium(
        web_app_client,
        mock_piecework_response,
        mock_picework_reserve_current,
        body,
        headers,
        status,
        expected_data,
):

    response = await web_app_client.post(
        '/piecework', json=body, headers=headers,
    )
    assert response.status == status
    if status == 200:
        content = await response.json()
        assert content == expected_data


@pytest.mark.parametrize(
    'headers,body,status,expected_data',
    [
        (
            HEADERS,
            {
                'login': 'webalex',
                'start_date': '2022-01-01',
                'end_date': '2022-01-15',
            },
            200,
            {
                'full_period': False,
                'start_date': '2022-01-01',
                'end_date': '2022-01-15',
                'period_receipt': [
                    {
                        'field_name': 'Обычные дни',
                        'field_type': 'day',
                        'value': {'value': 1, 'style': 'decimal'},
                    },
                    {
                        'field_name': 'Обычные дни',
                        'field_type': 'night',
                        'value': {'value': 2, 'style': 'decimal'},
                    },
                    {
                        'field_name': 'Праздничные дни',
                        'field_type': 'night',
                        'value': {'value': 4, 'style': 'decimal'},
                    },
                    {
                        'field_name': 'Праздничные дни',
                        'field_type': 'day',
                        'value': {'value': 3, 'style': 'decimal'},
                    },
                ],
                'indicators': [],
                'details': [
                    {
                        'line': 'first',
                        'action': 'close',
                        'cost': {'value': 10, 'style': 'decimal'},
                        'count': 11,
                        'sum': {'value': 110, 'style': 'decimal'},
                    },
                ],
                'benefits': [],
            },
        ),
        (
            HEADERS,
            {
                'login': 'webalex',
                'start_date': '2022-01-01',
                'end_date': '2022-01-16',
            },
            200,
            {
                'full_period': True,
                'start_date': '2022-01-01',
                'end_date': '2022-01-16',
                'period_receipt': [
                    {
                        'field_name': 'Обычные дни',
                        'field_type': 'day',
                        'value': {'value': 15.12, 'style': 'decimal'},
                    },
                    {
                        'field_name': 'Обычные дни',
                        'field_type': 'night',
                        'value': {'value': 16.13, 'style': 'decimal'},
                    },
                    {
                        'field_name': 'Праздничные дни',
                        'field_type': 'night',
                        'value': {'value': 18.15, 'style': 'decimal'},
                    },
                    {
                        'field_name': 'Праздничные дни',
                        'field_type': 'day',
                        'value': {'value': 17.14, 'style': 'decimal'},
                    },
                ],
                'indicators': [
                    {
                        'field_name': 'hour_cost',
                        'value': {'value': 0, 'style': 'decimal'},
                    },
                    {
                        'field_name': 'hour_cost_ratio',
                        'value': {'value': 0, 'style': 'decimal'},
                    },
                    {
                        'field_name': 'Рейтинг',
                        'value': {'value': 12.12, 'style': 'percent'},
                    },
                    {
                        'field_name': 'Дисциплина',
                        'value': {'value': 13.13, 'style': 'decimal'},
                    },
                    {
                        'field_name': 'unified_qa_ratio',
                        'value': {'value': 0, 'style': 'decimal'},
                    },
                    {
                        'field_name': 'production',
                        'value': {'value': 5.0, 'style': 'decimal'},
                    },
                    {
                        'field_name': 'norm',
                        'value': {'value': 2618.17, 'style': 'decimal'},
                    },
                ],
                'details': [
                    {
                        'line': 'first',
                        'action': 'close',
                        'cost': {'value': 10, 'style': 'decimal'},
                        'count': 11,
                        'sum': {'value': 110, 'style': 'decimal'},
                    },
                ],
                'benefits': [
                    {
                        'field_name': 'Коэффицент',
                        'value': {'value': 0.14, 'style': 'percent'},
                    },
                ],
            },
        ),
        (
            HEADERS,
            {
                'login': 'liambaev',
                'start_date': '2022-01-01',
                'end_date': '2022-01-16',
            },
            200,
            {
                'full_period': True,
                'start_date': '2022-01-01',
                'end_date': '2022-01-16',
                'period_receipt': [],
                'indicators': [],
                'benefits': [],
                'details': [
                    {
                        'line': 'urgent',
                        'action': 'close',
                        'cost': {'value': 10, 'style': 'decimal'},
                        'count': 10,
                        'sum': {'value': 100, 'style': 'decimal'},
                    },
                    {
                        'line': 'urgent',
                        'action': 'comment',
                        'cost': {'value': 6.12, 'style': 'decimal'},
                        'count': 10,
                        'sum': {'value': 61.25, 'style': 'decimal'},
                    },
                ],
            },
        ),
        (
            HEADERS_HRMS,
            {
                'login': 'agent_hrms',
                'start_date': '2022-01-15',
                'end_date': '2022-01-16',
            },
            200,
            {
                'full_period': False,
                'start_date': '2022-01-15',
                'end_date': '2022-01-16',
                'period_receipt': [
                    {
                        'field_name': 'hrms_bonus',
                        'field_type': 'all',
                        'value': {'style': 'decimal', 'value': 746.6},
                    },
                    {
                        'field_name': 'hrms_bonus_fact',
                        'field_type': 'all',
                        'value': {'style': 'decimal', 'value': 447},
                    },
                ],
                'indicators': [
                    {
                        'field_name': 'qa_ratio',
                        'value': {'style': 'decimal', 'value': 0.6},
                    },
                    {
                        'field_name': 'efficiency_ratio',
                        'value': {'style': 'decimal', 'value': 1},
                    },
                ],
                'benefits': [],
                'details': [
                    {
                        'line': 'Отбор, мезонин 2-5',
                        'action': 'штуки',
                        'cost': {'value': 1.1, 'style': 'decimal'},
                        'count': 259,
                        'sum': {'value': 284.9, 'style': 'decimal'},
                    },
                    {
                        'line': 'Отбор товаров',
                        'action': 'штуки',
                        'cost': {'value': 1.1, 'style': 'decimal'},
                        'count': 36,
                        'sum': {'value': 39.6, 'style': 'decimal'},
                    },
                    {
                        'line': 'Отбор товаров КГТ',
                        'action': 'штуки',
                        'cost': {'value': 3.3, 'style': 'decimal'},
                        'count': 13,
                        'sum': {'value': 42.9, 'style': 'decimal'},
                    },
                    {
                        'line': 'Отбор, мезонин 1',
                        'action': 'штуки',
                        'cost': {'value': 0.96, 'style': 'decimal'},
                        'count': 395,
                        'sum': {'value': 379.2, 'style': 'decimal'},
                    },
                ],
            },
        ),
        (
            HEADERS_HRMS,
            {
                'login': 'agent_hrms',
                'start_date': '2022-01-16',
                'end_date': '2022-01-17',
            },
            200,
            {
                'full_period': False,
                'start_date': '2022-01-16',
                'end_date': '2022-01-17',
                'period_receipt': [],
                'indicators': [],
                'benefits': [],
                'details': [],
            },
        ),
        (
            HEADERS,
            {
                'login': 'user_not_agent',
                'start_date': '2022-01-01',
                'end_date': '2022-01-16',
            },
            403,
            {
                'start_date': '2022-01-01',
                'end_date': '2022-01-16',
                'details': [],
            },
        ),
    ],
)
@pytest.mark.translations(
    agent={
        'detailing_period_receipt_field_name_daytime_cost': {
            'ru': 'Обычные дни',
        },
        'detailing_period_receipt_field_name_night_cost': {
            'ru': 'Обычные дни',
        },
        'detailing_period_receipt_field_name_holidays_daytime_cost': {
            'ru': 'Праздничные дни',
        },
        'detailing_period_receipt_field_name_holidays_night_cost': {
            'ru': 'Праздничные дни',
        },
        'detailing_indicator_field_name_rating_prcnt': {'ru': 'Рейтинг'},
        'detailing_indicator_field_name_discipline_ratio': {
            'ru': 'Дисциплина',
        },
        'detailing_benefits_field_name_benefits_per_bo': {'ru': 'Коэффицент'},
    },
)
@pytest.mark.config(
    AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS,
    AGENT_DETAILING_INDICATORS_BY_PROJECT={
        'default': {
            'discipline_ratio': {'order': 4, 'style': 'decimal'},
            'hour_cost': {'order': 1, 'style': 'decimal'},
            'hour_cost_ratio': {'order': 2, 'style': 'decimal'},
            'rating_prcnt': {'order': 3, 'style': 'percent'},
            'unified_qa_ratio': {'order': 5, 'style': 'decimal'},
            'production': {'order': 6, 'style': 'decimal'},
            'norm': {'order': 7, 'style': 'decimal'},
        },
    },
    AGENT_DETAILING_BENEFITS_BY_PROJECT={
        'default': {'benefits_per_bo': {'order': 1, 'style': 'percent'}},
    },
)
async def test_piecework_detailing(
        web_app_client,
        mock_piecework_details,
        mock_piecework_calculation_load,
        mock_piecework_daily_load,
        mock_hrms_finances_one_person,
        headers,
        body,
        status,
        expected_data,
):
    mock_piecework_daily_load(
        response={
            'calculation': {'commited': True},
            'logins': [
                {
                    'login': 'webalex',
                    'date': '2022-01-01',
                    'bo': {
                        'daytime_cost': 1,
                        'night_cost': 2,
                        'holidays_daytime_cost': 1,
                        'holidays_night_cost': 2,
                    },
                },
                {
                    'login': 'webalex',
                    'date': '2022-01-02',
                    'bo': {
                        'daytime_cost': 0,
                        'night_cost': 0,
                        'holidays_daytime_cost': 2,
                        'holidays_night_cost': 2,
                    },
                },
            ],
        },
    )

    response = await web_app_client.post(
        '/piecework/basic-score/detailing', json=body, headers=headers,
    )
    assert response.status == status
    if status == 200:
        content = await response.json()
        assert content == expected_data
