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
async def test_accept(web_app_client, web_context: wc.Context):
    response404 = await web_app_client.post(
        '/v1/park/affiliations/mock-driver-react',
        params={
            'record_id': 'bad_id',
            'park_id': 'park_id',
            'reaction': 'accept',
        },
    )
    assert response404.status == 404
    await check_state(web_context, 'affiliation_id', 'new')

    response200 = await web_app_client.post(
        '/v1/park/affiliations/mock-driver-react',
        params={
            'record_id': 'affiliation_id',
            'park_id': 'park_id',
            'reaction': 'accept',
        },
    )
    assert response200.status == 200
    await check_state(web_context, 'affiliation_id', 'active')

    # Repeating is accepted but skipped internally
    response200_2 = await web_app_client.post(
        '/v1/park/affiliations/mock-driver-react',
        params={
            'record_id': 'affiliation_id',
            'park_id': 'park_id',
            'reaction': 'accept',
        },
    )
    assert response200_2.status == 200
    await check_state(web_context, 'affiliation_id', 'active')

    response409 = await web_app_client.post(
        '/v1/park/affiliations/mock-driver-react',
        params={
            'record_id': 'affiliation_id',
            'park_id': 'park_id',
            'reaction': 'reject',
        },
    )
    assert response409.status == 409
    await check_state(web_context, 'affiliation_id', 'active')


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
async def test_accept_nolocal(web_app_client, web_context: wc.Context):
    response404 = await web_app_client.post(
        '/v1/park/affiliations/mock-driver-react',
        params={
            'record_id': 'bad_id',
            'park_id': 'park_id',
            'reaction': 'accept',
        },
    )
    assert response404.status == 404
    await check_state(web_context, 'affiliation_id', 'new')

    response200 = await web_app_client.post(
        '/v1/park/affiliations/mock-driver-react',
        params={
            'record_id': 'affiliation_id',
            'park_id': 'park_id',
            'reaction': 'accept',
        },
    )
    assert response200.status == 200
    await check_state(web_context, 'affiliation_id', 'accepted')

    # Repeating is accepted but skipped internally
    response200_2 = await web_app_client.post(
        '/v1/park/affiliations/mock-driver-react',
        params={
            'record_id': 'affiliation_id',
            'park_id': 'park_id',
            'reaction': 'accept',
        },
    )
    assert response200_2.status == 200
    await check_state(web_context, 'affiliation_id', 'accepted')

    response409 = await web_app_client.post(
        '/v1/park/affiliations/mock-driver-react',
        params={
            'record_id': 'affiliation_id',
            'park_id': 'park_id',
            'reaction': 'reject',
        },
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
async def test_reject(web_app_client, web_context: wc.Context):
    response404 = await web_app_client.post(
        '/v1/park/affiliations/mock-driver-react',
        params={
            'record_id': 'bad_id',
            'park_id': 'park_id',
            'reaction': 'reject',
        },
    )
    assert response404.status == 404
    await check_state(web_context, 'affiliation_id', 'new')

    response200 = await web_app_client.post(
        '/v1/park/affiliations/mock-driver-react',
        params={
            'record_id': 'affiliation_id',
            'park_id': 'park_id',
            'reaction': 'reject',
        },
    )
    assert response200.status == 200
    await check_state(web_context, 'affiliation_id', 'rejected')

    # Repeating is accepted but skipped internally
    response200_2 = await web_app_client.post(
        '/v1/park/affiliations/mock-driver-react',
        params={
            'record_id': 'affiliation_id',
            'park_id': 'park_id',
            'reaction': 'reject',
        },
    )
    assert response200_2.status == 200
    await check_state(web_context, 'affiliation_id', 'rejected')

    response409 = await web_app_client.post(
        '/v1/park/affiliations/mock-driver-react',
        params={
            'record_id': 'affiliation_id',
            'park_id': 'park_id',
            'reaction': 'accept',
        },
    )
    assert response409.status == 409
    await check_state(web_context, 'affiliation_id', 'rejected')


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
async def test_prod_disabled(web_app_client, patch):
    from taxi import settings

    @patch('taxi.settings.get_environment')
    def _get_env():
        return settings.PRODUCTION

    response404 = await web_app_client.post(
        '/v1/park/affiliations/mock-driver-react',
        params={
            'record_id': 'affiliation_id',
            'park_id': 'park_id',
            'reaction': 'accept',
        },
    )
    assert response404.status == 404
