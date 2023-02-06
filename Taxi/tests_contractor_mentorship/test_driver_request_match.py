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
    default_value={
        'ignore_newbie_checks': False,
        'chat_icon': 'mentorship_widget_exp',
        'match_driver': True,
    },
    clauses=[],
)
async def test_contractor_request_match(
        taxi_contractor_mentorship,
        stq,
        unique_drivers,
        fleet_parks,
        driver_orders,
):
    unique_drivers.set_retrieve_by_uniques('nudid2', 'd2', 'p2')
    unique_drivers.set_retrieve_by_profiles('nudid2', 'd2', 'p2')

    fleet_parks.set_response('rus')

    driver_orders.set_response(False)

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
            'icon_type': 'mentorship_widget_exp',
        },
    }
    assert stq.contractor_mentorship_initialize_request.times_called == 1
    stq_kwargs = stq.contractor_mentorship_initialize_request.next_call()[
        'kwargs'
    ]
    stq_kwargs.pop('log_extra')
    assert stq_kwargs == {'unique_driver_id': 'nudid2'}


@pytest.mark.experiments3(
    is_config=False,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_mentorship_user_groups',
    consumers=['contractor-mentorship'],
    default_value={'group_id': '1_test'},
    clauses=[],
)
@pytest.mark.ydb(files=['insert_mentorship_and_free_mentor.sql'])
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
        'match_driver': True,
    },
    clauses=[],
)
@pytest.mark.now('2021-10-31T11:20:00.000+0000')
async def test_stq_request_match(stq_runner, mockserver, ydb):
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
                    'lat': 55.5,
                    'lon': 37.5,
                    'timestamp': 1630479600,
                },
                'type': 'raw',
            },
        )

    await stq_runner.contractor_mentorship_initialize_request.call(
        task_id=f'some_id',
        args=[],
        kwargs={'unique_driver_id': 'nudid2'},
        expect_fail=False,
    )

    assert profiles_response.times_called == 1
    assert personal_response.times_called == 1
    assert fleet_rent_response.times_called == 1
    assert trackstory_response.times_called == 1

    cursor = ydb.execute(
        'SELECT * FROM mentorships where newbie_unique_driver_id = "nudid2"',
    )

    assert cursor[0].rows[0] == {
        'created_at': 1635679200000000,
        'id': b'10',
        'mentor_full_name': b'Tim',
        'mentor_last_read_at': None,
        'mentor_park_driver_profile_id': b'park1_driver1',
        'mentor_phone_pd_id': b'+78005553535_id',
        'mentor_unique_driver_id': b'unique1',
        'newbie_last_read_at': None,
        'newbie_park_driver_profile_id': b'p2_d2',
        'newbie_unique_driver_id': b'nudid2',
        'original_connected_dttm': 1635679200000000,
        'status': b'matched',
        'country_id': b'rus',
    }


@pytest.mark.experiments3(
    is_config=False,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_mentorship_user_groups',
    consumers=['contractor-mentorship'],
    default_value={'group_id': '1_test'},
    clauses=[],
)
@pytest.mark.ydb(files=['insert_mentorship_and_mentor_gha.sql'])
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_mentorship_country_settings',
    consumers=['contractor-mentorship'],
    default_value={
        'ignore_newbie_checks': False,
        'chat_icon': 'mentorship_widget_exp',
        'match_driver': True,
    },
    clauses=[],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geo_nodes(_DEFAULT_GEONODES)
async def test_stq_request_match_no_mentor(stq_runner, mockserver, ydb):
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
                    'lat': 55.5,
                    'lon': 37.5,
                    'timestamp': 1630479600,
                },
                'type': 'raw',
            },
        )

    await stq_runner.contractor_mentorship_initialize_request.call(
        task_id=f'some_id',
        args=[],
        kwargs={'unique_driver_id': 'nudid2'},
        expect_fail=True,
    )

    assert profiles_response.times_called == 1
    assert personal_response.times_called == 1
    assert fleet_rent_response.times_called == 1
    assert trackstory_response.times_called == 1


@pytest.mark.experiments3(
    is_config=False,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_mentorship_user_groups',
    consumers=['contractor-mentorship'],
    default_value={'group_id': '1_test'},
    clauses=[],
)
@pytest.mark.ydb(files=['insert_mentorship_and_least_busy_mentor.sql'])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geo_nodes(_DEFAULT_GEONODES)
@pytest.mark.now('2021-10-31T11:20:00.000+0000')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='contractor_mentorship_country_settings',
    consumers=['contractor-mentorship'],
    default_value={
        'ignore_newbie_checks': False,
        'chat_icon': 'mentorship_widget_exp',
        'match_driver': True,
    },
    clauses=[],
)
async def test_stq_request_match_least_busy_mentor(
        stq_runner, mockserver, ydb,
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
                    'lat': 55.5,
                    'lon': 37.5,
                    'timestamp': 1630479600,
                },
                'type': 'raw',
            },
        )

    await stq_runner.contractor_mentorship_initialize_request.call(
        task_id=f'some_id',
        args=[],
        kwargs={'unique_driver_id': 'nudid2'},
        expect_fail=False,
    )

    assert profiles_response.times_called == 1
    assert personal_response.times_called == 1
    assert fleet_rent_response.times_called == 1
    assert trackstory_response.times_called == 1

    cursor = ydb.execute(
        'SELECT * FROM mentorships where newbie_unique_driver_id = "nudid2"',
    )

    assert cursor[0].rows[0] == {
        'created_at': 1635679200000000,
        'id': b'10',
        'mentor_full_name': b'Tim',
        'mentor_last_read_at': None,
        'mentor_park_driver_profile_id': b'park1_driver2',
        'mentor_phone_pd_id': b'+78005553535_id',
        'mentor_unique_driver_id': b'unique2',
        'newbie_last_read_at': None,
        'newbie_park_driver_profile_id': b'p2_d2',
        'newbie_unique_driver_id': b'nudid2',
        'original_connected_dttm': 1635679200000000,
        'status': b'matched',
        'country_id': b'rus',
    }
