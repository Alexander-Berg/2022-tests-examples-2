import http

import pytest


@pytest.mark.parametrize(
    ('params', 'request_body', 'expected_code', 'expected_count'),
    (
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': '1'},
            http.HTTPStatus.OK,
            1,
            id='single',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': '1-10'},
            http.HTTPStatus.OK,
            10,
            id='interval',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': '1-10,12'},
            http.HTTPStatus.OK,
            11,
            id='single-and-interval',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': '1,2-5,10,12-15,7,20,D1,D5-D7'},
            http.HTTPStatus.OK,
            16,
            id='mix',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': 'D1-D5,Я1-Я5'},
            http.HTTPStatus.OK,
            10,
            id='letters-interval',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': 'B10'},
            http.HTTPStatus.OK,
            1,
            id='non-digit-single',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': 'D5D11-D5D15,1D5D11-1D5D15'},
            http.HTTPStatus.OK,
            10,
            id='mixed-digit-interval',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': 'Стол 1-Стол 5'},
            http.HTTPStatus.BAD_REQUEST,
            None,
            id='whitespace-in-name',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': ' 10 , 11-12 , D1-D2 '},
            http.HTTPStatus.OK,
            5,
            id='whitespace-between-groups',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': 'Стол 1'},
            http.HTTPStatus.BAD_REQUEST,
            None,
            id='whitespace-in-single-table',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': '1-a'},
            http.HTTPStatus.BAD_REQUEST,
            None,
            id='digit-non-digit-interval',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': 'D1-DD10'},
            http.HTTPStatus.BAD_REQUEST,
            None,
            id='bad-non-digit-interval',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': 'D10-D1'},
            http.HTTPStatus.BAD_REQUEST,
            None,
            id='reverse-non-digit-interval',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': '10-5'},
            http.HTTPStatus.BAD_REQUEST,
            None,
            id='invalid-interval',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': '10-10'},
            http.HTTPStatus.BAD_REQUEST,
            None,
            id='same-interval',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': '1-100'},
            http.HTTPStatus.OK,
            100,
            id='max-interval',
        ),
        pytest.param(
            {'place_id': 'place_id__1'},
            {'tables': '1-101'},
            http.HTTPStatus.BAD_REQUEST,
            None,
            id='too-many',
        ),
        pytest.param(
            {'place_id': 'not_found'},
            {'tables': '1'},
            http.HTTPStatus.NOT_FOUND,
            None,
            id='no-place',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_admin_tables_create_auto(
        taxi_eats_integration_offline_orders_web,
        patch,
        params,
        request_body,
        expected_code,
        expected_count,
):
    response = await taxi_eats_integration_offline_orders_web.post(
        '/admin/v1/tables/create_auto', params=params, json=request_body,
    )
    body = await response.json()
    assert response.status == expected_code
    if response.status != http.HTTPStatus.OK:
        return
    assert len(body['tables']) == expected_count
