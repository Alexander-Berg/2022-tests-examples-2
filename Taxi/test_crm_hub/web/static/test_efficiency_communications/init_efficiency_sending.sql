INSERT INTO crm_hub.efficiency_sending (
    id,
    state,
    table_path,
    created_at
)
VALUES
(
    '00000000000000000000000000000001',
    'new',
    '//home/table01',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000002',
    'new',
    '//home/table01',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000003',
    'new',
    '//home/table01',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000004',
    'new',
    '//home/table01',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000005',
    'new',
    '//home/table01',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000011',
    'error',
    '//home/table11',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000012',
    'finished',
    '//home/table12',
    now() AT TIME ZONE 'UTC'
);
