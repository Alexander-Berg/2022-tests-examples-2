import pytest


RETRIEVE_BY_PROFILES_RESPONSE = {
    'uniques': [
        {
            'park_driver_profile_id': 'sample_id',
            'data': {'unique_driver_id': 'mentoruid1'},
        },
    ],
}

MENTROSHIP_TRANSLATIONS = {
    'contractor_mentorship': {
        'to_mentor.newbie_matched': {
            'ru': '%(mentor_name)s, Я %(newbie_name)s',
        },
        'to_mentor.newbie_in_progress': {
            'ru': (
                'Подопечный: %(newbie_name)s. Активность: %(avg_dp_7d)s. '
                'Рейтинг: %(rate_avg_7d)s. Число часов на линии: %(sh_7d)s.'
            ),
        },
        'to_mentor.newbie_failed': {
            'ru': (
                'Подопечный: %(newbie_name)s. '
                'Активность: %(avg_dp_14d)s. Рейтинг: %(rate_avg_14d)s. '
                'Число часов на линии: %(sh_14d)s. Тест: %(correct_answers)s. '
                'Неудача.'
            ),
        },
        'to_mentor.newbie_succeeded': {
            'ru': (
                'Подопечный: %(newbie_name)s. '
                'Активность: %(avg_dp_14d)s. Рейтинг: %(rate_avg_14d)s. '
                'Число часов на линии: %(sh_14d)s. Тест: %(correct_answers)s. '
                'Успех.'
            ),
        },
        'to_newbie.mentor_matched': {
            'ru': '%(newbie_name)s, Я %(mentor_name)s. Я помогу вам в такси.',
        },
        'to_mentor.text_message_from_newbie': {
            'ru': 'Смска от %(newbie_name)s для %(mentor_name)s.',
        },
        'to_newbie.text_message_from_mentor': {
            'ru': 'Смска от %(mentor_name)s для %(newbie_name)s.',
        },
    },
}

TO_MENTOR_MATCHED_MESSAGE = {
    'is_new': True,
    'message': 'Vasiliy Petrovich, Я Иван Иванов',
}
TO_MENTOR_IN_PROGRESS_MESSAGE = {
    'is_new': True,
    'message': (
        'Подопечный: Иван Иванов. '
        'Активность: 100. Рейтинг: 5. '
        'Число часов на линии: 3.'
    ),
}

HEADERS = {
    'User-Agent': 'Taximeter 9.1 (1234)',
    'Accept-Language': 'ru',
    'X-Request-Application-Version': '9.1',
    'X-YaTaxi-Park-Id': 'np1',
    'X-YaTaxi-Driver-Profile-Id': 'nd1',
}


@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.ydb(files=['insert_mentorships_not_matched.sql'])
async def test_chat_mentorship_not_matched(
        taxi_contractor_mentorship, unique_drivers,
):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )
    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['payload']['contacts'] == []


@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.ydb(files=['insert_mentorships_matched.sql'])
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
async def test_chat_mentorship_matched(
        taxi_contractor_mentorship, unique_drivers,
):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )
    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert len(response.json()['payload']['contacts']) == 1
    assert response.json()['mentorship_icon'] == 'mentorship_widget_exp'
    assert response.json()['payload']['contacts'][0]['messages'] == [
        TO_MENTOR_MATCHED_MESSAGE,
    ]


@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.ydb(files=['insert_mentorships_matched.sql'])
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
async def test_chat_mentorship_matched_from_newbie(
        taxi_contractor_mentorship, unique_drivers,
):
    unique_drivers.retrieve_by_profiles_response = {
        'uniques': [
            {
                'park_driver_profile_id': 'sample_id',
                'data': {'unique_driver_id': 'newbieuid1'},
            },
        ],
    }
    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert (
        response.json()['payload']['contacts'][0]['deeplink']
        == 'whatsapp://send?text=%s&phone=%s'
    )
    assert response.json()['payload']['contacts'][0]['messages'] == [
        {
            'is_new': True,
            'message': (
                'Иван Иванов, Я Vasiliy Petrovich. Я помогу вам в такси.'
            ),
        },
    ]


@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.ydb(files=['insert_mentorships_in_progress.sql'])
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
async def test_chat_mentorship_in_progress(
        taxi_contractor_mentorship, unique_drivers,
):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )
    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['payload']['contacts'][0]['role'] == 'newbie'
    assert (
        response.json()['payload']['contacts'][0]['deeplink']
        == 'whatsapp://send?text=%s&phone=%s'
    )
    assert response.json()['payload']['contacts'][0]['messages'] == [
        TO_MENTOR_MATCHED_MESSAGE,
        TO_MENTOR_IN_PROGRESS_MESSAGE,
    ]


@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.ydb(files=['insert_mentorships_succeeded.sql'])
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
        taxi_contractor_mentorship, unique_drivers,
):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )
    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['mentorship_icon'] == 'mentorship_widget_exp'
    assert response.json()['payload']['contacts'][0]['role'] == 'newbie'
    assert (
        response.json()['payload']['contacts'][0]['deeplink']
        == 'whatsapp://send?text=%s&phone=%s'
    )
    assert response.json()['payload']['contacts'][0]['messages'] == [
        TO_MENTOR_MATCHED_MESSAGE,
        TO_MENTOR_IN_PROGRESS_MESSAGE,
        {
            'is_new': True,
            'message': (
                'Подопечный: Иван Иванов. '
                'Активность: 100. Рейтинг: 5. '
                'Число часов на линии: 3. '
                'Тест: 0. Успех.'
            ),
        },
    ]


@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.ydb(files=['insert_mentorships_failed.sql'])
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
async def test_chat_mentorship_failed(
        taxi_contractor_mentorship, unique_drivers,
):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )
    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['payload']['contacts'][0]['role'] == 'newbie'
    assert (
        response.json()['payload']['contacts'][0]['deeplink']
        == 'whatsapp://send?text=%s&phone=%s'
    )
    assert response.json()['payload']['contacts'][0]['messages'] == [
        TO_MENTOR_MATCHED_MESSAGE,
        TO_MENTOR_IN_PROGRESS_MESSAGE,
        {
            'is_new': True,
            'message': (
                'Подопечный: Иван Иванов. '
                'Активность: 100. Рейтинг: 5. '
                'Число часов на линии: 3. '
                'Тест: 0. Неудача.'
            ),
        },
    ]


@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.ydb(files=['insert_mentorships_from_crm_no_created_status.sql'])
async def test_chat_response_no_mentorship_for_driver(
        taxi_contractor_mentorship, unique_drivers,
):

    unique_drivers.retrieve_by_profiles_response = {
        'uniques': [
            {
                'park_driver_profile_id': 'sample_id',
                'data': {'unique_driver_id': 'unknown_unique_id'},
            },
        ],
    }

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200


@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.ydb(files=['insert_mentorships_from_crm_no_created_status.sql'])
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
async def test_chat_matched_from_crm(
        taxi_contractor_mentorship, unique_drivers,
):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['payload']['contacts'][0]['role'] == 'newbie'
    assert (
        response.json()['payload']['contacts'][0]['deeplink']
        == 'whatsapp://send?text=%s&phone=%s'
    )
    assert response.json()['payload']['contacts'][0]['messages'] == [
        TO_MENTOR_MATCHED_MESSAGE,
        TO_MENTOR_IN_PROGRESS_MESSAGE,
    ]


@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_mentorship_chat_expiration_days',
    consumers=['contractor-mentorship'],
    clauses=[
        {
            'value': {'expiration_days': 30},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_type': 'string',
                    'arg_name': 'driver_profile_id',
                    'value': 'nd1',
                },
            },
        },
    ],
)
@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.ydb(files=['insert_mentorships_matched_outdated.sql'])
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
async def test_chat_outdated_mentorships(
        taxi_contractor_mentorship, unique_drivers,
):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert len(response.json()['payload']['contacts']) == 1


@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.config(
    CONTRACTOR_MENTORSHIP_START_DATE='2021-11-11T00:02:00+00:00',
)
@pytest.mark.ydb(files=['insert_mentorships_matched.sql'])
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
async def test_chat_outdated_by_config_mentorships(
        taxi_contractor_mentorship, unique_drivers,
):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['payload']['contacts'] == []


@pytest.mark.now('2021-11-11T00:00:01+0000')
async def test_chat_no_driver_found(
        taxi_contractor_mentorship, unique_drivers,
):
    unique_drivers.retrieve_by_profiles_response = {'uniques': []}

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 400


@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.ydb(files=[])
async def test_chat_no_data(taxi_contractor_mentorship, unique_drivers):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200


@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.ydb(files=['insert_mentorships_in_progress.sql'])
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
async def test_chat_seen(taxi_contractor_mentorship, unique_drivers):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat/seen',
        json={'matching_id': '1'},
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert not response.json()['payload']['contacts'][0]['messages'][0][
        'is_new'
    ]
    assert not response.json()['payload']['contacts'][0]['messages'][1][
        'is_new'
    ]


@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.ydb(files=['insert_mentorships_in_progress.sql'])
async def test_chat_seen_not_ok(taxi_contractor_mentorship, unique_drivers):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )
    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat/seen',
        json={'invalid': 'body'},
        headers=HEADERS,
    )

    assert response.status_code == 400


# todo weird warning here
@pytest.mark.now('2021-11-11T00:00:01+0000')
@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.ydb(files=['insert_mentorships_succeeded.sql'])
@pytest.mark.parametrize(
    'is_header_polling_policy_incl',
    [
        pytest.param(True, marks=(pytest.mark.no_client_events_version,)),
        pytest.param(False),
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
async def test_chat_mentorship_headers(
        taxi_contractor_mentorship,
        unique_drivers,
        is_header_polling_policy_incl,
):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    if is_header_polling_policy_incl:
        parts = response.headers['X-Polling-Power-Policy'].split(', ')
        parts.sort()
        assert parts == [
            'background=1200s',
            'full=600s',
            'idle=1800s',
            'powersaving=1200s',
        ]
    else:
        assert response.json()['version']


@pytest.mark.ydb(files=['insert_mentorships_to_be_deleted.sql'])
async def test_chat_mentorship_to_be_deleted(
        taxi_contractor_mentorship, unique_drivers,
):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )
    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['payload']['contacts'] == []


@pytest.mark.ydb(files=['insert_mentorships_stopped.sql'])
async def test_chat_mentorship_topped(
        taxi_contractor_mentorship, unique_drivers,
):
    unique_drivers.retrieve_by_profiles_response = (
        RETRIEVE_BY_PROFILES_RESPONSE
    )
    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/chat', data={}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()['payload']['contacts'] == []
