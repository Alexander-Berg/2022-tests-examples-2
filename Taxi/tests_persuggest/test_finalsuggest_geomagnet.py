import pytest

from tests_persuggest import persuggest_common

URL = '/4.0/persuggest/v1/finalsuggest'

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': '12345678901234567890123456789012',
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Request-Application': 'app_name=iphone',
    'X-Request-Language': 'ru',
    'X-Remote-IP': '10.10.10.10',
}

# pylint: disable=redefined-outer-name
@pytest.fixture()
async def geomagnet_common(mockserver, load_json, yamaps, taxi_persuggest):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return {}

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        geosearch_map = {
            '37.642648,55.735067': 'geosearch_geomagnet1.json',
            '37.642572,55.734760': 'geosearch_geomagnet2.json',
            'Россия;Москва;Садовническая улица;82с2': (
                'geosearch_geomagnet3.json'
            ),
        }
        return [load_json(geosearch_map[request.args['text']])]

    class _common:
        async def perform_request(self, entrance, position):
            request = {
                'action': 'geomagnet',
                'entrance': entrance,
                'position': position,
                'prev_log': '',
                'state': {
                    'accuracy': 20,
                    'bbox': [30, 50, 40, 60],
                    'fields': [],
                    'location': [0, 0],
                },
                'type': 'b',
            }
            response = await taxi_persuggest.post(
                URL, request, headers=AUTHORIZED_HEADERS,
            )
            return response

    yield _common()
    await taxi_persuggest.invalidate_caches()


@pytest.mark.parametrize(
    'position,entrance,expected',
    [
        # Good entrance:
        ([37.642648, 55.735067], '4', 'geomagnet_expected1.json'),
        # Non-existent entrance:
        ([37.642648, 55.735067], '3', 'geomagnet_expected2.json'),
        # Explicit request to reset the entrance
        ([37.642572, 55.734760], '', 'geomagnet_expected2.json'),
    ],
)
async def test_finalsuggest_geomagnet(
        load_json, position, entrance, expected, geomagnet_common,
):
    response = await geomagnet_common.perform_request(entrance, position)
    expected_ans = load_json(expected)
    if entrance == '':
        del expected_ans['results'][0]['entrance']
    assert response.status_code == 200
    assert persuggest_common.logparse(
        response.json(),
    ) == persuggest_common.logparse(expected_ans)


@pytest.mark.config(MAX_ENTRANCE_LENGTH=6)
@pytest.mark.parametrize('entrance,code', [('9' * 7, 400), ('9' * 6, 200)])
async def test_finalsuggest_geomagnet_long_entrance(
        entrance, code, geomagnet_common,
):
    response = await geomagnet_common.perform_request(
        entrance, [37.642648, 55.735067],
    )
    assert response.status_code == code


@pytest.mark.parametrize(
    'has_exp,expected',
    [(True, 'geomagnet_expected2.json'), (False, 'geomagnet_expected3.json')],
)
@pytest.mark.translations(
    client_messages={
        'entrance_template_full': {
            'ru': '%(address)s, подъезд %(entrance)s full',
        },
        'entrance_template_short': {
            'ru': '%(address)s, подъезд %(entrance)s short',
        },
    },
)
async def test_finalsuggest_geomagnet_append(
        load_json, geomagnet_common, experiments3, has_exp, expected,
):
    experiments3.add_experiment(
        name='dont_append_entrance',
        consumers=['persuggest/finalsuggest'],
        match={'enabled': has_exp, 'predicate': {'type': 'true'}},
        clauses=[],
        default_value={},
    )
    response = await geomagnet_common.perform_request(
        '3', [37.642648, 55.735067],
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected)
