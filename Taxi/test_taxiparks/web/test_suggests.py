import pytest

ROUTE_MEDIUMS = '/get_mediums'
ROUTE_PARKS = '/arrays/find_taxiparks'


@pytest.mark.usefixtures('log_in')
@pytest.mark.parametrize(
    'route',
    [
        '/suggests/organization'
    ]
)
def test_simple_suggests(taxiparks_client, route):
    response = taxiparks_client.get(
        route,
        query_string={},
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'found', [True, False],
)
def test_gambling(patch, taxiparks_client_factory, get_mongo, found):

    @patch('infranaim.clients.gambling.Gambling.choose_taxipark')
    def _gambling(*args, **kwargs):
        if found:
            return {
                'parks': [
                    {
                        '_id': 'SOME_ID',
                        'city': 'Москва',
                        'taximeter_name': 'Some name'
                    }
                ],
                'park_choice_states': []
            }
        return {
            'parks': [],
            'park_choice_states': []
        }

    mongo = get_mongo
    client = taxiparks_client_factory(
        mongo,
        configs={
            'PROXY_HIRING_TAXIPARKS_GAMBLING': True,
        },
    )
    user = {
        'login': 'root',
        'password': 'root_pass',
        'csrf_token': client.get('/get_token').json['token']
    }
    client.post('/login', json=user)
    request = {
        'city': 'Москва',
        'csrf_token': client.get('/get_token').json['token']
    }
    response = client.post(
        ROUTE_PARKS,
        json=request,
    )
    assert response.status_code == 200


@pytest.mark.usefixtures('log_in')
@pytest.mark.parametrize(
    'env',
    [
        'TESTING', 'PRODUCTION',
    ]
)
def test_mediums(taxiparks_client_factory, get_mongo, env):
    mongo = get_mongo
    client = taxiparks_client_factory(
        mongo,
        configs={
            'ENVIRONMENT': env,
        },
    )
    user = {
        'login': 'root',
        'password': 'root_pass',
        'csrf_token': client.get('/get_token').json['token']
    }
    client.post('/login', json=user)
    response = client.get(ROUTE_MEDIUMS)
    assert response.status_code == 200
    mediums = set(item['id'] for item in response.json)
    if env == 'TESTING':
        assert 'TEST_MEDIUM' in mediums
    else:
        assert 'PROD_MEDIUM' in mediums
