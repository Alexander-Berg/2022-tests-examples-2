import pytest


@pytest.mark.now('2018-05-27T11:00:00+0300')
async def test_request(taxi_special_zones, load_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/localize',
        json={'uris': ['ytpp://luzha/p1', 'ytpp://luzha/p3']},
        headers={'Accept-Language': 'ru-RU;q=1, en-US;q=0.9'},
    )

    assert response.status_code == 200
    assert response.json() == load_json('expected.json')


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.filldb(pickup_zone_items='with_choice')
@pytest.mark.parametrize(
    'headers',
    [
        {'Accept-Language': 'en'},
        {'Accept-Language': 'en', 'X-Request-Language': 'en'},
        {'X-Request-Language': 'en'},
        {},
    ],
)
async def test_request_choices(taxi_special_zones, load_json, headers):
    response = await taxi_special_zones.post(
        'special-zones/v1/localize',
        json={'uris': ['ytpp://luzha/p1', 'ytpp://luzha/p3']},
        headers=headers,
    )

    assert response.status_code == 200
    expected_response = (
        'expected_with_choice_en.json'
        if headers
        else 'expected_with_choice.json'
    )
    assert response.json() == load_json(expected_response)


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.filldb(pickup_zone_items='with_single_choice')
async def test_request_single_choice(taxi_special_zones, load_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/localize',
        json={'uris': ['ytpp://luzha/p1', 'ytpp://luzha/p3']},
        headers={'Accept-Language': 'ru-RU;q=1, en-US;q=0.9'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_with_single_choice.json')


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.filldb(pickup_zone_items='with_choice')
async def test_bad_uri(taxi_special_zones, load_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/localize',
        json={'uris': ['ytpp://luzha/(){}>', 'ytpp://luzha/p3']},
        headers={'Accept-Language': 'ru-RU;q=1, en-US;q=0.9'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_with_one_empty.json')

    bad_requests = [{'uris': ['ytpp://&*@/(){}^']}, {'uris': ['hello']}]
    for request in bad_requests:
        response = await taxi_special_zones.post(
            'special-zones/v1/localize',
            json=request,
            headers={'Accept-Language': 'ru-RU;q=1, en-US;q=0.9'},
        )

        assert response.status_code == 200
        assert response.json() == {'results': [{}]}


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.filldb(pickup_zone_items='with_choice')
async def test_bad_request(taxi_special_zones, load_json):
    bad_requests = [{'uris': []}, {'trash': 'ddii92kd'}]
    for request in bad_requests:
        response = await taxi_special_zones.post(
            'special-zones/v1/localize',
            json=request,
            headers={'Accept-Language': 'ru-RU;q=1, en-US;q=0.9'},
        )

        assert response.status_code == 400


@pytest.mark.now('2018-05-27T11:00:00+0300')
@pytest.mark.filldb(pickup_zone_items='tariffs_in_pp')
async def test_with_category(taxi_special_zones, load_json):
    response = await taxi_special_zones.post(
        'special-zones/v1/localize',
        json={
            'uris': ['ytpp://luzha/p1', 'ytpp://luzha/p2'],
            'selected_tariff': 'vip',
            'type': 'a',
        },
        headers={'Accept-Language': 'en', 'X-Request-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json() == load_json('expected_with_tariff.json')
