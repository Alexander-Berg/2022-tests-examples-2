# pylint: disable=E1101,W0612
import datetime

import pytest


@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.now('2021-03-22T04:05:00+0300')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_subventions(taxi_surge_calculator, mockserver, load_json):
    rules_select_requests = []

    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    def _point_employ(request):
        rules_select_requests.append(request.json)
        return mockserver.make_response(json=load_json('subventions.json'))

    point_a = [38.1, 51]
    request = {'point_a': point_a}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200
    data = response.json()

    # pipeline returns subventions instance value as surge and value_raw
    assert data['classes'][0]['surge']['value'] == -60 * 60
    assert data['classes'][0]['value_raw'] == pytest.approx(20.06, 0.1)
    assert rules_select_requests == [
        {
            'limit': 1000,
            'rule_types': ['single_ride'],
            'time_range': {
                'end': '2021-03-22T02:05:00+00:00',
                'start': '2021-03-22T01:05:00+00:00',
            },
            'zones': ['moscow'],
        },
    ]


@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.parametrize(
    'now,time_to_start',
    [
        ('2021-03-01T02:54:00+03:00', 0),
        ('2021-03-01T02:56:00+03:00', 9 * 60),
        ('2021-03-01T03:05:00+03:00', 0),
        ('2021-03-01T03:08:00+03:00', -3 * 60),
        ('2021-03-01T19:01:00+03:00', 0),
    ],
)
async def test_subventions_time_delta(
        taxi_surge_calculator, mocked_time, now, time_to_start,
):
    mocked_time.set(datetime.datetime.fromisoformat(now))
    await taxi_surge_calculator.invalidate_caches()

    point_a = [38.1, 51]
    request = {'point_a': point_a}
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200
    data = response.json()

    assert data['classes'][0]['surge']['value'] == time_to_start
