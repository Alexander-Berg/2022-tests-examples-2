import pytest

URL = '/v1/tariff_settings/copy/draft/check'


def _check_data(data, request_body):
    assert data['zone_from'] == request_body['zone_from']
    expected_can_be_copied = set()
    for zone in request_body['zones_to']:
        expected_can_be_copied.add(
            (zone, frozenset(request_body.get('categories_to_copy', []))),
        )
    data_can_be_copied = set()
    for zone_obj in data['can_be_copied_zones']:
        data_can_be_copied.add(
            (zone_obj['zone_name'], frozenset(zone_obj['categories_to_copy'])),
        )
    assert expected_can_be_copied == data_can_be_copied
    assert (
        bool(request_body.get('copy_zone_settings'))
        == data['copy_zone_settings']
    )
    assert (
        bool(request_body.get('copy_categories_common'))
        == data['copy_categories_common']
    )


def _check_lock_ids(lock_ids, zones):
    input_set = set((lock_id['id'], lock_id['custom']) for lock_id in lock_ids)
    expected_set = set()
    for zone in zones:
        expected_set.add((f'{zone}:set_tariff_settings', True))
    assert input_set == expected_set


def _check_change_doc_id(change_doc_id, zones):
    expected_id = ':'.join(zones) + ':copy_tariff_settings'
    assert change_doc_id == expected_id


def _check_diff(diff, zones_to, categories_to_copy):
    missing_zones = set(zones_to)
    current_docs = diff['current']['tariff_settings_docs']
    new_docs = diff['new']['tariff_settings_docs']
    for current_doc, new_doc in zip(current_docs, new_docs):
        assert current_doc['home_zone'] == new_doc['home_zone']
        missing_zones.remove(current_doc['home_zone'])
        # check zone settings
        assert new_doc['client_exact_order_round_minutes'] == 3
        assert new_doc['max_route_points_count'] == 4
        assert 'fixed_price_max_allowed_distance' not in new_doc
        # check categories common
        assert new_doc['discount'] == 3
        assert 'extra_charge' not in new_doc
        assert 'not_for_copy_field' not in new_doc
        missing_categories = set(categories_to_copy)
        # check categories
        for category in new_doc['categories']:
            missing_categories.remove(category['name'])
            assert category['tanker_key'] == category['name'] + '_tanker_key'
            assert category['max_route_points_count'] == 4

            assert 'free_cancel_timeout' not in category
            assert 'not_for_copy_field' not in category
            # check outer category settings
            if category['name'] == 'econom':
                assert (
                    new_doc['hide_dest_for_driver_by_class']['econom'] is False
                )
                assert new_doc['surge_ratio_upgrade']['econom'] == (
                    {
                        'surge_ratio': [1.5, 'courier'],
                        'price_ratio': [2.5, 'courier'],
                    }
                )
                assert new_doc['surge_tariff_class_upgrades']['econom'] == (
                    [3.5, 'courier']
                )
            elif category['name'] == 'courier':
                assert (
                    'courier' not in new_doc['hide_dest_for_driver_by_class']
                )
                assert 'courier' not in new_doc['surge_ratio_upgrade']
                assert 'courier' not in new_doc['surge_tariff_class_upgrades']
        assert not missing_categories, current_doc['home_zone']
    assert not missing_zones


pytestmark = pytest.mark.config(  # pylint: disable=invalid-name
    TARIFF_SETTINGS_COPY_FIELDS={
        'zone': {
            'required': ['client_exact_order_round_minutes'],
            'not_required': [
                'max_route_points_count',
                'fixed_price_max_allowed_distance',
            ],
        },
        'categories_common': {
            'required': [],
            'not_required': ['discount', 'extra_charge'],
        },
        'category': {
            'required': [
                't',
                'n',
                'r',
                'd',
                'oso',
                'sl',
                'cc',
                'persistent_reqs',
                'client_requirements',
            ],
            'not_required': ['mrpc', 'fct'],
        },
        'outer_category_settings': [
            'hide_dest_for_driver_by_class',
            'surge_tariff_class_upgrades',
            'surge_ratio_upgrade',
        ],
    },
)


@pytest.mark.parametrize(
    'request_body',
    (
        pytest.param(
            {
                'zone_from': 'source',
                'zones_to': ['destination1', 'destination2'],
                'categories_to_copy': ['econom', 'courier'],
                'copy_zone_settings': True,
                'copy_categories_common': True,
            },
            id=(
                'Copy only zone settings and'
                ' categories common fields in two zones'
            ),
        ),
    ),
)
async def test_normal_work(web_app_client, mongo, request_body):
    response = await web_app_client.post(URL, json=request_body)
    assert response.status == 200
    content = await response.json()
    data = content['data']
    _check_data(data, request_body)
    zones_for_ids = [request_body['zone_from'], *request_body['zones_to']]
    _check_change_doc_id(content['change_doc_id'], zones_for_ids)
    _check_lock_ids(content['lock_ids'], zones_for_ids)
    _check_diff(
        content['diff'],
        request_body['zones_to'],
        request_body['categories_to_copy'],
    )


@pytest.mark.parametrize(
    ('request_body', 'response_code', 'response_message'),
    (
        (
            {'zone_from': 'source', 'zones_to': ['destination1']},
            'empty_request',
            (
                'Should be copy_zone_settings:true or/and '
                'copy_categories_common:true or/and '
                'categories_to_copy has one or more items'
            ),
        ),
        (
            {
                'zone_from': 'wrong_source',
                'zones_to': ['destination1'],
                'copy_zone_settings': True,
            },
            'not_source_document',
            'tariff_settings document for zone_from was not found',
        ),
        (
            {
                'zone_from': 'source',
                'zones_to': ['destination1'],
                'copy_zone_settings': True,
                'categories_to_copy': ['econom', 'courier', 'express'],
            },
            'not_source_categories',
            (
                'In tariff_settings for zone_from '
                'there are not categories: express'
            ),
        ),
        (
            {
                'zone_from': 'without_requariment_fields',
                'zones_to': ['destination1'],
                'copy_zone_settings': True,
            },
            'no_required_field',
            (
                'No required field client_exact_order_round_minutes '
                'in source zone'
            ),
        ),
        (
            {
                'zone_from': 'source',
                'zones_to': ['wrong_destination'],
                'copy_zone_settings': True,
            },
            'cannot_copy',
            'Nothing can be copied',
        ),
        (
            {
                'zone_from': 'source',
                'zones_to': ['destination1'],
                'categories_to_copy': ['comfort'],
            },
            'cannot_copy',
            'Nothing can be copied',
        ),
        (
            {
                'zone_from': 'source',
                'zones_to': ['destination1', 'destination1'],
                'copy_zone_settings': True,
            },
            'duplicate_zones',
            'Duplicate of zones to which it is copied',
        ),
        (
            {
                'zone_from': 'source',
                'zones_to': ['destination1'],
                'copy_zone_settings': True,
                'categories_to_copy': ['econom', 'courier', 'econom'],
            },
            'duplicate_categories',
            'categories_to_copy has duplicate items',
        ),
        (
            {
                'zone_from': 'source',
                'zones_to': ['source'],
                'copy_zone_settings': True,
            },
            'copy_to_itself',
            'Attempt to copy a zone to itself',
        ),
    ),
)
async def test_fail(
        web_app_client, request_body, response_code, response_message,
):
    response = await web_app_client.post(URL, json=request_body)
    assert response.status == 400
    content = await response.json()
    assert content['code'] == response_code
    assert content['message'] == response_message


@pytest.mark.parametrize(
    ('request_body', 'message_titile', 'message_detailes'),
    (
        pytest.param(
            {
                'zone_from': 'source',
                'zones_to': ['destination1', 'some_zone'],
                'copy_zone_settings': True,
            },
            'Some objects cannot be copied',
            [
                {
                    'message': 'tariff_settings was not found',
                    'zone_name': 'some_zone',
                },
            ],
            id='Not tariff_setting for some_zone',
        ),
        pytest.param(
            {
                'zone_from': 'source',
                'zones_to': ['destination_without_tariff'],
                'copy_zone_settings': True,
                'categories_to_copy': ['econom'],
            },
            'Some objects cannot be copied',
            [
                {
                    'message': 'tariff was not found',
                    'zone_name': 'destination_without_tariff',
                },
            ],
            id='Not tariff for some_zone',
        ),
    ),
)
async def test_partial_success(
        web_app_client, request_body, message_titile, message_detailes,
):
    response = await web_app_client.post(URL, json=request_body)
    assert response.status == 200
    content = await response.json()
    data = content['data']
    assert data['message']['title'] == message_titile
    assert data['message']['details'] == message_detailes
    zones_for_ids = ['source', request_body['zones_to'][0]]
    _check_change_doc_id(content['change_doc_id'], zones_for_ids)
    _check_lock_ids(content['lock_ids'], zones_for_ids)


async def test_integration_data_format(web_app_client):
    check_request_body = {
        'zone_from': 'source',
        'zones_to': ['destination0', 'destination1'],
        'copy_zone_settings': True,
        'copy_categories_common': True,
        'categories_to_copy': ['econom', 'courier', 'comfort'],
    }
    check_response = await web_app_client.post(URL, json=check_request_body)
    assert check_response.status == 200

    content = await check_response.json()
    apply_request_body = content['data']
    apply_url = '/v1/tariff_settings/copy/draft/apply'
    apply_response = await web_app_client.post(
        apply_url, json=apply_request_body,
    )
    assert apply_response.status == 200
    content = await apply_response.json()
    assert content['status'] == 'succeeded'


async def test_requirements_in_tariff(web_app_client):
    request_body = {
        'zone_from': 'source',
        'zones_to': ['without_requariments_in_tariff'],
        'categories_to_copy': ['econom', 'courier'],
        'copy_zone_settings': True,
    }
    response = await web_app_client.post(URL, json=request_body)
    assert response.status == 200
    content = await response.json()
    data = content['data']
    assert data['message']['details'] == [
        {
            'message': (
                'For category econom in some intervals in tariff '
                'there are no requriments: animaltransport'
            ),
            'zone_name': 'without_requariments_in_tariff',
        },
    ]
    assert data['can_be_copied_zones'] == [
        {
            'zone_name': 'without_requariments_in_tariff',
            'categories_to_copy': ['courier'],
        },
    ]
