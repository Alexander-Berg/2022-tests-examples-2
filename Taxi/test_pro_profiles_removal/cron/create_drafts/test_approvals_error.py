import uuid

import pytest

from testsuite.utils import http

from pro_profiles_removal.generated.cron import cron_context as context
from pro_profiles_removal.generated.cron import run_cron


@pytest.mark.now('2022-06-30T12:00:00+00:00')
@pytest.mark.pgsql(
    'pro_profiles_removal',
    queries=[
        """
        INSERT INTO pro_profiles_removal.requests
        (id, phone_pd_id, state, created_at)
        VALUES
        (
            '00000000-0000-0000-0000-000000000001',
            'phone_pd_id1',
            'profiles_disabled',
            '2022-06-01'
        );
        """,
        """
        INSERT INTO pro_profiles_removal.profiles
        (request_id, park_id, contractor_profile_id)
        VALUES
        ('00000000-0000-0000-0000-000000000001', 'parkid11', 'profileid11');
        """,
    ],
)
async def test_approvals_error(
        cron_context: context.Context,
        mockserver,
        mock_taxi_approvals,
        mock_blocklist,
        mock_driver_profiles,
):
    @mock_taxi_approvals('/drafts/create/')
    async def _create_draft(request: http.Request):
        return mockserver.make_response(
            json={'code': '500', 'message': 'error'}, status=500,
        )

    @mock_blocklist('/internal/blocklist/v1/add')
    async def _add_block(request: http.Request):
        return {'block_id': 'block_id'}

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    def _retrieve_by_id(request: http.Request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid11_profileid11',
                    'data': {'license': {'pd_id': 'pd_id_1111'}},
                },
            ],
        }

    await run_cron.main(
        ['pro_profiles_removal.crontasks.create_drafts', '-t', '0'],
    )

    rows = await cron_context.pg.main_master.fetch(
        """
        SELECT id, draft_id, block_id
        FROM pro_profiles_removal.requests requests
            JOIN pro_profiles_removal.profiles profiles
            ON profiles.request_id = requests.id
        WHERE state = 'profiles_disabled'
        """,
    )
    assert len(rows) == 1
    assert rows[0]['id'] == uuid.UUID('00000000-0000-0000-0000-000000000001')
    assert not rows[0]['block_id']
    assert not rows[0]['draft_id']
