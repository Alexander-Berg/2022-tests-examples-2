INSERT INTO eats_place_rating.feedback_reports
(
    partner_id,
    idempotency_key,
    personal_uuid,
    file_format,
    filter
) VALUES 
(123, 'idemp1', 'uuid123', 'csv', ROW(ARRAY[1,2,3], ARRAY[1,2,3], ARRAY[1,2,3], '2021-04-05T00:00:00Z', '2021-04-06T00:00:00Z')),
(222, 'idemp2', 'uuid256', 'csv', NULL),
(666, 'idemp3', 'uuid789', 'xls', ROW(ARRAY[1,2,3], ARRAY[1,2,3], ARRAY[1,2,3], '2021-04-05T00:00:00Z', '2021-04-06T00:00:00Z')),
(777, 'idemp4', 'uuid888', 'csv', ROW(ARRAY[10], ARRAY[1,2,3,4,5], ARRAY[109151,116160], '2021-04-05T00:00:00Z', '2021-04-06T00:00:00Z')),
(888, 'idemp5', 'uuid999', 'csv', ROW(ARRAY[]::integer[], ARRAY[]::integer[], ARRAY[136015], '2021-06-10T00:00:00Z', '2021-06-11T00:00:00Z')),
(999, 'idemp9', 'uuid9999', 'csv', ROW(ARRAY[1,2,3], ARRAY[1,2,3], ARRAY[1,2,3], '2020-04-05T00:00:00Z', '2020-04-06T00:00:00Z')),
(100, 'idemp6', 'uuid100', 'csv', (ARRAY[]::integer[], ARRAY[]::integer[], ARRAY[555], '2021-06-10T00:00:00Z', '2021-06-11T00:00:00Z'));
