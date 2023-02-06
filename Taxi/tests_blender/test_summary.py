import pytest

HEADERS = {
    'X-Yandex-UID': '12345',
    'X-YaTaxi-UserId': '50b3bc6b41a4484384e34f5360962d12',
    'X-YaTaxi-PhoneId': 'phone_id',
}

PA_EXTRA_HEADERS = {
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_brand=yango,app_name=yango_android',
}


SCENARIO_RELEVANCE_MAPPING = {
    'econom': 0.2,
    'comfort': 0.25,
    'comfortplus': 0.28,
    'business': 0.73,
    'vip': 0.31,
}

SUMMARY_RULES_CONFIG_COMMON = {
    'experiments_priority': ['blender_summary_rules'],
    'add_unprocessed': True,
}


@pytest.fixture
def _mock_scenario_prediction(mockserver):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/scenario-prediction')
    def _get_scenario_prediction(request):
        app_state = request.json['state']
        assert app_state['current_mode'] == 'summary'
        results = [
            {'scenario': scenario, 'relevance': relevance}
            for scenario, relevance in SCENARIO_RELEVANCE_MAPPING.items()
        ]
        return mockserver.make_response(json={'results': results})


@pytest.fixture(name='mock_maps_search')
def _mock_maps_search(mockserver, load_json, yamaps):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if 'uri' in request.args:
            if request.args['uri'] == 'ymapsbm1://uri_of_airport':
                return [load_json('yamaps_org_types/geo_object_airport.json')]
            if request.args['uri'] == 'ymapsbm1://uri_of_restaurant':
                return [
                    load_json('yamaps_org_types/geo_object_restaurant.json'),
                ]
        if 'll' in request.args:
            if request.args['ll'] == '37.380031,55.815791':
                assert request.args['text'] == 'Аэропорт Домодедово'
                return [load_json('yamaps_org_types/geo_object_airport.json')]
        raise ValueError(f'Invalid request: {request.args}')


def compare_responses(lhs, rhs):
    priority_l = {i['class']: i['promoblocks_order'] for i in lhs['priority']}
    priority_r = {i['class']: i['promoblocks_order'] for i in rhs['priority']}
    assert priority_l == priority_r


@pytest.mark.config(
    BLENDER_SUMMARY_RULES_MANAGEMENT=SUMMARY_RULES_CONFIG_COMMON,
)
@pytest.mark.experiments3(filename='user_tags/experiment.json')
@pytest.mark.parametrize(
    'request_json, answer_json',
    [
        ('user_tags/request1.json', 'user_tags/response1.json'),
        ('user_tags/request2.json', 'user_tags/response2.json'),
    ],
)
async def test_user_tags(taxi_blender, load_json, request_json, answer_json):
    req_body = load_json(request_json)
    response = await taxi_blender.post(
        '/blender/v1/internal/summary/priority',
        json=req_body,
        headers=HEADERS,
    )
    assert response.status_code == 200
    resp_body = response.json()
    compare_responses(resp_body, load_json(answer_json))


@pytest.mark.config(
    BLENDER_SUMMARY_RULES_MANAGEMENT={
        **SUMMARY_RULES_CONFIG_COMMON,  # type: ignore
        'add_unprocessed': False,
    },
    BLENDER_YAMAPS_ENABLED=True,
)
@pytest.mark.experiments3(filename='yamaps_org_types/experiment.json')
@pytest.mark.parametrize(
    'request_json, answer_json',
    [
        ('yamaps_org_types/request1.json', 'yamaps_org_types/response1.json'),
        ('yamaps_org_types/request2.json', 'yamaps_org_types/response2.json'),
    ],
)
async def test_yamaps_org_types(
        taxi_blender, load_json, request_json, answer_json, mock_maps_search,
):
    req_body = load_json(request_json)
    response = await taxi_blender.post(
        '/blender/v1/internal/summary/priority',
        json=req_body,
        headers=HEADERS,
    )
    assert response.status_code == 200
    resp_body = response.json()
    compare_responses(resp_body, load_json(answer_json))


@pytest.mark.config(
    BLENDER_SUMMARY_RULES_MANAGEMENT=SUMMARY_RULES_CONFIG_COMMON,
)
@pytest.mark.experiments3(
    filename='user_tags/experiment_prohibited_promos.json',
)
@pytest.mark.parametrize(
    'request_json, answer_json',
    [
        (
            'user_tags/request1.json',
            'user_tags/response1_prohibited_promos.json',
        ),
    ],
)
async def test_user_tags_prohibited_promos(
        taxi_blender, load_json, request_json, answer_json,
):
    req_body = load_json(request_json)
    response = await taxi_blender.post(
        '/blender/v1/internal/summary/priority',
        json=req_body,
        headers=HEADERS,
    )
    assert response.status_code == 200
    resp_body = response.json()
    compare_responses(resp_body, load_json(answer_json))


@pytest.mark.config(
    BLENDER_SUMMARY_RULES_MANAGEMENT={
        **SUMMARY_RULES_CONFIG_COMMON,  # type: ignore
        'add_unprocessed': False,
    },
)
@pytest.mark.experiments3(filename='address_tariff/experiment.json')
@pytest.mark.parametrize(
    'request_json, answer_json',
    [
        ('address_tariff/request1.json', 'address_tariff/response1.json'),
        ('address_tariff/request2.json', 'address_tariff/response2.json'),
        ('address_tariff/request3.json', 'address_tariff/response3.json'),
    ],
)
async def test_address_tariff(
        taxi_blender, load_json, request_json, answer_json,
):
    req_body = load_json(request_json)
    response = await taxi_blender.post(
        '/blender/v1/internal/summary/priority',
        json=req_body,
        headers=HEADERS,
    )
    assert response.status_code == 200
    resp_body = response.json()
    compare_responses(resp_body, load_json(answer_json))


@pytest.mark.config(
    BLENDER_SUMMARY_RULES_MANAGEMENT={
        **SUMMARY_RULES_CONFIG_COMMON,  # type: ignore
        'add_unprocessed': False,
    },
)
@pytest.mark.experiments3(filename='random/experiment.json')
@pytest.mark.parametrize(
    'request_json, answer_json',
    [('random/request.json', 'random/response.json')],
)
async def test_random(taxi_blender, load_json, request_json, answer_json):
    req_body = load_json(request_json)
    response = await taxi_blender.post(
        '/blender/v1/internal/summary/priority',
        json=req_body,
        headers=HEADERS,
    )
    assert response.status_code == 200
    resp_body = response.json()
    compare_responses(resp_body, load_json(answer_json))


@pytest.mark.config(
    BLENDER_SUMMARY_RULES_MANAGEMENT={
        **SUMMARY_RULES_CONFIG_COMMON,  # type: ignore
        'add_unprocessed': False,
    },
)
@pytest.mark.experiments3(filename='scenario_prediction/experiment.json')
@pytest.mark.config(BLENDER_SCENARIO_PREDICTION_ENABLED=True)
@pytest.mark.parametrize(
    'request_json, answer_json',
    [
        (
            'scenario_prediction/request.json',
            'scenario_prediction/response.json',
        ),
    ],
)
async def test_scenario_prediction(
        taxi_blender,
        request_json,
        answer_json,
        load_json,
        _mock_scenario_prediction,
):
    req_body = load_json(request_json)
    response = await taxi_blender.post(
        '/blender/v1/internal/summary/priority',
        json=req_body,
        headers={**HEADERS, **PA_EXTRA_HEADERS},
    )
    assert response.status_code == 200
    resp_body = response.json()
    compare_responses(resp_body, load_json(answer_json))


@pytest.mark.config(
    BLENDER_SUMMARY_RULES_MANAGEMENT=SUMMARY_RULES_CONFIG_COMMON,
)
async def test_summary_no_exp(taxi_blender, load_json):
    req_body = load_json('no_exp/request.json')
    response = await taxi_blender.post(
        '/blender/v1/internal/summary/priority',
        json=req_body,
        headers=HEADERS,
    )
    assert response.status_code == 200
    resp_body = response.json()
    compare_responses(resp_body, load_json('no_exp/response.json'))
