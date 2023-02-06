import copy
import json

import pytest

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.geoareas(filename='geoareas_moscow.json'),
    pytest.mark.tariffs(filename='tariffs_moscow.json'),
]

URL = '4.0/persuggest/v2/shortcuts'

USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
    'X-AppMetrica-DeviceId': 'DeviceId',
}

BASIC_REQUEST = {
    'state': {
        'accuracy': 20,
        'bbox': [30, 50, 40, 60],
        'fields': [
            {'type': 'a', 'position': [10.1234, 11.1234], 'log': '{}'},
            {'type': 'b', 'position': [12.1234, 13.1234], 'log': '{}'},
        ],
        'location': [37.1, 55.1],
        'coord_providers': [
            {'type': 'gps', 'position': [14.1234, 15.1234], 'accuracy': 10.3},
            {
                'type': 'platform_lbs',
                'position': [16.1, 17.1],
                'accuracy': 4.2,
            },
        ],
    },
    'position': [37.1, 55.2],
    'type': 'b',
    'shortcuts': {
        'supported_actions': [
            {'type': 'taxi:summary-redirect', 'destination_support': False},
            {'type': 'deeplink'},
            {'type': 'sdc:route-selection'},
        ],
        'supported_features': [{'type': 'drive:fixpoint-offers'}],
    },
}

YAMAPS_ADDRESS = [
    {
        'business': {
            'address': {
                'formatted_address': 'Russia, Moscow',
                'country': 'Russia',
                'locality': 'Moscow',
            },
            'name': 'One-door community',
            'closed': 'UNKNOWN',
            'class': 'restaurant',
            'id': '1088700971',
        },
        'uri': 'ymapsbm1://URI_0_0',
        'name': 'One-door community',
        'description': 'Moscow, Russia',
        'geometry': [37.0, 55.0],
    },
    {
        'business': {
            'address': {
                'formatted_address': 'Russia, Moscow',
                'country': 'Russia',
                'locality': 'Moscow',
            },
            'name': 'Murakame',
            'closed': 'TEMPORARY',
            'id': '1088700971',
            'class': 'restaurant',
        },
        'uri': 'ymapsbm1://URI_1_1',
        'name': 'Murakame',
        'description': 'Moscow, Russia',
        'geometry': [37.01, 55.01],
    },
    {
        'll': '37.300000,55.300000',
        'geocoder': {
            'address': {
                'formatted_address': (
                    'Russia, Moscow, 2nd Krasnogvardeysky Drive, 10'
                ),
                'country': 'Russia',
                'locality': 'Moscow',
            },
            'id': '1',
        },
        'uri': 'ymapsbm1://URI_3_3',
        'name': '2nd Krasnogvardeysky Drive, 10',
        'description': 'Russia, Moscow',
        'geometry': [37.3, 55.3],
    },
    {
        'll': '37.700000,55.700000',
        'geometry': [37.7, 55.7],
        'description': 'Russia, Moscow',
        'uri': 'ymapsbm1://URI_7_7',
        'name': 'Tverskaya Zastava Square, 7',
        'geocoder': {
            'address': {
                'formatted_address': (
                    'Russia, Moscow, Tverskaya Zastava Square, 7'
                ),
                'country': 'Russia',
                'locality': 'Moscow',
            },
            'id': '1',
        },
    },
]


def validate(data, response):
    assert 'shortcuts' in data
    assert data['shortcuts']
    for idx, shortcut in enumerate(data['shortcuts']):
        assert 'id' in shortcut
        assert shortcut['id']
        data['shortcuts'][idx]['id'] = ''
    for idx, shortcut in enumerate(response['shortcuts']):
        if 'scenario_params' not in shortcut:
            continue
        sp = shortcut['scenario_params']
        if 'taxi_expected_destination_params' not in sp:
            continue
        tep = sp['taxi_expected_destination_params']
        tep2 = data['shortcuts'][idx]['scenario_params'][
            'taxi_expected_destination_params'
        ]
        assert ('log' in tep) == ('log' in tep2)
        if 'log' in tep:
            if not isinstance(tep['log'], dict) and tep['log'].startswith('{'):
                tep['log'] = json.loads(tep['log'])
            if not isinstance(tep2['log'], dict) and tep2['log'].startswith(
                    '{',
            ):
                tep2['log'] = json.loads(tep2['log'])
            if isinstance(tep['log'], dict) and 'tags' in tep['log']:
                tep['log']['tags'].sort()
            if isinstance(tep2['log'], dict) and 'tags' in tep2['log']:
                tep2['log']['tags'].sort()
    assert data == response


def validate_v2(data, response):
    assert 'scenario_tops' in data
    for scenario in data['scenario_tops']:
        assert scenario['shortcuts']
        for idx, shortcut in enumerate(scenario['shortcuts']):
            assert 'id' in shortcut
            assert shortcut['id']
            scenario['shortcuts'][idx]['id'] = ''
    assert data == response


@pytest.fixture(autouse=True)
def yamaps_wrapper(yamaps):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        for addr in YAMAPS_ADDRESS:
            if 'uri' in request.args and addr['uri'] == request.args['uri']:
                return [addr]
        return []


@pytest.mark.parametrize(
    'yandex_uid,num_of_answers', [('4003514353', None), ('4003514354', 1)],
)
@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'restaurant_type': {'shortcut': 'shortcuts_restaurant_tag'},
        'work_userplace_type': {'shortcut': 'shortcuts_work_userplace_tag'},
        'default_type': {'shortcut': 'shortcuts_default_tag'},
    },
    ORG_RUBRIC_TO_IMAGE_TYPE={'restaurant': 'restaurant_type'},
)
@pytest.mark.translations(
    client_messages={
        'go_to_work': {'ru': 'На работу'},
        'go_home': {'ru': 'Домой'},
    },
)
@pytest.mark.experiments3(filename='exp3_filter_closed_orgs.json')
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
@pytest.mark.experiments3(filename='exp3_max_size_shortcuts.json')
@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_4_0_shortcuts_ml_zerosuggest(
        taxi_persuggest, mockserver, load_json, yandex_uid, num_of_answers,
):
    headers = copy.deepcopy(PA_HEADERS)
    headers['X-Yandex-UID'] = yandex_uid

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        for header, value in headers.items():
            assert request.headers[header] == value
        expected_ml_request = load_json('uml_zerosuggest_request.json')
        assert json.loads(request.get_data()) == expected_ml_request
        return load_json('uml_zerosuggest_response.json')

    response = await taxi_persuggest.post(URL, BASIC_REQUEST, headers=headers)
    assert response.status_code == 200
    response_shortcuts = response.json()['scenario_tops'][0]
    expected_shortcuts = load_json('expected_response_ml_shortcuts.json')
    if num_of_answers:
        shortcuts = expected_shortcuts['shortcuts']
        expected_shortcuts['shortcuts'] = shortcuts[:num_of_answers]
    validate(response_shortcuts, expected_shortcuts)


@pytest.mark.translations(
    client_messages={
        'drive_shortcut_work_title': {'ru': 'На работу на Драйве'},
        'work': {'ru': 'Работа'},
        'drive_shortcut_subtitle': {'ru': 'идти %(walking_duration)s'},
        'drive_shortcut_noreg_subtitle': {
            'ru': 'идти незарегу %(walking_duration)s',
        },
    },
)
@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'work_userplace_type': {'shortcut': 'shortcuts_work_userplace_tag'},
    },
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'uberx', 'drive'],
    },
)
@pytest.mark.parametrize(
    'uuid,yandex_drive_resp,zerosuggest_resp,known_orders,is_empty',
    [
        (
            'UUID',
            'response_yandex_drive.json',
            'response_zerosuggest.json',
            [],
            False,
        ),
        (
            'UUID',
            'response_yandex_drive.json',
            'response_zerosuggest.json',
            ['drive:1234:1231'],
            True,
        ),
        (
            'UUID_noreg',
            'response_yandex_drive_not_registered.json',
            'response_zerosuggest.json',
            [],
            False,
        ),
        (
            'NO_EXP',
            'response_yandex_drive.json',
            'response_zerosuggest.json',
            [],
            True,
        ),
        (
            'UUID',
            'response_yandex_drive_too_far.json',
            'response_zerosuggest.json',
            [],
            True,
        ),
        (
            'UUID',
            'response_yandex_drive_too_far_walk.json',
            'response_zerosuggest.json',
            [],
            True,
        ),
        ('UUID', None, 'response_zerosuggest.json', [], True),
        ('UUID', 'response_yandex_drive.json', None, [], True),
        pytest.param(
            'UUID',
            'response_yandex_drive.json',
            'response_zerosuggest_no_userplace.json',
            [],
            True,
            marks=[pytest.mark.config(DRIVE_ONLY_HOME_WORK=True)],
        ),
        pytest.param(
            'UUID_redirect',
            'response_yandex_drive.json',
            'response_zerosuggest.json',
            [],
            False,
        ),
    ],
)
@pytest.mark.now('2020-01-24T10:00:00+0300')
@pytest.mark.experiments3(filename='exp3_add_drive_cars.json')
@pytest.mark.experiments3(filename='exp3_drive_shortcut_exps.json')
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
async def test_4_0_shortcuts_with_drive(
        taxi_persuggest,
        mockserver,
        load_json,
        uuid,
        yandex_drive_resp,
        zerosuggest_resp,
        known_orders,
        is_empty,
):
    headers = copy.deepcopy(PA_HEADERS)
    headers['X-AppMetrica-UUID'] = uuid

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        for header, value in headers.items():
            assert request.headers[header] == value
        expected_ml_request = load_json('uml_zerosuggest_request.json')
        assert json.loads(request.get_data()) == expected_ml_request
        if not zerosuggest_resp:
            return mockserver.make_response('fail', status=500)
        return load_json(zerosuggest_resp)

    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _mock_yandex_drive(request):
        # check first address is not home nor work
        assert zerosuggest_resp != 'response_zerosuggest_no_userplace.json'

        assert 'IC-Taxi-App-Build' not in request.headers
        assert request.headers['AC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.headers['UUID'] == uuid
        assert request.headers['DeviceId'] == 'DeviceId'
        assert request.args == {
            'src': '37.1 55.2',
            'dst': '10.1 20.2',
            'lang': 'ru',
            'offer_count_limit': '1',
            'fast': 'true',
        }
        if not yandex_drive_resp:
            return mockserver.make_response('fail', status=500)
        return mockserver.make_response(
            json=load_json(yandex_drive_resp), headers={'X-Req-Id': '123'},
        )

    request = copy.deepcopy(BASIC_REQUEST)
    request['state']['known_orders'] = known_orders
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    if is_empty:
        data = response.json()
        if data['scenario_tops']:
            data['scenario_tops'].pop(0)
        validate_v2(data, {'scenario_tops': []})
    else:
        validate_v2(
            response.json(), load_json('expected_response_with_drive.json'),
        )


@pytest.mark.translations(
    client_messages={
        'drive_shortcut_work_title': {'ru': 'На работу на Драйве'},
        'work': {'ru': 'Работа'},
        'drive_shortcut_subtitle': {'ru': 'идти %(walking_duration)s'},
    },
)
@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'work_userplace_type': {'shortcut': 'shortcuts_work_userplace_tag'},
    },
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'uberx', 'drive'],
    },
)
@pytest.mark.now('2020-01-24T10:00:00+0300')
@pytest.mark.experiments3(filename='exp3_add_drive_cars.json')
@pytest.mark.experiments3(filename='exp3_drive_shortcut_exps.json')
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
async def test_4_0_shortcuts_with_drive_redirect_supported(
        taxi_persuggest, mockserver, load_json,
):
    headers = copy.deepcopy(PA_HEADERS)
    headers['X-AppMetrica-UUID'] = 'UUID_redirect'

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('response_zerosuggest.json')

    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _mock_yandex_drive(request):
        assert 'IC-Taxi-App-Build' not in request.headers
        assert request.headers['AC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        return mockserver.make_response(
            json=load_json('response_yandex_drive.json'),
            headers={'X-Req-Id': '123'},
        )

    request = copy.deepcopy(BASIC_REQUEST)
    request['shortcuts']['supported_actions'][0]['destination_support'] = True
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    validate_v2(
        response.json(),
        load_json('expected_response_with_redirect_drive.json'),
    )


@pytest.mark.translations(
    client_messages={
        'drive_shortcut_work_title': {'ru': 'На работу на Драйве'},
        'work': {'ru': 'Работа'},
        'drive_shortcut_subtitle': {'ru': 'идти %(walking_duration)s'},
        'price_with_currency': {'ru': '%(currency)s%(price)s'},
    },
)
@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'work_userplace_type': {'shortcut': 'shortcuts_work_userplace_tag'},
    },
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'uberx', 'drive'],
    },
)
@pytest.mark.now('2020-01-24T10:00:00+0300')
@pytest.mark.experiments3(filename='exp3_add_drive_cars.json')
@pytest.mark.experiments3(filename='exp3_drive_shortcut_exps.json')
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
async def test_4_0_shortcuts_with_drive_price(
        taxi_persuggest, mockserver, load_json,
):
    headers = copy.deepcopy(PA_HEADERS)
    headers['X-AppMetrica-UUID'] = 'UUID_show_price'

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('response_zerosuggest.json')

    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _mock_yandex_drive(request):
        assert 'IC-Taxi-App-Build' not in request.headers
        assert request.headers['AC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        return mockserver.make_response(
            json=load_json('response_yandex_drive.json'),
            headers={'X-Req-Id': '123'},
        )

    request = copy.deepcopy(BASIC_REQUEST)
    request['shortcuts']['supported_actions'][0]['destination_support'] = True
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    validate_v2(
        response.json(), load_json('expected_response_with_shown_price.json'),
    )


@pytest.mark.translations(
    client_messages={
        'work': {'ru': 'Работа'},
        'drive_shortcut_subtitle': {'ru': 'идти %(walking_duration)s'},
        'shortcuts.route_eta.round.hours_minutes': {
            'ru': '%(hours).0f ч %(minutes).0f мин',
        },
        'shortcuts.route_eta.round.hours': {'ru': '%(value).0f ч'},
        'shortcuts.route_eta.round.tens_minutes': {'ru': '%(value).0f мин'},
    },
)
@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'work_userplace_type': {'shortcut': 'shortcuts_work_userplace_tag'},
    },
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'uberx', 'drive'],
    },
)
@pytest.mark.now('2020-01-24T10:00:00+0300')
@pytest.mark.experiments3(filename='exp3_add_drive_cars.json')
@pytest.mark.experiments3(filename='exp3_drive_shortcut_exps.json')
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
async def test_4_0_shortcuts_with_drive_not_userplace(
        taxi_persuggest, mockserver, load_json,
):
    headers = copy.deepcopy(PA_HEADERS)
    headers['X-AppMetrica-UUID'] = 'UUID_NOT_USERPLACE'

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('response_zerosuggest_no_userplace.json')

    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _mock_yandex_drive(request):
        assert 'IC-Taxi-App-Build' not in request.headers
        assert request.headers['AC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        assert request.args == {
            'src': '37.1 55.2',
            'dst': '37.1234 55.4321',
            'lang': 'ru',
            'offer_count_limit': '1',
            'fast': 'true',
        }
        return mockserver.make_response(
            json=load_json('response_yandex_drive.json'),
            headers={'X-Req-Id': '123'},
        )

    response = await taxi_persuggest.post(URL, BASIC_REQUEST, headers=headers)
    assert response.status_code == 200
    validate_v2(
        response.json(),
        load_json('expected_response_with_drive_not_userplace.json'),
    )


@pytest.mark.translations(
    client_messages={
        'work': {'ru': 'Работа'},
        'shortcuts.route_eta.round.hours_minutes': {
            'ru': '%(hours).0f ч %(minutes).0f мин',
        },
        'shortcuts.route_eta.round.hours': {'ru': '%(value).0f ч'},
        'shortcuts.route_eta.round.tens_minutes': {'ru': '%(value).0f мин'},
        'shuttle_shortcut_text_key': {'ru': 'Translated Attributed Text!'},
    },
)
@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'work_userplace_type': {'shortcut': 'shortcuts_work_userplace_tag'},
    },
)
@pytest.mark.now('2020-01-24T10:00:00+0300')
@pytest.mark.experiments3(filename='exp3_shuttle_in_routestats_exp.json')
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
@pytest.mark.parametrize('price_text', [True, False])
async def test_4_0_shortcuts_with_shuttle_not_userplace(
        taxi_persuggest, mockserver, load_json, experiments3, price_text,
):
    headers = copy.deepcopy(PA_HEADERS)
    headers['X-AppMetrica-UUID'] = 'UUID_NOT_USERPLACE'

    experiments3.add_experiments_json(
        load_json('exp3_shuttle_shortcut_exp_with_price_text.json')
        if price_text
        else load_json('exp3_shuttle_shortcut_exp.json'),
    )

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('response_zerosuggest_no_userplace.json')

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/match_shuttles',
    )
    def _mock_shuttle(request):
        assert request.headers['X-YaTaxi-PhoneId']
        assert request.headers['X-Yandex-UID']
        assert json.loads(request.get_data()) == load_json(
            'expected_shuttle_request.json',
        )
        return load_json('shuttle_match_response.json')

    response = await taxi_persuggest.post(URL, BASIC_REQUEST, headers=headers)
    assert response.status_code == 200
    assert _mock_shuttle.has_calls
    response_data = response.json()
    expected_data = copy.deepcopy(response_data)
    shuttle_scenario = (
        load_json('shuttle_scenario.json')
        if not price_text
        else load_json('shuttle_scenario_price_text.json')
    )
    expected_data['scenario_tops'][-1] = shuttle_scenario
    for scenario in expected_data['scenario_tops']:
        for shortcut in scenario['shortcuts']:
            shortcut['id'] = ''
    validate_v2(response_data, expected_data)


@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'restaurant_type': {'shortcut': 'shortcuts_restaurant_tag'},
        'work_userplace_type': {'shortcut': 'shortcuts_work_userplace_tag'},
        'default_type': {'shortcut': 'shortcuts_default_tag'},
    },
    ORG_RUBRIC_TO_IMAGE_TYPE={'restaurant': 'restaurant_type'},
)
@pytest.mark.translations(
    client_messages={
        'go_to_work': {'ru': 'На работу'},
        'go_home': {'ru': 'Домой'},
    },
)
@pytest.mark.experiments3(filename='exp3_filter_closed_orgs.json')
@pytest.mark.experiments3(filename='exp3_suggest_icons_disabled.json')
@pytest.mark.now('2017-01-24T10:00:00+0300')
async def test_4_0_shortcuts_disabled_images(
        taxi_persuggest, mockserver, load_json,
):
    headers = copy.deepcopy(PA_HEADERS)

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        for header, value in headers.items():
            assert request.headers[header] == value
        expected_ml_request = load_json('uml_zerosuggest_request.json')
        assert json.loads(request.get_data()) == expected_ml_request
        return load_json('uml_zerosuggest_response.json')

    response = await taxi_persuggest.post(URL, BASIC_REQUEST, headers=headers)
    assert response.status_code == 200
    response = response.json()['scenario_tops'][0]
    validate(response, load_json('expected_response_wo_images.json'))


@pytest.mark.translations(
    client_messages={
        'go_to_work': {'ru': 'На работу'},
        'go_home': {'ru': 'Домой'},
        'shortcuts_event_info_overlay': {'ru': 'Киношка в %(HH_MM)s'},
    },
)
@pytest.mark.experiments3(filename='exp3_add_events_to_zerosuggest.json')
@pytest.mark.experiments3(filename='exp3_shortcuts_event_info_overlay.json')
@pytest.mark.now('2017-01-25T10:00:00+0300')
async def test_4_0_shortcuts_cinema_overlays(
        taxi_persuggest, mockserver, load_json,
):
    headers = copy.deepcopy(PA_HEADERS)

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return {'results': []}

    @mockserver.json_handler('/userplaces/userplaces/events')
    def _mock_userplaces_events(request):
        return load_json('userplaces_events_response.json')

    response = await taxi_persuggest.post(URL, BASIC_REQUEST, headers=headers)
    assert response.status_code == 200
    response = response.json()['scenario_tops'][0]
    validate(response, load_json('expected_response_with_event.json'))


@pytest.mark.parametrize(
    'expected_shortcut_color, expected_shortcut_icon_color',
    [
        pytest.param('#F5F2E4', '#D2CDB6', id='normal mode'),
        pytest.param(
            'custom_bg_color',
            'custom_icon_bg_color',
            marks=pytest.mark.experiments3(
                filename='exp3_persuggest_ultima_mode.json',
            ),
            id='ultima mode',
        ),
    ],
)
@pytest.mark.config(
    IMAGE_TYPE_TO_IMAGE_TAG={
        'work_userplace_type': {'shortcut': 'shortcuts_work_userplace_tag'},
        'default_type': {'shortcut': 'shortcuts_default_tag'},
    },
)
@pytest.mark.experiments3(filename='exp3_suggest_icons_enabled.json')
async def test_4_0_shortcuts_ultima_mode(
        taxi_persuggest,
        mockserver,
        load_json,
        expected_shortcut_color,
        expected_shortcut_icon_color,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('uml_zerosuggest_response.json')

    response = await taxi_persuggest.post(
        URL, BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    taxi_shortcuts = response.json()['scenario_tops'][0]['shortcuts']
    for shortcut in taxi_shortcuts:
        assert shortcut['content']['color'] == expected_shortcut_color
        assert (
            shortcut['scenario_params']['taxi_expected_destination_params'][
                'icon'
            ]['background']['color']
            == expected_shortcut_icon_color
        )


@pytest.mark.translations(
    client_messages={
        'sdc.selection_screen_a.title': {'ru': 'Выберите точку А'},
        'sdc.selection_screen_a.subtitle': {
            'ru': 'беспилотник может забрать вас не везде',
        },
        'sdc.selection_screen_a.button_text': {'ru': 'Далее'},
        'sdc.selection_screen_b.title': {'ru': 'Выберите точку Б'},
        'sdc.selection_screen_b.subtitle': {
            'ru': 'беспилотник может высадить вас не везде',
        },
        'sdc.selection_screen_b.button_text': {'ru': 'Готово'},
        'sdc_shortcut_title_key': {'ru': 'Беспилотник'},
        'sdc_shortcut_subtitle_key': {'ru': 'покатаемся'},
        'sdc_shortcut_label.first_text': {'ru': 'прикольная'},
        'sdc_shortcut_label.second_text': {'ru': 'тема'},
        'emergency_disabled_sdc_title_key': {'ru': 'У беспилотника лапки'},
        'emergency_disabled_sdc_subtitle_key': {'ru': 'Приходи когда починят'},
        'not_working_by_schedule_title_key': {'ru': 'Беспилотник спит'},
        'not_working_by_schedule_subtitle_key': {
            'ru': 'Приходи когда проснется',
        },
    },
)
@pytest.mark.experiments3(filename='exp3_sdc_flow_trap_shortcut.json')
@pytest.mark.config(
    MODES=[
        {
            'alerts': {
                'out_of_zone': {
                    'button_text': '',
                    'content': '',
                    'notification_params': {
                        'due_date': '2023-01-24T10:00:00+0300',
                        'max_alerts_per_session': 5,
                        'max_alerts_per_user': 100,
                    },
                    'title': '',
                },
            },
            'experiment': 'enable_sdc_2',
            'mode': 'sdc',
            'title': 'zoneinfo.modes.title.sdc',
            'zone_activation': {
                'point_image_tag': 'custom_pp_icons_2_red',
                'point_title': 'selfdriving.pickuppoint_name',
                'zone_type': 'sdc',
            },
        },
    ],
)
@pytest.mark.parametrize(
    'pin_zone_id,screen',
    [
        ('sdc_yasenevo', 'main'),
        ('bad_zone', 'main'),
        ('sdc_yasenevo', 'multiorder'),
    ],
)
@pytest.mark.parametrize(
    'in_schedule',
    [
        pytest.param(
            True,
            marks=pytest.mark.now('2020-01-24T10:00:00+0300'),
            id='in-schedule',
        ),
        pytest.param(
            False,
            marks=pytest.mark.now('2020-01-24T02:00:00+0300'),
            id='not-in-schedule',
        ),
    ],
)
@pytest.mark.parametrize(
    'emergency_disabled',
    [
        pytest.param(
            False,
            marks=pytest.mark.experiments3(filename='exp3_enable_sdc_2.json'),
            id='not-emergency-disabled',
        ),
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='exp3_enable_sdc_2_emergency_disabled.json',
            ),
            id='emergency-disabled',
        ),
    ],
)
async def test_4_0_shortcuts_sdc_flow_trap(
        taxi_persuggest,
        mockserver,
        load_json,
        pin_zone_id,
        screen,
        in_schedule,
        emergency_disabled,
):
    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas(request):
        return {'results': []}

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_sz_zones(request):
        resp = load_json('response_zones.json')
        resp['pin_zone_id'] = pin_zone_id
        return resp

    headers = copy.deepcopy(PA_HEADERS)
    request = copy.deepcopy(BASIC_REQUEST)
    request['state']['screen_type'] = screen
    request['state']['current_mode'] = 'normal'
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200

    resp_data = response.json()
    has_shortcut = (pin_zone_id == 'sdc_yasenevo') and (screen == 'main')
    if has_shortcut:
        if not in_schedule:
            expected = load_json(
                'expected_sdc_shortcut_out_of_schedule_response.json',
            )
        elif emergency_disabled:
            expected = load_json(
                'expected_sdc_shortcut_emergency_disabled_response.json',
            )
        else:
            expected = load_json('expected_sdc_shortcut_response.json')

        resp_data['scenario_tops'][0]['shortcuts'][0].pop('id')
        assert resp_data == expected
    else:
        assert not resp_data['scenario_tops']


@pytest.mark.translations(
    client_messages={
        'go_to_work': {'ru': 'На работу'},
        'go_home': {'ru': 'Домой'},
        'event.spief.title': {'ru': 'ПМЭФ'},
    },
)
@pytest.mark.parametrize(
    'selected_class, expected_response_json',
    [
        ('ultimate', 'expected_response_with_pief_event.json'),
        ('econom', 'expected_response_without_pief_event.json'),
    ],
)
@pytest.mark.experiments3(filename='exp3_pief_event.json')
@pytest.mark.now('2017-01-25T10:00:00+0300')
async def test_4_0_shortcuts_pief(
        taxi_persuggest,
        mockserver,
        load_json,
        selected_class,
        expected_response_json,
):
    headers = copy.deepcopy(PA_HEADERS)
    request = copy.deepcopy(BASIC_REQUEST)
    request['state']['selected_class'] = selected_class

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/zerosuggest')
    def _mock_umlaas_geo(request):
        return load_json('uml_zerosuggest_response.json')

    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    response = response.json()['scenario_tops'][0]
    expected_response = load_json(expected_response_json)
    validate(response, expected_response)
