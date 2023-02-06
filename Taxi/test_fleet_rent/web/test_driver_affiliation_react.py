import pytest

from fleet_rent.generated.web import web_context as wc


async def check_state(web_context: wc.Context, affiliation_id, state):
    aff = await web_context.pg_access.affiliation.sys.get_record(
        affiliation_id,
    )
    assert aff.state.to_raw() == state


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.affiliations
    (record_id, state,
     park_id, local_driver_id,
     original_driver_park_id, original_driver_id,
     creator_uid, created_at_tz)
    VALUES
    ('affiliation_id', 'new',
     'park_id', 'local_driver_id',
     'driver_park_id', 'driver_id',
     'creator_uid', '2020-01-01+00')
        """,
    ],
)
async def test_accept(
        web_app_client, web_context: wc.Context, driver_auth_headers, stq,
):
    response404 = await web_app_client.post(
        '/driver/v1/periodic-payments/affiliations/react',
        params={'affiliation_id': 'bad_id', 'reaction': 'accept'},
        headers=driver_auth_headers,
    )
    assert response404.status == 404
    await check_state(web_context, 'affiliation_id', 'new')

    response200 = await web_app_client.post(
        '/driver/v1/periodic-payments/affiliations/react',
        params={'affiliation_id': 'affiliation_id', 'reaction': 'accept'},
        headers=driver_auth_headers,
    )
    assert response200.status == 200
    await check_state(web_context, 'affiliation_id', 'active')

    # Repeating is accepted but skipped internally
    response200_2 = await web_app_client.post(
        '/driver/v1/periodic-payments/affiliations/react',
        params={'affiliation_id': 'affiliation_id', 'reaction': 'accept'},
        headers=driver_auth_headers,
    )
    assert response200_2.status == 200
    await check_state(web_context, 'affiliation_id', 'active')

    response409 = await web_app_client.post(
        '/driver/v1/periodic-payments/affiliations/react',
        params={'affiliation_id': 'affiliation_id', 'reaction': 'reject'},
        headers=driver_auth_headers,
    )
    assert response409.status == 409
    await check_state(web_context, 'affiliation_id', 'active')

    assert not stq.create_affiliated_driver.has_calls


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.affiliations
    (record_id, state,
     park_id, local_driver_id,
     original_driver_park_id, original_driver_id,
     creator_uid, created_at_tz)
    VALUES
    ('affiliation_id', 'new',
     'park_id', NULL,
     'driver_park_id', 'driver_id',
     'creator_uid', '2020-01-01+00')
        """,
    ],
)
async def test_accept_nolocal(
        web_app_client, web_context: wc.Context, driver_auth_headers, stq,
):
    response404 = await web_app_client.post(
        '/driver/v1/periodic-payments/affiliations/react',
        params={'affiliation_id': 'bad_id', 'reaction': 'accept'},
        headers=driver_auth_headers,
    )
    assert response404.status == 404
    await check_state(web_context, 'affiliation_id', 'new')

    assert not stq.create_affiliated_driver.has_calls
    response200 = await web_app_client.post(
        '/driver/v1/periodic-payments/affiliations/react',
        params={'affiliation_id': 'affiliation_id', 'reaction': 'accept'},
        headers=driver_auth_headers,
    )
    assert response200.status == 200
    await check_state(web_context, 'affiliation_id', 'accepted')
    assert stq.create_affiliated_driver.has_calls

    # Repeating is accepted but skipped internally
    response200_2 = await web_app_client.post(
        '/driver/v1/periodic-payments/affiliations/react',
        params={'affiliation_id': 'affiliation_id', 'reaction': 'accept'},
        headers=driver_auth_headers,
    )
    assert response200_2.status == 200
    await check_state(web_context, 'affiliation_id', 'accepted')

    response409 = await web_app_client.post(
        '/driver/v1/periodic-payments/affiliations/react',
        params={'affiliation_id': 'affiliation_id', 'reaction': 'reject'},
        headers=driver_auth_headers,
    )
    assert response409.status == 409
    await check_state(web_context, 'affiliation_id', 'accepted')


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.affiliations
    (record_id, state,
     park_id, local_driver_id,
     original_driver_park_id, original_driver_id,
     creator_uid, created_at_tz)
    VALUES
    ('affiliation_id', 'new',
     'park_id', 'local_driver_id',
     'driver_park_id', 'driver_id',
     'creator_uid', '2020-01-01+00')
        """,
    ],
)
async def test_reject(
        web_app_client, web_context: wc.Context, driver_auth_headers, stq,
):
    response404 = await web_app_client.post(
        '/driver/v1/periodic-payments/affiliations/react',
        params={'affiliation_id': 'bad_id', 'reaction': 'reject'},
        headers=driver_auth_headers,
    )
    assert response404.status == 404

    response200 = await web_app_client.post(
        '/driver/v1/periodic-payments/affiliations/react',
        params={'affiliation_id': 'affiliation_id', 'reaction': 'reject'},
        headers=driver_auth_headers,
    )
    assert response200.status == 200

    # Repeating is accepted but skipped internally
    response200_2 = await web_app_client.post(
        '/driver/v1/periodic-payments/affiliations/react',
        params={'affiliation_id': 'affiliation_id', 'reaction': 'reject'},
        headers=driver_auth_headers,
    )
    assert response200_2.status == 200

    response409 = await web_app_client.post(
        '/driver/v1/periodic-payments/affiliations/react',
        params={'affiliation_id': 'affiliation_id', 'reaction': 'accept'},
        headers=driver_auth_headers,
    )
    assert response409.status == 409

    assert not stq.create_affiliated_driver.has_calls
