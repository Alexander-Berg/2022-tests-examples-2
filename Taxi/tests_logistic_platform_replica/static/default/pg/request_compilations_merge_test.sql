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
(1, '_', '_', '_', 0, '_', '13aad1ae-c205-42e8-94e1-e7c96728d738', 'PG_DATA_STRING_PG1', 'first_employer', 'request_code1',
    'canceled', 1743399569, 1743399579, 'min_by_request', '123456789abc', 'strizh'),
(2, '_', '_', '_', 0, '_', '07243441-785b-4a70-a2c2-bf48348f4225', 'PG_DATA_STRING_PG2', 'second_employer', 'request_code2',
    'unknown', 17416948410, 1741694862, 'unknown', 'qwerty', 'lavka'),
(3, '_', '_', '_', 0, '_', '09c7720b-8e6c-4d30-bd73-5d52916be754', 'PG_DATA_STRING_PG3', 'first_employer', 'request_code5', 
    'finished', 1771161946, 1781161946, 'unknown', '124567abc', 'unknown'),
(4, '_', '_', '_', 0, '_', '288affa0-50e8-458e-8ab7-5bdb8938de7a', 'PG_DATA_STRING_PG4', 'first_employer', 'request_code6', 
    'canceled', 1770766632, 1770866632, 'min_by_request', 'some_id', 'market'),
(5, '_', '_', '_', 0, '_', '5d04acd2-aee3-4058-a194-57b6ddc635f5', 'PG_DATA_STRING_PG5', 'second_employer', 'request_code7', 
    'processing', 1770017115, 1772017125, 'another_policy', '124567abc', 'strizh'),
(6, '_', '_', '_', 0, '_', '0000acd2-aee3-4058-a194-57b6ddc635f5', 'PG_DATA_STRING_PG6', 'first_employer', 'request_code1',
    'processing', 1770017115, 1770017125, 'min_by_request', '12456789abc', 'strizh');