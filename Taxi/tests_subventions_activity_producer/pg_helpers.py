import json

PG_CLUSTER = 'subventions-activity-producer'
SHARDS = ['shard0', 'shard1', 'shard2']


def get_raw_driver_events_grouped(pgsql, schema, cluster=PG_CLUSTER):
    cursor = pgsql[cluster].cursor()
    cursor.execute(
        """SELECT dbid_uuid,chunk_ts,chunk_end_ts,updated_ts,driver_data,timestamps
         FROM {}.raw_driver_events_grouped
         ORDER BY (dbid_uuid, chunk_ts);""".format(
            schema,
        ),
    )
    raw_rows = list(cursor)
    return [
        {
            'dbid_uuid': row[0],
            'chunk_ts': row[1].isoformat(),
            'chunk_end_ts': row[2].isoformat(),
            'updated_ts': row[3].isoformat(),
            'driver_data': row[4],
            'timestamps': row[5],
        }
        for row in raw_rows
    ]


def prepare_raw_driver_events(pgsql, schema, docs, cluster=PG_CLUSTER):
    cursor = pgsql[cluster].cursor()
    for doc in docs:
        cursor.execute(
            """INSERT INTO {schema}.raw_driver_events_grouped
         (dbid_uuid,chunk_ts,chunk_end_ts,updated_ts,timestamps,driver_data)
         VALUES
          ('{dbid_uuid}','{chunk_ts}','{chunk_end_ts}','{updated_ts}'
          ,'{timestamps}','{driver_data}');""".format(
                schema=schema,
                dbid_uuid=doc['dbid_uuid'],
                chunk_ts=doc['chunk_ts'],
                chunk_end_ts=doc['chunk_end_ts'],
                updated_ts=doc['updated_ts'],
                timestamps=json.dumps(doc['timestamps']),
                driver_data=json.dumps(doc['driver_data']),
            ),
        )


def init_raw_driver_events_grouped(load_json, pgsql, datafiles_by_shard):
    for i, datafile in enumerate(datafiles_by_shard):
        init_doc = load_json(datafile)
        schema = SHARDS[i]
        prepare_raw_driver_events(pgsql, schema, init_doc)


def get_incomplete_event_groups(pgsql, schema, cluster=PG_CLUSTER):
    cursor = pgsql[cluster].cursor()
    cursor.execute(
        """SELECT group_id,dbid_uuid,chunk_ts,chunk_end_ts,
                  updated_ts,driver_data,timestamps
         FROM {}.incomplete_driver_events
         ORDER BY (dbid_uuid, chunk_ts);""".format(
            schema,
        ),
    )
    raw_rows = list(cursor)
    return [
        {
            'group_id': row[0],
            'dbid_uuid': row[1],
            'chunk_ts': row[2].isoformat(),
            'chunk_end_ts': row[3].isoformat(),
            'updated_ts': row[4].isoformat(),
            'driver_data': row[5],
            'timestamps': row[6],
        }
        for row in raw_rows
    ]


def _prepare_incomplete_event_groups(pgsql, schema, docs, cluster=PG_CLUSTER):
    cursor = pgsql[cluster].cursor()
    for doc in docs:
        cursor.execute(
            """INSERT INTO {schema}.incomplete_driver_events
         (group_id,dbid_uuid,chunk_ts,chunk_end_ts,updated_ts,timestamps,driver_data)
         VALUES
          ('{group_id}','{dbid_uuid}','{chunk_ts}','{chunk_end_ts}','{updated_ts}'
          ,'{timestamps}','{driver_data}');""".format(
                schema=schema,
                group_id=doc['group_id'],
                dbid_uuid=doc['dbid_uuid'],
                chunk_ts=doc['chunk_ts'],
                chunk_end_ts=doc['chunk_end_ts'],
                updated_ts=doc['updated_ts'],
                timestamps=json.dumps(doc['timestamps']),
                driver_data=json.dumps(doc['driver_data']),
            ),
        )


def init_incomplete_event_groups(load_json, pgsql, datafiles_by_shard):
    for i, datafile in enumerate(datafiles_by_shard):
        init_doc = load_json(datafile)
        schema = SHARDS[i]
        _prepare_incomplete_event_groups(pgsql, schema, init_doc)


def _sort_timestamp_in_group(group):
    group['timestamps'] = sorted(group['timestamps'], key=lambda k: k['time'])
    return group


def extract_incomplete_event_groups(
        load_json, pgsql, datafiles_expected_by_shard,
):
    expected_shards_datas = []
    actual_shards_datas = []
    for i, datafile in enumerate(datafiles_expected_by_shard):
        expected = load_json(datafile)
        schema = SHARDS[i]
        actual = get_incomplete_event_groups(pgsql, schema)

        expected_datas = [
            _sort_timestamp_in_group(group) for group in expected
        ]
        actual_datas = [_sort_timestamp_in_group(group) for group in actual]

        expected_shards_datas.append(expected_datas)
        actual_shards_datas.append(actual_datas)
    return expected_shards_datas, actual_shards_datas


def _prepare_activity_events_unsent(pgsql, schema, docs, cluster=PG_CLUSTER):
    cursor = pgsql[cluster].cursor()
    for doc in docs:
        cursor.execute(
            """INSERT INTO {schema}.activity_events_unsent
            (event_at,activity_event)
            VALUES ('{event_at}','{event_data}');
            """.format(
                schema=schema,
                event_at=doc['event_at'],
                event_data=json.dumps(doc['activity_event']),
            ),
        )


def init_activity_events_unsent(load_json, pgsql, datafiles_by_shard):
    for i, datafile in enumerate(datafiles_by_shard):
        init_doc = load_json(datafile)
        schema = SHARDS[i]
        _prepare_activity_events_unsent(pgsql, schema, init_doc)


def get_activity_events_unsent(pgsql, schema, cluster=PG_CLUSTER):
    cursor = pgsql[cluster].cursor()
    cursor.execute(
        """SELECT event_at,activity_event
         FROM {}.activity_events_unsent
         ORDER BY id;""".format(
            schema,
        ),
    )
    raw_rows = list(cursor)
    events = [
        {'event_at': row[0].isoformat(), 'activity_event': row[1]}
        for row in raw_rows
    ]
    return sorted(events, key=lambda event: event['activity_event']['start'])


def _prepare_activity_events_verification(
        pgsql, schema, doc, cluster=PG_CLUSTER,
):
    cursor = pgsql[cluster].cursor()
    for obj in doc:
        cursor.execute(
            """INSERT INTO {schema}.activity_events_verification
            (updated_at, event_id, event_from_pg, event_from_redis)
            VALUES
            ('{updated_at}','{event_id}','{event_from_pg}','{event_from_redis}');
            """.format(
                schema=schema,
                updated_at=obj['updated_at'],
                event_id=obj['event_id'],
                event_from_pg=json.dumps(obj['event_from_pg']),
                event_from_redis=json.dumps(obj['event_from_redis']),
            ),
        )


def init_activity_events_verification(  # pylint: disable=C0103
        load_json, pgsql, datafiles_by_shard,
):
    for i, datafile in enumerate(datafiles_by_shard):
        init_doc = load_json(datafile)
        schema = SHARDS[i]
        _prepare_activity_events_verification(pgsql, schema, init_doc)


def get_verification_events(pgsql, schema, cluster=PG_CLUSTER):
    cursor = pgsql[cluster].cursor()
    cursor.execute(
        """
        SELECT event_id, updated_at, event_from_pg,
               event_from_redis
        FROM {}.activity_events_verification;
        """.format(
            schema,
        ),
    )
    events = [
        {
            'event_id': row[0],
            'updated_at': row[1].isoformat(),
            'event_from_pg': row[2],
            'event_from_redis': row[3],
        }
        for row in cursor
    ]
    return sorted(events, key=lambda event: event['event_id'])
