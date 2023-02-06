import pytest

TAGS_CONFIG = dict(
    SELFREG_MOCK_TAGS_BY_TYPE_STEP={
        'driver': {
            'common': ['selfreg_v2_driver_unreg'],
            'start': ['selfreg_v2_driver_unreg_step_start'],
            'license': ['selfreg_v2_driver_unreg_step_license'],
            'car': ['selfreg_v2_driver_unreg_step_car'],
            'park': ['selfreg_v2_driver_unreg_step_park'],
        },
        'courier': {
            'common': ['selfreg_v2_courier_unreg'],
            'start': ['selfreg_v2_courier_unreg_step_start'],
        },
        'profi': {
            'common': ['selfreg_v2_profi_unreg'],
            'start': ['selfreg_v2_profi_unreg_step_start'],
        },
        'selfemployed': {},
    },
)


@pytest.mark.parametrize(
    'token, expect_code, call_personal, expect_response',
    [
        ('bad_token', 404, 0, None),
        (
            'old_token',
            200,
            1,
            {
                'city_id': 'Санкт-Петербург',
                'country_id': 'rus',
                'phone_pd_id': '+70009325297_personal',
                'selfreg_id': '5a7581722016667706734a33',
                'selfreg_type': 'driver',
                'mock_tags': [],
            },
        ),
        (
            'good_token',
            200,
            0,
            {
                'city_id': 'Москва',
                'country_id': 'rus',
                'phone_pd_id': 'phone_pd_id',
                'selfreg_id': '5a7581722016667706734a34',
                'mock_tags': [],
            },
        ),
    ],
)
async def test_internal_validate_ok(
        taxi_selfreg,
        mockserver,
        mock_personal,
        token,
        expect_code,
        call_personal,
        expect_response,
):
    response = await taxi_selfreg.get(
        '/internal/selfreg/v1/validate/', params={'token': token},
    )
    assert response.status == expect_code
    if expect_response:
        response = await response.json()
        assert response == expect_response
    assert mock_personal.store_phone.times_called == call_personal


@pytest.mark.config(**TAGS_CONFIG)
@pytest.mark.parametrize(
    'token, expect_code, expected_tags',
    [
        ('bad_token', 404, None),
        ('old_token', 200, ['selfreg_v2_driver_unreg']),
        ('token_profi', 200, ['selfreg_v2_profi_unreg']),
        (
            'token_step_start',
            200,
            ['selfreg_v2_driver_unreg', 'selfreg_v2_driver_unreg_step_start'],
        ),
        (
            'token_step_license',
            200,
            [
                'selfreg_v2_driver_unreg',
                'selfreg_v2_driver_unreg_step_license',
            ],
        ),
        ('token_step_permission', 200, ['selfreg_v2_driver_unreg']),
    ],
)
async def test_internal_validate_tags(
        taxi_selfreg,
        mockserver,
        mock_personal,
        token,
        expect_code,
        expected_tags,
):
    response = await taxi_selfreg.get(
        '/internal/selfreg/v1/validate/', params={'token': token},
    )
    assert response.status == expect_code
    if expected_tags is not None:
        response = await response.json()
        assert response['mock_tags'] == expected_tags
