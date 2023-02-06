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
            'pending',
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
@pytest.mark.config(PRO_PROFILES_REMOVAL_TIME_BEFORE_REMOVING={'days': 27})
async def test_ok(
        cron_context: context.Context,
        mock_blocklist,
        mock_taxi_approvals,
        mock_driver_login,
        mock_unique_drivers,
        mock_tags,
        mock_parks,
):
    @mock_unique_drivers('/internal/unique-drivers/v1/remove-profiles')
    async def _remove_profiles(request: http.Request):
        assert request.json == {'profile_id_in_set': ['parkid11_profileid11']}
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

    @mock_driver_login('/driver-login/v1/bulk-logout')
    async def _logout(request: http.Request):
        assert request.json == {
            'comment': 'PROFILES_REMOVAL',
            'is_full_logout': True,
            'drivers': [
                {'park_id': 'parkid11', 'driver_profile_id': 'profileid11'},
            ],
        }
        return {
            'drivers': [
                {
                    'driver': {
                        'park_id': 'parkid11',
                        'driver_profile_id': 'profileid11',
                    },
                    'is_logged_out': True,
                },
            ],
        }

    @mock_taxi_approvals('/drafts/1/')
    async def _get_status():
        return {'id': 1, 'version': 2, 'status': 'approved'}

    @mock_blocklist('/internal/blocklist/v1/delete')
    async def _delete_block(request: http.Request):
        body = request.json
        assert body['identity']['name'] == 'pro-profiles-removal'
        assert body['identity']['type'] == 'service'
        assert body['identity']['id'] == 'blockid1111'
        assert body['block']['block_id'] == body['identity']['id']
        assert body['block']['comment'] == 'This profile has been removed'
        return {}

    @mock_taxi_approvals('/drafts/1/finish/')
    async def _finish_draft(request: http.Request):
        assert request.json == {
            'final_status': 'succeeded',
            'comment': 'Profiles have been removed',
        }
        return {'id': 1, 'version': 1, 'status': 'succeeded'}

    @mock_parks('/internal/driver-profiles/profile')
    async def _fire_profile(request: http.Request):
        assert request.query == {'park_id': 'parkid11', 'id': 'profileid11'}
        assert request.json == {
            'driver_profile': {'set': {'work_status': 'fired'}},
        }
        return {
            'driver_profile': {
                'id': 'profileid',
                'park_id': 'parkid',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phones': ['phone'],
                'work_status': 'fired',
            },
        }

    await run_cron.main(
        ['pro_profiles_removal.crontasks.remove_profiles', '-t', '0'],
    )

    rows = await cron_context.pg.main_master.fetch(
        """
        SELECT id
        FROM pro_profiles_removal.requests requests
        WHERE state = 'completed'
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
            'pending',
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
@pytest.mark.config(
    PRO_PROFILES_REMOVAL_TIME_BEFORE_REMOVING={'days': 27},
    PRO_PROFILES_REMOVAL_DRAFT_INFO={
        'author': 'author_login',
        'description': 'draft description',
        'summon_users': ['summon_user'],
        'ticket_info': {
            'description': 'ticket description',
            'summary': 'ticket summary',
        },
    },
)
async def test_not_approved_draft(
        cron_context: context.Context, mock_taxi_approvals,
):
    @mock_taxi_approvals('/drafts/1/')
    async def _get_status():
        return {'id': 1, 'version': 2, 'status': 'need_approval'}

    @mock_taxi_approvals('/drafts/1/summon_approvers/')
    async def _summon_approvers(request: http.Request):
        assert request.json == {'summon_users': ['summon_user']}
        return {
            'summoned_users': [
                {'login': 'summon_user', 'summoned': '2022-06-30T12:00:00'},
            ],
        }

    await run_cron.main(
        ['pro_profiles_removal.crontasks.remove_profiles', '-t', '0'],
    )

    rows = await cron_context.pg.main_master.fetch(
        """
        SELECT id
        FROM pro_profiles_removal.requests requests
        WHERE state = 'pending'
        """,
    )
    assert len(rows) == 1
    assert rows[0]['id'] == uuid.UUID('00000000-0000-0000-0000-000000000001')
