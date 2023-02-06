import pytest

YAMAPS_ORGS = [
    {
        'll': '37.000000,55.000000',
        'business': {
            'address': {
                'formatted_address': 'Russia, Moscow',
                'country': 'Russia',
                'locality': 'Moscow',
                'street': 'Mendeleevskaya street',
                'house': '11',
            },
            'name': 'One-door community',
            'class': 'restaurant',
            'id': '1',
        },
        'uri': 'ymapsbm1://URI_0_0',
        'name': 'One-door community',
        'description': 'Russia, Moscow',
        'geometry': [37.0, 55.0],
    },
    {
        'll': '38.000000,56.000000',
        'business': {
            'address': {
                'formatted_address': 'Russia, Moscow',
                'country': 'Russia',
                'locality': 'Moscow',
                'street': 'Sherementievskoe highway',
                'house': '83',
            },
            'class': 'airports',
            'name': 'Sherementievo',
            'id': '1',
        },
        'uri': 'ymapsbm1://URI_1_1',
        'name': 'Sherementievo',
        'description': 'Russia, Moscow',
        'geometry': [38.0, 56.0],
    },
]

YAMAPS_ADDRS = [
    {
        'll': '37.000000,55.000000',
        'geocoder': {
            'address': {
                'formatted_address': (
                    'Russia, Moscow, 2nd Krasnogvardeysky Drive, 10'
                ),
                'country': 'Russia',
                'locality': 'Moscow',
                'street': '2nd Krasnogvardeysky Drive',
                'house': '10',
            },
            'id': '',
        },
        'uri': 'ymapsbm1://URI_3_3',
        'name': '2nd Krasnogvardeysky Drive, 10',
        'description': 'Russia, Moscow',
        'geometry': [37.0, 55.0],
    },
    {
        'll': '38.000000,56.000000',
        'geocoder': {
            'address': {
                'formatted_address': (
                    'Russia, Moscow, 2nd Krasnogvardeysky Drive, 10'
                ),
                'country': 'Russia',
                'locality': 'Moscow',
                'street': '2nd Krasnogvardeysky Drive',
                'house': '10',
            },
            'id': '',
        },
        'uri': 'ymapsbm1://URI_3_3',
        'name': '2nd Krasnogvardeysky Drive, 10',
        'description': 'Russia, Moscow',
        'geometry': [38.0, 56.0],
    },
]


@pytest.fixture(autouse=True)
def yamaps_wrapper(yamaps):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        lookup = None
        if 'mode' in request.args and request.args['mode'] == 'uri':
            lookup = YAMAPS_ADDRS
        if 'type' in request.args:
            if request.args['type'] == 'geo':
                lookup = YAMAPS_ADDRS
            if request.args['type'] == 'biz':
                lookup = YAMAPS_ORGS
        assert lookup, 'Bad request'
        for addr in lookup:
            if 'uri' in request.args and addr['uri'] == request.args['uri']:
                return [addr]
            if 'll' in request.args and addr['ll'] == request.args['ll']:
                return [addr]
        return []


async def test_uri_request(taxi_persuggest, load_json):

    headers = {'Accept-Language': 'en'}
    request = {'uri': 'ymapsbm1://URI_3_3'}

    response = await taxi_persuggest.post(
        '/3.0/geosearch', request, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_uri.json')


async def test_point_request(taxi_persuggest, yamaps, load_json):

    headers = {'Accept-Language': 'en'}
    request = {'what': [37.000000, 55.00000]}

    response = await taxi_persuggest.post(
        '/3.0/geosearch', request, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')
    assert yamaps.times_called() == 2


async def test_point_and_text_request(taxi_persuggest, yamaps, load_json):

    headers = {'Accept-Language': 'en'}
    request = {'ll': [37.000000, 55.00000], 'what': 'anything'}

    response = await taxi_persuggest.post(
        '/3.0/geosearch', request, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')
    assert yamaps.times_called() == 2


async def test_bbox_and_text_request(taxi_persuggest, yamaps, load_json):

    headers = {'Accept-Language': 'en'}
    request = {
        'tl': [20.000000, 77.000000],
        'br': [56.000000, 35.000000],
        'what': 'anything',
    }

    response = await taxi_persuggest.post(
        '/3.0/geosearch', request, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_bbox.json')
    assert yamaps.times_called() == 2


@pytest.mark.parametrize(
    ['accept_lang', 'expected_lang'],
    [
        ('en-IL;q=0.9, ru-RU;q=0.1', 'en_IL'),
        ('en;q=1, en-IL;q=0.9', 'en'),
        ('en-undefined', 'en'),
        ('en-IL', 'en_IL'),
        (None, 'en'),
        ('', 'en'),
    ],
)
async def test_locale_and_country(
        taxi_persuggest, yamaps, load_json, accept_lang, expected_lang,
):

    yamaps.set_checks({'lang': expected_lang})

    headers = {'Accept-Language': accept_lang, 'X-Request-Language': 'en'}

    request = {'ll': [37.000000, 55.00000], 'what': 'anything'}

    response = await taxi_persuggest.post(
        '/3.0/geosearch', request, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')
    assert yamaps.times_called() == 2
