import pytest


@pytest.mark.config(
    COMBO_CONTRACTORS_PSQL_CLEANUP_SETTINGS={
        'cleanup_chunk_size': 1,
        'expired_order_ttl': 300,
        'finished_order_ttl': 100,
    },
)
@pytest.mark.config(
    COMBO_CONTRACTORS_PSQL_BATCH_CLEANUP_SETTINGS={
        'cleanup_chunk_size': 1,
        'expired_batch_ttl': 1,
    },
)
@pytest.mark.pgsql('combo_contractors', files=['orders.sql', 'batches.sql'])
async def test_psql_cleanup(taxi_combo_contractors, pgsql):
    await taxi_combo_contractors.run_task('distlock/psql-cleaner')
    cursor = pgsql['combo_contractors'].cursor()
    cursor.execute('SELECT order_id FROM combo_contractors.customer_order')
    result = sorted([item[0] for item in cursor.fetchall()])
    assert result == ['order_id0', 'order_id1', 'order_id2']

    cursor.execute('SELECT order_id FROM combo_contractors.combo_batch')
    result = sorted([item[0] for item in cursor.fetchall()])
    assert result == ['order_id0', 'order_id1', 'order_id2']


@pytest.mark.pgsql('combo_contractors', files=['orders_combo.sql'])
@pytest.mark.config(
    COMBO_CONTRACTORS_PSQL_CLEANUP_SETTINGS={
        'cleanup_chunk_size': 10,
        'expired_order_ttl': 300,
        'finished_order_ttl': 100,
    },
)
async def test_psql_cleanup_combo(taxi_combo_contractors, pgsql):
    await taxi_combo_contractors.run_task('distlock/psql-cleaner')
    cursor = pgsql['combo_contractors'].cursor()
    cursor.execute('SELECT order_id FROM combo_contractors.customer_order')
    result = sorted([item[0] for item in cursor.fetchall()])
    assert result == ['order_id0', 'order_id1', 'order_id2', 'order_id3']
