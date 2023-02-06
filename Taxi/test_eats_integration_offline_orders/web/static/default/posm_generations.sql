INSERT INTO posm_generations (
    place_id,
    status,
    author,
    comment,
    tables,
    idempotency_token,
    created_at,
    deleted_at
)
VALUES
(
    'place_id__1',
    'in_progress',
    'username',
    NULL,
    '[{"id": 1, "uuid": "uuid__1", "table_pos_name": "table_id__1"}]',
    'unique-idempotency-token-1',
    '2022-05-17 17:00:00',
    NULL
),
(
    'place_id__1',
    'done',
    'another_user',
    NULL,
    '[{"id": 1, "uuid": "table_uuid__1", "table_pos_name": "1"},{"id": 2, "uuid": "table_uuid__2", "table_pos_name": "2"}]',
    'unique-idempotency-token-2',
    '2022-05-17 18:00:00',
    NULL
),
(
    'place_id__1',
    'created',
    'username',
    NULL,
    '[{"id": 2, "uuid": "uuid__2", "table_pos_name": "table_id__2"}]',
    'unique-idempotency-token-3',
    '2022-05-17 19:00:00',
    NULL
),
(
    'place_id__1',
    'done',
    'username',
    NULL,
    '[{"id": 2, "uuid": "uuid__2", "table_pos_name": "table_id__2"}]',
    'unique-idempotency-token-4',
    '2022-05-17 19:00:00',
    NOW()
),
(
    'place_id__2',
    'done',
    'another_user',
    NULL,
    '[{"id": 2, "uuid": "uuid__2", "table_pos_name": "table_id__2"}]',
    'unique-idempotency-token-5',
    '2022-05-17 18:00:00',
    NULL
)
;
