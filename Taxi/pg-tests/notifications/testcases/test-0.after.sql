INSERT INTO communications.notifications (
    order_id,
    x_yandex_login,
    ts,
    tanker_key,
    notification_type,
    notification_title,
    notification_text,
    intent,
    source,
    personal_phone_id,
    taxi_user_id,
    delivered
)
VALUES
    ('6776feef-01bb-400c-ab48-840fc00e0690'::UUID, NULL, '2020-12-31T18:00:00.0000+03:00'::timestamptz, 'cancel_card_failed', 'sms', NULL, 'text', 'intent', 'admin', NULL, NULL, NULL)
    ('6776feef-01bb-400c-ab48-840fc00e0690'::UUID, NULL, '2021-01-01T01:00:00.0000+03:00'::timestamptz, 'cancel_card_failed', 'sms', NULL, 'text', 'intent', 'admin', NULL, NULL, NULL)
    ('6776feef-01bb-400c-ab48-840fc00e0690'::UUID, NULL, '2021-01-01T05:00:00.0000+03:00'::timestamptz, 'cancel_card_failed', 'sms', NULL, 'text', 'intent', 'admin', NULL, NULL, NULL)
    ('6776feef-01bb-400c-ab48-840fc00e0690'::UUID, NULL, '2021-01-01T11:00:00.0000+03:00'::timestamptz, 'cancel_card_failed', 'sms', NULL, 'text', 'intent', 'admin', NULL, NULL, NULL)
