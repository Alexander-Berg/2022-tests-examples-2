INSERT INTO dispatch.dispatches_history
    (id, order_id, performer_id, dispatch_type, version, status, order_info, performer_info, updated, status_meta, wave)
VALUES
    ('6776feef-01bb-400c-ab48-840fc00e0693'::UUID, 'order_id3', 'performer_id3', 'dispatch_type3', 1, 'finished'::dispatch.dispatch_status_t, '{}', '{}', '2021-06-01T12:01:00.0000+03:00'::timestamptz, '{}', 0),
    ('6776feef-01bb-400c-ab48-840fc00e0694'::UUID, 'order_id4', 'performer_id4', 'dispatch_type4', 1, 'finished'::dispatch.dispatch_status_t, '{}', '{}', '2021-06-01T12:02:00.0000+03:00'::timestamptz, '{}', 0),
    ('6776feef-01bb-400c-ab48-840fc00e0695'::UUID, 'order_id5', 'performer_id5', 'dispatch_type5', 1, 'finished'::dispatch.dispatch_status_t, '{}', '{}', '2021-06-01T12:03:00.0000+03:00'::timestamptz, '{}', 0);
