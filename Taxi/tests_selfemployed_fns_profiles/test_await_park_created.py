import pytest


@pytest.mark.experiments3(
    name='pro_selfemployed_fns_profiles_screen_await_park_created',
    consumers=['selfemployed_fns_profiles/state_filled'],
    is_config=True,
    default_value={'Invalid_case': 'never occured'},
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {'type': 'bool', 'init': {'arg_name': 'is_resident'}},
            'value': {
                'title': 'step_title_await_park_created',
                'items': [
                    {
                        'type': 'header',
                        'gravity': 'left',
                        'subtitle': 'step_await_park_created.header.subtitle',
                        'horizontal_divider_type': 'none',
                    },
                    {
                        'text': 'text',
                        'type': 'text',
                        'markdown': True,
                        'horizontal_divider_type': 'none',
                    },
                ],
                'bottom_items': [
                    {
                        'type': 'button',
                        'title': 'default_button.title',
                        'accent': True,
                        'payload': {
                            'url': 'https://yandex.ru/',
                            'type': 'navigate_url',
                            'is_external': True,
                        },
                        'horizontal_divider_type': 'none',
                    },
                ],
            },
        },
    ],
)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES
            ('passport', 'puid1', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state,
             address, apartment_number,
             postal_code, agreements,
             inn_pd_id, residency_state,
             created_park_id, created_contractor_id,
             salesforce_account_id, salesforce_requisites_case_id,
             initial_park_id, initial_contractor_id, external_id)
         VALUES
            ('PHONE_PD_ID', 'FINISHED',
             'address', '123',
             '1234567', '{"general": true, "gas_stations": false}',
             'inn_pd_id', 'RESIDENT',
             'created_park_id', 'created_contractor_id',
             NULL, NULL,
             'passport', 'puid1', 'external_id');
        """,
    ],
)
async def test_get_await_park_created(
        taxi_selfemployed_fns_profiles, mockserver, prepare_get_rq,
):
    @mockserver.json_handler(
        '/pro-profiles/platform/v1/profiles/drafts/find-by-passport-uid/v1',
    )
    def _find_by_passport(request):
        assert request.json == {'passport_uid': 'puid1'}
        return {
            'profiles': [
                {
                    'park_id': 'created_park_id',
                    'driver_id': 'created_contractor_id',
                    'profession': 'Driver',
                    'status': 'ready',
                    'city': 'Москва',
                },
            ],
        }

    request = prepare_get_rq(step='await-park-created', passport_uid='puid1')

    response = await taxi_selfemployed_fns_profiles.get(**request)
    assert response.status == 200
    content = response.json()
    assert content == {
        'title': 'Заголовок для await-park-created',
        'items': [
            {
                'horizontal_divider_type': 'none',
                'gravity': 'left',
                'subtitle': (
                    'Подзаголовок очередной кнопки для await-park-created'
                ),
                'type': 'header',
            },
            {
                'horizontal_divider_type': 'none',
                'markdown': True,
                'text': 'text',
                'type': 'text',
            },
        ],
        'bottom_items': [
            {
                'accent': True,
                'horizontal_divider_type': 'none',
                'payload': {
                    'url': 'https://yandex.ru/',
                    'is_external': True,
                    'type': 'navigate_url',
                },
                'title': 'Далее',
                'type': 'button',
            },
        ],
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES
            ('passport', 'puid1', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state,
             address, apartment_number,
             postal_code, agreements,
             inn_pd_id, residency_state,
             created_park_id, created_contractor_id,
             salesforce_account_id, salesforce_requisites_case_id,
             initial_park_id, initial_contractor_id, external_id)
         VALUES
            ('PHONE_PD_ID', 'FINISHED',
             'address', '123',
             '1234567', '{"general": true, "gas_stations": false}',
             'inn_pd_id', 'RESIDENT',
             'created_park_id', 'created_contractor_id',
             NULL, NULL,
             'passport', 'puid1', 'external_id');
        """,
    ],
)
async def test_post_await_park_created(
        taxi_selfemployed_fns_profiles, prepare_post_rq,
):
    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('await-park-created', 'puid1'),
    )
    assert response.status == 200
    content = response.json()
    assert content == {
        'next_step': 'requisites',
        'step_index': 8,
        'step_count': 9,
    }


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id, phone_pd_id)
        VALUES
            ('passport', 'puid1', 'PHONE_PD_ID');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state,
             address, apartment_number,
             postal_code, agreements,
             inn_pd_id, residency_state,
             created_park_id, created_contractor_id,
             salesforce_account_id, salesforce_requisites_case_id,
             initial_park_id, initial_contractor_id, external_id)
         VALUES
            ('PHONE_PD_ID', 'FILLED',
             'address', '123',
             '1234567', '{"general": true, "gas_stations": false}',
             'inn_pd_id', 'RESIDENT',
             'created_park_id', 'created_contractor_id',
             NULL, NULL,
             'passport', 'puid1', 'external_id');
        """,
    ],
)
async def test_post_await_park_created_park_not_finished(
        taxi_selfemployed_fns_profiles, prepare_post_rq,
):
    response = await taxi_selfemployed_fns_profiles.post(
        **prepare_post_rq('await-park-created', 'puid1'),
    )
    assert response.status == 409
