import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


def _make_body(mid_point_airport):
    request = {'source': {'geopoint': [39.52449, 52.69810]}}
    if mid_point_airport:
        request['destinations'] = [{'geopoint': [39.52450, 52.69811]}]
    elif mid_point_airport is False:
        request['destinations'] = [{'geopoint': [39.60258, 52.569089]}]

    return {
        'requests': [
            {
                'search': {
                    'order_id': '16e83c16beb74880b819d2a7b1c06d93',
                    'order': {'request': request},
                    'allowed_classes': ['econom'],
                },
                'candidates': [
                    {
                        'id': 'dbid0_uuid0',
                        'route_info': {
                            'time': 0,
                            'distance': 5,
                            'approximate': False,
                        },
                        'unique_driver_id': 'udid0',
                        'position': [39.52449, 52.69810],
                        'classes': ['econom'],
                    },
                    {
                        'id': 'dbid1_uuid1',
                        'route_info': {
                            'time': 0,
                            'distance': 5,
                            'approximate': False,
                        },
                        'unique_driver_id': 'udid1',
                        'position': [39.524234, 52.69800],
                        'classes': ['econom', 'business'],
                    },
                ],
            },
        ],
        'intent': 'dispatch-buffer',
    }


@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.geoareas(filename='lipetsk.json')
async def test_route_point_info_fetcher_source_only(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=_make_body(None),
    )
    assert response.status_code == 200

    resp_json = sorted(
        response.json()['responses'][0]['candidates'], key=lambda x: x['id'],
    )
    assert resp_json == [
        {'id': 'dbid0_uuid0', 'score': -3.0},
        {'id': 'dbid1_uuid1', 'score': -3.0},
    ]


@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.geoareas(filename='lipetsk.json')
@pytest.mark.parametrize('mid_point_airport', [False, True])
async def test_route_point_info_fetcher_with_destinations(
        taxi_driver_scoring, mid_point_airport,
):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=_make_body(mid_point_airport),
    )
    assert response.status_code == 200

    resp_json = sorted(
        response.json()['responses'][0]['candidates'], key=lambda x: x['id'],
    )
    if mid_point_airport:
        assert resp_json == [
            {'id': 'dbid0_uuid0', 'score': -10.0},
            {'id': 'dbid1_uuid1', 'score': -10.0},
        ]
    else:
        assert resp_json == [
            {'id': 'dbid0_uuid0', 'score': -6.0},
            {'id': 'dbid1_uuid1', 'score': -6.0},
        ]
