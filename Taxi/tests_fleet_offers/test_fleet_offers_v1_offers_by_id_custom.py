import pytest

from tests_fleet_offers import utils

ENDPOINT = '/fleet/offers/v1/offers/by-id/custom'


def build_params(offer_id, kind, resign_required=None):
    params = {'id': offer_id, 'kind': kind}
    if resign_required is not None:
        params['resign_required'] = resign_required

    return params


OK_PARAMS = [
    (
        '00000000-0000-0000-0000-000000000001',
        'custom_driver_balance',
        None,
        'token1',
        0,
        0,
        0,
    ),
    (
        '00000000-0000-0000-0000-000000000001',
        'custom_main',
        None,
        'token11',
        1,
        1,
        0,
    ),
    (
        '00000000-0000-0000-0000-000000000001',
        'custom_driver_balance',
        False,
        'token11',
        1,
        1,
        0,
    ),
    (
        '00000000-0000-0000-0000-000000000001',
        'custom_main',
        True,
        'token11',
        1,
        1,
        1,
    ),
]


@pytest.mark.parametrize(
    'offer_id, kind, resign_required, idempotency_token,'
    'mds_calls, expected_rev, expected_base_rev',
    OK_PARAMS,
)
async def test_create(
        taxi_fleet_offers,
        mock_fleet_parks,
        mock_parks_replica,
        mock_billing_replication,
        mock_balance_replica,
        mockserver,
        load,
        pgsql,
        offer_id,
        kind,
        resign_required,
        idempotency_token,
        mds_calls,
        expected_rev,
        expected_base_rev,
):
    @mockserver.handler(f'/park1/{offer_id}/{expected_rev}')
    def mock_mds(request):
        return mockserver.make_response('OK', 200)

    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_fleet_headers(
            park_id='park1',
            idempotency_token=idempotency_token,
            content_type=(
                'application/vnd.openxmlformats-'
                'officedocument.wordprocessingml.document'
            ),
        ),
        params=build_params(
            offer_id=offer_id, kind=kind, resign_required=resign_required,
        ),
        data=utils.FILE_DATA,
    )

    assert response.status_code == 204, response.text

    assert mock_mds.times_called == mds_calls

    cursor = pgsql['fleet_offers'].cursor()
    cursor.execute(
        f"""
        SELECT
            rev,
            base_rev,
            kind,
            idempotency_token
        FROM
            fleet_offers.active_offers
        WHERE
            park_id = \'park1\'
            AND id = \'{offer_id}\'
        """,
    )
    row = cursor.fetchone()
    assert row[0] == expected_rev
    assert row[1] == expected_base_rev
    assert row[2] == kind
    assert row[3] == idempotency_token

    cursor.execute(
        f"""
        SELECT
            MAX(rev)
        FROM
            fleet_offers.offers
        WHERE
            park_id = \'park1\'
            AND id = \'{offer_id}\'
        """,
    )
    row = cursor.fetchone()
    assert row[0] == expected_rev


async def test_not_found(taxi_fleet_offers, load):
    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_fleet_headers(
            park_id='park1',
            idempotency_token='token2',
            content_type=(
                'application/vnd.openxmlformats-'
                'officedocument.wordprocessingml.document'
            ),
        ),
        params=build_params(
            offer_id='00000000-0000-0000-0000-100000000001',
            kind='custom_main',
        ),
        data=utils.FILE_DATA,
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'offer_not_found',
        'localized_message': 'Оферта не найдена',
    }
