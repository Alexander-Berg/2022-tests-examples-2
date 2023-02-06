import pytest


SCREEN_CONFIG = {
    'title': 'step_agreement.title',
    'enabled': True,
    'items': [
        {
            'type': 'header',
            'gravity': 'left',
            'subtitle': 'step_agreement.header.subtitle',
            'horizontal_divider_type': 'none',
        },
        {
            'text': 'text',
            'type': 'text',
            'markdown': True,
            'horizontal_divider_type': 'none',
        },
        {
            'title': 'default_button.title',
            'subtitle': 'default_button.title',
            'id': 'required_id',
            'type': 'default_check',
            'checked': True,
            'enabled': True,
            'payload': {'type': 'primary', 'required': True},
        },
        {
            'title': 'default_button.title',
            'subtitle': 'default_button.title',
            'id': 'not_required_id',
            'type': 'default_check',
            'checked': True,
            'enabled': True,
            'payload': {'type': 'primary', 'required': False},
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
}


@pytest.mark.experiments3(
    name='pro_selfemployed_fns_profiles_screen_agreement',
    consumers=['selfemployed_fns_profiles/state_initial'],
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value=SCREEN_CONFIG,
    clauses=[],
)
@pytest.mark.parametrize(
    'request_body, expected_response_code, '
    'expected_response, expected_agreements',
    [
        # all required agreements accepted
        (
            {
                'agreements': [
                    {'id': 'required_id', 'state': True},
                    {'id': 'not_required_id', 'state': True},
                ],
            },
            200,
            {'next_step': 'permission', 'step_index': 6, 'step_count': 9},
            {'required_id': True, 'not_required_id': True},
        ),
        # not all required agreements accepted
        (
            {
                'agreements': [
                    {'id': 'required_id', 'state': False},
                    {'id': 'not_required_id', 'state': True},
                ],
            },
            409,
            {
                'code': 'REQUIRED_AGREEMENTS_ERROR',
                'message': 'Не все обязательные соглашения приняты',
            },
            {'required_id': False, 'not_required_id': True},
        ),
    ],
)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id,
            phone_pd_id, is_phone_verified, profession)
        VALUES ('passport', 'puid1', 'PHONE_PD_ID', true, 'profession');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id)
         VALUES ('PHONE_PD_ID', 'FILLING', 'external_id');
        """,
    ],
)
async def test_post_agreement(
        taxi_selfemployed_fns_profiles,
        pgsql,
        prepare_post_rq,
        request_body,
        expected_response_code,
        expected_response,
        expected_agreements,
):
    response = await taxi_selfemployed_fns_profiles.post(
        json=request_body, **prepare_post_rq('agreement', 'puid1'),
    )
    assert response.status == expected_response_code
    content = response.json()
    assert content == expected_response

    sql = """
        SELECT agreements FROM se.ownpark_profile_forms_common
        WHERE phone_pd_id = 'PHONE_PD_ID'
        """
    cursor = pgsql['selfemployed_main'].cursor()
    cursor.execute(sql)
    agreements_raw = cursor.fetchone()
    assert agreements_raw == (expected_agreements,)


@pytest.mark.experiments3(
    name='pro_selfemployed_fns_profiles_screen_agreement',
    consumers=['selfemployed_fns_profiles/state_initial'],
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value=SCREEN_CONFIG,
    clauses=[],
)
@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.ownpark_profile_forms_contractor
            (initial_park_id, initial_contractor_id,
            phone_pd_id, is_phone_verified, profession)
        VALUES ('passport', 'puid1', 'PHONE_PD_ID', true, 'profession');
        INSERT INTO se.ownpark_profile_forms_common
            (phone_pd_id, state, external_id, agreements)
         VALUES
            ('PHONE_PD_ID', 'FILLING', 'external_id',
            '{"is_not_required": true}');
        """,
    ],
)
async def test_get_agreement(
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
                    'park_id': 'new_park_id',
                    'driver_id': 'new_contractor_id',
                    'profession': 'Driver',
                    'status': 'ready',
                    'city': 'Москва',
                },
            ],
        }

    request = prepare_get_rq(step='agreement', passport_uid='puid1')

    response = await taxi_selfemployed_fns_profiles.get(**request)
    assert response.status == 200
