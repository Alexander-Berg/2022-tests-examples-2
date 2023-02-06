import aiohttp.web
import pytest

from testsuite.utils import http

from fleet_rent.generated.cron import cron_context as context_module
from fleet_rent.utils import create_affiliated_driver


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
        INSERT INTO rent.affiliations
        (record_id,
         park_id, local_driver_id,
         original_driver_park_id, original_driver_id,
         creator_uid, created_at_tz, modified_at_tz,
         state)
        VALUES ('affiliation_id',
                'park_id', NULL,
                'original_driver_park_id', 'original_driver_id',
                'creator_uid', NOW(), NOW(),
                'accepted')
        """,
    ],
)
@pytest.mark.now('2020-01-01T01:00:00')
async def test_success(
        cron_context: context_module.Context, load_json, mock_parks,
):
    mock_data = load_json('test_success.json')

    @mock_parks('/driver-profiles/list')
    async def _list_dps(request: http.Request):
        assert request.json == mock_data['parks_dp_list']['request']
        return mock_data['parks_dp_list']['response']

    @mock_parks('/internal/driver-profiles/create')
    async def _create_dp(request: http.Request):
        assert request.json == mock_data['parks_create_driver']['request']
        return mock_data['parks_create_driver']['response']

    affiliation = await cron_context.pg_access.affiliation.sys.get_record(
        'affiliation_id',
    )

    await create_affiliated_driver.run(cron_context, affiliation)

    updated_affiliation = (
        await cron_context.pg_access.affiliation.sys.get_record(
            'affiliation_id',
        )
    )

    assert updated_affiliation.state.to_raw() == 'active'
    assert updated_affiliation.local_driver_id == 'new_driver_id'


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
        INSERT INTO rent.affiliations
        (record_id,
         park_id, local_driver_id,
         original_driver_park_id, original_driver_id,
         creator_uid, created_at_tz, modified_at_tz,
         state)
        VALUES ('affiliation_id',
                'park_id', NULL,
                'original_driver_park_id', 'original_driver_id',
                'creator_uid', NOW(), NOW(),
                'accepted')
        """,
    ],
)
@pytest.mark.now('2020-01-01T01:00:00')
async def test_collided(
        cron_context: context_module.Context,
        load_json,
        mock_parks,
        patch,
        mock_driver_profiles,
):
    mock_data = load_json('test_collided.json')

    @mock_parks('/driver-profiles/list')
    async def _list_dps(request: http.Request):
        assert request.json == mock_data['parks_dp_list']['request']
        return mock_data['parks_dp_list']['response']

    @mock_parks('/internal/driver-profiles/create')
    async def _create_dp(request: http.Request):
        assert request.json == mock_data['parks_create_driver']['request']
        return aiohttp.web.json_response(
            status=400, data=mock_data['parks_create_driver']['response'],
        )

    @patch('taxi.clients.personal.PersonalApiClient.bulk_store')
    async def _mock_store(
            data_type, request_values, validate=True, log_extra=None,
    ):
        assert data_type == 'phones'
        assert request_values == ['+70003906587']
        return [{'id': 'phone_id_1'}]

    @mock_driver_profiles('/v1/driver/profiles/retrieve_by_phone')
    async def _driver_profiles(request: http.Request):
        assert request.json == mock_data['driver_profiles']['request']
        return mock_data['driver_profiles']['response']

    affiliation = await cron_context.pg_access.affiliation.sys.get_record(
        'affiliation_id',
    )

    await create_affiliated_driver.run(cron_context, affiliation)

    updated_affiliation = (
        await cron_context.pg_access.affiliation.sys.get_record(
            'affiliation_id',
        )
    )

    assert updated_affiliation.state.to_raw() == 'creating_collision'
    assert updated_affiliation.local_driver_id == 'collided_driver_id'


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
        INSERT INTO rent.affiliations
        (record_id,
         park_id, local_driver_id,
         original_driver_park_id, original_driver_id,
         creator_uid, created_at_tz, modified_at_tz,
         state)
        VALUES ('affiliation_id',
                'park_id', NULL,
                'original_driver_park_id', 'original_driver_id',
                'creator_uid', NOW(), NOW(),
                'accepted')
        """,
    ],
)
@pytest.mark.now('2020-01-01T01:00:00')
async def test_failed(
        cron_context: context_module.Context, load_json, mock_parks,
):
    mock_data = load_json('test_failed.json')

    @mock_parks('/driver-profiles/list')
    async def _list_dps(request: http.Request):
        assert request.json == mock_data['parks_dp_list']['request']
        return mock_data['parks_dp_list']['response']

    @mock_parks('/internal/driver-profiles/create')
    async def _create_dp(request: http.Request):
        assert request.json == mock_data['parks_create_driver']['request']
        return aiohttp.web.json_response(
            status=400, data=mock_data['parks_create_driver']['response'],
        )

    affiliation = await cron_context.pg_access.affiliation.sys.get_record(
        'affiliation_id',
    )

    await create_affiliated_driver.run(cron_context, affiliation)

    updated_affiliation = (
        await cron_context.pg_access.affiliation.sys.get_record(
            'affiliation_id',
        )
    )

    assert updated_affiliation.state.to_raw() == 'creation_error'
    assert updated_affiliation.local_driver_id is None
