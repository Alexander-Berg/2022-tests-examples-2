import json

import pytest

from . import utils


@pytest.fixture(autouse=True)
def mock_graph(mockserver):
    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_graph(request):
        data = json.loads(request.get_data())
        assert data['max_distance'] == 1000.0
        if data['longitude'] == 10.2 and data['latitude'] == 20.2:
            return {
                'adjusted': [
                    {'longitude': 10.1, 'latitude': 20.1, 'geo_distance': 100},
                ],
            }
        return {'adjusted': []}


@pytest.mark.parametrize('order_name', [f'order_{n}' for n in range(1, 10)])
async def test_stq_add_pg(
        stq_runner, load_json, yamaps, pgsql, order_name, mockserver,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))
    yamaps.set_checks({'uri': 'ymapsbm1://org_uri'})

    kwargs = load_json('kwargs.json')[order_name]
    await stq_runner.routehistory_add.call(
        task_id=kwargs['order_id'], kwargs=kwargs, expect_fail=False,
    )
    cursor = pgsql['routehistory'].cursor()
    cursor_ph = pgsql['routehistory_ph'].cursor()
    records = utils.read_phone_history_db(cursor, cursor_ph)

    expected = load_json('expected_pg_db.json')[order_name]
    assert records.strings == expected['strings']
    assert records.phone_history == expected['phone_history']
    assert records.users == expected['users']


def kwarg_spoilers():
    def _missing_created(kwargs):
        del kwargs['created']

    def _missing_brand(kwargs):
        del kwargs['brand']

    def _bad_route(kwargs):
        kwargs['route'] = ['bad route']

    def _bad_driver_point(kwargs):
        kwargs['driver_point'] = 'bad driver point'

    def _invalid_driver_point_index(kwargs):
        del kwargs['driver_point']
        kwargs['driver_points'] = [[1, 2], None]
        kwargs['driver_point_index'] = 10

    return [
        _missing_created,
        _missing_brand,
        _bad_route,
        _bad_driver_point,
        _invalid_driver_point_index,
    ]


@pytest.mark.parametrize('kwargs_spoiler', kwarg_spoilers())
async def test_bad_kwargs(stq_runner, load_json, kwargs_spoiler):
    kwargs = load_json('kwargs.json')['order_1']
    kwargs_spoiler(kwargs)
    await stq_runner.routehistory_add.call(
        task_id=kwargs['order_id'], kwargs=kwargs, expect_fail=True,
    )
