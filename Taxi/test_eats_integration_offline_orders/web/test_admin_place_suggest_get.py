import http
import typing

import pytest


def _make_response(place_ids: typing.Iterable[str], has_more: bool = False):
    return {
        'places': [{'place_id': place_id} for place_id in place_ids],
        'has_more': has_more,
    }


@pytest.mark.parametrize(
    ('params', 'expected_response'),
    (
        pytest.param(
            {},
            _make_response(
                [
                    'place_id__1',
                    'place_id__2',
                    'place_id__3',
                    'place_id__4',
                    'place_id__5',
                ],
                False,
            ),
            id='no-place-id',
        ),
        pytest.param(
            {'limit': 1}, _make_response(['place_id__1'], True), id='limit',
        ),
        pytest.param(
            {'limit': 1, 'offset': 1},
            _make_response(['place_id__2'], True),
            id='offset',
        ),
        pytest.param(
            {'place_id': 'place_id__3'},
            _make_response(['place_id__3'], False),
            id='specific-place-id',
        ),
        pytest.param(
            {'place_id': '__3'},
            _make_response(['place_id__3'], False),
            id='place-id-part',
        ),
        pytest.param(
            {'place_id': 'place_id_'},
            _make_response(
                [
                    'place_id__1',
                    'place_id__2',
                    'place_id__3',
                    'place_id__4',
                    'place_id__5',
                ],
                False,
            ),
            id='place-id-part-2',
        ),
        pytest.param(
            {'place_id': 'not-found'},
            _make_response([], False),
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql'],
)
async def test_admin_place_suggest_get(
        taxi_eats_integration_offline_orders_web, params, expected_response,
):
    response = await taxi_eats_integration_offline_orders_web.get(
        '/admin/v1/place/suggest', params=params,
    )
    body = await response.json()
    assert response.status == http.HTTPStatus.OK
    assert body == expected_response
