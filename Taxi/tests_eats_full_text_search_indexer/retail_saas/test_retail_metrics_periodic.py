import pytest

PERIODIC_NAME = 'retail-metrics-periodic'


@pytest.mark.parametrize(
    'place_statuses, expected_places_with_errors',
    [
        ([('place_slug_1', None), ('place_slug_2', None)], 0),
        ([('place_slug_1', 'Some error'), ('place_slug_2', None)], 1),
        (
            [
                ('place_slug_1', 'Some error 1'),
                ('place_slug_2', 'Some error 2'),
                ('place_slug_3', 'Some error 3'),
            ],
            3,
        ),
    ],
)
async def test_metrics(
        taxi_eats_full_text_search_indexer,
        taxi_eats_full_text_search_indexer_monitor,
        pgsql,
        # parametrize
        place_statuses,
        expected_places_with_errors,
):
    """
    Проверяем заполнение метрики places_with_errors
    """

    _set_update_status(pgsql, place_statuses)

    await taxi_eats_full_text_search_indexer.run_periodic_task(PERIODIC_NAME)

    metric = await taxi_eats_full_text_search_indexer_monitor.get_metric(
        'update_retail_place',
    )
    assert metric['places_with_errors'] == expected_places_with_errors


def _set_update_status(pgsql, place_statuses):
    cursor = pgsql['eats_full_text_search_indexer'].cursor()
    for place_slug, error_text in place_statuses:
        last_error_at = 'now()' if error_text else 'null'
        error = f'\'{error_text}\'' if error_text else 'null'
        cursor.execute(
            f"""
            insert into fts_indexer.update_retail_place_status(
                place_slug, error, last_error_at
            ) values
                ('{place_slug}', {error}, {last_error_at})
            """,
        )
