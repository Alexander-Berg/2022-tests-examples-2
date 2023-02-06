import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_driver_scoring_js_bonuses_user_tags(
        taxi_driver_scoring, load_json,
):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=load_json('main_request_body.json'),
    )
    assert response.status_code == 200

    assert response.json()['responses'] == [
        {
            'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
            'candidates': [
                {'id': 'dbid1_uuid1', 'score': 14.0},
                {'id': 'dbid0_uuid0', 'score': 540.0},
            ],
        },
        {
            'search': {},
            'candidates': [
                {'id': 'dbid1_uuid1', 'score': 124.0},
                {'id': 'dbid0_uuid0', 'score': 650.0},
            ],
        },
        {
            'search': {},
            'candidates': [
                {'id': 'dbid1_uuid1', 'score': 24.0},
                {'id': 'dbid0_uuid0', 'score': 550.0},
            ],
        },
    ]


@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.pgsql('driver_scoring', files=['js_bonus_for_empty_tagset.sql'])
@pytest.mark.passenger_tags_entities(
    user_id_entities={'user_id_without_tags': []},
    user_phone_id_entities={'user_phone_id_without_tags': []},
)
async def test_fetch_empty_passenger_tags_set(taxi_driver_scoring, load_json):
    # Make mocked `passenger-tags` return empty array of tags for the user
    # and check that `order_context.user_tags` is not `undefined`
    request_body = load_json('request_body.json')
    request_body['requests'][0]['search']['order'][
        'user_id'
    ] = 'user_id_without_tags'
    request_body['requests'][0]['search']['order'][
        'user_phone_id'
    ] = 'user_phone_id_without_tags'

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
                'candidates': [{'id': 'dbid0_uuid0', 'score': 600.0}],
            },
        ],
    }


@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.pgsql('driver_scoring', files=['js_bonus_for_undefined.sql'])
async def test_fail_fetch_user_tags(
        taxi_driver_scoring, mockserver, load_json,
):
    # Make mocked `passenger-tags` return error code on valid request,
    # so that we check that `order_context.user_tags` equals to `undefined`
    @mockserver.json_handler('/passenger-tags/v2/match')
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
                'candidates': [{'id': 'dbid0_uuid0', 'score': 600.0}],
            },
        ],
    }
