import copy

import pytest

DEFAULT_HEADERS = {
    'X-Yandex-UID': '1234567890',
    'X-YaTaxi-UserId': 'test_user_id',
    'X-YaTaxi-PhoneId': 'test_phone_id',
    'User-Agent': (
        'yandex-taxi/3.107.0.dev_sergu_b18dbfd* Android/6.0.1 (LGE; Nexus 5)'
    ),
    'X-Request-Application': (
        'app_name=android,app_brand=yataxi,app_ver1=1,app_ver2=2,app_ver3=3'
    ),
    'X-Request-Language': 'ru',
}
DEFAULT_DATA = {'size_hint': 320}
DEFAULT_IMAGE_SIZE_HINT_CONF = {
    128: {'scale': 1, 'screen_height': 1334, 'screen_width': 750},
    320: {'scale': 2, 'screen_height': 480, 'screen_width': 320},
    640: {'scale': 3, 'screen_height': 1920, 'screen_width': 1080},
}


@pytest.mark.parametrize(
    ['promotion_id', 'code', 'fail_reason'],
    [
        ('id_bad_notification_no_translation', 500, 'not_build'),
        ('id_bad_card_no_yql', 500, 'not_build'),
        ('id_story1', 500, 'not_build'),
        ('id_missing', 404, 'not_found'),
    ],
)
async def test_failures(
        taxi_inapp_communications,
        mockserver,
        load_json,
        promotion_id,
        code,
        fail_reason,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response.json')

    data = copy.deepcopy(DEFAULT_DATA)
    data['promotion_id'] = promotion_id
    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/promotion/retrieve',
        json=data,
        headers=DEFAULT_HEADERS,
    )

    assert response.status == code
    assert response.json()['code'] == fail_reason


@pytest.mark.parametrize(
    'promotion_id',
    [
        # here should return id_fs_ok_test_all_fields:v2,
        # newer version, but with old id
        'id_fs_ok_test_all_fields:v1',
        'id_card_ok:v1',
        'id_notification_ok',
        'id_story_ok:v1',
    ],
)
async def test_200(
        taxi_inapp_communications, mockserver, load_json, promotion_id,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response.json')

    data = copy.deepcopy(DEFAULT_DATA)
    data['promotion_id'] = promotion_id
    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/promotion/retrieve',
        json=data,
        headers=DEFAULT_HEADERS,
    )

    assert response.status == 200
    body = response.json()
    assert body == load_json('inapp_retrieve_dummy.json')[promotion_id]


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
    INAPP_YQL_VARIABLES_L10N_TEMPLATES={
        'l10n_field': 'l10n_field_{}_key',
        'l10n_field2': 'l10n_field_{}_{}_key',
        'l10n_field3': 'missing_key_{}',
        'trips': '10_years_trips',
        'times': '10_years_times',
    },
)
@pytest.mark.pgsql('promotions', files=['promotions_default.sql'])
@pytest.mark.translations(
    backend_promotions={
        'key_attr_text': {'ru': '<bold>alt_title</bold> {field1}'},
        'key_attr_text_no_arg': {'ru': '<bold>alt_title</bold>'},
        'key2': {'ru': 'key2_translation', 'en': 'key2_translation_en'},
        'key1': {
            'ru': 'key1_translation {field1}',
            'en': 'key1_translation_en {field1}',
        },
        'l10n_field_10_key': {'ru': 'октябрь', 'en': 'october'},
    },
)
@pytest.mark.parametrize(
    'promotion_id, filename, status',
    [
        pytest.param(
            'id1_yql:v1',
            'inapp_retrieve_yql_and_translation.json',
            200,
            id='no attr text, only yql and tanker',
        ),
        pytest.param(
            'id_yql_AT:v2',
            'inapp_retrieve_AT_and_yql_and_translation.json',
            200,
            id='all the types of substitutions',
        ),
        pytest.param(
            'id_AT:v2',
            'inapp_retrieve_AT_and_translation.json',
            200,
            id='no yql data in attr text substitution',
        ),
        pytest.param(
            'id_yql_var_l10n:v2',
            'inapp_retrieve_yql_var_l10n.json',
            200,
            id='yql data localization',
        ),
        pytest.param(
            'id_yql_var_l10n_invalid_template:v2',
            'inapp_retrieve_yql_var_l10n_invalid_template.json',
            500,
            id='yql data localization: invalid template',
        ),
        pytest.param(
            'id_yql_var_l10n_no_l10n:v2',
            None,
            500,
            id='yql data localization: no l10n',
        ),
        pytest.param(
            'id_yql_var_l10n_plural:v2',
            'inapp_retrieve_yql_var_l10n_plural.json',
            200,
            id='yql data localization: plural variable',
        ),
        pytest.param(
            'id_yql_var_l10n_plural_invalid_plural:v2',
            None,
            500,
            id='yql data localization: plural variable with invalid plural',
        ),
        pytest.param(
            'id_yql_var_l10n_no_template_for_plural:v2',
            None,
            500,
            id='yql data localization: plural variable with no template',
        ),
        pytest.param(
            'id_yql_var_l10n_no_l10n_for_plural:v2',
            None,
            500,
            id='yql data localization: plural variable with no l10n',
        ),
        pytest.param(
            'id_yql_var_locale_parametrization:v2',
            'inapp_retrieve_yql_var_locale_parametrization.json',
            200,
            id='yql data locale parametrization',
        ),
        pytest.param(
            'id_yql_AT_no_data:v2',
            None,
            500,
            id='no neccessary yql data for promotion',
        ),
    ],
)
async def test_promotions_personalization(
        taxi_inapp_communications,
        mockserver,
        load_json,
        promotion_id,
        filename,
        status,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_personalization.json')

    data = copy.deepcopy(DEFAULT_DATA)
    data['promotion_id'] = promotion_id
    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/promotion/retrieve',
        json=data,
        headers=DEFAULT_HEADERS,
    )

    assert response.status == status
    if status == 200:
        body = response.json()
        assert body == load_json(filename)


@pytest.mark.pgsql('promotions', files=['pg_promotions.sql'])
@pytest.mark.parametrize('has_yql_data', [True, False])
async def test_yql(
        taxi_inapp_communications, mockserver, load_json, has_yql_data,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        result = load_json('promotions_service_response_yql.json')
        result['stories'][0]['options']['has_yql_data'] = has_yql_data
        return result

    data = copy.deepcopy(DEFAULT_DATA)
    data['promotion_id'] = 'id_story_yql:v1'
    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/promotion/retrieve',
        json=data,
        headers=DEFAULT_HEADERS,
    )

    if has_yql_data:
        assert response.status == 200, response.text
        assert response.json() == load_json('inapp_retrieve_story_yql.json')
    else:
        assert response.status == 500
        assert response.json()['code'] == 'not_build'


@pytest.mark.parametrize(
    'status_code,min_pages_amount,pages_requirements',
    [(200, 1, [True, False]), (500, 2, [True, False]), (500, 1, [True, True])],
)
@pytest.mark.pgsql('promotions', files=['pg_promotions.sql'])
async def test_story_invalid_pages(
        taxi_inapp_communications,
        mockserver,
        load_json,
        status_code,
        min_pages_amount,
        pages_requirements,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        result = load_json('promotions_service_response_yql.json')
        result['stories'][0]['payload']['pages'][0]['text'][
            'content'
        ] = 'abc {null_key} def'
        # allow story to build with no pages
        result['stories'][0]['payload']['min_pages_amount'] = 0
        result = load_json(
            'promotions_service_response_invalid_pages_building.json',
        )
        result['stories'][0]['payload']['min_pages_amount'] = min_pages_amount
        for page, requirement in zip(
                result['stories'][0]['payload']['pages'], pages_requirements,
        ):
            page['required'] = requirement
        return result

    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/promotion/retrieve',
        json={**DEFAULT_DATA, 'promotion_id': 'id_story_yql:v1'},
        headers=DEFAULT_HEADERS,
    )

    assert response.status == status_code
    if status_code == 200:
        expected_json = load_json('inapp_retrieve_story_yql.json')
        assert response.json() == expected_json


@pytest.mark.parametrize(
    'promotion_id', ['id_fs:v1', 'id_card:v1', 'id_story_2:v1'],
)
async def test_promotions_mediatag(
        taxi_inapp_communications, mockserver, load_json, promotion_id,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_image_tag.json')

    data = copy.deepcopy(DEFAULT_DATA)
    data['promotion_id'] = promotion_id
    data['media_size_info'] = {
        'scale': 1,
        'screen_height': 480,
        'screen_width': 320,
    }
    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/promotion/retrieve',
        json=data,
        headers=DEFAULT_HEADERS,
    )

    assert response.status == 200
    body = response.json()
    assert body == load_json('inapp_retrieve_dummy.json')[promotion_id]


@pytest.mark.parametrize('size_hint', [310, 320, 1000])
@pytest.mark.config(
    INAPP_IMAGE_SIZE_HINT_TO_SCREEN_INFO=DEFAULT_IMAGE_SIZE_HINT_CONF,
)
async def test_promotions_mediatag_sizehint(
        taxi_inapp_communications, mockserver, load_json, size_hint,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_image_tag.json')

    data = copy.deepcopy(DEFAULT_DATA)
    data['promotion_id'] = 'id_card:v1'
    data['size_hint'] = size_hint
    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/promotion/retrieve',
        json=data,
        headers=DEFAULT_HEADERS,
    )

    assert response.status == 200
    body = response.json()

    if size_hint <= 320:
        assert body['image'] == 'some_image-scale2'
    else:
        assert body['image'] == 'some_image-scale3'
