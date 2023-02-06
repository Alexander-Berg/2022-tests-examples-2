import copy

import pytest


from testsuite.utils import ordered_object


DEFAULT_RULE_NAME = 'some_name'
DEFAULT_CONFIG = {
    'enabled': True,
    'limit': 1000,
    'rule_name': DEFAULT_RULE_NAME,
    'period_seconds': 3600,
}
DEFAULT_TRANSLATIONS = {
    'tanker_key_both': {'en': 'En and ru', 'ru': 'Английский и русский'},
    'tanker_key_en_only': {'en': 'En only', 'ru': ''},
    'tanker_key_ru_only': {'ru': 'Только русский', 'en': ''},
    'tanker_key_fr_only': {'fr': '123', 'ru': '', 'en': ''},
}


@pytest.mark.translations(virtual_catalog=DEFAULT_TRANSLATIONS)
@pytest.mark.config(GROCERY_PRODUCTS_LOCALIZATION_REPLICATION=DEFAULT_CONFIG)
@pytest.mark.suspend_periodic_tasks('localization-replication-periodic')
@pytest.mark.now('2021-05-24T13:29:24.653875123+00:00')
async def test_basic_replication(
        taxi_grocery_products, mockserver, now, testpoint,
):
    """ Periodic task send virtual_catalog keyset
    en and ru localizations to replication service """

    @mockserver.json_handler('/replication/data/' + DEFAULT_RULE_NAME)
    def mock_replication(request):
        request_items = request.json['items']

        expected = [
            {
                'data': {
                    'en': '',
                    'key': 'tanker_key_fr_only',
                    'ru': '',
                    'updated': now.isoformat() + '+00:00',
                },
                'id': 'tanker_key_fr_only',
            },
            {
                'data': {
                    'en': 'Только русский',
                    'key': 'tanker_key_ru_only',
                    'ru': 'Только русский',
                    'updated': now.isoformat() + '+00:00',
                },
                'id': 'tanker_key_ru_only',
            },
            {
                'data': {
                    'en': 'En and ru',
                    'key': 'tanker_key_both',
                    'ru': 'Английский и русский',
                    'updated': now.isoformat() + '+00:00',
                },
                'id': 'tanker_key_both',
            },
            {
                'data': {
                    'en': 'En only',
                    'key': 'tanker_key_en_only',
                    'ru': '',
                    'updated': now.isoformat() + '+00:00',
                },
                'id': 'tanker_key_en_only',
            },
        ]

        ordered_object.assert_eq(request_items, expected, [''])
        response_items = []
        for item in request_items:
            response_items.append({'id': item['id'], 'status': 'ok'})
        return {'items': response_items}

    @testpoint('localization-replication-end')
    def testpoint_logs(data):
        assert data['items_put_ctr'] == len(DEFAULT_TRANSLATIONS)
        assert data['total_items'] == len(DEFAULT_TRANSLATIONS)

    await taxi_grocery_products.invalidate_caches()
    await taxi_grocery_products.run_periodic_task(
        'localization-replication-periodic',
    )
    assert mock_replication.times_called == 1
    assert testpoint_logs.has_calls is True


@pytest.mark.translations(virtual_catalog=DEFAULT_TRANSLATIONS)
@pytest.mark.suspend_periodic_tasks('localization-replication-periodic')
async def test_replication_data_split(
        taxi_grocery_products, mockserver, taxi_config, testpoint,
):
    """ Limit from config is used to split data into chunks """

    replication_config = copy.deepcopy(DEFAULT_CONFIG)
    replication_config['limit'] = 3
    taxi_config.set(
        GROCERY_PRODUCTS_LOCALIZATION_REPLICATION=replication_config,
    )

    items_in_request = []
    expected_item_in_request = [3, 1]

    @mockserver.json_handler('/replication/data/' + DEFAULT_RULE_NAME)
    def mock_replication(request):
        request_items = request.json['items']
        items_in_request.append(len(request_items))
        response_items = []
        for item in request_items:
            response_items.append({'id': item['id'], 'status': 'ok'})
        return {'items': response_items}

    @testpoint('localization-replication-end')
    def testpoint_logs(data):
        assert data['items_put_ctr'] == len(DEFAULT_TRANSLATIONS)
        assert data['total_items'] == len(DEFAULT_TRANSLATIONS)

    await taxi_grocery_products.invalidate_caches()
    await taxi_grocery_products.run_periodic_task(
        'localization-replication-periodic',
    )
    assert mock_replication.times_called == len(expected_item_in_request)
    assert items_in_request == expected_item_in_request
    assert testpoint_logs.has_calls is True


@pytest.mark.translations(virtual_catalog=DEFAULT_TRANSLATIONS)
@pytest.mark.suspend_periodic_tasks('localization-replication-periodic')
async def test_replication_disabled(
        taxi_grocery_products, mockserver, taxi_config,
):
    """ There is no replication service calls when
    replication is disabled by config """

    replication_config = copy.deepcopy(DEFAULT_CONFIG)
    replication_config['enabled'] = False
    taxi_config.set(
        GROCERY_PRODUCTS_LOCALIZATION_REPLICATION=replication_config,
    )

    @mockserver.json_handler('/replication/data/' + DEFAULT_RULE_NAME)
    def mock_replication(request):
        pass

    await taxi_grocery_products.invalidate_caches()
    await taxi_grocery_products.run_periodic_task(
        'localization-replication-periodic',
    )
    assert mock_replication.has_calls is False


@pytest.mark.translations(virtual_catalog=DEFAULT_TRANSLATIONS)
@pytest.mark.config(GROCERY_PRODUCTS_LOCALIZATION_REPLICATION=DEFAULT_CONFIG)
@pytest.mark.suspend_periodic_tasks('localization-replication-periodic')
async def test_replication_500(
        taxi_grocery_products, mockserver, testpoint, taxi_config,
):
    """ Nothing should happen when replication service
    is unavailable """

    @mockserver.json_handler('/replication/data/' + DEFAULT_RULE_NAME)
    def mock_replication(request):
        return mockserver.make_response('some error', 500)

    @testpoint('localization-replication-end')
    def testpoint_logs(data):
        assert data['items_put_ctr'] == 0
        assert data['total_items'] == len(DEFAULT_TRANSLATIONS)

    await taxi_grocery_products.invalidate_caches()
    await taxi_grocery_products.run_periodic_task(
        'localization-replication-periodic',
    )

    assert mock_replication.has_calls is True
    assert testpoint_logs.has_calls is True


@pytest.mark.translations(
    virtual_catalog={
        'tanker_key_ok': {'en': 'en_ok', 'ru': 'ru_ok'},
        'tanker_key_error': {'en': 'en_err', 'ru': 'ru_err'},
    },
)
@pytest.mark.config(GROCERY_PRODUCTS_LOCALIZATION_REPLICATION=DEFAULT_CONFIG)
@pytest.mark.suspend_periodic_tasks('localization-replication-periodic')
async def test_replication_errors(
        taxi_grocery_products, mockserver, testpoint, taxi_config,
):
    """ Errors from replication service are correctly processed """

    @mockserver.json_handler('/replication/data/' + DEFAULT_RULE_NAME)
    def mock_replication(request):
        return {
            'items': [
                {'id': 'tanker_key_ok', 'status': 'ok'},
                {
                    'id': 'tanker_key_error',
                    'status': 'error',
                    'error_message': 'something bad happened',
                },
            ],
        }

    @testpoint('localization-replication-end')
    def testpoint_logs(data):
        assert data['items_put_ctr'] == 1
        assert data['total_items'] == 2

    await taxi_grocery_products.invalidate_caches()
    await taxi_grocery_products.run_periodic_task(
        'localization-replication-periodic',
    )

    assert mock_replication.has_calls is True
    assert testpoint_logs.has_calls is True
