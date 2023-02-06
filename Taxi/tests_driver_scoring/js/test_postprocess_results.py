import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


EXPECTED_SCORING = [
    {
        'search': {'order_id': 'deadb0d4'},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': 34.0},
            {'id': 'dbid0_uuid0', 'score': 560.0},
        ],
    },
    {
        'search': {},
        'candidates': [
            {'id': 'dbid3_uuid3', 'score': 410.0},
            {'id': 'dbid0_uuid0', 'score': 560.0},
        ],
    },
]


@pytest.mark.experiments3(filename='postprocess_results_config3.json')
@pytest.mark.experiments3(filename='postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_no_script(taxi_driver_scoring, load_json):
    request_body = load_json('request_body.json')
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == {'responses': EXPECTED_SCORING}


@pytest.mark.experiments3(filename='postprocess_results_config3.json')
@pytest.mark.experiments3(filename='postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_base(taxi_driver_scoring, load_json, testpoint):
    @testpoint('PostprocessResults::create_out_parameters')
    def create_out_parameters(data):
        return data

    script = """
    for (let order_idx = 0; order_idx < order_contexts.length; order_idx++) {
        let order = order_contexts[order_idx];
        let candidates = candidates_contexts[order_idx];
        var scored_order = scoring_results.orders[order_idx];
        var score = 0;
        for (let cand_idx = 0; cand_idx < candidates.length; cand_idx++) {
            if (scored_order.candidates[cand_idx].score !== undefined) {
                score += scored_order.candidates[cand_idx].score;
            }
        }
        scoring_results.orders[order_idx].retention_score = score + 1;
        scoring_results.orders[order_idx].misc.fallback_score = score + 2;
        scoring_results.orders[order_idx].misc.test_additional_property = 42;
        traces.orders[order_idx].text = "passed";
    }
    """
    add_response = await taxi_driver_scoring.post(
        'v2/admin/scripts/add',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'script_name': 'foo_bar',
            'type': 'postprocess_results',
            'content': script,
        },
    )
    assert add_response.status_code == 200

    activate_response = await taxi_driver_scoring.post(
        'v2/admin/scripts/activate',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'id': 12,
            'revision': 0,
            'script_name': 'foo_bar',
            'type': 'postprocess_results',
        },
    )
    assert activate_response.status_code == 202

    await taxi_driver_scoring.invalidate_caches()

    request_body = load_json('request_body.json')
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=request_body,
    )
    assert (await create_out_parameters.wait_call())['data'] == {
        'orders': [
            {
                'candidates': [
                    {
                        'score': 560.0,
                        'is_pessimized': False,
                        'is_filtered': False,
                        'orders_count': 2,
                    },
                    {
                        'score': 34.0,
                        'is_pessimized': False,
                        'is_filtered': False,
                        'orders_count': 1,
                    },
                ],
                'candidates_count': 2,
                'best_cand_index': 1,
                'misc': {},
            },
            {
                'candidates': [
                    {
                        'score': 560.0,
                        'is_pessimized': False,
                        'is_filtered': False,
                        'orders_count': 2,
                    },
                    {
                        'score': 410.0,
                        'is_pessimized': False,
                        'is_filtered': False,
                        'orders_count': 1,
                    },
                ],
                'candidates_count': 2,
                'best_cand_index': 1,
                'misc': {},
            },
        ],
    }
    assert response.status_code == 200
    assert response.json() == {
        'responses': [
            {
                'search': {
                    'order_id': 'deadb0d4',
                    'retention_score': 595.0,
                    'disable_eta_delay': True,
                    'misc': {
                        'fallback_score': 596.0,
                        'test_additional_property': 42,
                    },
                },
                'candidates': [
                    {'id': 'dbid1_uuid1', 'score': 34.0},
                    {'id': 'dbid0_uuid0', 'score': 560.0},
                ],
            },
            {
                'search': {
                    'retention_score': 971.0,
                    'disable_eta_delay': True,
                    'misc': {
                        'fallback_score': 972.0,
                        'test_additional_property': 42,
                    },
                },
                'candidates': [
                    {'id': 'dbid3_uuid3', 'score': 410.0},
                    {'id': 'dbid0_uuid0', 'score': 560.0},
                ],
            },
        ],
    }


@pytest.mark.experiments3(filename='postprocess_results_config3.json')
@pytest.mark.experiments3(filename='postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_script_timeout(taxi_driver_scoring, load_json):
    script = """
    var score = 0;
    for (let i = 0; i < 100000000000; i++) {
        score += 1;
    }
    """
    add_response = await taxi_driver_scoring.post(
        'v2/admin/scripts/add',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'script_name': 'foo_bar',
            'type': 'postprocess_results',
            'content': script,
        },
    )
    assert add_response.status_code == 200

    activate_response = await taxi_driver_scoring.post(
        'v2/admin/scripts/activate',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'id': 12,
            'revision': 0,
            'script_name': 'foo_bar',
            'type': 'postprocess_results',
        },
    )
    assert activate_response.status_code == 202

    await taxi_driver_scoring.invalidate_caches()

    request_body = load_json('request_body.json')
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == {'responses': EXPECTED_SCORING}


@pytest.mark.experiments3(filename='postprocess_results_config3.json')
@pytest.mark.experiments3(filename='postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_change_score(taxi_driver_scoring, load_json):
    script = """
    for (let order_idx = 0; order_idx < order_contexts.length; order_idx++) {
        let order = order_contexts[order_idx];
        let candidates = candidates_contexts[order_idx];
        var scored_order = scoring_results.orders[order_idx];
        for (let cand_idx = 0; cand_idx < candidates.length; cand_idx++) {
            scored_order.candidates[cand_idx].score = 1
        }
        scoring_results.orders[order_idx].retention_score = 1;
        scoring_results.orders[order_idx].misc.fallback_score = 1;
    }
    """
    add_response = await taxi_driver_scoring.post(
        'v2/admin/scripts/add',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'script_name': 'foo_bar',
            'type': 'postprocess_results',
            'content': script,
        },
    )
    assert add_response.status_code == 200

    activate_response = await taxi_driver_scoring.post(
        'v2/admin/scripts/activate',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'id': 12,
            'revision': 0,
            'script_name': 'foo_bar',
            'type': 'postprocess_results',
        },
    )
    assert activate_response.status_code == 202

    await taxi_driver_scoring.invalidate_caches()

    request_body = load_json('request_body.json')
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json()['responses'][0]['candidates'] == [
        {'id': 'dbid0_uuid0', 'score': 1.0},
        {'id': 'dbid1_uuid1', 'score': 1.0},
    ]
    assert response.json()['responses'][1]['candidates'] == [
        {'id': 'dbid0_uuid0', 'score': 1.0},
        {'id': 'dbid3_uuid3', 'score': 1.0},
    ]
    for response in response.json()['responses']:
        assert response['search']['retention_score'] == 1
        assert response['search']['misc']['fallback_score'] == 1


@pytest.mark.experiments3(filename='postprocess_results_config3.json')
@pytest.mark.experiments3(filename='postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_pessimize(taxi_driver_scoring, load_json):
    script = """
    scoring_results.orders[0].candidates[1].is_pessimized = true;
    scoring_results.orders[1].candidates[1].is_pessimized = true;
    """
    add_response = await taxi_driver_scoring.post(
        'v2/admin/scripts/add',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'script_name': 'foo_bar',
            'type': 'postprocess_results',
            'content': script,
        },
    )
    assert add_response.status_code == 200

    activate_response = await taxi_driver_scoring.post(
        'v2/admin/scripts/activate',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'id': 12,
            'revision': 0,
            'script_name': 'foo_bar',
            'type': 'postprocess_results',
        },
    )
    assert activate_response.status_code == 202

    await taxi_driver_scoring.invalidate_caches()

    request_body = load_json('request_body.json')
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json()['responses'][0]['candidates'] == [
        {'id': 'dbid0_uuid0', 'score': 560.0},
        {'id': 'dbid1_uuid1', 'score': 561.0},
    ]
    assert response.json()['responses'][1]['candidates'] == [
        {'id': 'dbid0_uuid0', 'score': 560.0},
        {'id': 'dbid3_uuid3', 'score': 561.0},
    ]


@pytest.mark.experiments3(filename='postprocess_results_config3.json')
@pytest.mark.experiments3(filename='postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_exclude(taxi_driver_scoring, load_json):
    script = """
    scoring_results.orders[0].candidates[1].is_filtered = true;
    scoring_results.orders[1].candidates[1].is_filtered = true;
    """
    add_response = await taxi_driver_scoring.post(
        'v2/admin/scripts/add',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'script_name': 'foo_bar',
            'type': 'postprocess_results',
            'content': script,
        },
    )
    assert add_response.status_code == 200

    activate_response = await taxi_driver_scoring.post(
        'v2/admin/scripts/activate',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'id': 12,
            'revision': 0,
            'script_name': 'foo_bar',
            'type': 'postprocess_results',
        },
    )
    assert activate_response.status_code == 202

    await taxi_driver_scoring.invalidate_caches()

    request_body = load_json('request_body.json')
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json()['responses'][0]['candidates'] == [
        {'id': 'dbid0_uuid0', 'score': 560.0},
    ]
    assert response.json()['responses'][1]['candidates'] == [
        {'id': 'dbid0_uuid0', 'score': 560.0},
    ]


@pytest.mark.experiments3(filename='postprocess_results_config3.json')
@pytest.mark.experiments3(filename='postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_include(taxi_driver_scoring, load_json):
    script = """
    scoring_results.orders[0].candidates[1].is_filtered = false;
    """
    add_response = await taxi_driver_scoring.post(
        'v2/admin/scripts/add',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'script_name': 'foo_bar',
            'type': 'postprocess_results',
            'content': script,
        },
    )
    assert add_response.status_code == 200

    activate_response = await taxi_driver_scoring.post(
        'v2/admin/scripts/activate',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
            'id': 12,
            'revision': 0,
            'script_name': 'foo_bar',
            'type': 'postprocess_results',
        },
    )
    assert activate_response.status_code == 202

    await taxi_driver_scoring.invalidate_caches()

    request_body = load_json('request_body.json')
    request_body['requests'][0]['search']['order_id'] = 'filter'

    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=request_body,
    )
    assert response.status_code == 200

    assert response.json()['responses'][0]['candidates'] == [
        {'id': 'dbid1_uuid1', 'score': 124.0},
    ]  # reincluded back
    assert response.json()['responses'][1]['candidates'] == [
        {'id': 'dbid3_uuid3', 'score': 410.0},
        {'id': 'dbid0_uuid0', 'score': 560.0},
    ]
