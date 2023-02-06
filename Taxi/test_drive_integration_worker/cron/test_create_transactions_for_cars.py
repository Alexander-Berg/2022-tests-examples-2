# pylint: disable=redefined-outer-name
import pytest

from drive_integration_worker import utils
from drive_integration_worker.crontasks import (
    create_transactions_for_cars as ctfc,
)
from drive_integration_worker.generated.cron import run_cron


@pytest.fixture(name='fleet_parks_data_fixture')
def _fleet_parks_data_fixture(mock_fleet_parks):
    @mock_fleet_parks('/v1/parks/list')
    async def _parks_list(request):
        return {
            'parks': [
                {
                    'id': '123',
                    'login': 'q123',
                    'name': 'some park',
                    'is_active': True,
                    'city_id': '234234',
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'RU',
                    'demo_mode': False,
                    'tz_offset': 3,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }


@pytest.mark.now('2020-01-12T20:42:46+00:00')
@pytest.mark.config(
    DRIVE_INTEGRATION_CARSHARING_FTA_CATEGORY='partner_service_manual_21',
)
async def test_start(
        mock_ext_carsharing,
        mock_fleet_transactions_api,
        load_json,
        cron_context,
        fleet_parks_data_fixture,
):
    @mock_ext_carsharing('/api/taxisharing/bills/history')
    async def _sharing_bills(request):
        assert request.query['account_name'] == 'taxisharing'
        if request.query.get('cursor') is None:
            return load_json('response_bills.json')
        if request.query.get('cursor') == '111':
            return {'cursor': 111, 'sessions': []}
        assert False, 'Unexpected cursor'

    @mock_ext_carsharing('/api/taxisharing/refunds/history')
    async def _sharing_refunds(request):
        assert request.query['account_name'] == 'taxisharing'
        if request.query.get('cursor') is None:
            return load_json('response_refunds.json')
        if request.query.get('cursor') == '222':
            return {'cursor': 222, 'sessions': []}
        assert False, 'Unexpected cursor'

    @mock_ext_carsharing('/api/taxisharing/user_tags/list')
    async def _sharing_tags(request):
        query = request.query
        assert query['object_id'] == 'b9f418dd-202e-4b97-b616-41a8f89d0359'
        return load_json('tags_response.json')

    @mock_fleet_transactions_api(
        '/v1/parks/driver-profiles/transactions/by-platform',
    )
    async def _fta_create_transaction(request):
        headers = request.headers
        body = request.json
        assert headers.get('X-Ya-Service-Name') == 'drive-integration'
        if (
                headers.get('X-Idempotency-Token')
                == 'bill-ef6b256f-6f80d00e-cef1f8ca-854e6112'
        ):
            assert body == load_json('fta_req_bill.json')
            return load_json('fta_resp.json')
        if (
                headers.get('X-Idempotency-Token')
                == 'refund-ef6b256f-6f80d00e-cef1f8ca-854e6112'
        ):
            assert body == load_json('fta_req_refund.json')
            return load_json('fta_resp.json')
        assert False, headers.get('X-Idempotency-Token')

    await run_cron.main(
        [
            'drive_integration_worker.crontasks.create_transactions_for_cars',
            '-t',
            '0',
        ],
    )
    async with cron_context.pg.read_pool.acquire() as conn:
        await utils.fix_pg_jsonb(conn)
        cursors = await conn.fetch(
            'SELECT id, kind, data FROM state.process_cursors ORDER BY id;',
        )
    cursors = [dict(x) for x in cursors]
    assert cursors == [
        {'data': {'cursor': 111}, 'id': 1, 'kind': 'carsharing_chargings'},
        {'data': {'cursor': 222}, 'id': 2, 'kind': 'carsharing_refunds'},
    ]


@pytest.mark.now('2020-01-13T20:42:46+03:00')
@pytest.mark.config(
    DRIVE_INTEGRATION_CARSHARING_FTA_CATEGORY='partner_service_manual_21',
)
async def test_valid_event_at_one_day_back(
        mock_ext_carsharing,
        mock_fleet_transactions_api,
        load_json,
        cron_context,
        fleet_parks_data_fixture,
):
    @mock_ext_carsharing('/api/taxisharing/bills/history')
    async def _sharing_bills(request):
        assert request.query['account_name'] == 'taxisharing'
        if request.query.get('cursor') is None:
            return load_json('response_bills.json')
        if request.query.get('cursor') == '111':
            return {'cursor': 111, 'sessions': []}
        assert False, 'Unexpected cursor'

    @mock_ext_carsharing('/api/taxisharing/refunds/history')
    async def _sharing_refunds(request):
        assert request.query['account_name'] == 'taxisharing'
        if request.query.get('cursor') is None:
            return load_json('response_refunds.json')
        if request.query.get('cursor') == '222':
            return {'cursor': 222, 'sessions': []}
        assert False, 'Unexpected cursor'

    @mock_ext_carsharing('/api/taxisharing/user_tags/list')
    async def _sharing_tags(request):
        query = request.query
        assert query['object_id'] == 'b9f418dd-202e-4b97-b616-41a8f89d0359'
        return load_json('tags_response.json')

    @mock_fleet_transactions_api(
        '/v1/parks/driver-profiles/transactions/by-platform',
    )
    async def _fta_create_transaction(request):
        headers = request.headers
        body = request.json
        assert headers.get('X-Ya-Service-Name') == 'drive-integration'
        if (
                headers.get('X-Idempotency-Token')
                == 'bill-ef6b256f-6f80d00e-cef1f8ca-854e6112'
        ):
            expected = load_json('fta_req_bill.json')
            assert body['event_at'] == '2020-01-12T23:43:46+03:00'
            expected['event_at'] = body['event_at']
            assert body == expected
            return load_json('fta_resp.json')
        if (
                headers.get('X-Idempotency-Token')
                == 'refund-ef6b256f-6f80d00e-cef1f8ca-854e6112'
        ):
            expected = load_json('fta_req_refund.json')
            assert body['event_at'] == '2020-01-12T23:43:46+03:00'
            expected['event_at'] = body['event_at']
            return load_json('fta_resp.json')
        assert False, headers.get('X-Idempotency-Token')

    await run_cron.main(
        [
            'drive_integration_worker.crontasks.create_transactions_for_cars',
            '-t',
            '0',
        ],
    )
    async with cron_context.pg.read_pool.acquire() as conn:
        await utils.fix_pg_jsonb(conn)
        cursors = await conn.fetch(
            'SELECT id, kind, data FROM state.process_cursors ORDER BY id;',
        )
    cursors = [dict(x) for x in cursors]
    assert cursors == [
        {'data': {'cursor': 111}, 'id': 1, 'kind': 'carsharing_chargings'},
        {'data': {'cursor': 222}, 'id': 2, 'kind': 'carsharing_refunds'},
    ]


@pytest.mark.config(
    DRIVE_INTEGRATION_CARSHARING_FTA_CATEGORY='partner_service_manual_21',
)
@pytest.mark.pgsql(
    'drive_integration',
    queries=[
        """INSERT INTO state.process_cursors(kind, data)
    VALUES ('carsharing_chargings', '{"cursor":111}'::JSONB),
        ('carsharing_refunds', '{"cursor":222}'::JSONB);""",
    ],
)
async def test_cursors(
        cron_context, mock_ext_carsharing, fleet_parks_data_fixture,
):
    @mock_ext_carsharing('/api/taxisharing/bills/history')
    async def _sharing_bills(request):
        assert request.query['account_name'] == 'taxisharing'
        assert request.query['cursor'] == '111'
        return {'cursor': 111, 'sessions': []}

    @mock_ext_carsharing('/api/taxisharing/refunds/history')
    async def _sharing_refunds(request):
        assert request.query['account_name'] == 'taxisharing'
        assert request.query['cursor'] == '222'
        return {'cursor': 222, 'sessions': []}

    await run_cron.main(
        [
            'drive_integration_worker.crontasks.create_transactions_for_cars',
            '-t',
            '0',
        ],
    )

    async with cron_context.pg.read_pool.acquire() as conn:
        await utils.fix_pg_jsonb(conn)
        cursors = await conn.fetch(
            'SELECT id, kind, data FROM state.process_cursors ORDER BY id;',
        )
    cursors = [dict(x) for x in cursors]
    assert cursors == [
        {'data': {'cursor': 111}, 'id': 1, 'kind': 'carsharing_chargings'},
        {'data': {'cursor': 222}, 'id': 2, 'kind': 'carsharing_refunds'},
    ]


async def test_no_config():
    try:
        await run_cron.main(
            [
                'drive_integration_worker.crontasks'
                '.create_transactions_for_cars',
                '-t',
                '0',
            ],
        )
        assert False, 'Must throw'
    except ctfc.InvalidConfig:
        pass
