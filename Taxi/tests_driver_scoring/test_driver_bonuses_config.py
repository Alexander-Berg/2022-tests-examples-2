import copy

import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets

BULK_BODY = {
    'requests': [
        {
            'search': {
                'order_id': '16e83c16beb74880b819d2a7b1c06d93',
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
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 650,
                        'distance': 1450,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'business'],
                },
                {
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 124,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.609112, 52.570000],
                    'classes': ['econom', 'business'],
                },
            ],
        },
        {
            'search': {
                'order': {
                    'request': {
                        'source': {'geopoint': [39.60258, 52.569089]},
                        'surge_price': 5.0,
                    },
                },
                'allowed_classes': ['business'],
            },
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 650,
                        'distance': 1450,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['vip', 'business'],
                },
                {
                    'id': 'dbid3_uuid3',
                    'route_info': {
                        'time': 500,
                        'distance': 5000,
                        'approximate': False,
                    },
                    'position': [39.609112, 52.570001],
                    'classes': ['econom', 'business'],
                },
            ],
        },
    ],
    'intent': 'dispatch-buffer',
}


def _add_reposition_score_experiment(experiments3):
    experiments3.add_experiment(
        consumers=['driver-scoring/reposition-score'],
        name='driver_scoring_reposition_score',
        match={
            'enabled': True,
            'consumers': [{'name': 'driver-scoring/reposition-score'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'home',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'reposition_mode',
                        'arg_type': 'string',
                        'value': 'home',
                    },
                },
                'value': {'b': 100.0, 'c': 1.0, 'd': 40.0},
            },
        ],
    )


@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.experiments3(filename='driver_bonuses_conditional.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.parametrize(
    'intent,zone,allowed_classes,order_id,expected_bonus',
    [
        ('dispatch-buffer', 'moscow', ['econom'], 'random_order_id', 10),
        ('eta', 'moscow', ['econom', 'child_tariff'], 'random_order_id', 20),
        (
            'direct-assignment',
            'moscow',
            ['econom', 'child_tariff'],
            'experimental_order_id',
            30,
        ),
        (
            'dispatch-buffer',
            'spb',
            ['econom', 'child_tariff'],
            'random_order_id',
            40,
        ),
        ('eta', 'spb', ['econom'], 'random_order_id', 50),
    ],
)
async def test_driver_bonuses_config(
        taxi_driver_scoring,
        intent,
        zone,
        allowed_classes,
        order_id,
        expected_bonus,
):
    body = {
        'request': {
            'search': {
                'order_id': order_id,
                'order': {
                    'request': {
                        'source': {'geopoint': [39.60258, 52.569089]},
                        'surge_price': 5.0,
                    },
                    'nearest_zone': zone,
                },
                'allowed_classes': allowed_classes,
            },
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 300,
                        'distance': 3000,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': allowed_classes,
                },
                {
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 200,
                        'distance': 2000,
                        'approximate': False,
                    },
                    'position': [39.609112, 52.570000],
                    'classes': allowed_classes,
                },
            ],
        },
        'intent': intent,
    }
    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 200

    assert response.json() == {
        'search': {'order_id': order_id},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': 200.0 - expected_bonus},
            {'id': 'dbid0_uuid0', 'score': 300.0 - expected_bonus},
        ],
    }


@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.experiments3(
    filename='driver_bonuses_conditional_js_fallback.json',
)
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.config(
    DRIVER_SCORING_JS_FALLBACK=True,
    VERYBUSY_BONUS={'__default__': {'__default__': -90}},
)
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'silver'),  # bonus: 10
        ('dbid_uuid', 'dbid1_uuid1', 'silver'),  # bonus: 10
    ],
)
@pytest.mark.reposition_matcher_check_results(
    {
        (b'dbid0', b'uuid0', b'random_order_id'): {
            'mode': 'home',
            'score': 0.5,
        },  # bonus: 120
        (b'dbid1', b'uuid1', b'random_order_id'): {
            'mode': 'home',
            'score': 0.5,
        },  # bonus: 120
    },
)
@pytest.mark.parametrize(
    'intent,zone,allowed_classes,order_id,expected_bonus',
    [
        ('dispatch-buffer', 'moscow', ['econom'], 'random_order_id', 10),
        ('eta', 'moscow', ['econom', 'child_tariff'], 'random_order_id', 120),
        (
            'direct-assignment',
            'moscow',
            ['econom', 'child_tariff'],
            'experimental_order_id',
            -600,
        ),
        ('dispatch-buffer', 'spb', ['econom', 'vip'], 'random_order_id', -90),
    ],
)
async def test_driver_bonuses_js_fallback_config(
        taxi_driver_scoring,
        intent,
        zone,
        allowed_classes,
        order_id,
        expected_bonus,
        experiments3,
):
    _add_reposition_score_experiment(experiments3)

    body = {
        'request': {
            'search': {
                'order_id': order_id,
                'order': {
                    'request': {
                        'source': {'geopoint': [39.60258, 52.569089]},
                        'destinations': [{'geopoint': [39.60258, 52.569089]}],
                        'surge_price': 5.0,
                    },
                    'nearest_zone': zone,
                },
                'allowed_classes': allowed_classes,
            },
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 300,
                        'distance': 3000,
                        'approximate': True,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': allowed_classes,
                    'status': {'driver': 'verybusy'},
                    'metadata': {'verybusy_order': True},
                },
                {
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 200,
                        'distance': 2000,
                        'approximate': True,
                    },
                    'position': [39.609112, 52.570000],
                    'classes': allowed_classes,
                    'status': {'driver': 'verybusy'},
                    'metadata': {'verybusy_order': True},
                },
            ],
        },
        'intent': intent,
    }
    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['candidates']) == 2
    assert resp_json['candidates'][0]['id'] == 'dbid1_uuid1'
    assert resp_json['candidates'][0]['score'] == 200.0 - expected_bonus
    assert resp_json['candidates'][1]['id'] == 'dbid0_uuid0'
    assert resp_json['candidates'][1]['score'] == 300.0 - expected_bonus


@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.experiments3(filename='bonuses_by_user_id.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
async def test_driver_bonuses_config_by_user_id(taxi_driver_scoring):
    body = copy.deepcopy(BULK_BODY)
    body['requests'][0]['search']['order']['user_id'] = 'user_id0'
    body['requests'][1]['search']['order']['user_id'] = 'user_id1'

    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 200
    assert response.json()['responses'][0] == {
        'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': 114.0},
            {'id': 'dbid0_uuid0', 'score': 640.0},
        ],
    }
    assert response.json()['responses'][1] == {
        'search': {},
        'candidates': [
            {'id': 'dbid3_uuid3', 'score': 480.0},
            {'id': 'dbid0_uuid0', 'score': 630.0},
        ],
    }


@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.experiments3(filename='bonuses_by_user_uid.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
async def test_driver_bonuses_config_by_user_uid(taxi_driver_scoring):
    body = copy.deepcopy(BULK_BODY)
    body['requests'][0]['search']['order']['user_uid'] = 'user_uid0'
    body['requests'][1]['search']['order']['user_uid'] = 'user_uid1'

    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 200
    assert response.json()['responses'][0] == {
        'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': 114.0},
            {'id': 'dbid0_uuid0', 'score': 640.0},
        ],
    }
    assert response.json()['responses'][1] == {
        'search': {},
        'candidates': [
            {'id': 'dbid3_uuid3', 'score': 480.0},
            {'id': 'dbid0_uuid0', 'score': 630.0},
        ],
    }


@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.experiments3(filename='bonuses_by_experiments_names_10.json')
@pytest.mark.experiments3(filename='bonuses_by_experiments_names_20.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
async def test_driver_bonuses_config_by_experiments_names(taxi_driver_scoring):
    body = copy.deepcopy(BULK_BODY)
    body['requests'][0]['search']['metadata'] = {
        'experiments': [
            {'name': 'bonus-10', 'version': 0, 'position': 0, 'value': {}},
            {'name': 'other', 'version': 0, 'position': 0, 'value': {}},
        ],
    }
    body['requests'][1]['search']['metadata'] = {
        'experiments': [
            {'name': 'bonus-20', 'version': 0, 'position': 0, 'value': {}},
        ],
    }

    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 200
    assert response.json()['responses'][0] == {
        'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': 114.0},
            {'id': 'dbid0_uuid0', 'score': 640.0},
        ],
    }
    assert response.json()['responses'][1] == {
        'search': {},
        'candidates': [
            {'id': 'dbid3_uuid3', 'score': 480.0},
            {'id': 'dbid0_uuid0', 'score': 630.0},
        ],
    }


@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.experiments3(filename='bonuses_by_phone_id.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
async def test_driver_bonuses_config_by_phone_id(taxi_driver_scoring):
    body = copy.deepcopy(BULK_BODY)
    body['requests'][0]['search']['order']['user_phone_id'] = 'phone_id0'

    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 200
    assert response.json()['responses'][0] == {
        'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': 114.0},
            {'id': 'dbid0_uuid0', 'score': 640.0},
        ],
    }
    assert response.json()['responses'][1] == {
        'search': {},
        'candidates': [
            {'id': 'dbid3_uuid3', 'score': 480.0},
            {'id': 'dbid0_uuid0', 'score': 630.0},
        ],
    }
