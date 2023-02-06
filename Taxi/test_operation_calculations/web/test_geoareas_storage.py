import http
import json

from aiohttp import web
import pytest

from operation_calculations.geosubventions import geoareas_storage as gs


@pytest.fixture
def test_geoareas(open_file):
    with open_file('test_data.json', mode='rb', encoding=None) as fp:
        data = json.load(fp)
    return data


async def test_load_polygons_all(
        web_context, mock_geoareas, test_geoareas,
):  # pylint: disable=W0621
    @mock_geoareas('/subvention-geoareas/admin/v1/geoareas')
    def _geoareas_select_handler(request):
        assert request.method == 'GET'
        return web.json_response(test_geoareas)

    result = await gs.load_polygons(web_context)
    for poly in test_geoareas['geoareas']:
        assert poly['name'] in result
        assert (
            poly['geometry']['coordinates']
            == result[poly['name']]['coordinates']
        )


async def test_load_polygons_filtered(
        web_context, mock_geoareas, test_geoareas,
):  # pylint: disable=W0621
    @mock_geoareas('/subvention-geoareas/admin/v1/geoareas')
    def _geoareas_select_handler(request):
        assert request.method == 'POST'
        geoareas = [
            geoarea
            for geoarea in test_geoareas['geoareas']
            if geoarea['name'] in request.json['names']
        ]
        return web.json_response({'geoareas': geoareas})

    poly_names = {'pol8'}
    result = await gs.load_polygons(web_context, poly_names=poly_names)

    for poly in test_geoareas['geoareas']:
        if poly['name'] not in poly_names:
            assert poly['name'] not in result
            continue
        assert poly['name'] in result
        assert (
            poly['geometry']['coordinates']
            == result[poly['name']]['coordinates']
        )


async def test_load_polygons_filtered_with_nonexisting(
        web_context, mock_geoareas, test_geoareas,
):  # pylint: disable=W0621
    @mock_geoareas('/subvention-geoareas/admin/v1/geoareas')
    def _geoareas_select_handler(request):
        assert request.method == 'POST'
        existing_geoarea_names = {
            geoarea['name'] for geoarea in test_geoareas['geoareas']
        }
        missing = [
            name
            for name in request.json['names']
            if name not in existing_geoarea_names
        ]
        if missing:
            msg = ', '.join(missing)
            return web.json_response(
                {
                    'code': 'NOT_FOUND',
                    'message': f'Could not find geoarea with names: {msg}',
                },
                status=http.HTTPStatus.NOT_FOUND,
            )
        geoareas = [
            geoarea
            for geoarea in test_geoareas['geoareas']
            if geoarea['name'] in request.json['names']
        ]
        return web.json_response({'geoareas': geoareas})

    poly_names = {'pol8'}
    missing_names = {'not_exists_1', 'not_exists_2'}
    result = await gs.load_polygons(
        web_context, poly_names=poly_names | missing_names,
    )

    for poly in test_geoareas['geoareas']:
        if poly['name'] not in poly_names:
            assert poly['name'] not in result
            continue
        assert poly['name'] in result
        assert (
            poly['geometry']['coordinates']
            == result[poly['name']]['coordinates']
        )
