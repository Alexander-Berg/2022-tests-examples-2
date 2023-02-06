INSERT INTO eats_place_rating.feedback_reports
(
    partner_id,
    idempotency_key,
    personal_uuid,
    file_format,
    status,
    is_cache_cleared
) VALUES
(1, 'idemp1', 'uuid1', 'csv', 'done', false),
(2, 'idemp2', 'uuid2', 'csv', 'new', false),
(3, 'idemp3', 'uuid3', 'xls', 'fail', false),
(4, 'idemp4', 'uuid4', 'csv', 'table_created', false),
(5, 'idemp5', 'uuid5', 'csv', 'table_created', true);
