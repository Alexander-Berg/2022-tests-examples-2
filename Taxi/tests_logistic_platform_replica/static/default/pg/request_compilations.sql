WITH
  emulation_date_bound AS (VALUES(extract(epoch from timezone('utc', now()))::BIGINT - 2592000))
INSERT INTO request_compilations (
    history_event_id,
    history_user_id, 
    history_originator_id, 
    history_action, 
    history_timestamp, 
    history_comment, 
    request_id, 
    data, 
    employer_code, 
    request_code, 
    request_status, 
    created_at, 
    delivery_date, 
    delivery_policy, 
    recipient_phone_pd_id,
    operator_id 
) VALUES
(1, '_', '_', '_', 0, '_', 'PGaad1ae-c205-42e8-94e1-e7c96728d738', 'PG_DATA_STRING_1', 'first_employer', 'request_code1', 
    'canceled', 1800000000, 1800000010, 'min_by_request', '123456789abc', 'strizh'),
(2, '_', '_', '_', 0, '_', 'PG243441-785b-4a70-a2c2-bf48348f4225', 'PG_DATA_STRING_2', 'second_employer', 'request_code2', 
    'unknown', 1800000005, 1800000011, 'unknown', 'qwerty', 'lavka'),
(3, '_', '_', '_', 0, '_', 'PG6fb2df-15b9-4855-9cc1-e51f5f1bc674', 'PG_DATA_STRING_3', 'third_employer', 'request_code3', 
    'processing', 1800001005, 1800001011, 'interval_with_fees', 'some_pd_id', 'strizh'),
(4, '_', '_', '_', 0, '_', 'PG21c950-1024-4be1-9ba5-33e6dae2da4a', 'PG_DATA_STRING_4', 'third_employer', 'request_code1', 
    'canceled', 1800000005, 1800005011, 'interval_with_fees', 'qwerty', 'unknown'),
(5, '_', '_', '_', 0, '_', 'PGdc50f7-5654-4f38-a669-de2aee65aeac', 'PG_DATA_STRING_5', 'fourth_employer', 'request_code4', 
    'processing', 1800000000, 1800000110, 'min_by_request', 'one_two', 'drozd'),
(6, '_', '_', '_', 0, '_', 'PGc7720b-8e6c-4d30-bd73-5d52916be754', 'PG_DATA_STRING_6', 'first_employer', 'request_code5', 
    'finished', 1800001000, 1800100110, 'unknown', '124567abc', 'unknown'),
(7, '_', '_', '_', 0, '_', 'PG8affa0-50e8-458e-8ab7-5bdb8938de7a', 'PG_DATA_STRING_7', 'first_employer', 'request_code6', 
    'canceled', 1800002000, 1800200210, 'min_by_request', 'some_id', 'market'),
(8, '_', '_', '_', 0, '_', 'PG04acd2-aee3-4058-a194-57b6ddc635f5', 'PG_DATA_STRING_8', 'second_employer', 'request_code7', 
    'processing', 1800000001, 1800000020, 'another_policy', '124567abc', 'strizh'),
(9, '_', '_', '_', 0, '_', 'PG05acd2-aee3-4058-a194-57b6ddc635f5', 'PG_DATA_STRING_9', 'second_employer', 'request_code8', 
    'processing', (TABLE emulation_date_bound) - 10, 1800000020, 'another_policy', '124567abc', 'strizh'),
(10, '_', '_', '_', 0, '_', 'PG65acd2-aee3-4058-a194-57b6ddc635f5', 'PG_DATA_STRING_10', 'other_employer', 'request_code8', 
    'other', (TABLE emulation_date_bound) + 10, 1800000020, 'other', 'other', 'other');