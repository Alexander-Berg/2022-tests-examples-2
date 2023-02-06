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
    'operation_calculations', files=['pg_geosubventions_multidrafts.sql'],
)
async def test_geosubventions_update_drafts_statuses(
        web_context, web_app_client, mock_taxi_approvals,
):
    @mock_taxi_approvals('/multidrafts/')
    async def handler(request):  # pylint: disable=W0612
        multidraft_id = int(request.query['id'])
        assert multidraft_id in {1, 3}
        if multidraft_id == 1:
            response = {'id': multidraft_id, 'status': 'succeeded'}
        else:
            response = {'id': multidraft_id, 'status': 'waiting_check'}

        return web.json_response(response)

    await run_cron.main(
        [
            'operation_calculations.crontasks.geosubventions_update_drafts_statuses',  # noqa: E501
            '-t',
            '0',
        ],
    )

    storage = storage_lib.GeoSubventionsStorage(web_context)
    drafts_statuses = await storage.get_drafts_by_statuses(ALL_STATUSES)
    assert dict(drafts_statuses) == {
        1: 'SUCCEEDED',
        2: 'SUCCEEDED',
        3: 'WAITING_CHECK',
        4: 'REJECTED',
    }
