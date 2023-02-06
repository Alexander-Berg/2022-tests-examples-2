import pytest


@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.pgsql('processing_db', files=['pg_events_data.sql'])
@pytest.mark.parametrize(
    'is_replicated',
    [
        pytest.param(
            False,
            marks=[
                pytest.mark.yt(
                    schemas=['yt_events_schema.yaml'],
                    dyn_table_data=['yt_events_data_non_replicated.yaml'],
                ),
            ],
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.yt(
                    schemas=['yt_events_schema.yaml'],
                    dyn_table_data=['yt_events_data_replicated.yaml'],
                ),
            ],
        ),
    ],
)
async def test_procaas_restore_idempotency(
        taxi_processing, yt_apply, pgsql, is_replicated,
):
    item_id = 'c898154320771871bb1efbd81416cfb8'
    for _ in range(10):
        resp = await taxi_processing.get(
            '/v1/testsuite/foo/events',
            params={'item_id': item_id, 'allow_restore': True},
        )
        assert resp.status_code == 200
        events = list(_fetch_from_pg(pgsql, item_id))
        assert {i[0]: (i[1], i[2]) for i in events} == {
            '97eea4ca99964576914cc5caacd77494': (-5, -5),
            '24ac232f433242abbd9d0eeeda42a58c': (-4, -4),
            '3796869cc63d47ba9b81b189cfb3351c': (-3, -3),
            '0f3852fac2db4c709ba5ee7c4f2d660c': (-2, -2),
            '5556e8e39ae54591b22117296e1f73f1': (-1, -1),
            'c9bb864c99cd4f208628026c20515e52': (0, 0),
        }


def _fetch_from_pg(pgsql, item_id):
    cursor = pgsql['processing_db'].cursor()
    cursor.execute(
        'SELECT event_id, order_key, handling_order_key '
        'FROM processing.events '
        'WHERE item_id=%(item_id)s ',
        {'item_id': item_id},
    )
    return cursor
