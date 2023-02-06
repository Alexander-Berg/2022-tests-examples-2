# flake8: noqa
import aiohttp.web
import pytest

from taxi.clients import personal

RESPONSE409 = {'body': '', 'code': 'NOT_ALLOWED_STATUS', 'message': '409'}


@pytest.mark.config(TVM_RULES=[{'src': 'fleet-reports', 'dst': 'personal'}])
@pytest.mark.pgsql('fleet_reports', files=('success.sql',))
async def test_success(
        stq_runner, mockserver, load_json, mock_driver_profiles,
):
    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_frs(request):
        return None

    stub = load_json('service_success.json')
    driver_profiles_stub = load_json('driver_profiles.json')

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _v1_driver_profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-reports'}
        assert request.json == driver_profiles_stub['request']
        return aiohttp.web.json_response(driver_profiles_stub['response'])

    @mockserver.json_handler('/personal/v1/deptrans_ids/bulk_retrieve')
    async def _deptrans_ids_bulk_retrieve(request):
        assert request.json == {'items': [{'id': 'kis_art_id1'}]}
        return {'items': [{'id': 'kis_art_id1', 'value': 'real_kis_art_id1'}]}

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    async def _phones_bulk_retrieve(request):
        assert request.json == {
            'items': [
                {'id': 'fa866b5c515a48a8b0dee01a7d74b477'},
                {'id': '7da1236a76e0405eb1307e1bffc07491'},
                {'id': '7da1236a76e0405eb1307e1bffc07400'},
            ],
        }
        return {
            'items': [
                {
                    'id': 'fa866b5c515a48a8b0dee01a7d74b477',
                    'value': '_value_1',
                },
                {
                    'id': '7da1236a76e0405eb1307e1bffc07491',
                    'value': '_value_2',
                },
                {
                    'id': '7da1236a76e0405eb1307e1bffc07400',
                    'value': '_value_2',
                },
            ],
        }

    await stq_runner.fleet_reports_kis_art_detailed_download_async.call(
        task_id='1', args=(), kwargs=stub['request'],
    )

    assert _mock_frs.times_called == 1
    assert _v1_driver_profiles_retrieve.times_called == 1
