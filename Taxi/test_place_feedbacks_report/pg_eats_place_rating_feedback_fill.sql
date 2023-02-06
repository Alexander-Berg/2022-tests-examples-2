INSERT INTO eats_place_rating.feedback_reports
(
    partner_id,
    idempotency_key,
    personal_uuid,
    file_format,
    filter,
    status,
    error_info
) VALUES (1, '1au', '1', 'csv', ('{1, 2, 3}', '{3, 5}', '{1, 2}', '2020-11-24'::DATE, '2020-11-24'::DATE), 'new', '');

