import pytest


MENTROSHIP_TRANSLATIONS = {
    'contractor_mentorship': {
        'to_newbie.mentorship_requested_from_stories_title': {
            'ru': 'Наставничество',
        },
        'to_newbie.mentorship_requested_from_stories_body': {
            'ru': 'Отлично, ваша заявка принята.',
        },
        'to_newbie.mentorship_not_new_requested_from_stories_body': {
            'ru': (
                'К сожалению, мы не сможем назначить вам Наставника. '
                'Стать подопечными могут только водители, '
                'которые ещё не выполняли заказы с сервисом.'
            ),
        },
        'to_newbie.mentorship_not_new_requested_from_stories_title': {
            'ru': 'Вы уже не новичок',
        },
    },
}

_DEFAULT_GEONODES = [
    {
        'name': 'br_root',
        'name_en': 'Basic Hierarchy',
        'name_ru': 'Базовая иерархия',
        'node_type': 'root',
    },
    {
        'name': 'br_russia',
        'name_en': 'Russia',
        'name_ru': 'Россия',
        'node_type': 'agglomeration',
        'parent_name': 'br_root',
        'region_id': '225',
    },
    {
        'name': 'br_moscow',
        'name_en': 'Moscow',
        'name_ru': 'Москва',
        'node_type': 'agglomeration',
        'parent_name': 'br_russia',
        'tariff_zones': ['moscow'],
    },
    {
        'name': 'br_moscow_adm',
        'name_en': 'Moscow (adm)',
        'name_ru': 'Москва (адм)',
        'node_type': 'node',
        'parent_name': 'br_moscow',
        'region_id': '213',
        'tariff_zones': ['moscow'],
    },
    {
        'name': 'br_spb',
        'name_en': 'St. Petersburg',
        'name_ru': 'Cанкт-Петербург',
        'node_type': 'agglomeration',
        'parent_name': 'br_russia',
        'tariff_zones': ['spb'],
        'region_id': '2',
    },
    {
        'name': 'br_uk',
        'name_en': 'UK',
        'name_ru': 'Великобритания',
        'node_type': 'agglomeration',
        'parent_name': 'br_root',
        'tariff_zones': ['london'],
        'region_id': '102',
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
@pytest.mark.config(CONTRACTOR_MENTORSHIP_REQ_MATCHING_ENABLED=True)
@pytest.mark.ydb(files=['insert_mentorships.sql'])
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_mentorship_country_settings',
    consumers=['contractor-mentorship'],
    clauses=[
        {
            'value': {
                'ignore_newbie_checks': False,
                'chat_icon': 'mentorship_widget',
                'match_driver': False,
            },
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_type': 'string',
                    'arg_name': 'country_id',
                    'value': 'rus',
                },
            },
        },
        {
            'value': {
                'ignore_newbie_checks': True,
                'chat_icon': 'mentorship_widget',
                'match_driver': False,
            },
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_type': 'string',
                    'arg_name': 'country_id',
                    'value': 'gha',
                },
            },
        },
    ],
)
@pytest.mark.parametrize(
    'country_id, has_finished, checks_performed',
    [('rus', False, True), ('gha', True, False), ('gha', False, False)],
)
async def test_contractor_request(
        taxi_contractor_mentorship,
        country_id,
        has_finished,
        checks_performed,
        ydb,
        stq,
        unique_drivers,
        fleet_parks,
        driver_orders,
):
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
            'body': 'Отлично, ваша заявка принята.',
            'title': 'Наставничество',
            'icon_type': 'mentorship_widget',
        },
    }
    assert stq.contractor_mentorship_initialize_request.times_called == 1
    stq_kwargs = stq.contractor_mentorship_initialize_request.next_call()[
        'kwargs'
    ]
    stq_kwargs.pop('log_extra')
    assert stq_kwargs == {'unique_driver_id': 'nudid2'}
    assert unique_drivers.retrieve_by_profiles.times_called == 1
    assert unique_drivers.retrieve_by_uniques.times_called == (
        1 if checks_performed else 0
    )
    assert driver_orders.has_finished.times_called == (
        1 if checks_performed else 0
    )

    cursor_mentorship = ydb.execute(
        'SELECT * FROM mentorships '
        'WHERE newbie_unique_driver_id = "nudid2" '
        'and status = "created"'
        f'and country_id = "{country_id}";',
    )
    assert len(cursor_mentorship) == 1
    assert len(cursor_mentorship[0].rows) == 1

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/request?is_accepted=True',
        headers=HEADERS,
        data={},
    )

    assert response.status_code == 200
    assert response.json() == {
        'message': {
            'body': 'Отлично, ваша заявка принята.',
            'title': 'Наставничество',
            'icon_type': 'mentorship_widget',
        },
    }
    assert stq.contractor_mentorship_initialize_request.times_called == 0
    assert unique_drivers.retrieve_by_profiles.times_called == 2
    assert unique_drivers.retrieve_by_uniques.times_called == (
        1 if checks_performed else 0
    )
    assert driver_orders.has_finished.times_called == (
        1 if checks_performed else 0
    )


@pytest.mark.config(CONTRACTOR_MENTORSHIP_REQ_MATCHING_ENABLED=True)
@pytest.mark.ydb(files=['insert_mentorships.sql'])
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
async def test_contractor_rejected(
        taxi_contractor_mentorship, stq, unique_drivers, driver_orders,
):

    unique_drivers.set_retrieve_by_uniques('nudid2', 'd2', 'p2')
    unique_drivers.set_retrieve_by_profiles('nudid2', 'd2', 'p2')

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/request?is_accepted=false',
        headers=HEADERS,
        data={},
    )

    assert response.status_code == 200
    assert response.json() == {'message': None}
    assert stq.contractor_mentorship_initialize_request.times_called == 0
    assert unique_drivers.retrieve_by_profiles.times_called == 1
    assert unique_drivers.retrieve_by_uniques.times_called == 1
    assert driver_orders.has_finished.times_called == 1

    # todo check yt


@pytest.mark.parametrize(
    'latitude,longitude,stq_fail, status',
    [
        pytest.param(1, 1, True, 'created'),
        pytest.param(55.5, 37.5, False, 'requested'),
    ],
)
@pytest.mark.experiments3(filename='contractor_mentorship_user_groups.json')
@pytest.mark.ydb(files=['insert_mentorships.sql', 'insert_stq_request.sql'])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geo_nodes(_DEFAULT_GEONODES)
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
async def test_stq_request(
        stq_runner, mockserver, ydb, latitude, longitude, stq_fail, status,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def profiles_response(request):
        return mockserver.make_response(
            status=200,
            json={
                'profiles': [
                    {
                        'data': {'phone_pd_ids': [{'pd_id': 'pdid2'}]},
                        'park_driver_profile_id': 'p2_d2',
                    },
                ],
            },
        )

    @mockserver.json_handler('personal/v1/phones/retrieve')
    def personal_response(request):
        return mockserver.make_response(
            status=200, json={'id': 'pdid2', 'value': '+70000000000'},
        )

    @mockserver.json_handler('fleet-rent/v1/sys/affiliations/by-driver')
    def fleet_rent_response(request):
        return mockserver.make_response(
            status=200,
            json={
                'records': [
                    {
                        'record_id': 'r2',
                        'park_id': 'p2',
                        'original_driver_park_id': 'p2',
                        'original_driver_id': 'd2',
                        'creator_uid': 'cu2',
                        'created_at': '2021-09-01T11:20:00.000000Z',
                        'modified_at': '2021-09-01T11:20:00.000000Z',
                        'state': 'active',
                    },
                ],
            },
        )

    @mockserver.json_handler('driver-trackstory/position')
    def trackstory_response(request):
        return mockserver.make_response(
            status=200,
            json={
                'position': {
                    'lat': latitude,
                    'lon': longitude,
                    'timestamp': 1630479600,
                },
                'type': 'raw',
            },
        )

    await stq_runner.contractor_mentorship_initialize_request.call(
        task_id=f'some_id',
        args=[],
        kwargs={'unique_driver_id': 'nudid2'},
        expect_fail=stq_fail,
    )

    assert profiles_response.times_called == 1
    assert personal_response.times_called == 1
    assert fleet_rent_response.times_called == 1
    assert trackstory_response.times_called == 1

    cursor_mentorship = ydb.execute(
        'SELECT * FROM mentorships '
        'WHERE newbie_unique_driver_id = "nudid2";',
    )
    assert len(cursor_mentorship) == 1
    assert len(cursor_mentorship[0].rows) == 1

    row = cursor_mentorship[0].rows[0]
    assert status == row['status'].decode(
        'utf-8',
    )  # `b` due to String format, not Utf8

    if not stq_fail:
        mentorships_id = row['id'].decode('utf-8')
        cursor_status = ydb.execute(
            'SELECT * FROM status_transitions '
            'WHERE mentorship_id = "{}";'.format(mentorships_id),
        )
        assert len(cursor_status) == 1
        assert len(cursor_status[0].rows) == 1

        row = cursor_status[0].rows[0]
        assert row['from'] == b'created'
        assert status == row['to'].decode('utf-8')


@pytest.mark.ydb(files=['insert_mentorships.sql'])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_contractor_without_unique(
        taxi_contractor_mentorship, unique_drivers,
):

    headers = {
        'User-Agent': 'Taximeter 9.1 (1234)',
        'Accept-Language': 'ru',
        'X-Request-Application-Version': '9.1',
        'X-YaTaxi-Driver-Profile-Id': 'test',
        'X-YaTaxi-Park-Id': 'test',
    }
    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/request?is_accepted=True',
        headers=headers,
        data={},
    )
    assert response.status_code == 200
    assert unique_drivers.retrieve_by_profiles.times_called == 1


@pytest.mark.translations(**MENTROSHIP_TRANSLATIONS)
@pytest.mark.ydb(files=['insert_mentorships.sql'])
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
async def test_contractor_is_not_new(
        ydb, taxi_contractor_mentorship, unique_drivers, driver_orders,
):
    unique_drivers.set_retrieve_by_uniques('nudid2', 'd2', 'p2')
    unique_drivers.set_retrieve_by_profiles('nudid2', 'd2', 'p2')

    driver_orders.set_response(True)

    response = await taxi_contractor_mentorship.post(
        'driver/v1/contractor-mentorship/v1/request?is_accepted=True',
        headers=HEADERS,
        data={},
    )

    assert response.status_code == 200
    assert response.json() == {
        'message': {
            'body': (
                'К сожалению, мы не сможем назначить вам Наставника. '
                'Стать подопечными могут только водители, '
                'которые ещё не выполняли заказы с сервисом.'
            ),
            'title': 'Вы уже не новичок',
            'icon_type': 'mentorship_widget_exp',
        },
    }
    cursor_mentorship = ydb.execute(
        'SELECT * FROM mentorships '
        'WHERE newbie_park_driver_profile_id = "p2_d2";',
    )
    assert len(cursor_mentorship) == 1
    assert not cursor_mentorship[0].rows

    assert unique_drivers.retrieve_by_profiles.times_called == 1
    assert unique_drivers.retrieve_by_uniques.times_called == 1
    assert driver_orders.has_finished.times_called == 1
