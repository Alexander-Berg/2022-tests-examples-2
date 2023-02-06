INSERT INTO crm_hub.efficiency_sending (
    id,
    state,
    table_path,
    created_at
)
VALUES
(
    '00000000000000000000000000000001',
    'processing',
    '//home/table01',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000011',
    'new',
    '//home/table11',
    now() AT TIME ZONE 'UTC'
),
(
    '00000000000000000000000000000012',
    'error',
    '//home/table12',
    now() AT TIME ZONE 'UTC'
);
