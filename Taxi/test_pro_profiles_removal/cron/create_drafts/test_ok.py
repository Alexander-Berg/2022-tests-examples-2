import uuid

import pytest

from testsuite.utils import http

from pro_profiles_removal.generated.cron import cron_context as context
from pro_profiles_removal.generated.cron import run_cron


@pytest.mark.config(
    PRO_PROFILES_REMOVAL_DRAFT_INFO={
        'description': 'draft description',
        'author': 'author',
        'summon_users': ['summon_user'],
        'ticket_info': {
            'description': 'ticket description',
            'summary': 'ticket summary',
        },
        'link_to_profile': (
            'https://tariff-editor.taxi.tst.yandex-team.ru/show-driver?uuid='
        ),
    },
)
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
        )
        """,
        """
        INSERT INTO pro_profiles_removal.profiles
        (request_id, park_id, contractor_profile_id)
        VALUES
        ('00000000-0000-0000-0000-000000000001', 'parkid11', 'profileid11');
        """,
    ],
)
async def test_ok(
        cron_context: context.Context,
        mock_taxi_approvals,
        mock_blocklist,
        mock_driver_profiles,
):
    @mock_taxi_approvals('/drafts/create/')
    async def _create_draft(request: http.Request):
        assert request.json == {
            'request_id': (
                'pro-profiles-removal_00000000000000000000000000000001'
            ),
            'change_doc_id': '00000000000000000000000000000001',
            'service_name': 'pro-profiles-removal',
            'api_path': 'pro_profiles_removal_v1',
            'mode': 'poll',
            'run_manually': False,
            'data': {'profiles': ['parkid11_profileid11']},
            'description': 'draft description',
            'summon_users': ['summon_user'],
            'tickets': {
                'create_data': {
                    'summary': 'ticket summary',
                    'description': (
                        'ticket description\n'
                        'https://tariff-editor.taxi.tst.yandex-team.ru'
                        '/show-driver?uuid=profileid11'
                    ),
                },
            },
        }
        return {'id': 1, 'version': 1, 'status': 'need_approval'}

    @mock_blocklist('/internal/blocklist/v1/add')
    async def _add_block(request: http.Request):
        assert request.json == {
            'block': {
                'predicate_id': '44444444-4444-4444-4444-444444444444',
                'kwargs': {'license_id': 'pd_id_1111', 'park_id': 'parkid11'},
                'reason': {'key': 'blocklist.reasons.pro_profiles_removal'},
                'comment': 'The account removal has been requested by user',
                'mechanics': 'pro_profiles_removal',
                'disable_service': ['candidates'],
            },
            'identity': {
                'name': 'pro-profiles-removal',
                'type': 'service',
                'id': 'parkid11_profileid11_00000000000000000000000000000001',
            },
        }
        return {'block_id': 'block_id'}

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    def _retrieve_by_id(request: http.Request):
        assert request.json['projection'] == ['data.license.pd_id']
        assert request.json['id_in_set'] == ['parkid11_profileid11']
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
        WHERE state = 'pending'
        """,
    )
    assert len(rows) == 1
    assert rows[0]['id'] == uuid.UUID('00000000-0000-0000-0000-000000000001')
    assert rows[0]['draft_id'] == 1
    assert rows[0]['block_id'] == 'block_id'


@pytest.mark.config(
    PRO_PROFILES_REMOVAL_DRAFT_INFO={
        'description': 'draft description',
        'author': 'author',
        'summon_users': ['summon_user'],
        'ticket_info': {
            'description': 'ticket description',
            'summary': 'ticket summary',
        },
    },
)
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
        )
        """,
        """
        INSERT INTO pro_profiles_removal.profiles
        (request_id, park_id, contractor_profile_id)
        VALUES
        ('00000000-0000-0000-0000-000000000001', 'parkid11', 'profileid11');
        """,
    ],
)
async def test_ok_without_link_to_profile(
        cron_context: context.Context,
        mock_taxi_approvals,
        mock_blocklist,
        mock_driver_profiles,
):
    @mock_taxi_approvals('/drafts/create/')
    async def _create_draft(request: http.Request):
        assert request.json == {
            'request_id': (
                'pro-profiles-removal_00000000000000000000000000000001'
            ),
            'change_doc_id': '00000000000000000000000000000001',
            'service_name': 'pro-profiles-removal',
            'api_path': 'pro_profiles_removal_v1',
            'mode': 'poll',
            'run_manually': False,
            'data': {'profiles': ['parkid11_profileid11']},
            'description': 'draft description',
            'summon_users': ['summon_user'],
            'tickets': {
                'create_data': {
                    'summary': 'ticket summary',
                    'description': 'ticket description\n' 'profileid11',
                },
            },
        }
        return {'id': 1, 'version': 1, 'status': 'need_approval'}

    @mock_blocklist('/internal/blocklist/v1/add')
    async def _add_block(request: http.Request):
        assert request.json == {
            'block': {
                'predicate_id': '44444444-4444-4444-4444-444444444444',
                'kwargs': {'license_id': 'pd_id_1111', 'park_id': 'parkid11'},
                'reason': {'key': 'blocklist.reasons.pro_profiles_removal'},
                'comment': 'The account removal has been requested by user',
                'mechanics': 'pro_profiles_removal',
                'disable_service': ['candidates'],
            },
            'identity': {
                'name': 'pro-profiles-removal',
                'type': 'service',
                'id': 'parkid11_profileid11_00000000000000000000000000000001',
            },
        }
        return {'block_id': 'block_id'}

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    def _retrieve_by_id(request: http.Request):
        assert request.json['projection'] == ['data.license.pd_id']
        assert request.json['id_in_set'] == ['parkid11_profileid11']
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
        WHERE state = 'pending'
        """,
    )
    assert len(rows) == 1
    assert rows[0]['id'] == uuid.UUID('00000000-0000-0000-0000-000000000001')
    assert rows[0]['draft_id'] == 1
    assert rows[0]['block_id'] == 'block_id'
