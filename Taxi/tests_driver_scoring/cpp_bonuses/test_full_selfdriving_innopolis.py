import copy

import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets

BODY = {
    'requests': [
        {
            'search': {
                'order_id': 'order_id',
                'order': {
                    'request': {
                        'source': {'geopoint': [39.60258, 52.569089]},
                        'surge_price': 5.0,
                    },
                },
                'allowed_classes': ['econom'],
            },
            'candidates': [
                {
                    'id': 'dbid_uuid',
                    'route_info': {
                        'time': 650,
                        'distance': 1450,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'business'],
                },
            ],
        },
    ],
    'intent': 'dispatch-buffer',
}

# pylint: disable=C0103,C1801
def _update(x, y):
    if not isinstance(y, dict):
        # override value by patch
        return y
    for k, v in y.items():
        if k in x:
            x[k] = _update(x[k], v)
        else:
            x[k] = v
    return x


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.parametrize(
    'test_name, filtered',
    [
        ('no_experiment', False),
        ('ok', False),
        ('wrong_source_and_destination', True),
        ('not_selfdriving_user', True),
        ('not_selfdriving_user_and_car', False),
        ('no_destination', True),
        ('source_is_ok_but_not_dest', True),
    ],
)
async def test_base(taxi_driver_scoring, load_json, test_name, filtered):
    body = copy.deepcopy(BODY)

    patch = load_json(f'{test_name}.json')
    body['requests'][0]['search'] = _update(
        body['requests'][0]['search'], patch,
    )

    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )

    assert response.status_code == 200
    assert len(response.json()['responses'][0]['candidates']) == (
        0 if filtered else 1
    )
