import json

CONSUMER_COMPONENT_NAME = 'nomenclature-snapshot-ready-consumer'
CONSUMER_NAME = 'nomenclature_snapshot_ready'

MESSAGE_COOKIE = 'cookie1'


async def test_consumer(
        component_config,
        update_taxi_config,
        testpoint,
        pg_realdict_cursor,
        push_lb_message,
):
    lb_topic = component_config.get(
        'logbroker-consumer', ['consumers', CONSUMER_NAME, 'topic'],
    )

    update_taxi_config(
        'EATS_RETAIL_SEO_LB_CONSUMERS',
        {CONSUMER_COMPONENT_NAME: {'is_enabled': True}},
    )

    @testpoint('logbroker_commit')
    def _commit(cookie):
        assert cookie == MESSAGE_COOKIE

    def _verify_paths(payload, db_data):
        assert payload == {
            f'{k}_table_name': v['table_path'] for (k, v) in db_data.items()
        }

    # write in empty DB

    payload = _generate_payload()

    await push_lb_message(
        topic_name=lb_topic,
        consumer_name=CONSUMER_NAME,
        cookie=MESSAGE_COOKIE,
        data=json.dumps(payload),
    )
    await _commit.wait_call()

    db_data_1 = _sql_get_snapshot_paths(pg_realdict_cursor)
    _verify_paths(payload, db_data_1)

    # update

    changed_table_id = 'products'
    payload[f'{changed_table_id}_table_name'] += '_changed'

    await push_lb_message(
        topic_name=lb_topic,
        consumer_name=CONSUMER_NAME,
        cookie=MESSAGE_COOKIE,
        data=json.dumps(payload),
    )

    await _commit.wait_call()

    db_data_2 = _sql_get_snapshot_paths(pg_realdict_cursor)
    _verify_paths(payload, db_data_2)
    for name in db_data_2.keys():
        if name == changed_table_id:
            assert (
                db_data_1[name]['updated_at'] <= db_data_2[name]['updated_at']
            )
        else:
            assert (
                db_data_1[name]['updated_at'] == db_data_2[name]['updated_at']
            )


def _get_table_ids():
    return [
        'products',
        'places_products',
        'categories',
        'categories_products',
        'categories_relations',
        'default_assortments',
    ]


def _generate_payload():
    return {f'{i}_table_name': f'{i}_path' for i in _get_table_ids()}


def _sql_get_snapshot_paths(pg_realdict_cursor):
    pg_realdict_cursor.execute(
        """
        select table_id, table_path, updated_at
        from eats_retail_seo.yt_snapshot_tables
        """,
    )
    return {
        i['table_id']: {
            'table_path': i['table_path'],
            'updated_at': i['updated_at'],
        }
        for i in pg_realdict_cursor
    }
