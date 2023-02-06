import copy
import json

import pytest

DEFAULT_HEADERS = {
    'X-Yandex-UID': 'uid_1',
    'X-YaTaxi-PhoneId': 'phone_id_1',
    'X-YaTaxi-UserId': 'user_id_1',
    'X-YaTaxi-Pass-Flags': 'portal,ya-plus',
    'User-Agent': 'android',
    'X-Request-Language': 'ru',
}

DEFAULT_REQUEST = {
    'communications_on_device': [],
    'media_size_info': {
        'screen_height': 1920,
        'screen_width': 1080,
        'scale': 1,
    },
    'state': {'accuracy': 10, 'location': [37, 55]},
    'supported_activate_conditions': [],
    'supported_actions': [],
}

REQUEST_WITH_ORDER = {
    'communications_on_device': [],
    'media_size_info': {
        'screen_height': 1920,
        'screen_width': 1080,
        'scale': 1,
    },
    'state': {'order_id': '34a9e2d883183237bd91e63dbe0151e7'},
    'supported_activate_conditions': [],
    'supported_actions': [],
}


def _get_sorted_stories(response_json):
    return sorted(
        response_json['stories'],
        key=lambda story: story['options']['priority'],
        reverse=True,
    )


@pytest.fixture(name='mock_plus_balances')
def _mock_plus_balances(mockserver):
    @mockserver.json_handler('/plus-wallet/v1/balances')
    def _handler(request):
        return {
            'balances': [
                {
                    'balance': '4771.0000',
                    'currency': 'RUB',
                    'wallet_id': 'wallet_id',
                },
            ],
        }

    return _handler


@pytest.mark.config(COMMUNICATIONS_ENABLED=False)
@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_disable_communications(
        taxi_inapp_communications, mockserver, load_json,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert not response.json()


@pytest.mark.experiments3(filename='exp3_not_fit.json')
async def test_exp3_not_fit(
        taxi_inapp_communications, mockserver, load_json, mock_plus_balances,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_not_fit.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert not response.json()['stories']


@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_dummy_with_experiments(
        taxi_inapp_communications, mockserver, load_json, mock_plus_balances,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert _get_sorted_stories(response.json()) == _get_sorted_stories(
        load_json('communications_response.json'),
    )


@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_diff(
        taxi_inapp_communications, mockserver, load_json, mock_plus_balances,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['communications_on_device'] = ['id1', 'id3']

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        request,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert len(response.json()['stories']) == 1
    assert response.json()['stories'][0]['id'] == 'id2'

    assert len(response.json()['items_to_delete']) == 1
    assert response.json()['items_to_delete'][0]['id'] == 'id3'
    assert (
        response.json()['items_to_delete'][0]['communication_type'] == 'story'
    )


@pytest.mark.experiments3(filename='exp3_with_order_data.json')
async def test_order_data_with_experiments_plus(
        taxi_inapp_communications, mockserver, load_json, mock_plus_balances,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_order_data.json')

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        data = json.loads(request.get_data())
        assert data['order_id'] == '34a9e2d883183237bd91e63dbe0151e7'
        return load_json('order_core_response.json')

    headers = {
        **DEFAULT_HEADERS,
        'X-SDK-Client-ID': 'taxi',
        'X-SDK-Version': '01.00.00',
    }

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        REQUEST_WITH_ORDER,
        headers=headers,
    )
    assert response.status_code == 200
    assert len(response.json()['stories']) == 2


@pytest.mark.pgsql('promotions', files=['promotions_default.sql'])
@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_yql_substitution(
        taxi_inapp_communications, mockserver, load_json, mock_plus_balances,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_yql_data.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert len(response.json()['stories']) == 2
    assert {str(i['id']) for i in response.json()['stories']} == {
        'id1_yql:jdkc',
        'id3_yql',
    }
    for communication in response.json()['stories']:
        if communication['id'] == 'id3_yql':
            assert communication['payload'] == {
                'pages': [
                    {'title': {'color': 'afafaf', 'content': '10.1 ququ'}},
                ],
            }
        else:
            assert communication['payload'] == {
                'pages': [
                    {
                        'backgrounds': [],
                        'title': {
                            'color': 'FFFFFF',
                            'content': 'test field1_data test',
                        },
                        'text': {
                            'color': 'FFFFFF',
                            'content': 'test 100500 test',
                        },
                    },
                ],
            }


@pytest.mark.experiments3(filename='exp3_dummy_time_scheduling.json')
async def test_dummy_with_experiments_time_scheduling(
        taxi_inapp_communications, mockserver, load_json, mock_plus_balances,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert _get_sorted_stories(response.json()) == _get_sorted_stories(
        load_json('communications_response.json'),
    )


@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_incremental_with_rev(
        taxi_inapp_communications, mockserver, load_json, mock_plus_balances,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        if 'created_at_from' in request.args:
            return load_json('promotions_service_response_with_rev_inc.json')

        return load_json('promotions_service_response_with_rev.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert {str(i['id']) for i in response.json()['stories']} == {
        'id1',
        'id2:v1',
        'id3:v1',
    }
    await taxi_inapp_communications.tests_control(
        invalidate_caches=True, clean_update=False,
    )
    request = copy.deepcopy(DEFAULT_REQUEST)
    request['communications_on_device'] = ['id1', 'id2:v1', 'id3:v1']
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        request,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert {str(i['id']) for i in response.json()['stories']} == {'id2:v2'}
    assert {str(i['id']) for i in response.json()['items_to_delete']} == {
        'id2:v1',
    }


@pytest.mark.experiments3(filename='exp3_kwarg_uid_type.json')
@pytest.mark.parametrize(
    'pass_flags, resp_ids',
    [('portal', ['id1']), ('phonish', ['id2']), ('', [])],
)
async def test_experiments_kwarg_uid_type(
        taxi_inapp_communications,
        mockserver,
        load_json,
        mock_plus_balances,
        pass_flags,
        resp_ids,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    headers = DEFAULT_HEADERS
    headers['X-YaTaxi-Pass-Flags'] = pass_flags
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        DEFAULT_REQUEST,
        headers=headers,
    )
    assert response.status_code == 200
    assert len(response.json()['stories']) == len(resp_ids)
    for commun in response.json()['stories']:
        assert commun['id'] in resp_ids


@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_sorted_stories_by_priority(
        taxi_inapp_communications, mockserver, load_json, mock_plus_balances,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_stories.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['stories'] == _get_sorted_stories(
        load_json('communications_stories_response.json'),
    )


@pytest.mark.experiments3(filename='exp3_dummy.json')
@pytest.mark.parametrize(
    'activation_screens, is_random_order',
    [
        (['test_house_of_plus'], True),
        (['test_house_of_plus', 'some_screen'], False),
    ],
)
async def test_random_stories(
        taxi_inapp_communications,
        mockserver,
        load_json,
        mock_plus_balances,
        activation_screens,
        is_random_order,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        responses = load_json('promotions_service_response_stories.json')
        for story in responses['stories']:
            if story['id'] != 'id3':
                story['options']['activate_condition'] = {
                    'screen': activation_screens,
                }
        return responses

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    if is_random_order:
        assert len(response.json()['stories']) == len(
            _get_sorted_stories(
                load_json('communications_stories_response.json'),
            ),
        )
    else:
        target_stories = _get_sorted_stories(
            load_json('communications_stories_response.json'),
        )
        for story in target_stories:
            story['options']['activate_condition'] = {
                'screens': activation_screens,
            }
        assert response.json()['stories'] == target_stories


@pytest.mark.pgsql('promotions', files=['promotions_default.sql'])
@pytest.mark.experiments3(filename='exp3_dummy.json')
@pytest.mark.translations(
    backend_promotions={
        'key1': {
            'ru': 'key1_translation {field1}',
            'en': 'key1_translation_en {field1}',
        },
    },
)
@pytest.mark.config(INAPP_FEEDS_CONTROL={'enabled': True})
async def test_feeds_integration(
        taxi_inapp_communications, mockserver, load_json, mock_plus_balances,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_yql_data.json')

    @mockserver.json_handler('/feeds/v1/fetch')
    def _mock_feeds(request):
        return load_json('feeds_stories.json')

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        json=DEFAULT_REQUEST,
        headers=DEFAULT_HEADERS,
    )

    assert _mock_feeds.times_called == 1
    assert response.status == 200
    stories = {
        (story['id'], story['options'].get('priority'))
        for story in response.json()['stories']
    }

    # Story id1_yql is from feeds, it overwrites story id1_yql:jdkc'
    # from promotions cache and has different priority (1001 instead of 1).
    # Story id3_yql is from promotions cache.
    assert stories == {('id1_yql', 1001), ('id3_yql', 1)}


@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_anonymous_user(
        taxi_inapp_communications, mockserver, load_json, mock_plus_balances,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_service_response_stories.json')

    headers = {
        # no homo, no yandex_uid and other uids
        'User-Agent': 'android',
        'X-Request-Language': 'ru',
    }

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        DEFAULT_REQUEST,
        headers=headers,
    )
    assert response.status == 200

    stories = {story['id'] for story in response.json()['stories']}
    assert stories == {'id1', 'id2'}
    assert mock_plus_balances.times_called == 0


@pytest.mark.parametrize('is_extended_request', [(True,), (False,)])
@pytest.mark.experiments3(filename='exp3_communications_subscription_id.json')
async def test_subscription_id(
        taxi_inapp_communications,
        experiments3,
        mockserver,
        load_json,
        mock_plus_balances,
        is_extended_request,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('default_promotions_service_response.json')

    request = copy.deepcopy(DEFAULT_REQUEST)
    if is_extended_request:
        request.update(
            {
                'plus_subscription_info': {
                    'available_subscription_id': 'testing_subscription_id',
                },
            },
        )
    exp_name = 'subscription_id_testing'
    api_url = '/4.0/inapp-communications/communications'

    exp3_recorder = experiments3.record_match_tries(exp_name)

    await taxi_inapp_communications.post(
        api_url, json=request, headers=DEFAULT_HEADERS,
    )

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    if is_extended_request:
        match_tries[0].ensure_matched_with_clause('test_match_subscription_id')
    else:
        match_tries[0].ensure_no_match()


@pytest.mark.parametrize('bank_account', [True, False])
@pytest.mark.experiments3(filename='exp3_bank_account.json')
async def test_bank_account(
        taxi_inapp_communications,
        bank_account,
        mockserver,
        load_json,
        mock_plus_balances,
):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return load_json('promotions_response_for_test_publish.json')

    headers = copy.deepcopy(DEFAULT_HEADERS)
    if bank_account:
        headers['X-YaTaxi-Pass-Flags'] = 'bank-account'
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/communications',
        json=DEFAULT_REQUEST,
        headers=headers,
    )

    assert response.status == 200, response.text
    promos = response.json().get('stories', [])
    assert len(promos) == (1 if bank_account else 0)
