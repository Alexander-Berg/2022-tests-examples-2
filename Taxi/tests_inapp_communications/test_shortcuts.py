# pylint: disable=too-many-lines

import copy
import json

import pytest


def _create_headers(phone_id):
    return {
        'X-YaTaxi-User': 'personal_phone_id=personal_phone_id_1',
        'X-Yandex-UID': 'uid_1',
        'X-YaTaxi-PhoneId': phone_id,
        'X-YaTaxi-UserId': 'user_id_1',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app=iphone',
    }


DEFAULT_HEADERS = _create_headers('phone_id_1')

DEFAULT_REQUEST = {
    'user_context': {
        'pin_position': [-37, -55],
        'show_at': '2019-01-10T22:39:50+03:00',
    },
}

DEFAULT_ATTR_TEXT_CONTENT = {
    'attributed_subtitle': {
        'items': [
            {
                'color': '#FEFEFE',
                'font_size': 15,
                'font_style': 'italic',
                'font_weight': 'regular',
                'meta_style': 'header-regular',
                'text': 'alt_title',
                'text_decoration': ['line_through'],
                'type': 'text',
            },
        ],
    },
    'attributed_title': {
        'items': [
            {
                'color': '#FEFEFE',
                'font_size': 15,
                'font_style': 'italic',
                'font_weight': 'regular',
                'meta_style': 'header-regular',
                'text': 'title',
                'text_decoration': ['line_through'],
                'type': 'text',
            },
            {'text': ' ', 'type': 'text'},
            {'text': 'field1_data', 'type': 'text'},
        ],
    },
    'subtitle': '<bold>alt_title</bold>',
    'text_color': '#FFFFFF',
    'title': '<bold>title</bold> field1_data',
}


def compare_shortcuts_key(shortcut):
    return shortcut['content']['title']


def compare_tops_key(top):
    return top['scenario']


def _get_promotion_id(shortcut):
    if 'media_stories_params' in shortcut['scenario_params']:
        return shortcut['scenario_params']['media_stories_params']['promo_id']
    return shortcut['scenario_params']['deeplink_params']['deeplink']


def _get_promotion_ids(data):
    promotion_ids = set()
    for scenario_top in data['scenario_tops']:
        for shortcut in scenario_top['shortcuts']:
            promotion_ids.add(_get_promotion_id(shortcut))
    return promotion_ids


@pytest.fixture(autouse=True)
def _eda_shortlist(mockserver, load_json):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _mock_eda_shortlist(request):
        return load_json('default_shortlist_service_response.json')

    return _mock_eda_shortlist


def _validate_dummy_shortcuts_response(response, load_json):
    assert response.status_code == 200

    response_text = response.json()

    assert len(response_text['scenario_tops']) >= 1
    assert response_text['scenario_tops'][0]['scenario'] == 'media_stories'
    assert len(response_text['scenario_tops'][0]['shortcuts']) >= 1
    assert response_text['scenario_tops'][0]['shortcuts'][0]['id']

    del response_text['scenario_tops'][0]['shortcuts'][0]['id']

    # should not expect id2 due to lack of payload
    assert response_text == load_json('dummy_shortcuts_test_response.json')


@pytest.mark.experiments3(filename='exp3_not_fit.json')
async def test_exp3_not_fit(taxi_inapp_communications, mockserver, load_json):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_not_fit.json')

    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        return {'tags': ['tag1', 'tag2']}

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert not response.json()['scenario_tops']


@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_dummy_with_experiments(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        data = json.loads(request.get_data())['match']
        data = sorted(data, key=lambda i: i['type'])
        assert data[0] == {
            'type': 'personal_phone_id',
            'value': 'personal_phone_id_1',
        }
        assert data[1] == {'type': 'user_id', 'value': 'user_id_1'}
        assert data[2] == {'type': 'user_phone_id', 'value': 'phone_id_1'}
        return {'tags': ['tag1', 'tag2']}

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    _validate_dummy_shortcuts_response(response, load_json)


@pytest.mark.experiments3(filename='exp3_tags.json')
async def test_tags(taxi_inapp_communications, mockserver, load_json):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        data = json.loads(request.get_data())['match']
        data = sorted(data, key=lambda i: i['type'])
        assert data[0] == {
            'type': 'personal_phone_id',
            'value': 'personal_phone_id_1',
        }
        assert data[1] == {'type': 'user_id', 'value': 'user_id_1'}
        assert data[2] == {'type': 'user_phone_id', 'value': 'phone_id_1'}
        assert data[3] == {'type': 'yandex_uid', 'value': 'uid_1'}
        return {'tags': ['tag1', 'tag2']}

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    response_text = response.json()
    assert len(response_text['scenario_tops'][0]['shortcuts']) == 2


@pytest.mark.experiments3(filename='exp3_tags.json')
async def test_screen_check(taxi_inapp_communications, mockserver, load_json):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_test_screen.json')

    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        return {'tags': ['tag1', 'tag2']}

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    response_text = response.json()
    # All communications in cache don't have appropriate screen
    assert not response_text['scenario_tops']


@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_media_tags_no_screen_info(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_test_image_tag.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    response_text = response.json()
    assert len(response_text['scenario_tops'][0]['shortcuts']) == 2
    assert {
        str(i['content']['image_tag'])
        for i in response_text['scenario_tops'][0]['shortcuts']
    } == {'id1_original', 'id2_url'}


@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_media_tags_screen_info(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_test_image_tag.json')

    request = {
        'user_context': {
            'pin_position': [-37, -55],
            'show_at': '2019-01-10T22:39:50+03:00',
            'media_size_info': {
                'screen_height': 1800,
                'screen_width': 1200,
                'scale': 2,
            },
        },
    }

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        request,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    response_text = response.json()
    assert {
        str(i['content']['image_tag'])
        for i in response_text['scenario_tops'][0]['shortcuts']
    } == {'id1_original', 'id2_url', 'id3_1440', 'id5_2', 'id6_3'}


@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_communications_sorter(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json(
            'promotions_service_response_communications_sorter.json',
        )

    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        return {'tags': ['tag1', 'tag2']}

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        json=DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    resp_json = response.json()['scenario_tops']

    result_ids = [
        [
            s['scenario_params']['media_stories_params']['promo_id']
            if 'media_stories_params' in s['scenario_params']
            else s['scenario_params']['deeplink_params']['deeplink']
            for s in response.json()['scenario_tops'][i]['shortcuts']
        ]
        for i in range(len(resp_json))
    ]
    assert len(result_ids) == 2
    assert ['id1:v1', 'id3:v1', 'id2:v2'] in result_ids
    assert [
        'id5',
        'deeplink88',
        'deeplink51',
        'id4',
        'deeplink0',
    ] in result_ids


@pytest.mark.experiments3(filename='exp3_dummy.json')
@pytest.mark.parametrize('add_overlays', [True, False])
@pytest.mark.translations(backend_promotions={'key_1': {'ru': 'overlay_1'}})
async def test_deeplink_shortcuts(
        taxi_inapp_communications,
        mockserver,
        load_json,
        add_overlays,
        taxi_config,
):
    taxi_config.set(INAPP_SHORTCUTS_ADD_OVERLAYS=add_overlays)

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_deeplink_shortcuts.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    response_text = response.json()
    correct_response = load_json('deeplink_shortcuts_test_response.json')
    correct_response['scenario_tops'] = sorted(
        correct_response['scenario_tops'], key=compare_tops_key,
    )
    response_text['scenario_tops'] = sorted(
        response_text['scenario_tops'], key=compare_tops_key,
    )

    for scenraio_top in response_text['scenario_tops']:
        scenraio_top['shortcuts'] = sorted(
            scenraio_top['shortcuts'], key=compare_shortcuts_key,
        )
        for i in scenraio_top['shortcuts']:
            del i['id']

    for scenraio_top in correct_response['scenario_tops']:
        scenraio_top['shortcuts'] = sorted(
            scenraio_top['shortcuts'], key=compare_shortcuts_key,
        )

    if add_overlays:
        overlays = [
            {
                'background': {
                    'color': '#123456',
                    'image_tag': 'tag',
                    'meta_color': '#123456',
                },
                'image_tag': 'tag',
                'is_tanker_key': True,
                'shape': 'bubble',
                'text': 'overlay_1',
                'text_color': '#123456',
            },
            {'text': 'overlay_2', 'is_tanker_key': False},
        ]
        correct_response['scenario_tops'][0]['shortcuts'][0]['content'].update(
            {'overlays': overlays},
        )

    assert correct_response == response_text


@pytest.mark.experiments3(filename='exp3_services_availability_check.json')
@pytest.mark.parametrize(
    'available, show_disabled, expected_promotion_ids',
    [
        # id1 promotion is using availability in point
        # enabled == mode.available
        # id2 promotion is using potential availability in point
        # enabled == mode.show_disabled || mode.available
        [False, False, []],
        [
            True,
            False,
            ['id1', 'id2'],
        ],  # id2 promotion is available, service is available in point
        [False, True, ['id2']],
        [True, True, ['id1', 'id2']],
    ],
)
async def test_services_availability_kwargs(
        taxi_inapp_communications,
        mockserver,
        load_json,
        available,
        show_disabled,
        expected_promotion_ids,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json(
            'promotions_service_response_services_availability_check.json',
        )

    request = copy.deepcopy(DEFAULT_REQUEST)
    test_service_parameters = {
        'available': available,
        'product_tag': 'some_service',
    }
    if show_disabled:
        test_service_parameters['show_disabled'] = True

    request['services_availability'] = {
        'modes': [
            {'mode': 'some_service', 'parameters': test_service_parameters},
        ],
        'products': [
            {
                'service': 'some_service',
                'tag': 'some_service',
                'title': 'Some Service',
            },
        ],
        'zone_name': 'Moscow',
    }

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        request,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    data = response.json()

    assert _get_promotion_ids(data) == set(expected_promotion_ids)


@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_different_scenarios(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json(
            'promotions_service_response_different_scenarios.json',
        )

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    response_text = response.json()
    scenarios = sorted(
        [scenario['scenario'] for scenario in response_text['scenario_tops']],
    )
    assert scenarios == ['meta_type_1', 'meta_type_2']


@pytest.mark.config(
    EXTENDED_TEMPLATE_STYLES_MAP={
        'bold': {
            'font_size': 15,
            'font_weight': 'regular',
            'font_style': 'italic',
            'color': '#FEFEFE',
            'meta_style': 'header-regular',
            'text_decoration': ['line_through'],
        },
    },
)
@pytest.mark.pgsql('promotions', files=['promotions_default.sql'])
@pytest.mark.translations(
    backend_promotions={
        'title_key': {'en': 'test {field1} test'},
        'subtitle_key': {'en': 'test {field2} test'},
        'title_key_attr_text': {'en': '<bold>title</bold> {field1}'},
        'subtitle_key_attr_text': {'en': '<bold>alt_title</bold>'},
    },
)
@pytest.mark.experiments3(filename='exp3_dummy.json')
@pytest.mark.experiments3(filename='exp3_test_publish.json')
async def test_personalization(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json(
            'promotions_service_response_test_personalization.json',
        )

    headers = copy.deepcopy(DEFAULT_HEADERS)
    headers['X-Request-Language'] = 'en'

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=headers,
    )
    assert response.status_code == 200

    response_text = response.json()

    assert _get_promotion_ids(response_text) == {
        'deeplink1',
        'deeplink2',
        'deeplink3',
        'id_story_translaton_and_yql:jdkc',
        'id_story_translaton_and_yql_no_exp:jdkc',
        'id_story_translaton_and_yql_test_published:jdkc',
        'id_story_attr_text:jdkc',
    }
    for shortcut in response_text['scenario_tops'][0]['shortcuts']:
        if _get_promotion_id(shortcut) == 'id_story_attr_text:jdkc':
            assert shortcut['content'] == DEFAULT_ATTR_TEXT_CONTENT
            continue
        assert shortcut['content']['title'] == 'test field1_data test'
        assert shortcut['content']['subtitle'] == 'test 100500 test'


@pytest.mark.config(
    INAPP_CREATE_BLENDER_BUILDING_CONTEXT=True,
    EXTENDED_TEMPLATE_STYLES_MAP={
        'bold': {
            'font_size': 15,
            'font_weight': 'regular',
            'font_style': 'italic',
            'color': '#FEFEFE',
            'meta_style': 'header-regular',
            'text_decoration': ['line_through'],
        },
    },
)
@pytest.mark.pgsql('promotions', files=['promotions_default.sql'])
@pytest.mark.translations(
    backend_promotions={
        'title_key': {'en': 'test {field1} test'},
        'subtitle_key': {'en': 'test {field2} test'},
        'title_key_attr_text': {'en': '<bold>title</bold> {field1}'},
        'subtitle_key_attr_text': {'en': '<bold>alt_title</bold>'},
    },
)
@pytest.mark.experiments3(filename='exp3_dummy.json')
@pytest.mark.experiments3(filename='exp3_test_publish.json')
async def test_building_context(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_building_context.json')

    headers = copy.deepcopy(DEFAULT_HEADERS)
    headers['X-Request-Language'] = 'en'

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=headers,
    )
    assert response.status_code == 200

    response_text = response.json()

    assert len(response_text['scenario_tops'][0]['shortcuts']) == 1
    assert (
        response_text['scenario_tops'][0]['shortcuts'][0]['scenario_params'][
            'promo_id'
        ]
        == 'id_story_attr_text:jdkc'
    )
    assert response_text['scenario_tops'][0]['building_context'] == {
        'shortcuts_promo_ids_to_build': [
            'id_deeplink_shortcuts:rev1',
            'id_deeplink_shortcuts2:rev1',
        ],
        'promo_ids_order': [
            'id_deeplink_shortcuts2:rev1',
            'id_story_attr_text:jdkc',
            'id_deeplink_shortcuts:rev1',
        ],
    }


@pytest.mark.config(EXTENDED_TEMPLATE_STYLES_MAP={})
@pytest.mark.pgsql('promotions', files=['promotions_default.sql'])
@pytest.mark.parametrize(
    'promotions_response',
    [
        'promotions_service_response_yql_data_fail.json',
        'promotions_service_response_translation_fail.json',
        'promotions_service_response_attr_text_fail.json',
    ],
)
@pytest.mark.translations(
    backend_promotions={
        'page_title_key': {'ro': 'page_title_key_ro'},
        'title_key': {'ro': 'title_key'},
        'title_key_attr_text': {'ru': '<bold>title</bold> {field3}'},
        'subtitle_key_attr_text': {'ru': '<bold>alt_title</bold>'},
    },
)
@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_failures(
        taxi_inapp_communications, mockserver, load_json, promotions_response,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json(promotions_response)

    headers = {
        'X-Yandex-UID': 'failurable_uid',
        'X-YaTaxi-PhoneId': 'failurable_phone_id',
        'X-YaTaxi-UserId': 'failurable_user',
        'X-Request-Language': 'ru',
        'X-Request-Application': 'app=iphone',
    }
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=headers,
    )
    assert response.status_code == 200
    response_text = response.json()
    assert not response_text['scenario_tops']


@pytest.mark.experiments3(filename='exp3_dummy_time_scheduling.json')
async def test_dummy_with_experiments_time_scheduling(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        return {'tags': ['tag1', 'tag2']}

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    response_text = response.json()
    assert len(response_text['scenario_tops']) >= 1
    assert len(response_text['scenario_tops'][0]['shortcuts']) >= 1
    assert response_text['scenario_tops'][0]['shortcuts'][0]['id']
    del response_text['scenario_tops'][0]['shortcuts'][0]['id']
    assert response_text['scenario_tops'][0]['scenario'] == 'media_stories'

    assert response_text == load_json('dummy_shortcuts_test_response.json')


@pytest.mark.experiments3(filename='exp3_dummy_restaurants.json')
async def test_dummy_with_experiments_restaurants(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        return {'tags': ['tag1', 'tag2']}

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    _validate_dummy_shortcuts_response(response, load_json)


@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_dummy_with_experiments_restaurants_eda_request_error(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.handler('/eda-catalog/v1/shortlist')
    def _mock_eda_shortlist(request):
        return mockserver.make_response('internal server error', status=500)

    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        return {'tags': ['tag1', 'tag2']}

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    assert _mock_eda_shortlist.times_called >= 1

    _validate_dummy_shortcuts_response(response, load_json)


@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_dummy_with_experiments_restaurants_disabled(
        taxi_inapp_communications, mockserver, load_json, _eda_shortlist,
):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_v2_match(request):
        return {'tags': ['tag1', 'tag2']}

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=_create_headers('phone_id_unknown'),
    )

    assert _eda_shortlist.times_called == 0

    _validate_dummy_shortcuts_response(response, load_json)


@pytest.mark.parametrize(
    'phone_id, is_in_test',
    [('phone_id_1', True), ('phone_id_not_in_test_publish', False)],
)
@pytest.mark.experiments3(filename='exp3_test_publish.json')
async def test_test_publish(
        taxi_inapp_communications, phone_id, is_in_test, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    headers = copy.deepcopy(DEFAULT_HEADERS)
    headers['X-YaTaxi-PhoneId'] = phone_id
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        json=DEFAULT_REQUEST,
        headers=headers,
    )

    assert response.status == 200, response.text
    scenario_tops = response.json()['scenario_tops']
    assert len(scenario_tops) == (2 if is_in_test else 0)


@pytest.mark.experiments3(filename='exp3_dummy.json')
@pytest.mark.translations(
    backend_promotions={
        'friday_key': {'ru': 'Пятница', 'en': 'Friday'},
        'personalized_new_year_congratulation': {
            'ru': 'С Новым Годом, %(username)s!',
        },
        'default_new_year_congratulation': {'ru': 'С Новым Годом!'},
    },
)
@pytest.mark.parametrize(
    'first_name, expected_title',
    [
        pytest.param(
            'Пассажир',
            'С Новым Годом, Пассажир!',
            marks=pytest.mark.experiments3(
                filename='exp3_inapp_username_length_limit.json',
            ),
            id='ok, Cyrillic name meets the requirements',
        ),
        pytest.param(
            'Passenger',
            'С Новым Годом, Passenger!',
            marks=pytest.mark.experiments3(
                filename='exp3_inapp_username_length_limit.json',
            ),
            id='ok, Latin name meets the requirements',
        ),
        pytest.param(
            None, 'С Новым Годом!', id='fallback, no passenger profile sent',
        ),
        pytest.param(
            'ОченьДлинноеИмя',
            'С Новым Годом!',
            marks=pytest.mark.experiments3(
                filename='exp3_inapp_username_length_limit.json',
            ),
        ),
        pytest.param(
            'ОченьДлинноеИмя',
            'С Новым Годом, ОченьДлинноеИмя!',
            id='ok, no limit on the name length',
        ),
    ],
)
async def test_showcases(
        taxi_inapp_communications,
        mockserver,
        load_json,
        first_name,
        expected_title,
):
    promotions_response = load_json(
        'promotions_service_response_showcases.json',
    )

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return promotions_response

    payload = copy.deepcopy(DEFAULT_REQUEST)
    passenger_profile = {'rating': '4.90'}
    if first_name:
        passenger_profile.update({'first_name': first_name})
    payload['user_context'].update({'passenger_profile': passenger_profile})

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        json=payload,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    showcases_from_promotions = promotions_response['showcases']
    showcases_from_inapp = response.json()['showcases']
    showcases_names_from_inapp = [s['name'] for s in showcases_from_inapp]
    assert showcases_names_from_inapp == [
        'showcase_name_2020',
        'showcase_name',
        'showcase_name_2018',
    ]
    promoblocks_2020 = showcases_from_promotions[1]['blocks']
    promoblocks_2018 = showcases_from_promotions[2]['blocks']
    assert showcases_from_inapp == [
        {
            'blocks': [
                {
                    'cells': promoblocks_2020[0]['collection_data']['cells'],
                    'name': 'title_2020',
                    'slug': promoblocks_2020[0]['collection_data']['name'],
                },
            ],
            'name': 'showcase_name_2020',
        },
        {
            'blocks': [
                {
                    'cells': showcases_from_promotions[0]['blocks'][0][
                        'collection_data'
                    ]['cells'],
                    'name': 'Пятница',  # localized
                    'slug': showcases_from_promotions[0]['blocks'][0][
                        'collection_data'
                    ]['name'],
                },
                {
                    'cells': showcases_from_promotions[0]['blocks'][1][
                        'collection_data'
                    ]['cells'],
                    'name': showcases_from_promotions[0]['blocks'][1][
                        'title'
                    ],  # not localized
                    'slug': showcases_from_promotions[0]['blocks'][1][
                        'collection_data'
                    ]['name'],
                },
                {
                    'cells': showcases_from_promotions[0]['blocks'][2][
                        'collection_data'
                    ]['cells'],
                    # no title
                    'slug': showcases_from_promotions[0]['blocks'][2][
                        'collection_data'
                    ]['name'],
                },
                {
                    'cells': showcases_from_promotions[0]['blocks'][3][
                        'collection_data'
                    ]['cells'],
                    'name': expected_title,
                    'slug': showcases_from_promotions[0]['blocks'][3][
                        'collection_data'
                    ]['name'],
                },
            ],
            'name': 'showcase_name',
        },
        {
            'blocks': [
                {
                    'cells': promoblocks_2018[0]['collection_data']['cells'],
                    'name': 'title_2018',
                    'slug': promoblocks_2018[0]['collection_data']['name'],
                },
            ],
            'name': 'showcase_name_2018',
        },
    ]


@pytest.mark.experiments3(filename='exp3_dummy.json')
@pytest.mark.experiments3(filename='exp3_inapp_username_length_limit.json')
@pytest.mark.parametrize(
    'screens, screen, match',
    [
        pytest.param(
            ['ANY_SCREEN'], None, True, id='no request screen, any screen',
        ),
        pytest.param(
            ['on_multiorder'],
            None,
            False,
            id='no request screen, not main screen',
        ),
        pytest.param(
            ['main'], None, True, id='no request screen, main screen',
        ),
        pytest.param(
            ['main', 'on_multiorder'],
            'scooters',
            False,
            id='screen not in screens',
        ),
        pytest.param(
            ['main', 'scooters'], 'scooters', True, id='screen in screens',
        ),
    ],
)
async def test_screen_matching(
        taxi_inapp_communications,
        mockserver,
        load_json,
        screens,
        screen,
        match,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        promotions_response = load_json(
            'promotions_service_response_showcases_matching.json',
        )
        promotions_response['showcases'][0]['screens'] = screens
        return promotions_response

    payload = copy.deepcopy(DEFAULT_REQUEST)
    if screen:
        payload.update({'screen': screen})

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        json=payload,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    showcases_from_inapp = response.json()['showcases']
    showcases_names_from_inapp = [s['name'] for s in showcases_from_inapp]
    assert showcases_names_from_inapp == (['showcase_name'] if match else [])


@pytest.mark.experiments3(filename='exp3_promotion_showcases.json')
@pytest.mark.parametrize('force_promotions', [True, False])
async def test_promotion_showcases(
        taxi_inapp_communications,
        mockserver,
        load_json,
        taxi_config,
        force_promotions,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json(
            'promotions_service_response_showcases_promotions.json',
        )

    taxi_config.set_values(
        {'INAPP_FORCE_PROMOTIONS': {'force_promotions': force_promotions}},
    )

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert len(response.json()['scenario_tops']) == 2

    scenarios = set(
        [
            response.json()['scenario_tops'][0]['scenario'],
            response.json()['scenario_tops'][1]['scenario'],
        ],
    )
    assert scenarios == {'deeplink_shortcut_meta_type', 'media_stories'}

    deeplink_shortcuts = [
        top['shortcuts']
        for top in response.json()['scenario_tops']
        if top['scenario'] == 'deeplink_shortcut_meta_type'
    ][0]

    media_stories_shortcuts = [
        top['shortcuts']
        for top in response.json()['scenario_tops']
        if top['scenario'] == 'media_stories'
    ][0]

    if force_promotions:
        assert len(deeplink_shortcuts) == 2
        assert len(media_stories_shortcuts) == 2

        assert deeplink_shortcuts[1]['scenario_params'] == {
            'promo_id': 'deeplink_shortcut_id_1:version',
            'deeplink_params': {'deeplink': 'deeplink1'},
        }

        assert deeplink_shortcuts[0]['scenario_params'] == {
            'promo_id': 'deeplink_shortcut_id_2:version',
            'deeplink_params': {'deeplink': 'deeplink2'},
        }

        assert media_stories_shortcuts[0]['scenario_params'] == {
            'media_stories_params': {
                'action_type': 'media_stories',
                'promo_id': 'stories_id_2:version',
            },
            'promo_id': 'stories_id_2:version',
        }

        assert media_stories_shortcuts[1]['scenario_params'] == {
            'media_stories_params': {
                'action_type': 'media_stories',
                'promo_id': 'stories_id_1:version',
            },
            'promo_id': 'stories_id_1:version',
        }

    else:
        assert len(deeplink_shortcuts) == 1
        assert len(media_stories_shortcuts) == 1

        assert deeplink_shortcuts[0]['scenario_params'] == {
            'promo_id': 'deeplink_shortcut_id_1:version',
            'deeplink_params': {'deeplink': 'deeplink1'},
        }

        assert media_stories_shortcuts[0]['scenario_params'] == {
            'media_stories_params': {
                'action_type': 'media_stories',
                'promo_id': 'stories_id_1:version',
            },
            'promo_id': 'stories_id_1:version',
        }


@pytest.mark.config(
    INAPP_CONFLICTING_PROMOTIONS={
        'conflicting_promotions': [
            {
                'high_priority_promotion_id': 'id1',
                'low_priority_promotion_id': 'id2',
            },
        ],
    },
)
@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_conflicting_promotions(
        taxi_inapp_communications, mockserver, load_json,
):
    # step 1: add two promotions to inapp response
    # step 2: remove second promotion in FilterMediaShortcuts
    # step 3: ensure that there is only 1 promo in response
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        promotions_response = load_json(
            'default_promotions_service_response.json',
        )
        preview = promotions_response['stories'][0]['payload']['preview']
        # add preview to promo 'id2' to remove it from inapp response by config
        promotions_response['stories'][1]['payload'].update(
            {'preview': preview},
        )
        return promotions_response

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    _validate_dummy_shortcuts_response(response, load_json)


@pytest.mark.surge_heatmap(
    cell_size_meter=500.123,
    envelope={'br': [37, 55], 'tl': [38, 56]},
    values=[{'x': 0, 'y': 0, 'surge': 1.2, 'weight': 1.0}],
)
@pytest.mark.experiments3(filename='exp3_test_shortcut_with_surge_kwarg.json')
async def test_shortcut_with_surge_kwarg(
        taxi_inapp_communications,
        heatmap_storage_fixture,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['user_context']['pin_position'] = [37, 55]

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        json=request,
        headers=DEFAULT_HEADERS,
    )

    assert response.status == 200, response.text
    scenario_tops = response.json()['scenario_tops']
    assert len(scenario_tops) == 2


@pytest.mark.experiments3(
    filename='exp3_test_shortcut_with_weather_kwargs.json',
)
async def test_shortcut_with_weather_kwargs(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['user_context']['pin_position'] = [37.5, 55.5]

    @mockserver.json_handler('/weather/graphql/query')
    def _weather(request):
        assert 'query' in request.json
        assert request.json['query'] == (
            '{weatherByPoint(request: { lat: 55.500000, lon: 37.500000 }) {'
            ' now { condition precType precStrength cloudiness } } }'
        )
        return {
            'data': {
                'weatherByPoint': {
                    'now': {
                        'condition': 'SNOWFALL',
                        'precType': 'HAIL',
                        'precStrength': 'VERY_STRONG',
                        'cloudiness': 'OVERCAST',
                    },
                },
            },
        }

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        json=request,
        headers=DEFAULT_HEADERS,
    )

    assert response.status == 200, response.text
    scenario_tops = response.json()['scenario_tops']
    assert len(scenario_tops) == 2


@pytest.mark.experiments3(
    filename='exp3_test_shortcut_with_promo_tags_kwargs.json',
)
@pytest.mark.parametrize(
    'eats_promo_tags', [[], ['tag1'], ['tag1', 'eats-new-user']],
)
@pytest.mark.parametrize(
    'lavka_promo_tags', [[], ['tag2'], ['tag2', 'lavka-new-user']],
)
@pytest.mark.parametrize(
    'market_promo_tags', [[], ['tag3'], ['tag3', 'market-new-user']],
)
async def test_shortcut_with_promo_tags_kwargs(
        taxi_inapp_communications,
        mockserver,
        load_json,
        eats_promo_tags,
        lavka_promo_tags,
        market_promo_tags,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['services_promo_tags'] = {
        'eats_promo_tags': eats_promo_tags,
        'lavka_promo_tags': lavka_promo_tags,
        'market_promo_tags': market_promo_tags,
    }

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        json=request,
        headers=DEFAULT_HEADERS,
    )

    assert response.status == 200, response.text
    scenario_tops = response.json()['scenario_tops']

    if (
            'eats-new-user' in eats_promo_tags
            and 'lavka-new-user' in lavka_promo_tags
            and 'market-new-user' in market_promo_tags
    ):
        assert len(scenario_tops) == 2
    else:
        assert not scenario_tops


@pytest.mark.experiments3(filename='exp3_test_shortcut_with_tags_kwarg.json')
@pytest.mark.parametrize('request_tags', [None, ['tag1']])
async def test_shortcut_with_tags_kwarg(
        taxi_inapp_communications, mockserver, load_json, request_tags,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _mock_passenger_tags(request):
        return {'tags': ['tag1']}

    request = copy.deepcopy(DEFAULT_REQUEST)
    if request_tags is not None:
        request['tags'] = request_tags

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        json=request,
        headers=DEFAULT_HEADERS,
    )

    assert response.status == 200, response.text
    assert len(response.json()['scenario_tops']) == 2

    if request_tags is None:
        assert _mock_passenger_tags.times_called == 1
    else:
        assert _mock_passenger_tags.times_called == 0


@pytest.mark.parametrize('bank_account', [True, False])
@pytest.mark.experiments3(filename='exp3_bank_account.json')
async def test_shortcut_with_bank_kwargs(
        taxi_inapp_communications, mockserver, load_json, bank_account,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    headers = copy.deepcopy(DEFAULT_HEADERS)
    if bank_account:
        headers['X-YaTaxi-Pass-Flags'] = 'bank-account'
        headers['X-Ya-User-Ticket'] = 'user-ticket'

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        json=DEFAULT_REQUEST,
        headers=headers,
    )

    assert response.status == 200
    promos = response.json()['scenario_tops']
    assert len(promos) == (2 if bank_account else 0)
