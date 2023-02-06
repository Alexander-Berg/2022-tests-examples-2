INSERT INTO crm_admin.quicksegment_schemas (
    audience,
    major_ver,
    minor_ver,
    name,
    format,
    body,
    created_at
)
VALUES
(
    'User',
    0,  -- major_ver
    123,  -- minor_ver
    'table_schema',
    'yaml',
    '---',
    '2020-11-24 01:00:00'
),
(
    'User',
    0,  -- major_ver
    123,  -- minor_ver
    'filter_schema',
    'yaml',
    '---',
    '2020-11-24 01:00:00'
),
(
    'User',
    0,  -- major_ver
    123,  -- minor_ver
    'input_schema',
    'json',
    '[{"id": "id1", "type": "type1", "label": "label1", "key1": "value1"}]',
    '2020-11-24 01:00:00'
),
(
    'User',
    1,  -- major_ver
    123,  -- minor_ver
    'table_schema',
    'yaml',
    '---',
    '2020-11-24 01:00:00'
),
(
    'User',
    1,  -- major_ver
    123,  -- minor_ver
    'filter_schema',
    'yaml',
    '---',
    '2020-11-24 01:00:00'
),
(
    'User',
    1,  -- major_ver
    123,  -- minor_ver
    'input_schema',
    'json',
    '[]',
    '2020-11-24 01:00:00'
),
(
    'User',
    1,  -- major_ver
    345,  -- minor_ver
    'table_schema',
    'yaml',
    '---',
    '2020-11-24 01:00:00'
),
(
    'User',
    1,  -- major_ver
    345,  -- minor_ver
    'filter_schema',
    'yaml',
    '---',
    '2020-11-24 01:00:00'
),
(
    'User',
    1,  -- major_ver
    345,  -- minor_ver
    'input_schema',
    'json',
    '[{"id": "id1", "type": "type1", "label": "label1", "key1": "value1"}]',
    '2020-11-24 01:00:00'
),
(
    'Driver',
    0,  -- major_ver
    12,  -- minor_ver
    'table_schema',
    'yaml',
    '---',
    '2020-11-24 01:00:00'
),
(
    'Driver',
    0,  -- major_ver
    12,  -- minor_ver
    'filter_schema',
    'yaml',
    '---',
    '2020-11-24 01:00:00'
),
(
    'Driver',
    0,  -- major_ver
    12,  -- minor_ver
    'input_schema',
    'json',
    '[{
        "id": "id2", "type": "type2", "label": "label2", "key2": "value2",
        "campaign_type": "oneshot"
    }]',
    '2020-11-24 01:00:00'
),
(
    'Driver',
    1,  -- major_ver
    456,  -- minor_ver
    'table_schema',
    'json',
    '{"tables": [{"name": "main", "path": "path"}], "root_table": "main"}',
    '2020-11-24 01:00:00'
),
(
    'Driver',
    1,  -- major_ver
    456,  -- minor_ver
    'filter_schema',
    'json',
    '{"filters": [{"id": "main", "where": "main.col > ${var}"}], "targets": "main"}',
    '2020-11-24 01:00:00'
),
(
    'Driver',
    1,  -- major_ver
    456,  -- minor_ver
    'input_schema',
    'json',
    '[{
        "id": "id2", "type": "type2", "label": "label2", "key2": "value2",
        "campaign_type": "oneshot"
    }]',
    '2020-11-24 01:00:00'
);


INSERT INTO crm_admin.campaign
(
    id,
    name,
    entity_type,
    trend,
    discount,
    state,
    owner_name,
    is_regular,
    created_at,
    updated_at
)
VALUES
(
    1,  -- campaign id
    'user campaign',
    'User',
    'trend',
    True,
    'NEW',
    'user',
    False,  -- is_regular
    '2020-12-23 01:00:00',
    '2020-12-23 01:00:00'
),
(
    2,  -- campaign id
    'driver campaign',
    'Driver',
    'trend',
    True,
    'NEW',
    'user',
    False,  -- is_regular
    '2020-12-23 01:00:00',
    '2020-12-23 01:00:00'
),
(
    3,  -- campaign id
    'regular campaign',
    'Driver',
    'trend',
    True,
    'NEW',
    'user',
    True,  -- is_regular
    '2020-12-23 01:00:00',
    '2020-12-23 01:00:00'
);
