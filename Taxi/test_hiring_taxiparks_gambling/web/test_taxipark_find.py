import freezegun
import pytest

from test_hiring_taxiparks_gambling import conftest


async def test_invalid_search_query(web_app_client, load_json, find_parks):
    invalid_requests = load_json('requests.json')['invalid']
    for request in invalid_requests:
        response = await find_parks(request)
        assert response.status == 400


@pytest.mark.usefixtures('upload_parks')
async def test_no_parks_in_city(web_app_client, load_json, find_parks):
    request = load_json('requests.json')['no_parks_in_city']
    response = await find_parks(request)
    response_body = await response.json()

    assert response.status == 200
    assert not response_body['parks']
    assert response_body['finished'] is True


@conftest.main_configuration
async def test_find_park_by_db_id(web_app_client, load_json, find_parks):
    real_parks = load_json('new_parks.json')['taxiparks']
    request = load_json('requests.json')['find_park_by_db_id']
    request['park'] = real_parks[0]['db_uuid']
    headers = {'X-External-Service': 'salesforce'}
    response = await find_parks(request, headers)
    response_body = await response.json()

    assert response.status == 200
    assert len(response_body['parks']) == 1
    assert response_body['parks'][0]['_id'] == real_parks[0]['_id']
    assert response_body['parks'][0]['db_id'].startswith('DB_ID')
    assert response_body['parks'][0]['contact_phone']
    assert response_body['parks'][0]['address']


@conftest.main_configuration
async def test_find_1_park_in_city(web_app_client, load_json, find_parks):
    request = load_json('requests.json')['1_park_in_city']
    headers = {'X-External-Service': 'taximeter'}
    response = await find_parks(request, headers)
    response_body = await response.json()

    assert response.status == 200
    assert len(response_body['parks']) == 1
    assert request['city'] in response_body['parks'][0]['city']


@pytest.mark.usefixtures('upload_parks')
async def test_find_2_parks_in_city(web_app_client, load_json, find_parks):
    request = load_json('requests.json')['2_parks_in_city']
    request['used_parks'] = []
    results_finished = []
    for idx in range(3):  # noqa pylint: disable=W0612
        response = await find_parks(request)
        assert response.status == 200
        response_body = await response.json()
        parks = response_body['parks']
        request['used_parks'].append(parks[0]['_id'])

        for park in parks:
            assert park.get('db_id') is None
            assert park.get('contact_phone') is None
            assert park.get('address') is None
        results_finished.append(response_body['finished'])
        if response_body['finished'] is False:
            assert len(parks) == 1
            assert request['city'] in parks[0]['city']
        else:
            assert len(parks) == 2
    assert results_finished.count(False) == 2
    assert results_finished.count(True) == 1


# Test if 'finished' flag indicates that park blacklist ('used_parks')
# had exhausted all output and had to be ignored.
# This behaviour is important for this task:
# https://st.yandex-team.ru/INFRANAIM-5771
@conftest.main_configuration
async def test_find_2_parks_with_blacklist(
        web_app_client, load_json, find_parks,
):
    headers = {'X-External-Service': 'taximeter'}
    request = load_json('requests.json')['2_parks_full']
    request['blacklisted_db_ids'] = []
    cases = [
        # both parks returned
        {'finished': False, 'len_parks': 2},
        # one park is blacklisted ('used_parks'), another one returned
        {'finished': False, 'len_parks': 1},
        # both parks blacklisted, return no parks
        {'finished': True, 'len_parks': 0},
    ]
    for case in cases:
        response = await find_parks(request, headers)
        assert response.status == 200
        response_body = await response.json()
        parks = response_body['parks']

        assert len(parks) == case['len_parks']
        assert response_body['finished'] == case['finished']
        if parks:
            for park in parks:
                assert park['db_id'] not in request['blacklisted_db_ids']
            request['blacklisted_db_ids'].append(parks[0]['db_id'])


@pytest.mark.usefixtures('upload_parks')
async def test_find_2_parks_full(web_app_client, load_json, find_parks):
    request = load_json('requests.json')['2_parks_full']
    request['used_parks'] = []
    cases = [
        # both parks returned
        {'finished': False, 'len_parks': 2},
        # one park is blacklisted ('used_parks'), another one returned
        {'finished': False, 'len_parks': 1},
        # both parks blacklisted, search finished, return both parks
        {'finished': True, 'len_parks': 2},
    ]
    for case in cases:
        response = await find_parks(request)
        assert response.status == 200
        response_body = await response.json()
        parks = response_body['parks']
        request['used_parks'].append(parks[0]['_id'])

        assert len(parks) == case['len_parks']
        assert response_body['finished'] == case['finished']
        for park in parks:
            assert park.get('db_id') is None
            assert park.get('contact_phone') is None
            assert park.get('address') is None
            assert request['city'] in park['city']


@pytest.mark.usefixtures('upload_parks')
async def test_proper_deaf_relation(web_app_client, load_json, find_parks):
    parks = load_json('new_parks.json')
    request = load_json('requests.json')['deaf']
    response = await find_parks(request)
    response_body = await response.json()

    assert response.status == 200
    deaf_park_ids = [
        park['_id']
        for park in parks['taxiparks']
        if park['deaf_relation'] in ['only_deaf', 'deaf_and_not_deaf']
    ]
    for suggest in response_body['parks']:
        assert suggest['_id'] in deaf_park_ids

    request = load_json('requests.json')['not_deaf']
    response = await find_parks(request)
    response_body = await response.json()

    assert response.status == 200
    deaf_park_ids = [
        park['_id']
        for park in parks['taxiparks']
        if park['deaf_relation'] in ['only_not_deaf', 'deaf_and_not_deaf']
    ]
    for suggest in response_body['parks']:
        assert suggest['_id'] in deaf_park_ids


@pytest.mark.usefixtures('upload_parks')
async def test_proper_mediums(web_app_client, load_json, patch, find_parks):
    @patch(
        'hiring_taxiparks_gambling.internal.experiments._request_experiments',
    )
    async def handler(*args):  # noqa pylint: disable=W0612
        class ExperimentResponse:
            name = 'hiring_park_choice'
            value = [
                {
                    'requested_field': 'medium',
                    'park_field': 'mediums',
                    'comparison': 'in',
                    'on_success': {
                        'action': 'add_state',
                        'value': 'medium_success',
                    },
                    'on_fail': {
                        'action': 'add_state',
                        'value': 'medium_failure',
                    },
                },
            ]

        return [ExperimentResponse()]

    requests = load_json('requests.json')

    request = requests['with_medium_online']
    response = await find_parks(request)
    response_body = await response.json()

    assert response.status == 200
    assert len(response_body['parks']) == 1
    assert response_body['parks'][0]['_id'] == 'MONGOID_3'
    assert 'medium_success' in response_body['park_choice_states']
    assert not response_body['finished']

    request = requests['medium_doesnt_exist']
    response = await find_parks(request)
    response_body = await response.json()

    assert response.status == 200
    assert 'medium_failure' in response_body['park_choice_states']
    assert not response_body['finished']

    request = requests['without_medium_parameter']
    response = await find_parks(request)
    response_body = await response.json()

    assert response.status == 200
    assert len(response_body['parks']) == 2
    assert not response_body['finished']


@pytest.mark.usefixtures('upload_parks')
async def test_proper_location(web_app_client, load_json, find_parks):
    request = load_json('requests.json')['with_location']
    response = await find_parks(request)
    response_body = await response.json()

    assert response.status == 200
    assert response_body['parks']
    for suggest in response_body['parks']:
        assert suggest.get('location')


@pytest.mark.usefixtures('upload_parks')
async def test_limit(web_app_client, load_json, find_parks):
    def _find_ids(all_parks: list):
        return set(item['_id'] for item in all_parks)

    request = load_json('requests.json')['with_limit']
    response = await find_parks(request)
    assert response.status == 200
    response_body = await response.json()
    all_parks = response_body['parks']
    assert all_parks

    all_parks_len = len(all_parks)
    assert len(_find_ids(all_parks)) == all_parks_len > 1
    while all_parks_len > 1:
        all_parks_len -= 1
        request['limit'] = all_parks_len
        response_limited = await find_parks(request)
        assert response_limited.status == 200
        body = await response_limited.json()
        parks = body['parks']
        assert len(parks) == all_parks_len
        assert len(_find_ids(parks)) == len(parks)


@pytest.mark.usefixtures('upload_parks')
@freezegun.freeze_time('2020-03-16T12:00:00')
async def test_schedule_exp3(web_app_client, patch, find_parks):
    @patch(
        'hiring_taxiparks_gambling.internal.experiments._request_experiments',
    )
    async def handler(*args):  # noqa pylint: disable=W0612
        class ExperimentResponse:
            name = 'hiring_park_choice'
            value = [
                {
                    'requested_field': '',
                    'park_field': 'schedule_rent',
                    'comparison': 'check_schedule',
                    'on_success': {
                        'action': 'add_state',
                        'value': 'schedule_success',
                    },
                    'on_fail': {
                        'action': 'add_state',
                        'value': 'schedule_failure',
                    },
                },
            ]

        return [ExperimentResponse()]

    request = {
        'city': 'Казань',
        'random_park': True,
        'rent': True,
        'deaf_relation': ['only_deaf'],
    }
    response = await find_parks(request)
    response_body = await response.json()

    assert response_body['parks']
    assert 'schedule_success' in response_body['park_choice_states']

    request = {
        'city': 'Набережные Челны',
        'random_park': True,
        'rent': True,
        'deaf_relation': ['only_not_deaf'],
    }
    response = await find_parks(request)
    response_body = await response.json()
    assert response_body['parks']
    assert 'schedule_failure' in response_body['park_choice_states']


@pytest.mark.usefixtures('upload_parks')
@pytest.mark.parametrize(
    'request_name',
    [
        'with_fleet_type_empty',
        'with_fleet_type_uberdriver',
        'with_fleet_type_non_existent',
    ],
)
@freezegun.freeze_time('2020-03-16T12:00:00')
async def test_fleet_type(
        web_app_client, patch, find_parks, load_json, request_name,
):
    request = load_json('requests.json')[request_name]
    parks = {
        item['_id']: item['fleet_type']
        for item in load_json('new_parks.json')['taxiparks']
        if item['city'] == 'Ереван'
    }
    response = await find_parks(request)
    response_body = await response.json()

    if request_name.endswith('non_existent'):
        assert not response_body['parks']
    else:
        assert response_body['parks']
        fleet_type = 'taximeter'
        if request_name.endswith('uberdriver'):
            fleet_type = 'uberdriver'
        for park in response_body['parks']:
            assert parks[park['_id']] == fleet_type


@pytest.mark.usefixtures('upload_parks')
async def test_check_weighted_random(
        web_app_client, load_json, patch, find_parks,
):
    async def check_weight(db_id, assert_with):
        _request = {'db_id': db_id}
        _response = await web_app_client.get(
            '/taxiparks/get-weights', params=_request,
        )
        _response_body = await _response.json()
        assert _response_body['park']['weight_rent'] == assert_with

    async def _find_parks(random):
        _request_find = load_json('requests.json')['2_parks_in_city_weighted']
        _request_find['random_park'] = random
        _response = await find_parks(_request_find)
        _response_body = await _response.json()
        assert _response.status == 200
        return _response_body['parks']

    @patch('random.choices')
    def _random(*args, **kwargs):
        population = kwargs.get('population')
        weights = kwargs.get('weights')
        park_weights = {
            item[0]['db_id']: item[1] for item in zip(population, weights)
        }
        assert park_weights['DB_ID0'] == 100
        assert park_weights['DB_ID2'] == 1
        return [population[0]]

    request = load_json('update_weights_requests.json')['for_weighted_random']
    response = await web_app_client.post(
        '/taxiparks/update-weights/',
        data=request,
        headers={'Content-Type': 'text/csv'},
    )
    assert response.status == 200

    mongo_main = 'DB_ID0'
    await check_weight(mongo_main, 100)
    mongo_secondary = 'DB_ID2'
    await check_weight(mongo_secondary, 1)

    parks = await _find_parks(False)
    assert len(parks) == 2

    await _find_parks(random=True)
    assert _random.calls
