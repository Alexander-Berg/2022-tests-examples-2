INSERT INTO eats_restapp_communications.place_digest_send_schedule
    (place_id, is_active, timezone, to_send_at, sent_at)
VALUES
    (11, true, 'Europe/Moscow', '10:00', '2022-06-20T10:03:00+0300'),
    (22, true, 'Europe/Saratov', '09:00', '2022-06-20T09:05:00+0400'),
    (33, true, 'Asia/Yekaterinburg', '08:00', '2022-06-20T08:04:00+0500'),
    (44, false, 'Europe/Moscow', NULL, NULL);
