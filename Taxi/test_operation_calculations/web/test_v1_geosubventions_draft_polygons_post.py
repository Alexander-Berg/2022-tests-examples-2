import json

from aiohttp import web
import pytest

from test_operation_calculations import conftest


@pytest.mark.parametrize(
    'test_key',
    [
        'all_existing',
        'broken_existing',
        'new',
        'valid_existing',
        'valid_new',
        'conflicts',
        'from_previous',
    ],
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
@pytest.mark.geo_nodes(conftest.GEO_NODES)
async def test_v1_geosubventions_draft_polygons_post(
        web_app_client, mock_geoareas, open_file, test_key,
):

    with open_file('test_data.json', mode='rb', encoding=None) as fp:
        test_data = json.load(fp)

    @mock_geoareas('/subvention-geoareas/admin/v1/geoareas')
    def _subvention_geoareas_select_handler(request):
        return web.json_response(test_data['subvention_geoareas'])

    response = await web_app_client.post(
        '/v1/geosubventions/draft_polygons/',
        json=test_data['request'][test_key],
    )
    expected = test_data['responce'][test_key]
    assert response.status == expected['status'], await response.text()
    assert await response.json() == expected['data']
