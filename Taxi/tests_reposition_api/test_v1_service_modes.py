import pytest


@pytest.mark.now('2017-11-19T16:47:54.721')
async def test_empty(taxi_reposition_api):
    response = await taxi_reposition_api.get('/v1/service/modes')

    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.now('2017-11-19T16:47:54.721')
@pytest.mark.parametrize('has_submodes', [False, True])
@pytest.mark.parametrize('has_offer_only', [False, True])
@pytest.mark.parametrize('has_district', [False, True])
async def test_get(
        taxi_reposition_api,
        pgsql,
        load,
        has_submodes,
        has_offer_only,
        has_district,
):
    queries = [load('mode_home.sql')]

    if has_submodes:
        queries.append(load('submodes_home.sql'))
    if has_offer_only:
        queries.append(load('mode_surge.sql'))
    if has_district:
        queries.append(load('mode_my_district.sql'))

    pgsql['reposition'].apply_queries(queries)

    expected_response = {'home': {'offer_only': False, 'type': 'to_point'}}

    if has_submodes:
        expected_response['home']['submodes'] = {'fast': {}, 'slow': {}}

    if has_offer_only:
        expected_response['surge'] = {'offer_only': True, 'type': 'to_point'}

    if has_district:
        expected_response['my_district'] = {
            'offer_only': False,
            'type': 'in_area',
        }

    response = await taxi_reposition_api.get('/v1/service/modes')

    assert response.status_code == 200
    assert response.json() == expected_response
