import pytest

AVAILABLE_INTERVALS = {
    'available_intervals': [
        {
            'from': '2022-02-19T19:10:00+00:00',
            'to': '2022-02-19T22:00:00+00:00',
        },
        {
            'from': '2022-02-20T02:10:00+00:00',
            'to': '2022-02-20T06:00:00+00:00',
        },
    ],
}


@pytest.mark.config(
    CARGO_SDD_TAXI_TARIFF_SETTINGS={
        'remove_in_tariffs': True,
        'remove_in_admin_tariffs': False,
        'name': 'cargo',
    },
)
async def test_get_intervals(
        taxi_cargo_matcher,
        mockserver,
        experiments3,
        exp3_same_day,
        corp_id='corp_client_id_12312312312312314',
):
    await exp3_same_day(corp_id=corp_id)

    @mockserver.json_handler(
        '/cargo-sdd/api/integration/v1/same-day/delivery-intervals',
    )
    def _intervals(request):
        assert request.json['corp_client_id'] == corp_id
        assert request.json['route_points'][0] == {
            'coordinates': {'lon': 37.1, 'lat': 55.1},
        }

        return AVAILABLE_INTERVALS

    response = await taxi_cargo_matcher.post(
        '/api/integration/v1/delivery-intervals',
        headers={'X-B2B-Client-Id': corp_id},
        json={'start_point': [37.1, 55.1]},
    )

    assert response.status_code == 200
    assert response.json() == AVAILABLE_INTERVALS


@pytest.mark.config(
    CARGO_SDD_TAXI_TARIFF_SETTINGS={
        'remove_in_tariffs': True,
        'remove_in_admin_tariffs': True,
        'name': 'night',
    },
)
async def test_not_sdd_tariff(
        taxi_cargo_matcher,
        mockserver,
        corp_id='corp_client_id_12312312312312314',
):
    @mockserver.json_handler(
        '/cargo-sdd/api/integration/v1/same-day/delivery-intervals',
    )
    def _intervals(request):
        return {}

    response = await taxi_cargo_matcher.post(
        '/api/integration/v1/delivery-intervals',
        headers={'X-B2B-Client-Id': corp_id},
        json={'start_point': [37.1, 55.1]},
    )

    assert _intervals.times_called == 0
    assert response.status_code == 200
    assert response.json() == {'available_intervals': []}


async def test_empty_coordinates_and_address(
        taxi_cargo_matcher,
        mockserver,
        corp_id='corp_client_id_12312312312312314',
):
    response = await taxi_cargo_matcher.post(
        '/api/integration/v1/delivery-intervals',
        headers={'X-B2B-Client-Id': corp_id},
        json={},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': 'Необходимо передать координаты или топоним точки',
    }


async def test_undefined_address(
        taxi_cargo_matcher, yamaps, corp_id='corp_client_id_12312312312312314',
):
    response = await taxi_cargo_matcher.post(
        '/api/integration/v1/delivery-intervals',
        headers={'X-B2B-Client-Id': corp_id},
        json={'fullname': 'abracadabra'},
    )

    assert response.status_code == 400
    assert (
        response.json()['message']
        == 'Не удалось преобразовать адрес abracadabra в координаты: '
        'проверьте корректность адреса или попробуйте'
        ' указать координаты вручную'
    )


@pytest.mark.config(
    CARGO_SDD_TAXI_TARIFF_SETTINGS={
        'remove_in_tariffs': True,
        'remove_in_admin_tariffs': False,
        'name': 'cargo',
    },
)
async def test_run_geocoder(
        taxi_cargo_matcher,
        mockserver,
        yamaps,
        load_json,
        exp3_same_day,
        corp_id='corp_client_id_12312312312312314',
):
    await exp3_same_day(corp_id=corp_id)

    @mockserver.json_handler(
        '/cargo-sdd/api/integration/v1/same-day/delivery-intervals',
    )
    def _intervals(request):
        assert (
            request.json['route_points'][0]['coordinates']['lon']
            == coordinates[0]
        )
        assert (
            request.json['route_points'][0]['coordinates']['lat']
            == coordinates[1]
        )
        return AVAILABLE_INTERVALS

    yamaps_response = load_json('yamaps_response.json')
    coordinates = yamaps_response['geometry']

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects_callback(req):
        return [yamaps_response]

    response = await taxi_cargo_matcher.post(
        '/api/integration/v1/delivery-intervals',
        headers={'X-B2B-Client-Id': corp_id},
        json={'fullname': 'fullname'},
    )

    assert response.status_code == 200
    assert _intervals.times_called == 1
