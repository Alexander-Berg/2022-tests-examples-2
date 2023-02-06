INSERT INTO eats_restapp_communications.place_digest_send_schedule
    (place_id, is_active, timezone, to_send_at, sent_at)
VALUES
    (11, true, 'Europe/Moscow', null, '2022-05-01 09:00:00+03:00'::timestamptz),
    (22, true, 'Europe/Moscow', null, '2022-05-01 09:00:00+03:00'::timestamptz),
    (33, true, 'Europe/Moscow', null, '2022-05-01 09:00:00+03:00'::timestamptz);
