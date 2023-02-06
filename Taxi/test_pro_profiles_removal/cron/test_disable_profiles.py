import uuid

import pytest

from testsuite.utils import http

from pro_profiles_removal.generated.cron import cron_context as context
from pro_profiles_removal.generated.cron import run_cron


@pytest.mark.now('2022-06-03T12:00:00+00:00')
@pytest.mark.pgsql('pro_profiles_removal')
async def test_ok(
        cron_context: context.Context,
        mockserver,
        mock_contractor_profiles_manager,
):
    @mock_contractor_profiles_manager(
        '/driver-profiles/contractors/v1/is-readonly',
    )
    async def _update_is_readonly(request: http.Request):
        body = request.json
        assert body['is_readonly']
        return {}

    @mockserver.json_handler('/tags/v1/assign')
    async def _v1_assign(request: http.Request):
        assert 'X-Idempotency-Token' in request.headers
        assert request.json['provider'] == 'pro-profiles-removal'
        entities: list = request.json['entities']
        assert len(entities) == 3
        for entity in entities:
            assert entity['type'] == 'dbid_uuid'
            assert entity['tags'] == {
                'removing_requested': {'until': '2022-07-03T15:00:00+0300'},
            }
            assert entity['name'] in [
                'parkid11_profileid11',
                'parkid11_profileid12',
                'parkid12_profileid11',
            ]
        return mockserver.make_response(
            json={'code': '200', 'message': 'ok'}, status=200,
        )

    await cron_context.pg.main_master.execute(
        """
        INSERT INTO pro_profiles_removal.requests
        (id, phone_pd_id, state, created_at)
        VALUES
        (
            '00000000-0000-0000-0000-000000000001',
            'phone_pd_id1',
            'created',
            '2022-06-01'
        );

        INSERT INTO pro_profiles_removal.profiles
        (request_id, park_id, contractor_profile_id)
        VALUES
        ('00000000-0000-0000-0000-000000000001', 'parkid11', 'profileid11'),
        ('00000000-0000-0000-0000-000000000001', 'parkid11', 'profileid12'),
        ('00000000-0000-0000-0000-000000000001', 'parkid12', 'profileid11');
        """,
    )

    await run_cron.main(
        ['pro_profiles_removal.crontasks.disable_profiles', '-t', '0'],
    )

    rows = await cron_context.pg.main_master.fetch(
        """
        SELECT id
        FROM pro_profiles_removal.requests
        WHERE state = 'profiles_disabled'
        """,
    )
    assert len(rows) == 1
    assert rows[0]['id'] == uuid.UUID('00000000-0000-0000-0000-000000000001')


@pytest.mark.now('2022-06-03T12:00:00+00:00')
@pytest.mark.pgsql('pro_profiles_removal')
@pytest.mark.parametrize(
    'request_id, result_state, do_return_error',
    [
        (
            uuid.UUID('00000000-0000-0000-0000-000000000001'),
            'profiles_disabled',
            False,
        ),
        (uuid.UUID('00000000-0000-0000-0000-000000000002'), 'created', True),
        (
            uuid.UUID('00000000-0000-0000-0000-000000000003'),
            'completed',
            False,
        ),
        (uuid.UUID('00000000-0000-0000-0000-000000000003'), 'completed', True),
    ],
)
async def test_several_requests(
        cron_context: context.Context,
        mockserver,
        mock_contractor_profiles_manager,
        request_id: uuid.UUID,
        result_state: str,
        do_return_error: bool,
):
    @mock_contractor_profiles_manager(
        '/driver-profiles/contractors/v1/is-readonly',
    )
    async def _update_is_readonly(request: http.Request):
        body = request.json
        assert body['is_readonly']
        return {}

    @mockserver.json_handler('/tags/v1/assign')
    async def _v1_assign(request: http.Request):
        if do_return_error:
            return mockserver.make_response(
                json={'code': '500', 'message': 'error'}, status=500,
            )
        return mockserver.make_response(
            json={'code': '200', 'message': 'ok'}, status=200,
        )

    await cron_context.pg.main_master.execute(
        """
        INSERT INTO pro_profiles_removal.requests
        (id, phone_pd_id, state, created_at)
        VALUES
        (
            '00000000-0000-0000-0000-000000000001',
            'phone_pd_id1',
            'created',
            '2022-06-01'
        ),
        (
            '00000000-0000-0000-0000-000000000002',
            'phone_pd_id2',
            'created',
            '2022-06-01'
        ),
        (
            '00000000-0000-0000-0000-000000000003',
            'phone_pd_id3',
            'completed',
            '2022-04-01'
        );

        INSERT INTO pro_profiles_removal.profiles
        (request_id, park_id, contractor_profile_id)
        VALUES
        ('00000000-0000-0000-0000-000000000001', 'parkid11', 'profileid11'),
        ('00000000-0000-0000-0000-000000000001', 'parkid11', 'profileid12'),
        ('00000000-0000-0000-0000-000000000001', 'parkid12', 'profileid11'),
        ('00000000-0000-0000-0000-000000000002', 'parkid20', 'profileid20'),
        ('00000000-0000-0000-0000-000000000003', 'parkid30', 'profileid30');
        """,
    )

    await run_cron.main(
        ['pro_profiles_removal.crontasks.disable_profiles', '-t', '0'],
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
