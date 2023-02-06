INSERT INTO crm_admin.segment(
    yql_shared_url,
    yt_table,
    control,
    created_at
)
VALUES
(
    'yql_shared_url',
    'yt_table',
    0,
    '2020-12-25T00:00:00+03:00'
);

INSERT INTO crm_admin.group(
    segment_id,
    params,
    created_at,
    updated_at
)
VALUES
(
    1,
    ('{"name": "test", "state": "NEW"}')::jsonb,
    '2020-03-20 01:00:00',
    '2020-03-20 01:00:00'
);

UPDATE crm_admin.group
SET params = params || '{"state": "SENT"}'
WHERE id=1;

DELETE FROM crm_admin.group
WHERE id=1;
