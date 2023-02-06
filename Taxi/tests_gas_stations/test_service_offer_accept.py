import pytest

from tests_gas_stations import helpers

HANDLER = 'service/v1/offer/accept'

PARK_ID = 'db1'

BODY_WITH_LIMIT = {'limit': 1000, 'park_id': PARK_ID}

BODY_WITHOUT_LIMIT = {'park_id': PARK_ID}

BODY_WITH_INVALID_LIMIT = {'park_id': PARK_ID, 'limit': 1000000}


@pytest.mark.experiments3(
    filename='gas_stations_offer_default_limit_enabled.json',
)
@pytest.mark.parametrize(
    'request_body,fleet_parks_response,'
    'expected_limit,expected_response,expected_status_code',
    [
        (
            BODY_WITH_LIMIT,
            [helpers.DEFAULT_PARKS],
            1000,
            helpers.RESPONSE200_IN_PROGRESS,
            200,
        ),
        (
            BODY_WITHOUT_LIMIT,
            [helpers.DEFAULT_PARKS],
            1333,
            helpers.RESPONSE200_IN_PROGRESS,
            200,
        ),
        (BODY_WITH_INVALID_LIMIT, [helpers.DEFAULT_PARKS], None, None, 400),
        (BODY_WITHOUT_LIMIT, [], None, None, 404),
        (
            BODY_WITHOUT_LIMIT,
            [helpers.make_park_not_active(helpers.DEFAULT_PARKS)],
            None,
            None,
            400,
        ),
        (
            BODY_WITHOUT_LIMIT,
            [helpers.make_park_wrong_partner_source(helpers.DEFAULT_PARKS)],
            None,
            None,
            400,
        ),
    ],
)
async def test_service_offer_accept(
        taxi_gas_stations,
        mock_fleet_parks_list,
        partner_contracts,
        mongodb,
        pgsql,
        request_body,
        fleet_parks_response,
        expected_limit,
        expected_response,
        expected_status_code,
):
    partner_contracts.set_response(helpers.DEFAULT_CONTRACTS_RESPONSE)
    mock_fleet_parks_list.set_parks(fleet_parks_response)

    response = await taxi_gas_stations.post(HANDLER, json=request_body)

    assert response.status_code == expected_status_code
    response_json = response.json()

    if expected_response:
        assert expected_response == response_json
    if expected_status_code == 200:
        cursor = pgsql['gas_stations'].cursor()
        cursor.execute(
            'SELECT park_id, clid, started, finished '
            'from gas_stations.partner_contracts_acceptance',
        )
        result = list(row for row in cursor)[0]
        assert result[0] == PARK_ID
        assert result[1] == helpers.DEFAULT_PARKS['provider_config']['clid']
        assert result[2] is not None  # start was recorded
        assert result[3] is None  # finish is None
    if expected_limit:
        actual_limits = [
            x.json['params']['limit'] for x in partner_contracts.requests
        ]
        assert actual_limits == [expected_limit]


@pytest.mark.experiments3(
    filename='gas_stations_offer_default_limit_disabled.json',
)
async def test_service_offer_accept_no_limit_config(
        taxi_gas_stations, mock_fleet_parks_list, partner_contracts,
):
    partner_contracts.set_response(helpers.DEFAULT_CONTRACTS_RESPONSE)
    mock_fleet_parks_list.set_parks([helpers.DEFAULT_PARKS])

    response = await taxi_gas_stations.post(HANDLER, json=BODY_WITHOUT_LIMIT)

    assert response.status_code == 500
    assert not partner_contracts.requests
