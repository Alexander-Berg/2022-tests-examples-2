from aiohttp import web
import pytest

from operation_calculations.generated.cron import run_cron
import operation_calculations.geosubventions.storage as storage_lib

ALL_STATUSES = [
    'NEED_APPROVAL',
    'APPROVED',
    'APPLYING',
    'SUCCEEDED',
    'FAILED',
    'EXPIRED',
    'REJECTED',
    'PARTIALLY_COMPLETED',
    'WAITING_CHECK',
]


@pytest.mark.pgsql(
    'operation_calculations', files=['pg_operations_results.sql'],
)
async def test_geosubventions_update_drafts_statuses(
        web_context, web_app_client, mock_taxi_approvals,
):
    @mock_taxi_approvals('/multidrafts/')
    async def handler(request):  # pylint: disable=W0612
        multidraft_id = int(request.query['id'])
        assert multidraft_id in {1, 3, 5}
        status = 200
        if multidraft_id == 1:
            response = {'id': multidraft_id, 'status': 'succeeded'}
        elif multidraft_id == 5:
            status = 404
            response = {}
        else:
            response = {'id': multidraft_id, 'status': 'waiting_check'}

        return web.json_response(response, status=status)

    await run_cron.main(
        [
            'operation_calculations.crontasks.nmfg_update_drafts_statuses',  # noqa: E501
            '-t',
            '0',
        ],
    )

    storage = storage_lib.GeoSubventionsStorage(web_context)
    drafts_statuses = await storage.get_nmfg_drafts_by_status(ALL_STATUSES)
    assert dict(drafts_statuses) == {
        1: 'SUCCEEDED',
        2: 'SUCCEEDED',
        3: 'WAITING_CHECK',
        4: 'REJECTED',
        5: 'REJECTED',
    }
