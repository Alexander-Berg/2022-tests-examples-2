INSERT INTO dispatch.dispatches
    (id, order_id, performer_id, dispatch_type, version, status, order_info, performer_info, updated, status_meta, wave, eta)
VALUES
    ('6776feef-01bb-400c-ab48-840fc00e0690'::UUID, 'order_id0', 'performer_id0', 'dispatch_type0', 1, 'finished'::dispatch.dispatch_status_t, '{}', '{}', '2021-06-01T11:57:00.0000+03:00'::timestamptz, '{}', 0, 10),
    ('6776feef-01bb-400c-ab48-840fc00e0691'::UUID, 'order_id1', 'performer_id1', 'dispatch_type1', 1, 'finished'::dispatch.dispatch_status_t, '{}', '{}', '2021-06-01T11:58:00.0000+03:00'::timestamptz, '{}', 0, 10),
    ('6776feef-01bb-400c-ab48-840fc00e0692'::UUID, 'order_id2', 'performer_id2', 'dispatch_type2', 1, 'finished'::dispatch.dispatch_status_t, '{}', '{}', '2021-06-01T11:59:00.0000+03:00'::timestamptz, '{}', 0, 10),
    ('6776feef-01bb-400c-ab48-840fc00e0693'::UUID, 'order_id3', 'performer_id3', 'dispatch_type3', 1, 'finished'::dispatch.dispatch_status_t, '{}', '{}', '2021-06-01T12:01:00.0000+03:00'::timestamptz, '{}', 0, 10),
    ('6776feef-01bb-400c-ab48-840fc00e0694'::UUID, 'order_id4', 'performer_id4', 'dispatch_type4', 1, 'finished'::dispatch.dispatch_status_t, '{}', '{}', '2021-06-01T12:02:00.0000+03:00'::timestamptz, '{}', 0, 10),
    ('6776feef-01bb-400c-ab48-840fc00e0695'::UUID, 'order_id5', 'performer_id5', 'dispatch_type5', 1, 'finished'::dispatch.dispatch_status_t, '{}', '{}', '2021-06-01T12:03:00.0000+03:00'::timestamptz, '{}', 0, 10);
