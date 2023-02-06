import pytest


DEFAULT_CONFIG = {'SELFREG_PARK_GAMBLING_SETTINGS': {'park_choices_limit': 1}}

DEFAULT_PARK = {
    '_id': 'someid',
    'db_id': 'someparkid',
    'city': 'Москва, Одинцово',
    'address': 'someaddr',
    'contact_phone': ['somephone'],
    'location': {'lat': 3.14, 'lon': 2.78},
}


FLEET_VEHICLES_RESPONSE = {
    'vehicles': [
        {
            'park_id_car_id': 'excluded_park_by_car_car_id',
            'data': {
                'park_id': 'excluded_park_by_car',
                'number_normalized': 'C00lC4R',
            },
        },
    ],
}

DEFAULT_LICENSE = 'FOOLICENSE'  # as in db_selfreg_profiles.json

SELFREG_TRANSLATIONS = {
    'selfreg_employment_screen_description': {
        'ru': 'Смз без комиссии, парк с комиссией',
    },
    'selfreg_employment_screen_title': {'ru': 'Хотите сотрудничать напрямую?'},
    'self_employment_title_default': {'ru': 'Стать самозанятым'},
    'self_employment_subtitle_default': {'ru': 'Через приложение Мой налог'},
    'park_employment_title_default': {'ru': 'Сотрудничать с парком'},
    'park_employment_subtitle_default': {'ru': 'Предложим подходящий'},
    'selfreg_v2_parks_choices_error_no_parks_owncar_text': {
        'ru': 'Нет парков для водилы на тачиле',
    },
    'selfreg_v2_parks_choices_error_no_parks_rent_text': {
        'ru': 'Нет парков для водилы без тачилы',
    },
    'selfreg_v2_parks_choices_error_no_parks_uberdriver_text': {
        'ru': 'Нет парков для uberdriver',
    },
}


RESPONSE_1 = {
    'title': 'Хотите сотрудничать напрямую?',
    'description': 'Смз без комиссии, парк с комиссией',
    'employment_options': [
        {
            'type': 'self-fns',
            'title': 'Стать самозанятым',
            'subtitle': 'Через приложение Мой налог',
        },
        {
            'type': 'park',
            'title': 'Сотрудничать с парком',
            'subtitle': 'Предложим подходящий',
        },
    ],
}

RESPONSE_2 = {
    'title': 'Хотите сотрудничать напрямую?',
    'description': 'Смз без комиссии, парк с комиссией',
    'employment_options': [
        {
            'type': 'self-fns',
            'title': 'Стать самозанятым',
            'subtitle': 'Через приложение Мой налог',
        },
    ],
}

RESPONSE_3 = {
    'title': 'Хотите сотрудничать напрямую?',
    'description': 'Смз без комиссии, парк с комиссией',
    'employment_options': [
        {
            'type': 'park',
            'title': 'Сотрудничать с парком',
            'subtitle': 'Предложим подходящий',
        },
    ],
}

RESPONSE_4 = {
    'code': 'no_parks_owncar',
    'message': 'Нет парков для водилы на тачиле',
}

RESPONSE_5 = {
    'code': 'no_parks_rent',
    'message': 'Нет парков для водилы без тачилы',
}

RESPONSE_6 = {
    'code': 'no_parks_uberdriver',
    'message': 'Нет парков для uberdriver',
}


@pytest.mark.translations(
    taximeter_backend_driver_messages=SELFREG_TRANSLATIONS,
)
@pytest.mark.config(
    **DEFAULT_CONFIG,
    TAXIMETER_SELFREG_SETTINGS={
        'enabled_countries': ['rus'],
        'enable_fns_selfemployment': True,
    },
    TAXIMETER_FNS_SELF_EMPLOYMENT_PROMO_SETTINGS={
        'cities': ['Москва'],
        'countries': [],
        'dbs': [],
        'dbs_disable': [],
        'enable': True,
    },
)
@pytest.mark.parametrize(
    'token, user_agent, expect_empty_lists,'
    'expected_response, response_status',
    [
        pytest.param(
            'token_self_park', 'Taximeter 9.61 (1234)', False, RESPONSE_1, 200,
        ),
        pytest.param(
            'token_self', 'Taximeter 9.61 (1234)', True, RESPONSE_2, 200,
        ),
        pytest.param(
            'token_park', 'Taximeter 9.61 (1234)', False, RESPONSE_3, 200,
        ),
        pytest.param(
            'token1_404', 'Taximeter 9.61 (1234)', True, RESPONSE_4, 404,
        ),
        pytest.param(
            'token2_404', 'Taximeter 9.61 (1234)', True, RESPONSE_5, 404,
        ),
        pytest.param(
            'token3_404', 'Taximeter-Uber 9.61 (1234)', True, RESPONSE_6, 404,
        ),
        pytest.param(
            'token_bad_city', 'Taximeter 9.61 (1234)', False, {}, 400,
        ),
    ],
)
async def test_get_conditions(
        mockserver,
        mongo,
        mock_hiring_taxiparks_gambling,
        taxi_selfreg,
        mock_personal,
        mock_driver_profiles_maker,
        token,
        user_agent,
        expected_response,
        expect_empty_lists,
        response_status,
):
    driver_profiles_mock = mock_driver_profiles_maker(
        DEFAULT_LICENSE, 'excluded_park',
    )

    @mock_hiring_taxiparks_gambling('/taxiparks/choose')
    async def _gambling_handler(request):
        assert request.method == 'POST'
        assert request.headers['X-External-Service'] == 'taximeter_selfreg'
        body = request.json
        is_rent = body.pop('rent')

        park_name = 'park_' + ('rent' if is_rent else 'owncar')
        return {
            'finished': False,
            'parks': (
                []
                if expect_empty_lists
                else [{**DEFAULT_PARK, 'taximeter_name': park_name}]
            ),
        }

    response = await taxi_selfreg.post(
        '/selfreg/v1/get-conditions',
        params={'token': token},
        headers={'User-Agent': user_agent},
    )
    assert response.status == response_status
    if response_status != 400:
        content = await response.json()
        assert content == expected_response
        assert mock_personal.store_licenses.times_called == 1
        assert _gambling_handler.has_calls
        assert driver_profiles_mock.retrieve_by_license_handler.has_calls
