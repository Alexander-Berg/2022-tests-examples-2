import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.config(DRIVER_SCORING_EATS_TAGS_FETCHERS_ENABLED=True)
async def test_driver_scoring_js_bonuses_eats_place_tags(
        taxi_driver_scoring, load_json, eats_tags,
):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=load_json('request_body_full_with_eats.json'),
    )
    assert response.status_code == 200

    assert response.json()['responses'] == [
        {
            'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
            'candidates': [
                {'id': 'dbid1_uuid1', 'score': 24.0},
                {'id': 'dbid0_uuid0', 'score': 550.0},
            ],
        },
        {
            'search': {},
            'candidates': [
                {'id': 'dbid1_uuid1', 'score': 124.0},
                {'id': 'dbid0_uuid0', 'score': 650.0},
            ],
        },
    ]


@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.pgsql('driver_scoring', files=['js_bonus_for_empty_tagset.sql'])
@pytest.mark.eats_tags_entities(place_id_entities={'0': []})
@pytest.mark.config(DRIVER_SCORING_EATS_TAGS_FETCHERS_ENABLED=True)
async def test_fetch_empty_eats_place_tags_set(
        taxi_driver_scoring, load_json, eats_tags,
):
    # Make mocked `eats-tags` return empty array of tags for the place
    # and check that `order_context.eats_place_tags` is not `undefined`
    request_body = load_json('request_body_with_eats.json')
    request_body['requests'][0]['search']['order']['request']['eats_batch'][0][
        'context'
    ]['place_id'] = 0

    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == {
        'responses': [
            {
                'search': {},
                'candidates': [{'id': 'dbid0_uuid0', 'score': 527.0}],
            },
        ],
    }


@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.pgsql('driver_scoring', files=['js_bonus_for_undefined.sql'])
@pytest.mark.config(DRIVER_SCORING_EATS_TAGS_FETCHERS_ENABLED=True)
async def test_fail_fetch_eats_place_tags(
        taxi_driver_scoring, mockserver, load_json, eats_tags,
):
    # Make mocked `eats-tags` return error code on valid request,
    # so that we check that `order_context.eats_place_tags`
    # equals to `undefined`
    @mockserver.json_handler('/eats-tags/v2/match')
    def _profiles(request):
        return mockserver.make_response(status=500)

    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=load_json('request_body.json'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'responses': [
            {
                'search': {},
                'candidates': [{'id': 'dbid0_uuid0', 'score': 535.0}],
            },
        ],
    }


@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.pgsql('driver_scoring', files=['js_bonus_for_undefined.sql'])
@pytest.mark.config(DRIVER_SCORING_EATS_TAGS_FETCHERS_ENABLED=True)
async def test_missing_eats_in_req_eats_place_tags(
        taxi_driver_scoring, mockserver, load_json, eats_tags,
):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=load_json('request_body.json'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'responses': [
            {
                'search': {},
                'candidates': [{'id': 'dbid0_uuid0', 'score': 535.0}],
            },
        ],
    }
