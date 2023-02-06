import pytest

from tests_cargo_corp import utils


def _get_headers(x_b2b_client_id):
    return {'X-B2B-Client-Id': x_b2b_client_id}


@pytest.mark.config(
    CARGO_CORP_CLIENTS_WITH_SKIP_CLIENT_NOTIFY_OPTION=[utils.CORP_CLIENT_ID],
)
@pytest.mark.parametrize(
    ('x_b2b_client_id', 'expected_skip_client_notify_available'),
    [
        (utils.CORP_CLIENT_ID, True),
        ('some_long_id_string_of_length_32', False),
    ],
)
async def test_get_client_settings(
        taxi_cargo_corp,
        x_b2b_client_id,
        expected_skip_client_notify_available,
):
    response = await taxi_cargo_corp.get(
        '/v1/client/settings', headers=_get_headers(x_b2b_client_id),
    )
    assert response.status_code == 200

    assert (
        response.json()['options']['skip_client_notify_available']
        == expected_skip_client_notify_available
    )
