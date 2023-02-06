import pytest

from discounts_operation_calculations.repositories import segment_stats


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_push_segment_stats.sql', 'fill_pg_flat_segment_stats.sql'],
)
async def test_get_push_segment_stats(web_context, load_dataframe_from_csv):
    segment_stats_storage = segment_stats.SegmentStatsStorage(web_context)

    stats = await segment_stats_storage.get_segment_stats(
        algorithm_id='kt',
        discounts_city='test_city',
        with_push=True,
        fallback_discount=6,
    )
    data = segment_stats_storage.create_dataframe_from_pg(stats)

    real_stats = load_dataframe_from_csv('stats.csv')
    for column in real_stats.columns:
        if column in ('segment', 'index', 'algorithm_id'):
            continue
        # pd.equals doesn't works with float columns
        # so we just compare the sum of columns
        assert real_stats[column].sum() == pytest.approx(data[column].sum())
