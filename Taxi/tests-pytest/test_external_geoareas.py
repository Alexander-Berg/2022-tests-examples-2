# -*- coding: utf-8 -*-

import pytest

from taxi.external import geoareas
from taxi.util.dates import parse_timestring

BASE_URL = 'http://geoareas.taxi.tst.yandex.net'

GET_ALL_ENDPOINT = 'subvention-geoareas/v1/geoareas'
GET_BY_DT_AND_GEOMETRY_ENDPOINT = (
    'subvention-geoareas/admin/v1/geoareas_by_time_and_geometry'
)


@pytest.mark.asyncenv('blocking')
def test_updates_geoareas(areq_request, load):
    @areq_request
    def _geoareas_request(method, url, **kwargs):
        assert method == 'GET'
        assert url == '{}/{}'.format(BASE_URL, GET_ALL_ENDPOINT)
        params = kwargs['params']
        assert params is None

        return areq_request.response(200, load('geoareas_response.json'))

    result_geoareas = geoareas.find_active_geoareas_in_point((0.5, 0.5))

    assert result_geoareas == [
        {
            '_id': '<msk2>',
            'name': 'msk',
            'created': parse_timestring('2020-02-02T02:03:02.000000Z'),
        },
    ]


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize(
    'params',
    [
        {'timestamp': 1602573539, 'point': '0, 0'},
        {'timestamp': 1602573539, 'top_left': '0, 1', 'bottom_right': '1, 0'},
    ],
)
def test_get_by_dt_and_geometry(areq_request, load, params):
    @areq_request
    def _geoareas_request(method, url, **kwargs):
        assert method == 'GET'
        assert url == '{}/{}'.format(BASE_URL, GET_BY_DT_AND_GEOMETRY_ENDPOINT)
        params = kwargs['params']
        assert 'timestamp' in params
        assert (
            'point' in params
            or 'top_left' in params
            and 'bottom_right' in params
        )

        return areq_request.response(200, load('geoareas_response.json'))

    result_geoareas = geoareas.get_by_dt_and_geometry(params)

    assert result_geoareas == [
        {
            'name': 'msk',
            'geometry': {
                'holes': [],
                'shell': [[0, 0], [1, 0], [1, 1], [1, 0]],
            },
        },
    ]
