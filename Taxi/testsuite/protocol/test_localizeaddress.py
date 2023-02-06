import json
import time

import pytest


def test_bad_request(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/localizeaddress',
        {'locale': 'ru', 'addresses': [{'text': 'my street 123'}]},
    )
    assert response.status_code == 400


def test_main(mockserver, load_json, taxi_protocol):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return load_json('main_yamaps_response.json')

    response = taxi_protocol.post(
        '3.0/localizeaddress',
        {
            'locale': 'en',
            'addresses': [
                {
                    'point': [37.642462, 55.734939],
                    'text': 'Россия, Москва, Садовническая улица, 82с2',
                },
            ],
        },
    )
    assert response.status_code == 200
    address = response.json()['addresses'][0]
    assert address['country'] == 'Russian Federation'
    assert address['description'] == 'Moscow, Russian Federation'
    assert (
        address['fullname']
        == 'Russian Federation, Moscow, Sadovnicheskaya Street, 82с2'
    )
    assert address['geopoint'] == [37.642462, 55.734939]
    assert address['locality'] == 'Moscow'
    assert address['object_type'] == 'другое'
    assert address['premisenumber'] == '82с2'
    assert address['short_text'] == 'Sadovnicheskaya Street, 82с2'
    assert address['thoroughfare'] == 'Sadovnicheskaya Street'
    assert address['type'] == 'address'
    assert len(address['uris']) == 1


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'protocol', 'dst': 'yamaps'}],
    TVM_SERVICES={'yamaps': 1337},
)
def test_yamaps_client_tvm(mockserver, load_json, taxi_protocol, tvm2_client):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        assert 'X-Ya-Service-Ticket' in request.headers
        assert request.headers['X-Ya-Service-Ticket'] == 'ticket'

        return load_json('main_yamaps_response.json')

    tvm2_client.set_ticket(json.dumps({'1337': {'ticket': 'ticket'}}))

    taxi_protocol.post(
        '3.0/localizeaddress',
        {
            'locale': 'en',
            'addresses': [
                {
                    'point': [37.642462, 55.734939],
                    'text': 'Россия, Москва, Садовническая улица, 82с2',
                },
            ],
        },
    )

    # not checking response, asserting for tvm-signed request in mockserver


@pytest.mark.parametrize(
    'zones_localize_response, expected_ans',
    [
        (
            'zones_localize_choices.json',
            'zones_localize_without_zone_name.json',
        ),
        (
            'zones_localize_choices_names.json',
            'zones_localize_choices_names_ans.json',
        ),
        (
            'zones_localize_one_choice_names.json',
            'zones_localize_one_choice_names_ans.json',
        ),
    ],
)
def test_localizeaddress_zones_choices(
        mockserver,
        load_json,
        taxi_protocol,
        zones_localize_response,
        expected_ans,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def zones_localize(request):
        return load_json(zones_localize_response)

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def batch_zones_filter(request):
        return {'results': [{'in_zone': True}]}

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return load_json('main_yamaps_response.json')

    response = taxi_protocol.post(
        '3.0/localizeaddress',
        {
            'locale': 'en',
            'orderid': '34b65957906674ef83837992a0fbd95d',
            'addresses': [
                {
                    'point': [37, 55],
                    'text': 'Россия, Москва, Садовническая улица, 82с2',
                    'uri': 'ytpp://luzhki/exit_1',
                },
            ],
        },
    )
    assert response.status_code == 200
    address = response.json()['addresses'][0]
    assert address == load_json(expected_ans)


def test_localizeaddress_airport(mockserver, load_json, taxi_protocol):
    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def zones_localize(request):
        return {'results': [{}]}

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return load_json('main_yamaps_response.json')

    response = taxi_protocol.post(
        '3.0/localizeaddress',
        {
            'locale': 'en',
            'addresses': [
                {
                    'point': [37, 55],
                    'text': 'Россия, Москва, Садовническая улица, 82с2',
                    'uri': 'ytpp://luzhki/exit_1',
                },
            ],
        },
    )
    assert response.status_code == 200
    address = response.json()['addresses'][0]
    assert address == load_json('zones_airport_ans.json')


# Test parallel translation.
# First task for yamaps is failed fast
# Second task is sleeping for 500ms and is successful
# Exception must produce no cores while second task is processing
@pytest.mark.user_experiments('some_unused_experiment')
def test_anticore(mockserver, load_json, taxi_protocol):
    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        if request.args.to_dict()['text'] == 'A':
            return mockserver.make_response(status=400)
        else:
            time.sleep(0.5)
            return load_json('main_yamaps_response.json')

    response = taxi_protocol.post(
        '3.0/localizeaddress',
        {
            'locale': 'en',
            'addresses': [
                {'point': [37, 55], 'text': 'A'},
                {'point': [37, 55], 'text': 'B'},
            ],
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'error': {'text': 'couldn\'t localize RoutePoint'},
    }


def test_title_for_org(mockserver, load_json, taxi_protocol):
    is_checked_as_org = False
    is_checked_as_addr = False
    lang = 'en'

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        assert request.args.get('lang') == lang
        if request.args.get('business_oid') is not None:
            nonlocal is_checked_as_org
            is_checked_as_org = True
            return load_json('org_yamaps_response.json')

        nonlocal is_checked_as_addr
        is_checked_as_addr = True
        return load_json('main_yamaps_response.json')

    response = taxi_protocol.post(
        '3.0/localizeaddress',
        {
            'locale': lang,
            'addresses': [
                {
                    'point': [37.588144, 55.733842],
                    'text': 'Россия, Москва, Садовническая улица, 82с2',
                    'oid': '12345',
                    'type': 'organization',
                },
            ],
        },
    )
    assert response.status_code == 200

    assert is_checked_as_org
    assert is_checked_as_addr

    address = response.json()['addresses'][0]
    assert address['title'] == 'Яндекс'
    assert address['short_text'] == 'ул. Льва Толстого, 16'
    assert address['type'] == 'organization'


def test_address_fallback_to_point_geocoding(
        mockserver, load_json, taxi_protocol,
):
    is_checked_with_rspn = False
    is_checked_with_point = False

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        if request.args.get('rspn') is not None:
            nonlocal is_checked_with_rspn
            is_checked_with_rspn = True
            return {'features': None}

        nonlocal is_checked_with_point
        is_checked_with_point = True
        assert request.args.get('experimental_geocoder_revmode') == 'taxi2'
        return load_json('main_yamaps_response.json')

    response = taxi_protocol.post(
        '3.0/localizeaddress',
        {
            'locale': 'en',
            'addresses': [
                {
                    'point': [37.642462, 55.734939],
                    'text': 'Россия, Москва, Садовническая улица, 82с2',
                    'type': 'address',
                },
            ],
        },
    )
    assert response.status_code == 200

    assert is_checked_with_rspn
    assert is_checked_with_point


@pytest.mark.parametrize(
    'uri, geopoint, short_text',
    [
        (
            None,
            [37.579186724853514, 55.71644381713112],
            'good_zone, good_point',
        ),
        (None, [37.642462, 55.734939], 'Sadovnicheskaya Street, 82с2'),
    ],
)
def test_intersected_zones(
        taxi_protocol, mockserver, load_json, uri, geopoint, short_text,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        izones = load_json('intersected_zones.json')
        request_json = json.loads(request.get_data())
        excluded_zones = []
        if ('filter' in request_json) and (
                'excluded_zone_types' in request_json['filter']
        ):
            excluded_zones = request_json['filter']['excluded_zone_types']
        # Check excluded_zone_types filter
        # Filter out all bad zones
        zones = []
        update_pin_zone_id = False
        for zone in izones['zones']:
            if zone['type'] not in excluded_zones:
                zones.append(zone)
            elif zone['id'] == izones['pin_zone_id']:
                update_pin_zone_id = True
        # If we removed pinned zone
        # make stupid logic with first zone and point
        if update_pin_zone_id and zones:
            izones['pin_zone_id'] = zones[0]['id']
            izones['pin_point_id'] = zones[0]['points'][0]['id']
        izones['zones'] = zones
        return izones

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        if request.args.get('business_oid') is not None:
            return load_json('org_yamaps_response.json')
        return load_json('main_yamaps_response.json')

    address = {'point': geopoint}
    if uri is not None:
        address['uri'] = uri
    response = taxi_protocol.post(
        '3.0/localizeaddress', {'locale': 'en', 'addresses': [address]},
    )

    assert response.status_code == 200
    address = response.json()['addresses'][0]
    # Anyway we should get this name
    # Cause we have pinned sdc zone
    # And uri of other zone
    assert address['short_text'] == short_text
    if uri is not None:
        assert address['uris'][0] == uri


def test_distance_fallback(taxi_protocol, mockserver, load_json):
    is_checked_with_rspn = False
    is_checked_with_point = False

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def zones(request):
        return {}

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        if request.args.get('rspn') is not None:
            nonlocal is_checked_with_rspn
            is_checked_with_rspn = True
            return load_json('main_yamaps_response.json')

        nonlocal is_checked_with_point
        is_checked_with_point = True
        return load_json('org_yamaps_response.json')

    response = taxi_protocol.post(
        '3.0/localizeaddress',
        {
            'locale': 'en',
            'addresses': [
                {
                    'point': [37.642462, 55.734939],
                    'text': 'Россия, Москва, Садовническая улица, 82с2',
                    'type': 'address',
                    'uri': 'ymapsbm1://org?oid=1124715036',
                },
            ],
        },
    )
    assert response.status_code == 200

    assert is_checked_with_rspn
    assert is_checked_with_point


@pytest.mark.parametrize(
    'uri, localize_called, zones_called',
    [
        ('ytpp://luzhki/exit_1', True, False),
        ('ymapsbm1://org?oid=1124715036', False, True),
    ],
)
def test_short_full_text_failure(
        mockserver,
        load_json,
        taxi_protocol,
        uri,
        localize_called,
        zones_called,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def mock_zones_localize(request):
        return {'results': [{}]}

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def batch_zones_filter(request):
        return {'results': [{'in_zone': True}]}

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_zones(request):
        return load_json('zones_airport.json')

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return load_json('main_yamaps_response.json')

    response = taxi_protocol.post(
        '3.0/localizeaddress',
        {
            'locale': 'en',
            'addresses': [
                {
                    'point': [37.56, 55.71],
                    'text': 'Россия, Москва, Садовническая улица, 82с2',
                    'uri': uri,
                },
            ],
        },
    )
    assert mock_zones.has_calls == zones_called
    assert mock_zones_localize.has_calls == localize_called
    assert response.status_code == 200
    address = response.json()['addresses'][0]
    assert 'short_text' in address
    assert address['short_text']
    assert 'fullname' in address
    assert address['fullname']
