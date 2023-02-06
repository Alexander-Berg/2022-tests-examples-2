import copy

import pytest


PERIODIC_CONFIG = {
    'period_in_sec': 3600,
    'is_enabled': True,
    'yt_path': '//analytics_yt/selector_statistics',
    'yt_batch_size': 1000,
    'yt_retries_max': 3,
    'batch_size': 1000,
    'percentage_threshold': 5,
    'count_threshold_perc': 10,
}
PERIODIC_CONFIG_NAME = (
    'EATS_FULL_TEXT_SEARCH_UPDATE_SELECTOR_STATISTICS_PERIODIC_SETTINGS'
)

PERIODIC_NAME = 'update-selector-statistics-periodic'

PERIODIC_FINISHED = f'eats_full_text_search_indexer::{PERIODIC_NAME}-finished'

YT_TABLE_SCHEMA = 'yt_schema.yaml'
YT_TABLE_DATA = 'yt_data.yaml'
YT_TABLE_PATH = '//analytics_yt/selector_statistics'


@pytest.mark.parametrize('is_enabled', [True, False])
async def test_periodic_enable(
        testpoint, taxi_eats_full_text_search, taxi_config, is_enabled,
):
    """
    Проверяем что код периодика не выполняется, если он выключен в конфиге
    """

    config = copy.deepcopy(PERIODIC_CONFIG)
    config['is_enabled'] = is_enabled
    taxi_config.set_values({PERIODIC_CONFIG_NAME: config})

    @testpoint(PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_full_text_search.run_distlock_task(PERIODIC_NAME)
    assert periodic_finished.has_calls == is_enabled


@pytest.mark.parametrize('revision_has_changed', [True, False])
@pytest.mark.yt(schemas=[YT_TABLE_SCHEMA], static_table_data=[YT_TABLE_DATA])
async def test_yt_revision(
        testpoint,
        taxi_eats_full_text_search,
        pgsql,
        taxi_config,
        yt_apply,
        revision_has_changed,
):
    """
    Проверяем что ревизия yt таблицы сохраняется корректно
    и данные из таблицы не читаются, если ревизия не изменилась
    """

    taxi_config.set_values({PERIODIC_CONFIG_NAME: PERIODIC_CONFIG})

    table_revision = 1
    new_table_revision = 2 if revision_has_changed else table_revision
    set_last_revision(pgsql, YT_TABLE_PATH, table_revision)

    @testpoint('eats_full_text_search_indexer::yt-revision')
    def _yt_revision(param):
        return {'yt_revision': new_table_revision}

    @testpoint('eats_full_text_search_indexer::yt-read-table')
    def yt_read_table(param):
        pass

    @testpoint(PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_full_text_search.run_distlock_task(PERIODIC_NAME)
    assert periodic_finished.has_calls
    assert yt_read_table.has_calls == revision_has_changed
    assert get_last_revision(pgsql, YT_TABLE_PATH) == new_table_revision


@pytest.mark.yt(schemas=[YT_TABLE_SCHEMA], static_table_data=[YT_TABLE_DATA])
async def test_selector_statistics_update(
        taxi_eats_full_text_search, pgsql, taxi_config, testpoint, yt_apply,
):
    """
    Проверяем обновление данных в таблице selector_statistics
    """

    @testpoint(PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    taxi_config.set_values({PERIODIC_CONFIG_NAME: PERIODIC_CONFIG})
    set_selector_statistics(pgsql)

    await taxi_eats_full_text_search.run_distlock_task(PERIODIC_NAME)
    assert periodic_finished.has_calls

    assert get_selector_statistics(pgsql) == [
        # данные обновляются, потому что restaurant_percentage и
        # shop_percentage изменились больше, чем на percentage_threshold
        {
            'query': 'арбуз',
            'count': 972,
            'restaurant_percentage': 6,
            'shop_percentage': 94,
        },
        # новые данные
        {
            'query': 'клубника',
            'count': 2149,
            'restaurant_percentage': 27,
            'shop_percentage': 72,
        },
        # новые данные
        {
            'query': 'мороженое',
            'count': 1737,
            'restaurant_percentage': 48,
            'shop_percentage': 51,
        },
        # данные обновляются, потому что count изменился больше,
        # чем на count_threshold_perc процентов
        {
            'query': 'пицца',
            'count': 12459,
            'restaurant_percentage': 99,
            'shop_percentage': 1,
        },
        # данные не обновляются, потому что изменения не превышают
        # пороговых значений
        {
            'query': 'шаурма',
            'count': 19230,
            'restaurant_percentage': 98,
            'shop_percentage': 1,
        },
        # subway удаляется
    ]


def get_last_revision(pgsql, table_path):
    cursor = pgsql['eats_full_text_search_indexer'].dict_cursor()
    cursor.execute(
        f"""
        SELECT revision
        FROM fts.selector_statistics_last_revision
        WHERE table_path = '{table_path}';
    """,
    )
    rows = [dict(row) for row in cursor]
    if rows:
        return rows[0]['revision']
    return None


def set_last_revision(pgsql, table_path, revision):
    cursor = pgsql['eats_full_text_search_indexer'].dict_cursor()
    cursor.execute(
        f"""
        INSERT INTO fts.selector_statistics_last_revision(
            table_path, revision
        )
        VALUES ('{table_path}', {revision});
    """,
    )


def set_selector_statistics(pgsql):
    cursor = pgsql['eats_full_text_search_indexer'].dict_cursor()
    cursor.execute(
        f"""
        INSERT INTO fts.selector_statistics(
            query, count, restaurant_percentage, shop_percentage
        )
        VALUES ('шаурма', 19230, 98, 1.27),
               ('пицца', 10253, 96, 2.3),
               ('арбуз', 958, 20, 78.4),
               ('subway', 767, 100, 0);
        """,
    )


def get_selector_statistics(pgsql):
    cursor = pgsql['eats_full_text_search_indexer'].dict_cursor()
    cursor.execute(
        f"""
        SELECT query, count, restaurant_percentage, shop_percentage
        FROM fts.selector_statistics
    """,
    )
    data = [dict(row) for row in cursor]
    return sorted(data, key=lambda elem: elem['query'])
