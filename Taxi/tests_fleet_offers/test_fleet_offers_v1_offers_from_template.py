import pytest

from tests_fleet_offers import utils

ENDPOINT = '/fleet/offers/v1/offers/from-template'


def build_params(kind, name):
    return {'kind': kind, 'name': name}


OK_PARAMS = [
    (
        'token2',
        'labor_contract',
        'offer_name',
        'fa1b0a45-bdcb-599e-9c0b-1a2ec58f627d',
        1,
    ),
    (
        'token1',
        'offer',
        'offer_name',
        '3f719db4-5d6b-5463-99a9-ac33e9ae5e17',
        0,
    ),
]


@pytest.mark.now('2020-01-01T12:00:00')
@pytest.mark.parametrize(
    'idempotency_token, kind, name, offer_id,  mds_calls', OK_PARAMS,
)
async def test_create(
        taxi_fleet_offers,
        mock_fleet_parks,
        mock_parks_replica,
        mock_billing_replication,
        mock_balance_replica,
        mockserver,
        pgsql,
        idempotency_token,
        kind,
        name,
        offer_id,
        mds_calls,
):
    @mockserver.handler(f'/service/templates/{kind}/0')
    def mock_mds_download(request):
        return mockserver.make_response('file_string_data', 200)

    @mockserver.handler(f'/park1/{offer_id}/0')
    def mock_mds_upload(request):
        return mockserver.make_response('OK', 200)

    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_fleet_headers(
            park_id='park1',
            content_type=(
                'application/vnd.openxmlformats-'
                'officedocument.wordprocessingml.document'
            ),
            idempotency_token=idempotency_token,
        ),
        params=build_params(kind=kind, name=name),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'signers_count': 0,
        'created_at': '2020-01-01T12:00:00+00:00',
        'id': offer_id,
        'is_enabled': True,
        'kind': kind,
        'name': name,
        'rev': 0,
    }

    assert mock_mds_download.times_called == mds_calls
    assert mock_mds_upload.times_called == mds_calls

    cursor = pgsql['fleet_offers'].cursor()
    cursor.execute(
        f"""
        SELECT
            id,
            name,
            rev,
            base_rev,
            idempotency_token
        FROM
            fleet_offers.active_offers
        WHERE
            park_id = \'park1\'
            AND id = \'{offer_id}\'
        """,
    )
    row = cursor.fetchone()
    assert row[0] == offer_id
    assert row[1] == 'offer_name'
    assert row[2] == 0
    assert row[3] == 0
    assert row[4] == idempotency_token

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
    assert row[0] == 0


async def test_already_exists(taxi_fleet_offers):
    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_fleet_headers(
            park_id='park1',
            idempotency_token='token1',
            content_type=(
                'application/vnd.openxmlformats-'
                'officedocument.wordprocessingml.document'
            ),
        ),
        params=build_params(kind='offer', name='new_offer_name'),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'offer_already_exists',
        'localized_message': 'Оферта уже существует',
    }
