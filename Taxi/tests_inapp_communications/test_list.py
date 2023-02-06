import copy
import itertools

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
DEFAULT_DATA = {'size_hint': 320, 'banners_seen': ['123', '456']}


@pytest.mark.experiments3(filename='exp3_default.json')
async def test_promotions_list(
        taxi_inapp_communications,
        mockserver,
        load_json,
        _communications_audience,
        _user_api,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response.json')

    _communications_audience([])
    _user_api()

    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/list', json=DEFAULT_DATA, headers=DEFAULT_HEADERS,
    )

    assert response.status == 200, response.text
    body = response.json()

    assert len(body['fullscreen_banners']) == 2
    assert len(body['cards']) == 1
    assert len(body['notifications']) == 1

    promos = [body['fullscreen_banners'], body['cards'], body['notifications']]
    for item in itertools.chain(*promos):
        assert item == load_json('inapp_list_dummy.json')[item['id']]

    assert body['typed_experiments']['items'] == [
        {'name': 'typed_exp_yandex_uid', 'value': {'enabled': True}},
        {'name': 'typed_exp_2', 'value': {'enabled': True}},
    ]


@pytest.mark.experiments3(filename='exp3_backend_only.json')
async def test_exp3_check(
        taxi_inapp_communications,
        mockserver,
        load_json,
        _communications_audience,
        _user_api,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_exp3_check.json')

    _communications_audience([])
    _user_api()

    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/list', json=DEFAULT_DATA, headers=DEFAULT_HEADERS,
    )

    assert response.status == 200, response.text
    assert len(response.json()['fullscreen_banners']) == 1


@pytest.mark.parametrize(
    'phone_id, is_in_test',
    [('phone_id_1', True), ('phone_id_not_in_test_publish', False)],
)
@pytest.mark.experiments3(filename='exp3_test_publish.json')
async def test_test_publish(
        taxi_inapp_communications,
        phone_id,
        is_in_test,
        mockserver,
        load_json,
        _communications_audience,
        _user_api,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    _communications_audience([])
    _user_api()

    headers = copy.deepcopy(DEFAULT_HEADERS)
    headers['X-YaTaxi-PhoneId'] = phone_id
    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/list', json=DEFAULT_DATA, headers=headers,
    )

    assert response.status == 200, response.text
    fs_banners = response.json()['fullscreen_banners']
    assert len(fs_banners) == (1 if is_in_test else 0)


@pytest.mark.pgsql('promotions', files=['pg_promotions.sql'])
@pytest.mark.experiments3(filename='exp3_default.json')
async def test_yql_publish(
        taxi_inapp_communications,
        mockserver,
        load_json,
        _communications_audience,
        _user_api,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_yql_data.json')

    _communications_audience([])
    _user_api()

    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/list', json=DEFAULT_DATA, headers=DEFAULT_HEADERS,
    )

    assert response.status == 200, response.text
    banners = response.json()['fullscreen_banners']
    assert {
        str(banner['id']) for banner in response.json()['fullscreen_banners']
    } == {'id_yql_without_exp', 'id_yql_matching_exp'}
    assert (
        banners[0]['pages'][0]['title']['content']
        == 'field1_data and field2_data testing'
    )


@pytest.mark.parametrize(
    'campaigns_response, communications_audience_enabled, expected',
    [
        pytest.param(
            ['test_campaign_id_2'], True, 2, id='no_fullscreens_matched',
        ),
        pytest.param(
            ['test_campaign_id_1'], True, 3, id='one_fullsreen_matched',
        ),
        pytest.param(
            ['test_campaign_id_1'],
            False,
            2,
            id='communications_audience_disabled',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_default.json')
@pytest.mark.now('2022-03-01T12:00:00+0000')
async def test_promotions_list_campaigns(
        campaigns_response,
        communications_audience_enabled,
        expected,
        taxi_inapp_communications,
        mockserver,
        load_json,
        taxi_config,
        _communications_audience,
        _user_api,
):
    taxi_config.set_values(
        {
            'INAPP_ENABLE_COMMUNICATIONS_AUDIENCE': (
                communications_audience_enabled
            ),
        },
    )

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_campaigns.json')

    _communications_audience(campaigns_response)
    _user_api('test_id')

    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/list', json=DEFAULT_DATA, headers=DEFAULT_HEADERS,
    )

    assert response.status == 200, response.text
    body = response.json()

    assert len(body['fullscreen_banners']) == expected


@pytest.mark.now('2022-03-01T12:00:00+0000')
async def test_promotions_list_match_all_by_campaign(
        taxi_inapp_communications,
        mockserver,
        load_json,
        _communications_audience,
        _user_api,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_all_types_by_campaign.json')

    _communications_audience(['test_campaign_id_1'])
    _user_api('test_id')

    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/list', json=DEFAULT_DATA, headers=DEFAULT_HEADERS,
    )

    assert response.status == 200, response.text
    body = response.json()

    assert len(body['fullscreen_banners']) == 1
    assert len(body['cards']) == 1
    assert len(body['notifications']) == 1


@pytest.mark.parametrize('bank_account', [True, False])
@pytest.mark.experiments3(filename='exp3_bank_account.json')
async def test_bank_account(
        taxi_inapp_communications,
        bank_account,
        mockserver,
        load_json,
        _communications_audience,
        _user_api,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    _communications_audience([])
    _user_api()

    headers = copy.deepcopy(DEFAULT_HEADERS)
    if bank_account:
        headers['X-YaTaxi-Pass-Flags'] = 'bank-account'
    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/list', json=DEFAULT_DATA, headers=headers,
    )

    assert response.status == 200, response.text
    promos = response.json()['fullscreen_banners']
    assert len(promos) == (1 if bank_account else 0)


@pytest.mark.experiments3(filename='exp3_default.json')
@pytest.mark.now('2022-05-04T12:00:00+0000')
async def test_promotions_list_test_campaigns(
        taxi_inapp_communications,
        mockserver,
        load_json,
        _communications_audience,
        _user_api,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_show_policy.json')

    _communications_audience(['test_campaign_id_1', 'test_campaign_id_4'])
    _user_api('test_id')

    response = await taxi_inapp_communications.post(
        '/4.0/promotions/v1/list', json=DEFAULT_DATA, headers=DEFAULT_HEADERS,
    )

    assert response.status == 200, response.text
    body = response.json()

    assert len(body['fullscreen_banners']) == 3

    assert 'show_policy' not in body['fullscreen_banners'][0]

    assert body['fullscreen_banners'][1]['show_policy'] == {
        'id': '987654321',
        'max_show_count': 5,
    }

    assert body['fullscreen_banners'][2]['show_policy'] == {
        'id': '123456789',
        'max_show_count': 5,
    }
