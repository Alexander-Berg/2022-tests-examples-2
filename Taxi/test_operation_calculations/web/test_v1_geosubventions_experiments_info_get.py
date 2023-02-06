import http

import pytest


@pytest.mark.parametrize(
    'params, expected_status, expected_content',
    (
        pytest.param(
            {'tariff_zones': 'moscow,himki'},
            http.HTTPStatus.OK,
            {
                'time_m5_money_m10': {
                    'share': 0.11,
                    'shift_interval': -5,
                    'shift_guarantee': -10,
                },
                'time_p5_money_m10': {
                    'share': 0.11,
                    'shift_interval': 5,
                    'shift_guarantee': -10,
                },
                'geotool_main': {'share': 0.12},
                'geotool_empty': {'share': 0.13, 'is_empty': True},
            },
        ),
    ),
)
@pytest.mark.config(
    ATLAS_GEOSUBVENTIONS_EXPERIMENTS={
        '__default__': [
            {'share': 0.11, 'shift_guarantee': -10, 'shift_interval': -5},
            {'share': 0.11, 'shift_guarantee': -10, 'shift_interval': 5},
            {'share': 0.12},
            {'share': 0.13, 'is_empty': True},
        ],
    },
)
async def test_v1_geosubventions_experiment_info_get(
        web_app_client, params, expected_status, expected_content, caplog,
):
    response = await web_app_client.get(
        f'/v1/geosubventions/experiment_info/', params=params,
    )
    assert response.status == expected_status, await response.text()
    assert await response.json() == expected_content
