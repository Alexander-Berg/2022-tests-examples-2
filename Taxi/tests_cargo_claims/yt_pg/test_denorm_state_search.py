import datetime

import pytest

NOW = datetime.datetime.now(datetime.timezone.utc)
NOW_STR = NOW.isoformat()
IN_TWO_HOURS = NOW - datetime.timedelta(hours=2, minutes=1)
IN_TWO_HOURS_STR = IN_TWO_HOURS.isoformat()
TWO_HOURS_AGO = NOW - datetime.timedelta(hours=2, minutes=1)
TWO_HOURS_AGO_STR = TWO_HOURS_AGO.isoformat()
TWO_HOURS_LATER_STR = (
    NOW + datetime.timedelta(hours=2, minutes=1)
).isoformat()
FOUR_HOURS_LATER_STR = (
    NOW + datetime.timedelta(hours=4, minutes=1)
).isoformat()


@pytest.mark.pgsql(
    'cargo_claims',
    files=['cargo_claims.sql', 'points.sql', 'claim_points.sql'],
)
@pytest.mark.parametrize(
    'state, claim_id',
    (
        ('active', 'b04a64bb1d0147258337412c01176fa2'),
        ('finished', 'b04a64bb1d0147258337412c01176fa3'),
        ('delayed', 'b04a64bb1d0147258337412c01176fa1'),
    ),
)
@pytest.mark.usefixtures('yt_apply')
async def test_denorm_search_by_state(
        pgsql, taxi_cargo_claims, get_default_corp_client_id, state, claim_id,
):
    # make one order inactive and one delayed
    pgsql['cargo_claims'].conn.cursor().execute(
        f"""
        UPDATE cargo_claims.claims
        SET status = 'delivered_finish'
        WHERE uuid_id = 'b04a64bb1d0147258337412c01176fa3';
        UPDATE cargo_claims.claims
        SET due = '{TWO_HOURS_LATER_STR}'
        WHERE uuid_id = 'b04a64bb1d0147258337412c01176fa1';
        """,
    )

    response = await taxi_cargo_claims.post(
        '/v1/test/claim/search',
        json={
            'limit': 10,
            'offset': 0,
            'criterias': {
                'state': state,
                'corp_client_id': get_default_corp_client_id,
            },
        },
    )

    assert response.status_code == 200
    claims = response.json()['claims']
    assert len(claims) == 1
    assert claims[0]['claims']['uuid_id'] == claim_id


@pytest.mark.pgsql(
    'cargo_claims',
    files=['cargo_claims.sql', 'points.sql', 'claim_points.sql'],
)
@pytest.mark.parametrize(
    'state, claim_id, phone',
    (
        pytest.param(
            'active',
            'b04a64bb1d0147258337412c01176fa2',
            '70009050402',
            id='active',
        ),
        pytest.param(
            'finished',
            'b04a64bb1d0147258337412c01176fa3',
            '70009050403',
            id='finished',
        ),
        pytest.param(
            'delayed',
            'b04a64bb1d0147258337412c01176fa1',
            '70009050401',
            id='delayed',
        ),
    ),
)
@pytest.mark.usefixtures('yt_apply')
async def test_denorm_search_by_state_and_phone(
        pgsql,
        taxi_cargo_claims,
        get_default_corp_client_id,
        state,
        claim_id,
        phone,
):
    # make one order inactive and one delayed
    pgsql['cargo_claims'].conn.cursor().execute(
        f"""
        UPDATE cargo_claims.claims
        SET status = 'delivered_finish'
        WHERE uuid_id = 'b04a64bb1d0147258337412c01176fa3';
        UPDATE cargo_claims.claims
        SET due = '{TWO_HOURS_LATER_STR}'
        WHERE uuid_id = 'b04a64bb1d0147258337412c01176fa1';
        """,
    )

    response = await taxi_cargo_claims.post(
        '/v1/test/claim/search',
        json={
            'limit': 10,
            'offset': 0,
            'criterias': {
                'state': state,
                'corp_client_id': get_default_corp_client_id,
                'phone': phone,
            },
        },
    )

    assert response.status_code == 200
    claims = response.json()['claims']
    assert len(claims) == 1
    assert claims[0]['claims']['uuid_id'] == claim_id
