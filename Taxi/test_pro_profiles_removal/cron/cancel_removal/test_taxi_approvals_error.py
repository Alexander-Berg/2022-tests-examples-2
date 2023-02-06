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
        (id, phone_pd_id, state, draft_id, created_at)
        VALUES
        (
            '00000000-0000-0000-0000-000000000001',
            'phone_pd_id1',
            'cancel_requested',
            1,
            '2022-06-01'
        );
        """,
        """
        INSERT INTO pro_profiles_removal.profiles
        (request_id, park_id, contractor_profile_id, block_id)
        VALUES
        (
            '00000000-0000-0000-0000-000000000001',
            'parkid11',
            'profileid11',
            'blockid1111'
        );
        """,
    ],
)
async def test_get_draft_error(
        cron_context: context.Context,
        mockserver,
        mock_blocklist,
        mock_taxi_approvals,
):
    @mock_blocklist('/internal/blocklist/v1/delete')
    async def _delete_block(request: http.Request):
        return {}

    @mock_taxi_approvals('/drafts/1/')
    async def _get_status():
        return mockserver.make_response(status=500)

    await run_cron.main(
        ['pro_profiles_removal.crontasks.cancel_removal', '-t', '0'],
    )

    rows = await cron_context.pg.main_master.fetch(
        """
        SELECT id
        FROM pro_profiles_removal.requests
        WHERE state = 'cancel_requested'
        """,
    )
    assert len(rows) == 1
    assert rows[0]['id'] == uuid.UUID('00000000-0000-0000-0000-000000000001')


@pytest.mark.now('2022-06-30T12:00:00+00:00')
@pytest.mark.pgsql(
    'pro_profiles_removal',
    queries=[
        """
        INSERT INTO pro_profiles_removal.requests
        (id, phone_pd_id, state, draft_id, created_at)
        VALUES
        (
            '00000000-0000-0000-0000-000000000001',
            'phone_pd_id1',
            'cancel_requested',
            1,
            '2022-06-01'
        );
        """,
        """
        INSERT INTO pro_profiles_removal.profiles
        (request_id, park_id, contractor_profile_id, block_id)
        VALUES
        (
            '00000000-0000-0000-0000-000000000001',
            'parkid11',
            'profileid11',
            'blockid1111'
        );
        """,
    ],
)
async def test_finish_draft_error(
        cron_context: context.Context,
        mockserver,
        mock_blocklist,
        mock_taxi_approvals,
):
    @mock_blocklist('/internal/blocklist/v1/delete')
    async def _delete_block(request: http.Request):
        return {}

    @mock_taxi_approvals('/drafts/1/')
    async def _get_status():
        return {'id': 1, 'version': 2, 'status': 'need_approval'}

    @mock_taxi_approvals('/drafts/1/finish/')
    async def _finish_draft(request):
        return mockserver.make_response(status=500)

    await run_cron.main(
        ['pro_profiles_removal.crontasks.cancel_removal', '-t', '0'],
    )

    rows = await cron_context.pg.main_master.fetch(
        """
        SELECT id
        FROM pro_profiles_removal.requests
        WHERE state = 'cancel_requested'
        """,
    )
    assert len(rows) == 1
    assert rows[0]['id'] == uuid.UUID('00000000-0000-0000-0000-000000000001')
