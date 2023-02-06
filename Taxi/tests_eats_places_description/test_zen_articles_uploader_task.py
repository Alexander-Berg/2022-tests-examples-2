import pytest


@pytest.mark.yt(
    schemas=['yt_zen_schema.yaml'], static_table_data=['yt_zen_articles.yaml'],
)
async def test_basic(
        taxi_eats_places_description,
        testpoint,
        yt_apply,
        taxi_eats_places_description_monitor,
):
    @testpoint('zen-articles-uploader-finished')
    def task_testpoint(data):
        pass

    await taxi_eats_places_description.run_distlock_task(
        'zen-articles-uploader',
    )

    assert task_testpoint.times_called == 1

    await taxi_eats_places_description.invalidate_caches(clean_update=False)

    metrics = await taxi_eats_places_description_monitor.get_metrics()

    assert metrics['zen-articles-uploader']['last-processed'] == 2
    assert metrics['zen-articles-uploader']['last-errors'] == 0

    response = await taxi_eats_places_description.post(
        '/v1/articles/zen/list', json={'limit': 3},
    )
    articles = response.json()['articles']['zenArticles']
    assert len(articles) == 2


@pytest.mark.yt(
    schemas=['yt_zen_schema.yaml'],
    static_table_data=['yt_zen_articles_replace.yaml'],
)
async def test_data_replace_by_publication_id(
        taxi_eats_places_description,
        testpoint,
        yt_apply,
        taxi_eats_places_description_monitor,
):
    @testpoint('zen-articles-uploader-finished')
    def task_testpoint(data):
        pass

    await taxi_eats_places_description.run_distlock_task(
        'zen-articles-uploader',
    )

    assert task_testpoint.times_called == 1

    await taxi_eats_places_description.invalidate_caches(clean_update=False)

    metrics = await taxi_eats_places_description_monitor.get_metrics()

    assert metrics['zen-articles-uploader']['last-processed'] == 3
    assert metrics['zen-articles-uploader']['last-errors'] == 0

    response = await taxi_eats_places_description.post(
        '/v1/articles/zen/list', json={'limit': 3},
    )
    articles = response.json()['articles']['zenArticles']
    assert len(articles) == 1

    assert articles[0]['title'] == 'автор 2'
    assert articles[0]['description'] == 'новый текст 2'
    assert articles[0]['url'] == 'http://урл2'
    assert articles[0]['authorAvatarUrl'] == 'asset://dzen'
    assert articles[0]['brandId'] == 999


@pytest.mark.yt(
    schemas=['yt_zen_schema.yaml'],
    static_table_data=['yt_zen_articles_deactivate.yaml'],
)
async def test_data_deactivate_by_publication_id(
        taxi_eats_places_description,
        testpoint,
        yt_apply,
        taxi_eats_places_description_monitor,
):
    @testpoint('zen-articles-uploader-finished')
    def task_testpoint(data):
        pass

    await taxi_eats_places_description.run_distlock_task(
        'zen-articles-uploader',
    )

    assert task_testpoint.times_called == 1

    await taxi_eats_places_description.invalidate_caches(clean_update=False)

    metrics = await taxi_eats_places_description_monitor.get_metrics()

    assert metrics['zen-articles-uploader']['last-processed'] == 3
    assert metrics['zen-articles-uploader']['last-errors'] == 0

    response = await taxi_eats_places_description.post(
        '/v1/articles/zen/list', json={'limit': 3},
    )
    articles = response.json()['articles']['zenArticles']
    assert len(articles) == 1

    assert articles[0]['title'] == 'автор основной'
    assert articles[0]['description'] == 'текст основной'
    assert articles[0]['url'] == 'http://урл_основной'
    assert articles[0]['authorAvatarUrl'] == 'asset://dzen'
    assert articles[0]['brandId'] == 999


@pytest.mark.yt(
    schemas=['yt_zen_schema.yaml'],
    static_table_data=['yt_zen_articles_reactivate.yaml'],
)
async def test_data_reactivate_by_publication_id(
        taxi_eats_places_description,
        testpoint,
        yt_apply,
        taxi_eats_places_description_monitor,
):
    @testpoint('zen-articles-uploader-finished')
    def task_testpoint(data):
        pass

    await taxi_eats_places_description.run_distlock_task(
        'zen-articles-uploader',
    )

    assert task_testpoint.times_called == 1

    await taxi_eats_places_description.invalidate_caches(clean_update=False)

    metrics = await taxi_eats_places_description_monitor.get_metrics()

    assert metrics['zen-articles-uploader']['last-processed'] == 2
    assert metrics['zen-articles-uploader']['last-errors'] == 0

    response = await taxi_eats_places_description.post(
        '/v1/articles/zen/list', json={'limit': 3},
    )
    articles = response.json()['articles']['zenArticles']
    assert len(articles) == 1

    assert articles[0]['title'] == 'автор 2'
    assert articles[0]['description'] == 'новый текст 2'
    assert articles[0]['url'] == 'http://урл2'
    assert articles[0]['authorAvatarUrl'] == 'asset://dzen'
    assert articles[0]['brandId'] == 999
