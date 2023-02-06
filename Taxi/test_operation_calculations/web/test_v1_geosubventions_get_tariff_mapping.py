import http

import pytest


@pytest.mark.parametrize(
    'expected_responce, expected_status',
    [
        pytest.param(
            {
                'code': 'BadRequest',
                'message': (
                    'Для следующих тарифов не задан'
                    ' маппинг на тарифы Яндекса: vezeteconom'
                ),
            },
            http.HTTPStatus.BAD_REQUEST,
        ),
        pytest.param(
            {'child_tariff': ['uberkids'], 'econom': ['uberx', 'vezeteconom']},
            http.HTTPStatus.OK,
            marks=pytest.mark.config(
                TARIFF_CLASSES_MAPPING={
                    'uberkids': {'classes': ['child_tariff']},
                    'uberx': {'classes': ['econom']},
                    'vezeteconom': {'classes': ['econom']},
                },
            ),
        ),
    ],
)
async def test_v1_geosubventions_get_tariff_mappings(
        web_app_client, expected_responce, expected_status,
):
    response = await web_app_client.get(
        '/v1/geosubventions/get_tariff_mappings/',
    )
    status = response.status
    msg = await response.json()
    assert msg == expected_responce
    assert status == expected_status
