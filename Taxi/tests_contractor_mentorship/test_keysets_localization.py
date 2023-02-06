import pytest


MENTROSHIP_TRANSLATIONS = {
    'contractor_mentorship': {
        'to_newbie.mentorship_requested_from_stories_title': {
            'ru': '(rus)mentorship_requested_from_stories_title',
        },
        'to_newbie.mentorship_requested_from_stories_body': {
            'ru': '(rus)mentorship_requested_from_stories_body',
        },
        'to_newbie.mentorship_not_new_requested_from_stories_body': {
            'ru': '(rus)mentorship_not_new_requested_from_stories_body',
        },
        'to_newbie.mentorship_not_new_requested_from_stories_title': {
            'ru': '(rus)mentorship_not_new_requested_from_stories_title',
        },
        'to_mentor.newbie_matched': {
            'ru': '(rus) %(mentor_name)s, Я %(newbie_name)s',
        },
        'to_mentor.newbie_in_progress': {
            'ru': (
                '(rus) Подопечный: %(newbie_name)s. Активность: %(avg_dp_7d)s.'
                ' Рейтинг: %(rate_avg_7d)s. Число часов на линии: %(sh_7d)s.'
            ),
        },
        'to_mentor.newbie_succeeded': {
            'ru': (
                '(rus) Подопечный: %(newbie_name)s. '
                'Активность: %(avg_dp_14d)s. Рейтинг: %(rate_avg_14d)s. '
                'Число часов на линии: %(sh_14d)s. Тест: %(correct_answers)s. '
                'Успех.'
            ),
        },
    },
    'contractor_mentorship_africa': {
        'to_newbie.mentorship_requested_from_stories_title': {
            'ru': '(afr)mentorship_requested_from_stories_title',
        },
        'to_newbie.mentorship_requested_from_stories_body': {
            'ru': '(afr)mentorship_requested_from_stories_body',
        },
        'to_newbie.mentorship_not_new_requested_from_stories_body': {
            'ru': '(afr)mentorship_not_new_requested_from_stories_body',
        },
        'to_newbie.mentorship_not_new_requested_from_stories_title': {
            'ru': '(afr)mentorship_not_new_requested_from_stories_title',
        },
        'to_mentor.newbie_matched': {
            'ru': '(afr) %(mentor_name)s, Я %(newbie_name)s',
        },
        'to_mentor.newbie_in_progress': {
            'ru': (
                '(afr) Подопечный: %(newbie_name)s. '
                'Активность: %(avg_dp_7d)s. '
                'Число часов на линии: %(sh_7d)s. '
            ),
        },
        'to_mentor.newbie_succeeded': {
            'ru': (
                '(afr) Подопечный: %(newbie_name)s. '
                'Активность: %(avg_dp_14d)s. '
                'Число часов на линии: %(sh_14d)s. '
                'Отличные результаты! '
            ),
        },
    },
}

MENTROSHIP_PARTIAL_TRANSLATIONS = {
    'contractor_mentorship': {
        'to_newbie.mentorship_requested_from_stories_title': {
            'ru': '(rus)mentorship_requested_from_stories_title',
        },
        'to_newbie.mentorship_requested_from_stories_body': {
            'ru': '(rus)mentorship_requested_from_stories_body',
        },
        'to_mentor.newbie_matched': {
            'ru': '(rus) %(mentor_name)s, Я %(newbie_name)s',
        },
        'to_mentor.newbie_in_progress': {
            'ru': (
                '(rus) Подопечный: %(newbie_name)s. Активность: %(avg_dp_7d)s.'
                ' Рейтинг: %(rate_avg_7d)s. Число часов на линии: %(sh_7d)s.'
            ),
        },
        'to_mentor.newbie_succeeded': {
            'ru': (
                '(rus) Подопечный: %(newbie_name)s. '
                'Активность: %(avg_dp_14d)s. Рейтинг: %(rate_avg_14d)s. '
                'Число часов на линии: %(sh_14d)s. Тест: %(correct_answers)s. '
                'Успех.'
            ),
        },
    },
    'contractor_mentorship_africa': {
        'to_newbie.mentorship_requested_from_stories_body': {
            'ru': '(afr)mentorship_requested_from_stories_body',
        },
        'to_mentor.newbie_in_progress': {
            'ru': (
                '(afr) Подопечный: %(newbie_name)s. '
                'Активность: %(avg_dp_7d)s. '
                'Число часов на линии: %(sh_7d)s. '
            ),
        },
        'to_mentor.newbie_succeeded': {
            'ru': (
                '(afr) Подопечный: %(newbie_name)s. '
                'Активность: %(avg_dp_14d)s. '
                'Число часов на линии: %(sh_14d)s. '
                'Отличные результаты! '
            ),
        },
    },
}

CHAT_RESPONSE_RUS = [
    {'is_new': True, 'message': '(rus) Vasiliy Petrovich, Я Иван Иванов'},
    {
        'is_new': True,
        'message': (
            '(rus) Подопечный: Иван Иванов. '
            'Активность: 99. Рейтинг: 4.9. '
            'Число часов на линии: 3.'
        ),
    },
    {
        'is_new': True,
        'message': (
            '(rus) Подопечный: Иван Иванов. '
            'Активность: 100. Рейтинг: 5. '
            'Число часов на линии: 4. '
            'Тест: 0. Успех.'
        ),
    },
]

CHAT_RESPONSE_AFR = [
    {'is_new': True, 'message': '(afr) Vasiliy Petrovich, Я Иван Иванов'},
    {
        'is_new': True,
        'message': (
            '(afr) Подопечный: Иван Иванов. '
            'Активность: 99. '
            'Число часов на линии: 3. '
        ),
    },
    {
        'is_new': True,
        'message': (
            '(afr) Подопечный: Иван Иванов. '
            'Активность: 100. '
            'Число часов на линии: 4. '
            'Отличные результаты! '
        ),
    },
]

HEADERS = {
    'User-Agent': 'Taximeter 9.1 (1234)',
    'Accept-Language': 'ru',
    'X-Request-Application-Version': '9.1',
    'X-YaTaxi-Driver-Profile-Id': 'd2',
    'X-YaTaxi-Park-Id': 'p2',
}


@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.parametrize(
    'config_keyset_settings, country_id, expected_keyset',
    [
        (None, 'rus', '(rus)'),
        (None, 'gha', '(rus)'),
        (
            {'abc': 'abc', '__default__': 'contractor_mentorship'},
            'gha',
            '(rus)',
        ),
        (
            {
                'rus': 'contractor_mentorship',
                'gha': 'contractor_mentorship_africa',
                '__default__': 'contractor_mentorship',
            },
            'gha',
            '(afr)',
        ),
        (
            {
                'rus': 'contractor_mentorship',
                'gha': 'contractor_mentorship_africa',
                '__default__': 'contractor_mentorship',
            },
            'rus',
            '(rus)',
        ),
    ],
)
@pytest.mark.parametrize(
    'has_finished, expected_response',
    [
        (
            True,
            {
                'body': 'mentorship_not_new_requested_from_stories_body',
                'title': 'mentorship_not_new_requested_from_stories_title',
            },
        ),
        (
            False,
            {
                'body': 'mentorship_requested_from_stories_body',
                'title': 'mentorship_requested_from_stories_title',
            },
        ),
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_mentorship_country_settings',
    consumers=['contractor-mentorship'],
    default_value={
        'ignore_newbie_checks': False,
        'chat_icon': 'mentorship_widget_exp',
        'match_driver': False,
    },
    clauses=[],
)
async def test_request(
        taxi_contractor_mentorship,
        taxi_config,
        unique_drivers,
        fleet_parks,
        driver_orders,
        config_keyset_settings,
        country_id,
        expected_keyset,
        has_finished,
        expected_response,
):
    if config_keyset_settings:
        taxi_config.set_values(
            {'CONTRACTOR_MENTORSHIP_KEYSET_SETTINGS': config_keyset_settings},
        )

    unique_drivers.set_retrieve_by_uniques('nudid2', 'd2', 'p2')
    unique_drivers.set_retrieve_by_profiles('nudid2', 'd2', 'p2')

    fleet_parks.set_response(country_id)

    driver_orders.set_response(has_finished)

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/request?is_accepted=True',
        headers=HEADERS,
        data={},
    )

    assert response.status_code == 200
    assert response.json() == {
        'message': {
            'body': expected_keyset + expected_response['body'],
            'title': expected_keyset + expected_response['title'],
            'icon_type': 'mentorship_widget_exp',
        },
    }


@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.parametrize(
    'config_keyset_settings, country_id, expected_response',
    [
        (None, 'rus', CHAT_RESPONSE_RUS),
        (None, 'gha', CHAT_RESPONSE_RUS),
        (
            {'abc': 'abc', '__default__': 'contractor_mentorship'},
            'gha',
            CHAT_RESPONSE_RUS,
        ),
        (
            {
                'rus': 'contractor_mentorship',
                'gha': 'contractor_mentorship_africa',
                '__default__': 'contractor_mentorship',
            },
            'gha',
            CHAT_RESPONSE_AFR,
        ),
        (
            {
                'rus': 'contractor_mentorship',
                'gha': 'contractor_mentorship_africa',
                '__default__': 'contractor_mentorship',
            },
            'rus',
            CHAT_RESPONSE_RUS,
        ),
    ],
)
@pytest.mark.ydb(files=['insert_succeeded_mentorships.sql'])
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_mentorship_country_settings',
    consumers=['contractor-mentorship'],
    default_value={
        'ignore_newbie_checks': False,
        'chat_icon': 'mentorship_widget_exp',
        'match_driver': False,
    },
    clauses=[],
)
async def test_chat_mentorship_succeeded(
        taxi_contractor_mentorship,
        taxi_config,
        unique_drivers,
        ydb,
        config_keyset_settings,
        country_id,
        expected_response,
):
    if config_keyset_settings:
        taxi_config.set_values(
            {'CONTRACTOR_MENTORSHIP_KEYSET_SETTINGS': config_keyset_settings},
        )

    unique_drivers.set_retrieve_by_profiles('nudid2', 'd2', 'p2')

    ydb.execute(
        f'UPDATE mentorships ' 'SET country_id = "{}";'.format(country_id),
    )

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert (
        response.json()['payload']['contacts'][0]['messages']
        == expected_response
    )


@pytest.mark.translations(**MENTROSHIP_PARTIAL_TRANSLATIONS)
@pytest.mark.config(
    CONTRACTOR_MENTORSHIP_KEYSET_SETTINGS={
        'rus': 'contractor_mentorship',
        'gha': 'contractor_mentorship_africa',
        '__default__': 'contractor_mentorship',
    },
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_mentorship_country_settings',
    consumers=['contractor-mentorship'],
    default_value={
        'ignore_newbie_checks': False,
        'chat_icon': 'mentorship_widget_exp',
        'match_driver': False,
    },
    clauses=[],
)
async def test_request_partial_translations(
        taxi_contractor_mentorship, unique_drivers, fleet_parks,
):
    unique_drivers.set_retrieve_by_uniques('nudid2', 'd2', 'p2')
    unique_drivers.set_retrieve_by_profiles('nudid2', 'd2', 'p2')

    fleet_parks.set_response('gha')

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/request?is_accepted=True',
        headers=HEADERS,
        data={},
    )

    assert response.status_code == 200
    assert response.json() == {
        'message': {
            'body': '(afr)mentorship_requested_from_stories_body',
            'title': '(rus)mentorship_requested_from_stories_title',
            'icon_type': 'mentorship_widget_exp',
        },
    }


@pytest.mark.translations(**MENTROSHIP_PARTIAL_TRANSLATIONS)
@pytest.mark.config(
    CONTRACTOR_MENTORSHIP_KEYSET_SETTINGS={
        'rus': 'contractor_mentorship',
        'gha': 'contractor_mentorship_africa',
        '__default__': 'contractor_mentorship',
    },
)
@pytest.mark.ydb(files=['insert_succeeded_mentorships.sql'])
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_mentorship_country_settings',
    consumers=['contractor-mentorship'],
    default_value={
        'ignore_newbie_checks': False,
        'chat_icon': 'mentorship_widget_exp',
        'match_driver': False,
    },
    clauses=[],
)
async def test_chat_mentorship_succeeded_partial_translations(
        taxi_contractor_mentorship, unique_drivers, ydb,
):
    unique_drivers.set_retrieve_by_profiles('nudid2', 'd2', 'p2')

    ydb.execute(f'UPDATE mentorships ' 'SET country_id = "{}";'.format('gha'))

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['payload']['contacts'][0]['messages'] == [
        {'is_new': True, 'message': '(rus) Vasiliy Petrovich, Я Иван Иванов'},
        {
            'is_new': True,
            'message': (
                '(afr) Подопечный: Иван Иванов. '
                'Активность: 99. '
                'Число часов на линии: 3. '
            ),
        },
        {
            'is_new': True,
            'message': (
                '(afr) Подопечный: Иван Иванов. '
                'Активность: 100. '
                'Число часов на линии: 4. '
                'Отличные результаты! '
            ),
        },
    ]
