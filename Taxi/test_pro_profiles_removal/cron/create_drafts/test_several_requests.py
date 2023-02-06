import uuid

import pytest

from testsuite.utils import http

from pro_profiles_removal.generated.cron import cron_context as context
from pro_profiles_removal.generated.cron import run_cron


@pytest.mark.now('2022-06-03T12:00:00+00:00')
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
@pytest.mark.parametrize(
    'request_id, result_state, do_return_error',
    [
        (uuid.UUID('00000000-0000-0000-0000-000000000001'), 'pending', False),
        (
            uuid.UUID('00000000-0000-0000-0000-000000000002'),
            'profiles_disabled',
            True,
        ),
        (
            uuid.UUID('00000000-0000-0000-0000-000000000003'),
            'completed',
            False,
        ),
        (uuid.UUID('00000000-0000-0000-0000-000000000003'), 'completed', True),
    ],
)
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
        ),
        (
            '00000000-0000-0000-0000-000000000002',
            'phone_pd_id2',
            'profiles_disabled',
            '2022-06-01'
        ),
        (
            '00000000-0000-0000-0000-000000000003',
            'phone_pd_id3',
            'completed',
            '2022-04-01'
        );
        """,
        """
        INSERT INTO pro_profiles_removal.profiles
        (request_id, park_id, contractor_profile_id)
        VALUES
        ('00000000-0000-0000-0000-000000000001', 'parkid11', 'profileid11'),
        ('00000000-0000-0000-0000-000000000001', 'parkid11', 'profileid12'),
        ('00000000-0000-0000-0000-000000000001', 'parkid12', 'profileid11'),
        ('00000000-0000-0000-0000-000000000002', 'parkid20', 'profileid20'),
        ('00000000-0000-0000-0000-000000000003', 'parkid30', 'profileid30');
        """,
    ],
)
async def test_several_requests(
        cron_context: context.Context,
        mockserver,
        mock_driver_profiles,
        mock_taxi_approvals,
        mock_blocklist,
        request_id: uuid.UUID,
        result_state: str,
        do_return_error: bool,
):
    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    def _retrieve_by_id(request: http.Request):
        assert request.json['projection'] == ['data.license.pd_id']
        if do_return_error:
            return mockserver.make_response(status=500)
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'parkid11_profileid11',
                    'data': {'license': {'pd_id': 'pd_id_1111'}},
                },
                {
                    'park_driver_profile_id': 'parkid11_profileid12',
                    'data': {'license': {'pd_id': 'pd_id_1112'}},
                },
                {
                    'park_driver_profile_id': 'parkid12_profileid11',
                    'data': {'license': {'pd_id': 'pd_id_1211'}},
                },
            ],
        }

    @mock_taxi_approvals('/drafts/create/')
    async def _create_draft(request: http.Request):
        return {'id': 1, 'version': 1, 'status': 'need_approval'}

    @mock_blocklist('/internal/blocklist/v1/add')
    async def _add_block(request: http.Request):
        return {'block_id': 'block_id'}

    await run_cron.main(
        ['pro_profiles_removal.crontasks.create_drafts', '-t', '0'],
    )

    rows = await cron_context.pg.main_master.fetch(
        """
        SELECT state
        FROM pro_profiles_removal.requests
        WHERE id = $1
        """,
        request_id,
    )
    assert len(rows) == 1
    assert rows[0]['state'] == result_state
