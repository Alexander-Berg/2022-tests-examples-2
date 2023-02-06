import copy

import pytest


PERIODIC_CONFIG = {
    'enable': True,
    'interval': 3600,
    'enable_check_interval': 60,
    'check_interval': 60,
    'yt_path': '//analytics_yt/product_SKU_score',
    'yt_batch_size': 1000,
    'yt_retries_max': 3,
    'batch_size': 1000,
    'score_threshold_perc': 10,
}
PERIODIC_CONFIG_NAME = (
    'EATS_FULL_TEXT_SEARCH_INDEXER_UPDATE_PRODUCTS_SCORE_PERIODIC_SETTINGS'
)

PERIODIC_NAME = 'update-product-scores-periodic'

PERIODIC_FINISHED = f'eats_full_text_search_indexer::{PERIODIC_NAME}-finished'
PERIODIC_DISABLED = f'eats_full_text_search_indexer::{PERIODIC_NAME}-disabled'

YT_TABLE_SCHEMA = 'yt_product_score_schema.yaml'
YT_TABLE_DATA = 'yt_product_score_data.yaml'
YT_TABLE_PATH = '//analytics_yt/product_SKU_score'


@pytest.mark.parametrize(
    'enable, expected_updated_at',
    [(True, '2021-01-01 12:00:00+03:00'), (False, 'None')],
)
@pytest.mark.now('2021-01-01T12:00:00+03:00')
async def test_periodic_enable(
        testpoint,
        taxi_eats_full_text_search_indexer,
        pgsql,
        taxi_config,
        enable,
        expected_updated_at,
):
    """
    Проверяем что код периодика не выполняется, если он выключен в конфиге,
    и что updated_at периодика обновляется корректно
    """

    config = copy.deepcopy(PERIODIC_CONFIG)
    config['enable'] = enable
    taxi_config.set_values({PERIODIC_CONFIG_NAME: config})

    @testpoint(PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    @testpoint(PERIODIC_DISABLED)
    def periodic_disabled(arg):
        pass

    await taxi_eats_full_text_search_indexer.run_task(PERIODIC_NAME)
    assert periodic_finished.has_calls == enable
    assert periodic_disabled.has_calls != enable

    updated_at = get_periodic_last_updated_at(pgsql)
    assert str(updated_at) == expected_updated_at


@pytest.mark.parametrize('revision_has_changed', [True, False])
@pytest.mark.yt(schemas=[YT_TABLE_SCHEMA], static_table_data=[YT_TABLE_DATA])
async def test_yt_revision(
        testpoint,
        taxi_eats_full_text_search_indexer,
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

    # pylint: disable=unused-variable
    @testpoint('eats_full_text_search_indexer::yt-revision')
    def yt_revision(param):
        return {'yt_revision': new_table_revision}

    @testpoint('eats_full_text_search_indexer::yt-read-table')
    def yt_read_table(param):
        pass

    @testpoint(PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    await taxi_eats_full_text_search_indexer.run_task(PERIODIC_NAME)
    assert periodic_finished.has_calls
    assert yt_read_table.has_calls == revision_has_changed
    assert get_last_revision(pgsql, YT_TABLE_PATH) == new_table_revision


@pytest.mark.yt(schemas=[YT_TABLE_SCHEMA], static_table_data=[YT_TABLE_DATA])
async def test_product_scores_update(
        taxi_eats_full_text_search_indexer,
        pgsql,
        taxi_config,
        testpoint,
        yt_apply,
):
    """
    Проверяем обновление данных в таблице product_scores
    """

    @testpoint(PERIODIC_FINISHED)
    def periodic_finished(arg):
        pass

    taxi_config.set_values({PERIODIC_CONFIG_NAME: PERIODIC_CONFIG})
    set_product_scores(pgsql)

    await taxi_eats_full_text_search_indexer.run_task(PERIODIC_NAME)
    assert periodic_finished.has_calls

    assert get_product_scores(pgsql) == {
        1: {'origin_id_1': 0.1, 'origin_id_2': 0.25, 'origin_id_7': 0.7},
        3: {'origin_id_5': 0.5, 'origin_id_6': 0.6},
    }


def get_periodic_last_updated_at(pgsql):
    cursor = pgsql['eats_full_text_search_indexer'].dict_cursor()
    cursor.execute(
        """
        SELECT updated_at
        FROM fts_indexer.update_product_scores_state
        WHERE id = 1;
    """,
    )
    rows = [dict(row) for row in cursor]
    if rows:
        return rows[0]['updated_at']
    return None


def get_last_revision(pgsql, table_path):
    cursor = pgsql['eats_full_text_search_indexer'].dict_cursor()
    cursor.execute(
        f"""
        SELECT revision
        FROM fts_indexer.product_scores_last_revision
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
        INSERT INTO fts_indexer.product_scores_last_revision(
            table_path, revision
        )
        VALUES ('{table_path}', {revision});
    """,
    )


def set_product_scores(pgsql):
    cursor = pgsql['eats_full_text_search_indexer'].dict_cursor()
    cursor.execute(
        f"""
        INSERT INTO fts_indexer.product_scores(
            brand_id, origin_id, score
        )
        VALUES (1, 'origin_id_1', 0.1),
               (1, 'origin_id_2', 0.2),
               (1, 'origin_id_3', 0.3),
               (2, 'origin_id_4', 0.4);
        """,
    )


def get_product_scores(pgsql):
    cursor = pgsql['eats_full_text_search_indexer'].dict_cursor()
    cursor.execute(
        f"""
        SELECT brand_id, origin_id, score
        FROM fts_indexer.product_scores
    """,
    )
    brand_to_product_scores = dict()
    for row in cursor:
        brand_id = row['brand_id']
        origin_id = row['origin_id']
        score = row['score']
        if brand_id not in brand_to_product_scores:
            brand_to_product_scores[brand_id] = dict()
        brand_to_product_scores[brand_id][origin_id] = score
    return brand_to_product_scores
