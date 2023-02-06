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
            'cancel_requested',
            '2022-06-01'
        );
        """,
        """
        INSERT INTO pro_profiles_removal.profiles
        (request_id, park_id, contractor_profile_id)
        VALUES
        (
            '00000000-0000-0000-0000-000000000001',
            'parkid11',
            'profileid11'
        );
        """,
    ],
)
async def test_cancel_removal(
        cron_context: context.Context,
        mock_tags,
        mock_blocklist,
        mock_contractor_profiles_manager,
):
    @mock_contractor_profiles_manager(
        '/driver-profiles/contractors/v1/is-readonly',
    )
    async def _update_is_readonly(request: http.Request):
        body = request.json
        assert not body['is_readonly']
        return {}

    @mock_blocklist('/internal/blocklist/v1/delete')
    async def _delete_block(request: http.Request):
        return {}

    @mock_tags('/v1/assign')
    async def _v1_assign(request: http.Request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'rm__00000000000000000000000000000001'
        )
        assert request.json == {
            'provider': 'pro-profiles-removal',
            'entities': [
                {
                    'name': 'parkid11_profileid11',
                    'type': 'dbid_uuid',
                    'tags': {},
                },
            ],
        }
        return {'code': '200', 'message': 'ok'}

    await run_cron.main(
        ['pro_profiles_removal.crontasks.cancel_removal', '-t', '0'],
    )

    rows = await cron_context.pg.main_master.fetch(
        """
        SELECT id
        FROM pro_profiles_removal.requests
        WHERE state = 'canceled'
        """,
    )
    assert len(rows) == 1
    assert rows[0]['id'] == uuid.UUID('00000000-0000-0000-0000-000000000001')
    assert not _delete_block.has_calls
