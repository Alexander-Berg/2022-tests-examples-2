INSERT INTO taxi_db_postgres_atlas_backend.source (
    source_cluster,
    source_type,
    source_path,
    source_name,
    description,
    is_partitioned,
    partition_key,
    partition_template,
    author,
    created_at,
    changed_by,
    changed_at,
    data_updated_at
) VALUES
(  -- source_id = 1
    'hahn',
    'chyt',
    '//home/some/path',
    'first_test_source',
    'first test source',
    False,
    '',
    '',
    '@source_author',
    to_timestamp(1355314332)::timestamp,  -- 2012-12-12 12:12:12+00:00
    '@source_author',
    to_timestamp(1638483742)::timestamp,  -- 2021-12-02 22:22:22+00:00
    to_timestamp(946684800)::timestamp  -- 2000-01-01 00:00:00+00:00
),
(  -- source_id = 2
    'arnold',
    'chyt',
    '//home/other/path',
    'second_test_source',
    'second test source',
    True,
    'timestamp',
    '%Y-%m',
    '@other_source_author',
    to_timestamp(1293840000)::timestamp,  -- 2011-01-01 00:00:00+00:00
    '@source_changer',
    to_timestamp(1325376000)::timestamp,  -- 2012-01-01 00:00:00+00:00
    to_timestamp(1262304000)::timestamp  -- 2010-01-01 00:00:00+00:00
),
(  -- source_id = 3
    'atlastest_mdb',
    'clickhouse',
    'some_database.some_table',
    'third_test_source',
    'third test source',
    False,
    '',
    '',
    '@source_author',
    to_timestamp(1293840001)::timestamp,  -- 2011-01-01 00:00:01+00:00
    '@other_source_changer',
    to_timestamp(1325376001)::timestamp,  -- 2012-01-01 00:00:01+00:00
    to_timestamp(1262304001)::timestamp  -- 2010-01-01 00:00:01+00:00
),
(  -- source_id = 4
    'atlas_mdb',
    'clickhouse',
    'other_database.other_table',
    'fourth_test_source',
    'fourth test source',
    False,
    '',
    '',
    '@another_source_author',
    to_timestamp(1293840002)::timestamp,  -- 2011-01-01 00:00:02+00:00
    '@another_source_changer',
    to_timestamp(1325376002)::timestamp,  -- 2012-01-01 00:00:02+00:00
    to_timestamp(1262304002)::timestamp  -- 2010-01-01 00:00:02+00:00
)
;
