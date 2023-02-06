import pytest

from testsuite.utils import ordered_object

UA_YANDEX_TAXI_ANDROID = (
    'yandex-taxi/3.113.0.85658 Android/9' ' (OnePlus; ONEPLUS A5010)'
)

PA_HEADERS = {
    'X-YaTaxi-UserId': 'user_id',
    'X-Yandex-UID': 'uid',
    'X-YaTaxi-Bound-Uids': 'uid1,uid2',
    'X-Yandex-Login': 'login',
    'X-YaTaxi-Pass-Flags': 'portal,ya-plus',
    'X-Request-Language': 'ru',
    'X-Request-Application': (
        'app_ver1=3,app_ver2=118,app_ver3=0,app_name=android,app_brand=yataxi'
    ),
    'X-YaTaxi-User': 'personal_phone_id=some_personal_phone_id',
}


def make_request(zone_name='moscow', point=None):
    request = {
        'options': True,
        'size_hint': 640,
        'supports_hideable_tariffs': True,
    }
    if zone_name:
        request['zone_name'] = zone_name
    if point:
        request['point'] = point
    return request


@pytest.mark.parametrize(
    'zone_name, point, response_code',
    [
        ('moscow', None, 200),
        (None, [37.5, 55.71], 200),
        ('moscow', [37.5, 55.71], 200),
        ('narnia', None, 404),
        (None, [37.5, 75.71], 404),  # no zone
        (None, None, 404),
    ],
)
@pytest.mark.config(
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['econom']},
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.experiments3()
async def test_zoneinfo_core_simple(
        taxi_zoneinfo, load_json, zone_name, point, response_code,
):
    response = await taxi_zoneinfo.post(
        '/v1/zoneinfo/core',
        headers=PA_HEADERS,
        json=make_request(zone_name, point),
    )
    assert response.status_code == response_code
    if response_code == 200:
        json = response.json()
        assert json == load_json('response.json')


@pytest.mark.parametrize(
    'skipped, hidden',
    [
        pytest.param(
            True,
            True,
            marks=[
                pytest.mark.config(
                    APPLICATION_BRAND_CATEGORIES_SETS={
                        '__default__': ['econom'],
                    },
                ),
                pytest.mark.tariff_settings(
                    visibility_overrides={
                        'moscow': {'cargo': {'visible_by_default': False}},
                    },
                ),
            ],
            id='skipped',
        ),
        pytest.param(
            False,
            True,
            marks=[
                pytest.mark.config(
                    APPLICATION_BRAND_CATEGORIES_SETS={
                        '__default__': ['econom', 'cargo'],
                    },
                ),
                pytest.mark.tariff_settings(
                    visibility_overrides={
                        'moscow': {'cargo': {'visible_by_default': False}},
                    },
                ),
            ],
            id='hidden',
        ),
        pytest.param(
            False,
            False,
            marks=[
                pytest.mark.config(
                    APPLICATION_BRAND_CATEGORIES_SETS={
                        '__default__': ['econom', 'cargo'],
                    },
                ),
                pytest.mark.tariff_settings(
                    visibility_overrides={
                        'moscow': {'cargo': {'visible_by_default': True}},
                    },
                ),
            ],
            id='skipped',
        ),
    ],
)
async def test_visibility_helper_simple(
        taxi_zoneinfo, load_json, skipped, hidden,
):
    response = await taxi_zoneinfo.post(
        '/v1/zoneinfo/core', headers=PA_HEADERS, json=make_request(),
    )
    assert response.status_code == 200
    json = response.json()
    if skipped:
        # just one - econom
        assert len(json['max_tariffs']) == 1
        assert json['max_tariffs'][0]['class'] == 'econom'
        return

    assert len(json['max_tariffs']) == 2
    assert json['max_tariffs'][1]['class'] == 'cargo'
    assert json['max_tariffs'][1]['is_hidden'] == hidden


@pytest.mark.config(
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['child_tariff']},
    ZONES_TARIFFS_SETTINGS={
        '__default__': {
            'child_tariff': {
                'subtitle': 'card.subtitle.child_tariff',
                'options': [
                    {'name': 'child_seats', 'value': '1'},
                    {'name': 'elderly_passengers', 'value': '1-2'},
                    {'name': 'max_luggage', 'value': '1-2'},
                ],
            },
        },
    },
)
async def test_zoneinfo_core_child_tariff(taxi_zoneinfo, load_json):
    response = await taxi_zoneinfo.post(
        '/v1/zoneinfo/core', headers=PA_HEADERS, json=make_request(),
    )
    assert response.status_code == 200
    json = response.json()
    assert json == load_json('response_child_tariff.json')


@pytest.mark.experiments3(filename='experiments3_translations.json')
@pytest.mark.config(
    EXPERIMENTS3_CLIENT_TRANSLATIONS=['translatable', 'bad_keys'],
)
@pytest.mark.translations(
    client_messages={
        'exp3.l10n.str': {'ru': 'Str translation'},
        'exp3.l10n.field': {'ru': 'Field translation'},
    },
)
async def test_zoneinfo_exp3_translations(taxi_zoneinfo):
    response = await taxi_zoneinfo.post(
        '/v1/zoneinfo/core', headers=PA_HEADERS, json=make_request(),
    )

    assert response.status_code == 200
    data = response.json()
    print(data['typed_experiments']['items'])
    ordered_object.assert_eq(
        data['typed_experiments']['items'],
        [
            {
                'name': 'untranslatable',
                'value': {
                    'translate_obj': {
                        'translate_field': '$tanker.exp3.l10n.field',
                    },
                    'translate_str': '$tanker.exp3.l10n.str',
                },
            },
            {
                'name': 'translatable',
                'value': {
                    'translate_obj': {'translate_field': 'Field translation'},
                    'translate_str': 'Str translation',
                    'translatable_arr': ['Str translation', 'Str translation'],
                    'translatable_obj_arr': [
                        {'translate_field': 'Field translation'},
                    ],
                    'untranslatable_str': 'Prefix $tanker.',
                },
            },
        ],
        [''],
    )


@pytest.mark.parametrize(
    'expected_classes',
    [
        pytest.param(
            {'econom', 'cargo', 'child_tariff'},
            marks=[
                pytest.mark.config(
                    ORDER_FOR_ANOTHER_COUNTRIES_AND_TARIFFS={'rus': {}},
                ),
            ],
            id='no include, no exclude',
        ),
        pytest.param(
            {},
            marks=[
                pytest.mark.config(
                    ORDER_FOR_ANOTHER_COUNTRIES_AND_TARIFFS={
                        'rus': {'include': []},
                    },
                ),
            ],
            id='empty include',
        ),
        pytest.param(
            {'econom', 'cargo', 'child_tariff'},
            marks=[
                pytest.mark.config(
                    ORDER_FOR_ANOTHER_COUNTRIES_AND_TARIFFS={
                        'rus': {'exclude': []},
                    },
                ),
            ],
            id='empty exclude',
        ),
        pytest.param(
            {'econom', 'cargo'},
            marks=[
                pytest.mark.config(
                    ORDER_FOR_ANOTHER_COUNTRIES_AND_TARIFFS={
                        'rus': {'include': ['econom', 'cargo']},
                    },
                ),
            ],
            id='normal include',
        ),
        pytest.param(
            {'child_tariff'},
            marks=[
                pytest.mark.config(
                    ORDER_FOR_ANOTHER_COUNTRIES_AND_TARIFFS={
                        'rus': {'exclude': ['econom', 'cargo']},
                    },
                ),
            ],
            id='normal exclude',
        ),
        pytest.param(
            {'econom'},
            marks=[
                pytest.mark.config(
                    ORDER_FOR_ANOTHER_COUNTRIES_AND_TARIFFS={
                        'rus': {'include': ['econom'], 'exclude': ['cargo']},
                    },
                ),
            ],
            id='include exclude, include has highest priority',
        ),
    ],
)
async def test_zoneinfo_order_for_other(taxi_zoneinfo, expected_classes):
    response = await taxi_zoneinfo.post(
        '/v1/zoneinfo/core', headers=PA_HEADERS, json=make_request(),
    )
    assert response.status_code == 200

    data = response.json()['max_tariffs']
    allowed_classes = {
        cls['class']
        for cls in data
        if cls['order_for_other_prohibited'] is False
    }
    assert allowed_classes == set(expected_classes)


@pytest.mark.parametrize(
    'expected_extra_phones',
    [
        pytest.param(
            {
                'econom': {
                    'phone_required_popup_properties': {
                        'button_text': 'on_empty_popup.button_text',
                        'description': 'on_empty_popup.description',
                        'title': 'on_empty_popup.title',
                    },
                    'required': False,
                    'requirement_label': 'requirement_label',
                    'selected_label': 'selected_label',
                    'phone_selection_screen': {
                        'title': 'phone_selection_screen.title',
                        'read_contacts_permission': (
                            'phone_selection_screen.read_contacts_permission'
                        ),
                        'choose_one_label': (
                            'phone_selection_screen.choose_one_label'
                        ),
                    },
                },
            },
            marks=[
                pytest.mark.config(
                    FOR_ANOTHER_OPTIONS_BY_TARIFF={
                        '__default__': {},
                        'econom': {'required': False},
                    },
                ),
            ],
            id='econom, not required',
        ),
        pytest.param(
            {
                'econom': {
                    'phone_required_popup_properties': {
                        'button_text': 'test.on_empty_popup.button_text',
                        'description': 'test.on_empty_popup.description',
                        'title': 'test.on_empty_popup.title',
                    },
                    'required': True,
                    'requirement_label': 'test.requirement_label',
                    'selected_label': 'test.selected_label',
                    'phone_selection_screen': {
                        'title': 'test.phone_selection_screen.title',
                        'read_contacts_permission': (
                            'test.phone_selection_screen.'
                            'read_contacts_permission'
                        ),
                        'choose_one_label': (
                            'test.phone_selection_screen.choose_one_label'
                        ),
                    },
                },
            },
            marks=[
                pytest.mark.config(
                    FOR_ANOTHER_OPTIONS_BY_TARIFF={
                        '__default__': {},
                        'econom': {
                            'required': True,
                            'tanker_prefix': 'test',
                            'disabled_by_experiment': 'undefined',
                        },
                    },
                ),
            ],
            id='econom, required',
        ),
        pytest.param(
            {},
            marks=[
                pytest.mark.config(
                    FOR_ANOTHER_OPTIONS_BY_TARIFF={
                        '__default__': {},
                        'econom': {
                            'required': True,
                            'tanker_prefix': 'test',
                            'disabled_by_experiment': 'disabled_phone_rules',
                        },
                    },
                ),
            ],
            id='disabled_by_experiment',
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_disabled_phone_rules.json')
async def test_zoneinfo_extra_phone(taxi_zoneinfo, expected_extra_phones):
    response = await taxi_zoneinfo.post(
        '/v1/zoneinfo/core', headers=PA_HEADERS, json=make_request(),
    )
    assert response.status_code == 200

    data = response.json()
    checked_count = 0
    for tariff in data['max_tariffs']:
        tariff_class = tariff['class']

        if tariff_class not in expected_extra_phones:
            assert 'extra_contact_phone_rules' not in tariff
        else:
            expected_options = expected_extra_phones[tariff_class]
            assert tariff['order_for_other_prohibited']
            assert tariff['extra_contact_phone_rules'] == expected_options
            checked_count += 1

    assert len(expected_extra_phones) == checked_count
