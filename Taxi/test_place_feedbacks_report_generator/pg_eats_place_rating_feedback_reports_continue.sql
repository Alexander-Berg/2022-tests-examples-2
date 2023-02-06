INSERT INTO eats_place_rating.feedback_reports
(
    partner_id,
    idempotency_key,
    personal_uuid,
    file_format,
    status,
    filter
) VALUES 
(123, 'idemp1', 'ea535bef-99e0-4340-b007-e2eca908bedb', 'csv', 'data_received', ROW(ARRAY[1,2,3], ARRAY[1,2,3], ARRAY[1,2,3], '2017-03-14T00:00:00Z', '2017-03-15T00:00:00Z'))
