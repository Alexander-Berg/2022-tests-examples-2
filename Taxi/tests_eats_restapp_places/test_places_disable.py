import psycopg2
import pytest

PARTNER_ID = 1
PLACE_ID = 42

HANDLE_URL = '/4.0/restapp-front/places/v1/disable?place_id={}'

VALID_HANDLE_REQUEST = {
    'reason_code': 47,
    'available_at': '2021-07-11T20:00:00+03:00',
    'orders_cancel': False,
}


@pytest.fixture(name='mock_eats_core_disable')
def _mock_eats_core_disable(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/disable')
    def _mock_authorizer(request):
        assert request.json == {
            'reason_code': 47,
            'available_at': '2021-07-11T17:00:00+00:00',
            'orders_cancel': False,
            'vendor_user_id': 1,
        }

        return mockserver.make_response(status=200, json={'isSuccess': True})


@pytest.mark.pgsql(
    'eats_restapp_places', files=['fill_switching_on_request.sql'],
)
async def test_places_disable_success(
        taxi_eats_restapp_places,
        mock_eats_core_disable,
        mock_restapp_authorizer,
        pgsql,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json=VALID_HANDLE_REQUEST,
    )

    assert response.status_code == 200

    cur = pgsql['eats_restapp_places'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cur.execute(
        'SELECT * '
        'FROM eats_restapp_places.switching_on_requested '
        'WHERE place_id = {!r}'.format(PLACE_ID),
    )
    place_deleted = cur.fetchone()
    assert place_deleted is None


async def test_places_disable_403_on_authorizer_403(
        taxi_eats_restapp_places, mock_restapp_authorizer_403,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json=VALID_HANDLE_REQUEST,
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Error: no access to the place or no permissions',
    }


async def test_places_disable_400_on_core_400(
        taxi_eats_restapp_places, mock_eats_core_400, mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        json=VALID_HANDLE_REQUEST,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error: core request failed',
    }
