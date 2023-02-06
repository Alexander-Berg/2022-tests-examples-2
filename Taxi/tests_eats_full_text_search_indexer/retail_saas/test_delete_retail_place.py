import pytest

SAAS_SERVICE = 'eats_retail_search'
SAAS_CATEGORIES_PREFIX = 1
SAAS_ITEMS_PREFIX = 2


async def test_invalid_place_id(stq_runner, stq, set_retail_settings):
    """
    Проверяем, что если в очередь приходит невалидный place_id,
    то таска не ретраится и завершается без ошибок
    """

    set_retail_settings()

    place_id = 'invalid_place_id'

    await stq_runner.eats_full_text_search_indexer_delete_retail_place.call(
        task_id='id_1', kwargs={'place_id': place_id}, expect_fail=False,
    )

    assert not stq.eats_full_text_search_indexer_delete_retail_place.has_calls


async def test_no_place_id(stq_runner, stq, set_retail_settings):
    """
    Проверяем, что если приходит валидный, но неизвестный place_id,
    то таска не ретраится и завершается без ошибок
    """

    set_retail_settings()

    place_id = '123'

    await stq_runner.eats_full_text_search_indexer_delete_retail_place.call(
        task_id='id_1', kwargs={'place_id': place_id}, expect_fail=False,
    )

    assert not stq.eats_full_text_search_indexer_delete_retail_place.has_calls


@pytest.mark.pgsql(
    'eats_full_text_search_indexer', files=['fill_document_meta.sql'],
)
@pytest.mark.parametrize('fail_limit', (1, 5, 10))
async def test_task_retry(
        stq_runner,
        stq,
        testpoint,
        taxi_config,
        set_retail_settings,
        # parametrize
        fail_limit,
):
    """
    Проверяем, что при ошибке таска ретраится
    fail_limit число раз, после чего завершается без ошибки
    """

    @testpoint('eats_full_text_search_indexer-fail_processing')
    def _testpoint(param):
        return {'inject_failure': True}

    set_retail_settings()
    taxi_config.set_values(
        {
            'EATS_FULL_TEXT_SEARCH_INDEXER_DELETE_RETAIL_PLACE_SETTINGS': {
                'fail_limit': fail_limit,
                'min_retry_delay_ms': 60000,
                'max_retry_delay_ms': 1800000,
            },
        },
    )

    place_id = '1'
    task_id = 'task_id_1'

    await stq_runner.eats_full_text_search_indexer_delete_retail_place.call(
        task_id=task_id, kwargs={'place_id': place_id}, expect_fail=False,
    )

    for i in range(fail_limit):
        assert stq.eats_full_text_search_indexer_delete_retail_place.has_calls
        task_info = (
            stq.eats_full_text_search_indexer_delete_retail_place.next_call()
        )
        assert task_info['id'] == task_id
        await stq_runner.eats_full_text_search_indexer_delete_retail_place.call(  # noqa: E501 pylint: disable=line-too-long
            task_id=task_id,
            kwargs={'place_id': place_id},
            reschedule_counter=i + 1,
        )

    assert not stq.eats_full_text_search_indexer_delete_retail_place.has_calls


@pytest.mark.pgsql(
    'eats_full_text_search_indexer', files=['fill_document_meta.sql'],
)
async def test_delete_data(stq_runner, mockserver, pgsql, set_retail_settings):
    """
    Проверяем, что данные удаляются из saas и из таблицы retail_document_meta
    """

    set_retail_settings()
    place_id = '1'

    deleted_urls = set()

    @mockserver.json_handler(
        '/saas-push/push/{service}'.format(service=SAAS_SERVICE),
    )
    def saas_retail_search_push(request):
        payload = request.json
        prefix = payload['prefix']
        if prefix == SAAS_ITEMS_PREFIX:  # item
            assert payload['action'] == 'delete'
            deleted_urls.add(payload['docs'][0]['url'])
        elif prefix == SAAS_CATEGORIES_PREFIX:  # category
            assert payload['action'] == 'delete'
            deleted_urls.add(payload['docs'][0]['url'])
        else:
            assert False, 'Unknown document prefix {}'.format(prefix)
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

    await stq_runner.eats_full_text_search_indexer_delete_retail_place.call(
        task_id='task_id_1', kwargs={'place_id': place_id}, expect_fail=False,
    )

    expected_deleted_urls = {
        '/place_slug/categories/category_id_1',
        '/place_slug/categories/category_id_2',
        '/1/items/item_id_1',
        '/1/items/item_id_2',
    }

    assert saas_retail_search_push.times_called == len(expected_deleted_urls)
    assert deleted_urls == expected_deleted_urls
    assert get_doc_meta_urls(pgsql) == set()


def get_doc_meta_urls(pgsql):
    cursor = pgsql['eats_full_text_search_indexer'].cursor()
    cursor.execute(
        f"""
        SELECT url
        FROM fts_indexer.retail_document_meta;
    """,
    )
    return {row[0] for row in cursor}
