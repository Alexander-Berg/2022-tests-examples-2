INSERT
INTO eats_logistics_performer_payouts.shift_fraud_event_cache
    (driver_uuid, time, event_type)
VALUES
    ('00D5', '2020-06-30T07:55:00+00:00', 'root_protector'),
    ('CC02', '2020-06-30T07:55:00+00:00', 'root_protector'),
    ('00A3', '2020-06-30T07:55:00+00:00', 'fake_gps_protector'),
    ('CFD5', '2020-06-30T07:55:00+00:00', 'fake_gps_protector'),
    ('00A3', '2020-06-30T08:05:00+00:00', 'fake_gps_protector'),
    ('00A3', '2020-06-30T07:25:00+00:00', 'fake_gps_protector'),
    ('00A3', '2020-06-30T07:35:00+00:00', 'fake_gps_protector'),
    ('0001', '2020-06-30T10:30:00+03:00', 'fake_gps_protector'),
    ('0002', '2020-06-30T10:50:00+03:00', 'root_protector'),
    ('0003', '2020-06-30T11:00:00+03:00', 'fake_gps_protector'),
    ('0004', '2020-06-30T11:30:00+03:00', 'fake_gps_protector'),
    ('0005', '2020-06-30T11:35:00+03:00', 'fake_gps_protector');

