import pytest


@pytest.mark.config(
    EXTRA_EXAMS_BY_ZONE={},
    ROUTER_SELECT=[
        {'routers': ['yamaps']},
        {'ids': ['moscow'], 'routers': ['linear-fallback']},
    ],
)
@pytest.mark.parametrize(
    'request_override,' 'found',
    [
        (
            {
                'order': {
                    'user_agent': (
                        'yandex-taxi/4.23.0.121835 '
                        'Android/10 (Google; Android SDK built for x86_64)'
                    ),
                },
            },
            ['dbid0_uuid0', 'dbid0_uuid1'],
        ),
        ({'order': {'user_agent': 'call_center'}}, ['dbid0_uuid1']),
    ],
)
@pytest.mark.experiments3(filename='forbid_deaf_driver_dispatch.json')
async def test_deaf_driver(
        taxi_candidates, driver_positions, request_override, found,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )
    request_body = {
        'limit': 10,
        'filters': ['efficiency/deaf_driver'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    request_body.update(request_override)
    response = await taxi_candidates.post('order-search', json=request_body)
    assert response.status_code == 200
    candidates = [
        candidate['id'] for candidate in response.json()['candidates']
    ]
    assert sorted(candidates) == found
