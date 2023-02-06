import pytest

from . import utils_v2


@pytest.fixture(name='exp_cargo_claims_geocoder')
async def _exp_cargo_claims_geocoder(taxi_cargo_claims, experiments3):
    async def wrapper(
            *,
            enabled=True,
            use_full_name_for_geocoder=True,
            rebuild_full_name=False,
            error_mode='warning',
            max_distance=None,
            max_fix_coordinates_distance=100500,
            required_address_fields=None,
            address_fields_to_replace=None,
            geocoder_text_format='newway',
            geocoder_check_rules=None,
            numeric_flat=False,
            trust_porch_if_exist=False,
            **kwargs,
    ):
        value = {
            'enabled': enabled,
            'error_mode': error_mode,
            'max_fix_coordinates_distance': max_fix_coordinates_distance,
            'required_address_fields': [],
            'geocoder_text_format': geocoder_text_format,
            'numeric_flat': numeric_flat,
            'trust_porch_if_exist': trust_porch_if_exist,
        }
        point_value = {
            'use_full_name_for_geocoder': use_full_name_for_geocoder,
            'rebuild_full_name': rebuild_full_name,
            'address_fields_to_replace': [],
        }
        if max_distance is not None:
            value['max_distance'] = max_distance
        if required_address_fields is not None:
            value['required_address_fields'] = required_address_fields
        if address_fields_to_replace is not None:
            point_value[
                'address_fields_to_replace'
            ] = address_fields_to_replace
        if geocoder_check_rules is not None:
            point_value['use_only_checked_results'] = True
            point_value['geocoder_check_rules'] = geocoder_check_rules

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claims_geocoder_by_point',
            consumers=['cargo-claims/geocoder-by-point'],
            clauses=[],
            default_value=point_value,
        )

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claims_geocoder',
            consumers=['cargo-claims/geocoder'],
            clauses=[],
            default_value=value,
        )
        await taxi_cargo_claims.invalidate_caches()

    await wrapper()
    return wrapper


@pytest.fixture(name='exp_cargo_claims_geocoder_old')
async def _exp_cargo_claims_geocoder_old(taxi_cargo_claims, experiments3):
    async def wrapper(value):
        point_params = {}
        point_params['rebuild_full_name'] = value.pop('rebuild_full_name')
        point_params['use_full_name_for_geocoder'] = value.pop(
            'use_full_name_for_geocoder',
        )
        point_params['address_fields_to_replace'] = value.pop(
            'address_fields_to_replace',
        )

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claims_geocoder_by_point',
            consumers=['cargo-claims/geocoder-by-point'],
            clauses=[],
            default_value=point_params,
        )

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_claims_geocoder',
            consumers=['cargo-claims/geocoder'],
            clauses=[],
            default_value=value,
        )
        await taxi_cargo_claims.invalidate_caches()

    return wrapper


def _set_geocoder_response(expected_geocoder_points, yamaps, load_json):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        assert request.args['ll'] in expected_geocoder_points
        assert (
            request.args['text']
            == expected_geocoder_points[request.args['ll']]
        )
        maps_response = load_json('yamaps_response.json')
        coordinates = [float(x) for x in request.args['ll'].split(',')]
        maps_response['geometry'] = coordinates
        return [maps_response]


@pytest.mark.parametrize(
    'expected_geocoder_points,expected_full_name,'
    'geocoder_exp, forwarded_addr',
    [
        pytest.param(
            {
                '37.500000,55.700000': 'БЦ Аврора',
                '37.600000,55.600000': 'Свободы, 30',
                '37.800000,55.400000': 'Склад',
            },
            'Россия, Москва, Садовническая улица',
            {
                'enabled': True,
                'use_full_name_for_geocoder': True,
                'rebuild_full_name': False,
                'error_mode': 'warning',
                'required_address_fields': ['shortname'],
                'address_fields_to_replace': [
                    'fullname',
                    'country',
                    'city',
                    'street',
                    'building',
                ],
            },
            None,
            id='replace_full_name',
        ),
        pytest.param(
            {
                '37.500000,55.700000': 'БЦ Аврора',
                '37.600000,55.600000': 'Свободы, 30',
                '37.800000,55.400000': 'Склад',
            },
            None,
            {
                'enabled': True,
                'use_full_name_for_geocoder': True,
                'rebuild_full_name': False,
                'error_mode': 'warning',
                'required_address_fields': ['shortname'],
                'address_fields_to_replace': [
                    'country',
                    'city',
                    'street',
                    'building',
                ],
            },
            None,
            id='no_replace_full_name',
        ),
        pytest.param(
            {
                '37.500000,55.700000': '37.500000,55.700000',
                '37.600000,55.600000': '37.600000,55.600000',
                '37.800000,55.400000': '37.800000,55.400000',
            },
            None,
            {
                'enabled': True,
                'use_full_name_for_geocoder': False,
                'rebuild_full_name': False,
                'error_mode': 'warning',
                'required_address_fields': ['shortname'],
                'address_fields_to_replace': [
                    'country',
                    'city',
                    'street',
                    'building',
                ],
            },
            None,
            id='no_full_name',
        ),
        pytest.param(
            {
                '37.500000,55.700000': '37.500000,55.700000',
                '37.600000,55.600000': '37.600000,55.600000',
                '37.800000,55.400000': '37.800000,55.400000',
            },
            None,
            {
                'enabled': True,
                'use_full_name_for_geocoder': False,
                'rebuild_full_name': False,
                'error_mode': 'warning',
                'required_address_fields': ['shortname'],
                'address_fields_to_replace': [
                    'country',
                    'city',
                    'street',
                    'building',
                ],
            },
            None,
            id='no_full_name',
        ),
        pytest.param(
            {
                '37.500000,55.700000': (
                    'Россия Москва Садовническая улица 82 подъезд 4'
                ),
                '37.600000,55.600000': 'Украина Киев Свободы 30 подъезд 2',
                '37.800000,55.400000': 'Россия Москва МКАД 50',
            },
            None,
            {
                'enabled': True,
                'use_full_name_for_geocoder': True,
                'rebuild_full_name': True,
                'error_mode': 'warning',
                'required_address_fields': ['shortname'],
                'address_fields_to_replace': [
                    'country',
                    'city',
                    'street',
                    'building',
                ],
            },
            None,
            id='rebuild_address',
        ),
        pytest.param(
            None,
            None,
            {
                'enabled': False,
                'use_full_name_for_geocoder': True,
                'rebuild_full_name': False,
                'error_mode': 'warning',
                'required_address_fields': ['shortname'],
                'address_fields_to_replace': [
                    'fullname',
                    'country',
                    'city',
                    'street',
                    'building',
                ],
            },
            [
                {
                    'fullname': 'БЦ Аврора',
                    'country': 'Россия',
                    'city': 'Москва',
                },
                {
                    'fullname': 'Свободы, 30',
                    'country': 'Украина',
                    'city': 'Киев',
                },
                {'fullname': 'Склад', 'country': 'Россия', 'city': 'Москва'},
            ],
            id='geocoder_disabled',
        ),
    ],
)
async def test_finish_estimate_geocoder(
        taxi_cargo_claims,
        state_controller,
        load_json,
        mockserver,
        yamaps,
        exp_cargo_claims_geocoder_old,
        expected_geocoder_points,
        expected_full_name,
        geocoder_exp,
        forwarded_addr,
):
    _set_geocoder_response(expected_geocoder_points, yamaps, load_json)
    await exp_cargo_claims_geocoder_old(geocoder_exp)

    claim_info = await state_controller.apply(target_status='estimating')
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        f'v1/claims/finish-estimate?claim_id={claim_id}',
        json={
            'cars': [
                {
                    'taxi_class': 'cargo',
                    'taxi_requirements': {'cargo_type': 'gaz'},
                    'items': [{'id': 1, 'quantity': 1}],
                },
                {'taxi_class': 'cargo', 'items': [{'id': 2, 'quantity': 1}]},
            ],
            'zone_id': 'moscow',
            'currency': 'RUB',
            'currency_rules': {
                'code': 'RUB',
                'sign': '₽',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
            },
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price_raw': 999,
                'price': '999.0010',
            },
        },
    )
    assert response.status_code == 200
    if expected_geocoder_points:
        assert yamaps.times_called() == len(expected_geocoder_points)
    response = await taxi_cargo_claims.get(
        'v2/claims/full', params={'claim_id': claim_id},
    )

    points = response.json().get('route_points')
    assert points
    for point in points:
        address = point.get('address', {})
        if expected_full_name:
            assert address.get('fullname') == expected_full_name

        if expected_geocoder_points:
            assert address.get('country') == 'Россия'
            assert address.get('city') == 'Москва'
            assert address.get('shortname') == 'Садовническая улица'
            assert address.get('uri') == 'ymapsbm1://geo?exit1'
            assert address.get('description') == 'Москва, Россия'
        else:
            addr = forwarded_addr[point.get('visit_order') - 1]
            assert address.get('fullname') == addr.get('fullname')
            assert address.get('country') == addr.get('country')
            assert address.get('city') == addr.get('city')


@pytest.mark.parametrize(
    'expected_geocoder_points,expected_full_name',
    [
        pytest.param(
            {
                '37.500000,55.700000': 'БЦ Аврора',
                '37.600000,55.600000': 'Свободы, 30',
                '37.800000,55.400000': 'Склад',
            },
            'Россия, Москва, Садовническая улица',
            id='replace_full_name',
        ),
    ],
)
async def test_create_v1_geocoder(
        taxi_cargo_claims,
        state_controller,
        load_json,
        mockserver,
        yamaps,
        exp_cargo_claims_geocoder_old,
        expected_geocoder_points,
        expected_full_name,
):
    _set_geocoder_response(expected_geocoder_points, yamaps, load_json)
    await exp_cargo_claims_geocoder_old(
        {
            'enabled': True,
            'use_full_name_for_geocoder': True,
            'rebuild_full_name': False,
            'error_mode': 'warning',
            'required_address_fields': ['shortname'],
            'address_fields_to_replace': [
                'fullname',
                'country',
                'city',
                'street',
                'building',
            ],
        },
    )

    claim_info = await state_controller.apply(target_status='new')
    claim_id = claim_info.claim_id

    assert yamaps.times_called() == len(expected_geocoder_points)
    response = await taxi_cargo_claims.get(
        'v2/claims/full', params={'claim_id': claim_id},
    )

    points = response.json().get('route_points')
    assert points
    for point in points:
        address = point.get('address', {})
        if expected_full_name:
            assert address.get('fullname') == expected_full_name
        assert address.get('shortname') == 'Садовническая улица'
        assert address.get('country') == 'Россия'
        assert address.get('city') == 'Москва'
        assert address.get('uri') == 'ymapsbm1://geo?exit1'
        assert address.get('description') == 'Москва, Россия'


@pytest.mark.parametrize(
    'expected_geocoder_points,expected_full_name',
    [
        pytest.param(
            {
                '37.200000,55.800000': '1',
                '37.000000,55.800000': '2',
                '37.000000,55.000000': '3',
                '37.000000,55.500000': '4',
            },
            'Россия, Москва, Садовническая улица',
            id='replace_full_name',
        ),
    ],
)
async def test_create_v2_geocoder(
        taxi_cargo_claims,
        state_controller,
        load_json,
        mockserver,
        yamaps,
        exp_cargo_claims_geocoder_old,
        expected_geocoder_points,
        expected_full_name,
):
    _set_geocoder_response(expected_geocoder_points, yamaps, load_json)
    await exp_cargo_claims_geocoder_old(
        {
            'enabled': True,
            'use_full_name_for_geocoder': True,
            'rebuild_full_name': False,
            'error_mode': 'warning',
            'required_address_fields': ['shortname'],
            'address_fields_to_replace': [
                'fullname',
                'country',
                'city',
                'street',
                'building',
            ],
        },
    )

    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='new')
    claim_id = claim_info.claim_id

    assert yamaps.times_called() == len(expected_geocoder_points)
    response = await taxi_cargo_claims.get(
        'v2/claims/full', params={'claim_id': claim_id},
    )

    points = response.json().get('route_points')
    assert points
    for point in points:
        address = point.get('address', {})
        if expected_full_name:
            assert address.get('fullname') == expected_full_name
        assert address.get('shortname') == 'Садовническая улица'
        assert address.get('country') == 'Россия'
        assert address.get('city') == 'Москва'
        assert address.get('uri') == 'ymapsbm1://geo?exit1'
        assert address.get('description') == 'Москва, Россия'


async def test_create_v2_warnings(
        taxi_cargo_claims, load_json, yamaps, exp_cargo_claims_geocoder_old,
):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        maps_response = load_json('yamaps_response.json')
        coordinates = [float(x) for x in request.args['text'].split(',')]
        maps_response['geometry'] = coordinates
        return [maps_response]

    await exp_cargo_claims_geocoder_old(
        {
            'enabled': True,
            'use_full_name_for_geocoder': True,
            'rebuild_full_name': False,
            'max_distance': 1,
            'error_mode': 'warning',
            'required_address_fields': ['shortname'],
            'address_fields_to_replace': [
                'fullname',
                'country',
                'city',
                'street',
                'building',
            ],
        },
    )

    create_request = utils_v2.get_create_request()
    for point in create_request['route_points']:
        point['address']['fullname'] = ','.join(
            map(str, point['address']['coordinates']),
        )
        point['address']['coordinates'] = [37.5, 55.1]
    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=create_request,
    )
    assert response.status_code == 200
    claim_id = response.json()['id']

    response = await taxi_cargo_claims.get(
        'v2/claims/full', params={'claim_id': claim_id},
    )

    warnings = response.json().get('warnings')
    assert warnings == [
        {
            'code': 'address_too_far',
            'message': (
                'Адрес 37.2,55.8 (55.8,37.2) слишком далеко от точки '
                '(55.1,37.5)'
            ),
            'source': 'route_points',
        },
        {
            'code': 'address_too_far',
            'message': (
                'Адрес 37.0,55.8 (55.8,37) слишком далеко от точки (55.1,37.5)'
            ),
            'source': 'route_points',
        },
        {
            'code': 'address_too_far',
            'message': (
                'Адрес 37.0,55.0 (55,37) слишком далеко от точки (55.1,37.5)'
            ),
            'source': 'route_points',
        },
        {
            'code': 'address_too_far',
            'message': (
                'Адрес 37.0,55.5 (55.5,37) слишком далеко от точки (55.1,37.5)'
            ),
            'source': 'route_points',
        },
    ]


async def test_create_v2_error(
        taxi_cargo_claims, load_json, yamaps, exp_cargo_claims_geocoder_old,
):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        maps_response = load_json('yamaps_response.json')
        coordinates = [float(x) for x in request.args['text'].split(',')]
        maps_response['geometry'] = coordinates
        return [maps_response]

    await exp_cargo_claims_geocoder_old(
        {
            'enabled': True,
            'use_full_name_for_geocoder': True,
            'rebuild_full_name': False,
            'max_distance': 1,
            'error_mode': 'error',
            'required_address_fields': ['shortname'],
            'address_fields_to_replace': [
                'fullname',
                'country',
                'city',
                'street',
                'building',
            ],
        },
    )
    create_request = utils_v2.get_create_request()
    for point in create_request['route_points']:
        point['address']['fullname'] = ','.join(
            map(str, point['address']['coordinates']),
        )
        point['address']['coordinates'] = [37.5, 55.1]
    response = await utils_v2.create_claim_v2(
        taxi_cargo_claims, request=create_request, expect_failure=True,
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'address_too_far'


@pytest.fixture(name='geocoder_state')
async def _geocoder_state(
        yamaps, load_json, exp_cargo_claims_geocoder, build_create_request,
):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        maps_response = load_json('yamaps_response.json')
        coordinates = [float(x) for x in request.args['text'].split(',')]
        maps_response['geometry'] = coordinates
        if context.house is not None:
            maps_response['geocoder']['address']['house'] = context.house
        if context.entrance is not None:
            maps_response['geocoder']['address']['entrance'] = context.entrance
            maps_response['arrival_points'] = [
                {'name': 'entrance_returned', 'point': coordinates},
            ]

        return [maps_response]

    yamaps.enable_debug_logging()

    class Context:
        def __init__(self):
            self.entrance = None
            self.house = None

        def request(self, *, lat_diff=0, lon_diff=0, entrance=None, **kwargs):
            request, _ = build_create_request(use_create_v2=True, **kwargs)

            lon, lat = 37.5, 55.1

            # Geocoder mock returns point with offset from original
            # lat_diff - latitude delta
            # lon_diff - longitude delta
            for point in request['route_points']:
                point['address']['fullname'] = ','.join(
                    map(str, [lon + lon_diff, lat + lat_diff]),
                )
                point['address']['coordinates'] = [lon, lat]
                if entrance is not None:
                    point['address']['porch'] = entrance

            return request

    context = Context()

    return context


async def test_coordinates_changed(
        geocoder_state,
        exp_cargo_claims_geocoder,
        build_create_request,
        claim_creator_v2,
):
    """
        Check coordinates changed according to geocoder response.
    """
    await exp_cargo_claims_geocoder(address_fields_to_replace=['coordinates'])
    response = await claim_creator_v2(
        request=geocoder_state.request(lon_diff=0.001),
    )
    assert response.status_code == 200

    coordinates = response.json()['route_points'][0]['address']['coordinates']
    assert coordinates == [37.501, 55.1]  # original should be [37.5, 55.1]


async def test_coordinates_not_changed(
        geocoder_state,
        exp_cargo_claims_geocoder,
        build_create_request,
        claim_creator_v2,
):
    """
        Check coordinates was not changed due to big distance from
        original coordinates.
    """
    await exp_cargo_claims_geocoder(
        address_fields_to_replace=['coordinates'],
        max_fix_coordinates_distance=100,
    )
    response = await claim_creator_v2(
        request=geocoder_state.request(lon_diff=0.01),
    )
    assert response.status_code == 200

    coordinates = response.json()['route_points'][0]['address']['coordinates']
    assert coordinates == [37.5, 55.1]  # changed should be [37.51, 55.1]


async def test_diagnostics_saved(
        taxi_cargo_claims,
        geocoder_state,
        exp_cargo_claims_geocoder,
        build_create_request,
        claim_creator_v2,
):
    """
        Check original address fields and coordinates was saved.
        And returned in internal handlers.
    """
    await exp_cargo_claims_geocoder(address_fields_to_replace=['coordinates'])
    response = await claim_creator_v2(
        request=geocoder_state.request(lon_diff=0.001),
    )
    assert response.status_code == 200
    claim = response.json()

    coordinates = response.json()['route_points'][0]['address']['coordinates']
    assert coordinates == [37.501, 55.1]  # original should be [37.5, 55.1]

    response = await taxi_cargo_claims.post(
        'v2/admin/claims/full', params={'claim_id': claim['id']},
    )
    assert response.status_code == 200

    point_diagnostics = response.json()['claim']['route_points'][0][
        'diagnostics'
    ]

    assert int(point_diagnostics['geocoder'].pop('distance_from_origin')) == 63
    assert point_diagnostics == {
        'geocoder': {
            'coordinates': [37.5, 55.1],
            'description': 'null',
            'shortname': 'null',
            'uri': 'null',
        },
    }


def _prepare_address_fields(
        address, *, building='building', sflat='flat', flat=1, porch='porch',
):
    address['country'] = 'country'
    address['city'] = 'city'
    address['street'] = 'street'

    if building is not None:
        address['building'] = building
    else:
        address.pop('building', None)

    if porch is not None:
        address['porch'] = porch
    else:
        address.pop('porch', None)

    if sflat is not None:
        address['sflat'] = sflat
    elif flat is not None:
        address['flat'] = flat
    else:
        address.pop('sflat', None)
        address.pop('flat', None)


async def test_geocoder_request_format(
        geocoder_state,
        exp_cargo_claims_geocoder,
        build_create_request,
        claim_creator_v2,
        yamaps,
        load_json,
        total_points=4,
):
    """
        Check geocoder request format.
        Geocoder text is build by address fields passed by client,
        and formatted according to CARGO_CLAIMS_GEOCODER_FORMAT_BY_LOCALE.
    """
    geocoder_request_texts = []

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        geocoder_request_texts.append(request.args['text'])
        return [load_json('yamaps_response.json')]

    await exp_cargo_claims_geocoder(
        rebuild_full_name=True, address_fields_to_replace=['coordinates'],
    )

    # Fill address fields
    request = geocoder_state.request()
    _prepare_address_fields(request['route_points'][0]['address'])
    _prepare_address_fields(request['route_points'][1]['address'], sflat=None)
    _prepare_address_fields(request['route_points'][2]['address'], porch=None)
    _prepare_address_fields(
        request['route_points'][3]['address'], building=None, porch=None,
    )

    response = await claim_creator_v2(request=request)
    assert response.status_code == 200

    assert yamaps.times_called() == total_points
    geocoder_request_texts = sorted(geocoder_request_texts)
    assert geocoder_request_texts == [
        'country,city,street,building,entrance porch,flat 1',
        'country,city,street,building,entrance porch,flat flat',
        'country,city,street,building,flat flat',
        'country,city,street,flat flat',
    ]


@pytest.mark.parametrize('numeric_flat', (True, False))
async def test_geocoder_flat_format(
        geocoder_state,
        exp_cargo_claims_geocoder,
        build_create_request,
        claim_creator_v2,
        yamaps,
        load_json,
        numeric_flat,
        total_points=4,
):
    """
        Check geocoder request format.
        Geocoder text is build by address fields passed by client,
        and formatted according to CARGO_CLAIMS_GEOCODER_FORMAT_BY_LOCALE.
    """
    geocoder_request_texts = []

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        geocoder_request_texts.append(request.args['text'])
        return [load_json('yamaps_response.json')]

    await exp_cargo_claims_geocoder(
        rebuild_full_name=True,
        address_fields_to_replace=['coordinates'],
        numeric_flat=numeric_flat,
    )

    # Fill address fields
    request = geocoder_state.request()
    _prepare_address_fields(request['route_points'][0]['address'])
    _prepare_address_fields(request['route_points'][1]['address'], sflat='A32')
    _prepare_address_fields(request['route_points'][2]['address'], sflat='32b')
    _prepare_address_fields(
        request['route_points'][3]['address'], sflat='X32b',
    )

    response = await claim_creator_v2(request=request)
    assert response.status_code == 200

    assert yamaps.times_called() == total_points
    geocoder_request_texts = sorted(geocoder_request_texts)
    expected_result = 'country,city,street,building,entrance porch,flat {}'
    assert geocoder_request_texts == sorted(
        [
            expected_result.format('' if numeric_flat else 'flat'),
            expected_result.format('32' if numeric_flat else 'A32'),
            expected_result.format('32' if numeric_flat else '32b'),
            expected_result.format('32' if numeric_flat else 'X32b'),
        ],
    )


@pytest.mark.parametrize('trust_porch_if_exist', (True, False))
async def test_geocoder_trust_porch_if_exist(
        geocoder_state,
        exp_cargo_claims_geocoder,
        build_create_request,
        claim_creator_v2,
        yamaps,
        load_json,
        trust_porch_if_exist,
        total_points=4,
):
    """
        Check geocoder request format.
        if porch exist and trust_porch_if_exist=True, geocoder request
        should not contain flat.
    """
    geocoder_request_texts = []

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        geocoder_request_texts.append(request.args['text'])
        return [load_json('yamaps_response.json')]

    await exp_cargo_claims_geocoder(
        rebuild_full_name=True,
        address_fields_to_replace=['coordinates'],
        trust_porch_if_exist=trust_porch_if_exist,
    )

    # Fill address fields
    request = geocoder_state.request()
    _prepare_address_fields(request['route_points'][0]['address'])
    _prepare_address_fields(
        request['route_points'][1]['address'], sflat=None, flat=None,
    )
    _prepare_address_fields(request['route_points'][2]['address'], porch=None)
    _prepare_address_fields(
        request['route_points'][3]['address'],
        porch=None,
        sflat=None,
        flat=None,
    )

    response = await claim_creator_v2(request=request)
    assert response.status_code == 200

    assert yamaps.times_called() == total_points
    geocoder_request_texts = sorted(geocoder_request_texts)
    expected_result = 'country,city,street,building{}{}'
    assert geocoder_request_texts == sorted(
        [
            expected_result.format(',entrance porch', '')
            if trust_porch_if_exist
            else expected_result.format(',entrance porch', ',flat flat'),
            expected_result.format(',entrance porch', ''),
            expected_result.format('', ',flat flat'),
            expected_result.format('', ''),
        ],
    )


async def test_coordinates_changed_with_porch(
        geocoder_state,
        exp_cargo_claims_geocoder,
        build_create_request,
        claim_creator_v2,
        entrance='entrance',
):
    """
        Check coordinates was changed due to geocoder
        returned same entrance.
    """
    geocoder_state.entrance = entrance

    await exp_cargo_claims_geocoder(
        address_fields_to_replace=['coordinates'],
        geocoder_check_rules=[{'field': 'porch', 'condition': 'exists'}],
    )
    response = await claim_creator_v2(
        request=geocoder_state.request(entrance=entrance, lon_diff=0.01),
    )
    assert response.status_code == 200

    coordinates = response.json()['route_points'][0]['address']['coordinates']
    assert coordinates == [37.51, 55.1]  # not changed should be [37.5, 55.1]


async def test_coordinates_not_changed_no_porch(
        geocoder_state,
        exp_cargo_claims_geocoder,
        build_create_request,
        claim_creator_v2,
):
    """
        Check coordinates was not changed due to geocoder
        did not return entrance.
    """
    await exp_cargo_claims_geocoder(
        address_fields_to_replace=['coordinates'],
        geocoder_check_rules=[{'field': 'porch', 'condition': 'exists'}],
    )
    response = await claim_creator_v2(
        request=geocoder_state.request(lon_diff=0.01),
    )
    assert response.status_code == 200

    coordinates = response.json()['route_points'][0]['address']['coordinates']
    assert coordinates == [37.5, 55.1]  # changed should be [37.51, 55.1]


async def test_coordinates_not_changed_due_building(
        geocoder_state,
        exp_cargo_claims_geocoder,
        build_create_request,
        claim_creator_v2,
):
    """
        Check coordinates was not changed due to geocoder
        returned different building by address.
    """
    geocoder_state.house = 'another_house'

    await exp_cargo_claims_geocoder(
        address_fields_to_replace=['coordinates'],
        geocoder_check_rules=[{'field': 'building', 'condition': 'equals'}],
    )
    response = await claim_creator_v2(
        request=geocoder_state.request(lon_diff=0.01),
    )
    assert response.status_code == 200

    coordinates = response.json()['route_points'][0]['address']['coordinates']
    assert coordinates == [37.5, 55.1]  # changed should be [37.51, 55.1]
