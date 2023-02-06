import pytest

SAAS_RETAIL_SEARCH_SERVICE = 'eats_retail_search'
SAAS_RETAIL_SEARCH_CATEGORIES_PREFIX = 1
SAAS_RETAIL_SEARCH_ITEMS_PREFIX = 2


@pytest.mark.parametrize('fail_limit', (1, 5, 10))
async def test_retry(
        pgsql,
        testpoint,
        stq_runner,
        stq,
        set_retail_settings,
        # parametrize
        fail_limit,
):
    """
    Проверяем, что при ошибке stq таска ставится повторно в очередь,
    пока не превышен лимит fail_limit, а ошибка сохраняется в базу
    только на последней итерации
    """

    @testpoint('eats_full_text_search_indexer-fail_processing')
    def _testpoint(param):
        return {'inject_failure': True, 'error_text': 'injected error'}

    set_retail_settings(
        saas_service_send_to='eats_retail_search', fail_limit=fail_limit,
    )

    place_slug = 'place_slug'
    task_id = 'id_1'

    await stq_runner.eats_full_text_search_indexer_update_retail_place.call(
        task_id=task_id, kwargs={'place_slug': place_slug},
    )

    for i in range(fail_limit):
        assert stq.eats_full_text_search_indexer_update_retail_place.has_calls
        task_info = (
            stq.eats_full_text_search_indexer_update_retail_place.next_call()
        )
        assert task_info['id'] == task_id
        assert not _sql_get_update_status(pgsql, place_slug)
        await stq_runner.eats_full_text_search_indexer_update_retail_place.call(  # noqa: E501 pylint: disable=line-too-long
            task_id=task_id,
            kwargs={'place_slug': place_slug},
            reschedule_counter=i + 1,
        )

    assert not stq.eats_full_text_search_indexer_update_retail_place.has_calls

    status = _sql_get_update_status(pgsql, place_slug)
    assert status
    assert not status['last_updated_at']
    assert status['last_error_at']
    assert status['error'] == 'injected error'


@pytest.mark.parametrize(
    'error_text',
    [
        'No settings in config for eats_retail_search saas',
        'Unknown config saas_service_send_to',
    ],
)
@pytest.mark.parametrize('fail_limit', (1, 5, 10))
async def test_non_retryable_errors(
        pgsql,
        testpoint,
        stq_runner,
        stq,
        set_retail_settings,
        # parametrize
        error_text,
        fail_limit,
):
    """
    Проверяем, что при определенных ошибках stq таска не ставится
    повторно в очередь, а ошибка сразу сохраняется в базу
    """

    @testpoint('eats_full_text_search_indexer-fail_processing')
    def _testpoint(param):
        return {'inject_failure': True, 'error_text': error_text}

    set_retail_settings(
        saas_service_send_to='eats_retail_search', fail_limit=fail_limit,
    )

    place_slug = 'place_slug'
    task_id = 'id_1'

    _sql_set_place_state(pgsql, place_slug)

    await stq_runner.eats_full_text_search_indexer_update_retail_place.call(
        task_id=task_id, kwargs={'place_slug': place_slug},
    )

    assert not stq.eats_full_text_search_indexer_update_retail_place.has_calls

    status = _sql_get_update_status(pgsql, place_slug)
    assert status
    assert not status['last_updated_at']
    assert status['last_error_at']
    assert status['error'] == error_text


@pytest.mark.parametrize(
    'old_error_text',
    [
        'No settings in config for eats_retail_search saas',
        'Cannot find place_id for slug place_slug',
        'Place place_slug not found in v1/place/assortments/data, skip it',
        None,
    ],
)
@pytest.mark.parametrize(
    'error, error_text',
    [
        ('no_settings', 'No settings in config for eats_retail_search saas'),
        ('no_place', 'Cannot find place_id for slug place_slug'),
        (
            'nomenclature_404',
            'Place place_slug not found in v1/place/assortments/data, skip it',
        ),
        (None, None),
    ],
)
async def test_update_status(
        pgsql,
        stq_runner,
        taxi_config,
        mockserver,
        load_json,
        set_retail_settings,
        # parametrize
        old_error_text,
        error,
        error_text,
):
    """
    Проверяем сохранение ошибки в таблицу update_retail_place_status
    """

    fail_limit = 1
    set_retail_settings(
        saas_service_send_to='eats_retail_search', fail_limit=fail_limit,
    )

    if error == 'no_settings':
        _remove_retail_settings(taxi_config)

    place_slug = 'place_slug'
    task_id = 'id_1'

    if old_error_text:
        _sql_set_error_status(pgsql, place_slug, old_error_text)

    if error != 'no_place':
        _sql_set_place_state(pgsql, place_slug)

    @mockserver.json_handler('eats-nomenclature/v1/place/assortments/data')
    def _nmn_assortment_names(request):
        if error == 'nomenclature_404':
            return mockserver.make_response(status=404, json={})
        return {'assortments': [{'name': 'partner'}]}

    @mockserver.json_handler(
        'eats-nomenclature/v1/place/categories/get_children',
    )
    def _nmn_categories(request):
        return load_json('nomenclature_categories_response.json')

    @mockserver.json_handler('eats-nomenclature/v1/products/info')
    def _nmn_products(request):
        return load_json('nomenclature_products_response.json')

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SAAS_RETAIL_SEARCH_SERVICE),
    )
    def _saas_retail_search_push(request):
        return {
            'written': True,
            'attempts': [
                {
                    'comment': 'ok',
                    'written': True,
                    'attemptƒ': 0,
                    'shard': '0-65535',
                },
            ],
            'comment': 'ok',
        }

    await stq_runner.eats_full_text_search_indexer_update_retail_place.call(
        task_id=task_id,
        kwargs={'place_slug': place_slug},
        reschedule_counter=fail_limit,
    )

    status = _sql_get_update_status(pgsql, place_slug)
    assert status
    assert (status['last_updated_at'] is None) == (error is not None)
    assert (status['last_error_at'] is None) == (error is None)
    assert status['error'] == error_text


@pytest.mark.parametrize(
    'error, error_text',
    [
        (
            'no_mapped_categories',
            'Couldn\'t convert any category to retail document, place_id = 1',
        ),
        (
            'no_mapped_items',
            'Couldn\'t convert any item to retail document, place_id = 1',
        ),
    ],
)
@pytest.mark.parametrize('nomenclature_has_categories', [True, False])
@pytest.mark.parametrize('nomenclature_has_items', [True, False])
async def test_mapping_errors(
        pgsql,
        stq_runner,
        mockserver,
        load_json,
        testpoint,
        set_retail_settings,
        # parametrize
        error,
        error_text,
        nomenclature_has_categories,
        nomenclature_has_items,
):
    """
    Проверяем, что ошибка конвертации товаров/категорий сохраняется,
    только если действительно были товары/категории, которые нужно
    было отправить в saas
    """

    @testpoint('eats_full_text_search_indexer-fail_category_mapping')
    def _testpoint_fail_category(param):
        inject_failure = error == 'no_mapped_categories'
        return {'inject_failure': inject_failure}

    @testpoint('eats_full_text_search_indexer-fail_item_mapping')
    def _testpoint_fail_item(param):
        inject_failure = error == 'no_mapped_items'
        return {'inject_failure': inject_failure}

    fail_limit = 1
    set_retail_settings(
        saas_service_send_to='eats_retail_search', fail_limit=fail_limit,
    )

    place_slug = 'place_slug'
    task_id = 'id_1'

    _sql_set_place_state(pgsql, place_slug)

    @mockserver.json_handler('eats-nomenclature/v1/place/assortments/data')
    def _nmn_assortment_names(request):
        return {'assortments': [{'name': 'partner'}]}

    @mockserver.json_handler(
        'eats-nomenclature/v1/place/categories/get_children',
    )
    def _nmn_categories(request):
        response = load_json('nomenclature_categories_response.json')
        if not nomenclature_has_categories:
            response['categories'] = []
        return response

    @mockserver.json_handler('eats-nomenclature/v1/products/info')
    def _nmn_products(request):
        response = load_json('nomenclature_products_response.json')
        if not nomenclature_has_items:
            response['products'] = []
        return response

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SAAS_RETAIL_SEARCH_SERVICE),
    )
    def _saas_retail_search_push(request):
        return {
            'written': True,
            'attempts': [
                {
                    'comment': 'ok',
                    'written': True,
                    'attempt': 0,
                    'shard': '0-65535',
                },
            ],
            'comment': 'ok',
        }

    def _get_expected_error():
        if error == 'no_mapped_categories' and nomenclature_has_categories:
            return error_text
        if (
                error == 'no_mapped_items'
                and nomenclature_has_items
                and nomenclature_has_categories
        ):
            return error_text
        return None

    expected_error = _get_expected_error()

    await stq_runner.eats_full_text_search_indexer_update_retail_place.call(
        task_id=task_id,
        kwargs={'place_slug': place_slug},
        reschedule_counter=fail_limit,
    )

    status = _sql_get_update_status(pgsql, place_slug)
    assert status

    assert (status['last_updated_at'] is None) == (expected_error is not None)
    assert (status['last_error_at'] is None) == (expected_error is None)
    assert status['error'] == expected_error


@pytest.mark.parametrize(
    'nmn_index_root_categories',
    (
        pytest.param(True, id='index root'),
        pytest.param(False, id='ignore root'),
    ),
)
@pytest.mark.parametrize(
    'nmn_index_promo_categories',
    (
        pytest.param(True, id='index promo'),
        pytest.param(False, id='ignore promo'),
    ),
)
@pytest.mark.parametrize('categories_type', ['custom_base', 'custom_promo'])
async def test_ignore_all_categories(
        pgsql,
        stq_runner,
        mockserver,
        load_json,
        testpoint,
        set_retail_settings,
        # parametrize
        nmn_index_root_categories,
        nmn_index_promo_categories,
        categories_type,
):
    """
    Проверяем, что если все категории должны игнорироваться при индексации,
    то никакая ошибка не сохраняется
    """

    @testpoint('eats_full_text_search_indexer-fail_category_mapping')
    def _testpoint_fail_category(param):
        return {'inject_failure': True}

    fail_limit = 1
    set_retail_settings(
        saas_service_send_to='eats_retail_search',
        fail_limit=fail_limit,
        index_root_categories=nmn_index_root_categories,
        index_promo_categories=nmn_index_promo_categories,
    )

    place_slug = 'place_slug'
    task_id = 'id_1'

    _sql_set_place_state(pgsql, place_slug)

    @mockserver.json_handler('eats-nomenclature/v1/place/assortments/data')
    def _nmn_assortment_names(request):
        return {'assortments': [{'name': 'partner'}]}

    @mockserver.json_handler(
        'eats-nomenclature/v1/place/categories/get_children',
    )
    def _nmn_categories(request):
        response = load_json('nomenclature_categories_response.json')
        for category in response['categories']:
            category['type'] = categories_type
        return response

    @mockserver.json_handler('eats-nomenclature/v1/products/info')
    def _nmn_products(request):
        return load_json('nomenclature_products_response.json')

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SAAS_RETAIL_SEARCH_SERVICE),
    )
    def _saas_retail_search_push(request):
        return {
            'written': True,
            'attempts': [
                {
                    'comment': 'ok',
                    'written': True,
                    'attempt': 0,
                    'shard': '0-65535',
                },
            ],
            'comment': 'ok',
        }

    def _should_has_error():
        return nmn_index_root_categories and (
            nmn_index_promo_categories or categories_type == 'custom_base'
        )

    should_has_error = _should_has_error()

    await stq_runner.eats_full_text_search_indexer_update_retail_place.call(
        task_id=task_id,
        kwargs={'place_slug': place_slug},
        reschedule_counter=fail_limit,
    )

    status = _sql_get_update_status(pgsql, place_slug)
    assert status

    assert (status['last_updated_at'] is None) == should_has_error
    assert (status['last_error_at'] is not None) == should_has_error
    assert (status['error'] is not None) == should_has_error


def _sql_get_update_status(pgsql, place_slug):
    cursor = pgsql['eats_full_text_search_indexer'].cursor()
    cursor.execute(
        f"""
            select last_updated_at, error, last_error_at
            from fts_indexer.update_retail_place_status
            where place_slug = {place_slug}
            """,
    )
    rows = list(cursor)
    if not rows:
        return None
    return {
        'last_updated_at': rows[0][0],
        'error': rows[0][1],
        'last_error_at': rows[0][2],
    }


def _sql_set_error_status(pgsql, place_slug, error_text):
    cursor = pgsql['eats_full_text_search_indexer'].cursor()
    cursor.execute(
        f"""
            insert into fts_indexer.update_retail_place_status(
                place_slug, error, last_error_at
            ) values (
                '{place_slug}', '{error_text}', now()
            )
            """,
    )


def _remove_retail_settings(taxi_config):
    config_name = 'EATS_FULL_TEXT_SEARCH_INDEXER_UPDATE_RETAIL_PLACE_SETTINGS'
    config = taxi_config.get(config_name)
    del config['retail_saas_settings']
    taxi_config.set(**{config_name: config})


def _sql_set_place_state(pgsql, place_slug):
    cursor = pgsql['eats_full_text_search_indexer'].cursor()
    cursor.execute(
        f"""
            insert into fts_indexer.place_state(
                place_id, place_slug, enabled, business
            ) values (
                1, 'place_slug', true, 'shop'
            )
            """,
    )
