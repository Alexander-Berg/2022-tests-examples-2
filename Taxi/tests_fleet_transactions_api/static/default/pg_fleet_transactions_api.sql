INSERT INTO fleet_transactions_api.park_transaction_categories VALUES
(
    'park_id_test',
    1, -- category index in park
    'Штрафы',
    'abcd1234cdef5678',
    TRUE,
    current_timestamp,
    current_timestamp
),
(
    'park_id_test',
    2, -- category index in park
    'по Расписанию',
    'zyx9876543210cba',
    FALSE,
    current_timestamp,
    current_timestamp
),
(
    '7ad35b',
    1, -- category index in park
    'Барщина',
    'abcd1234cdef5678',
    FALSE,
    current_timestamp,
    current_timestamp
),
(
    '7ad35b',
    2, -- category index in park
    'Оброк',
    'zyx9876543210cba',
    TRUE,
    current_timestamp,
    current_timestamp
);
