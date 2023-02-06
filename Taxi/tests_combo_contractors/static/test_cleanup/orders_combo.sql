INSERT INTO combo_contractors.customer_order (order_id, dbid_uuid, updated, taxi_status,
                                              destination, chunk_id, event_index, ready_status,
                                              tariff_class, tariff_zone, has_comment, source, calc_alternative_type)
VALUES
    -- Combo with two rides, both are pending. None should be deleted.
    ('order_id0', 'dbid_uuid0', (NOW() AT TIME ZONE 'UTC') - INTERVAL '200 seconds',
     'transporting', '(37.66, 55.71)',
     0, 0, 'pending', 'econom', 'moscow',
     FALSE, '(37.66, 55.71)', ''),
    ('order_id1', 'dbid_uuid0', (NOW() AT TIME ZONE 'UTC') - INTERVAL '200 seconds',
     'transporting', '(37.66, 55.71)',
     0, 0, 'pending', 'econom', 'moscow',
     FALSE, '(37.66, 55.71)', ''),

    -- Combo with two rides, one is finished and another is pending. None should be deleted.
    ('order_id2', 'dbid_uuid1', (NOW() AT TIME ZONE 'UTC') - INTERVAL '200 seconds',
     'transporting', '(37.66, 55.71)',
     1, 0, 'finished', 'econom', 'moscow',
     FALSE, '(37.66, 55.71)', ''),
    ('order_id3', 'dbid_uuid1', (NOW() AT TIME ZONE 'UTC') - INTERVAL '200 seconds',
     'transporting', '(37.66, 55.71)',
     1, 0, 'pending', 'econom', 'moscow',
     FALSE, '(37.66, 55.71)', ''),

    -- Combo with two rides, both are finished and ttl passed. Both should be deleted.
    ('order_id4', 'dbid_uuid2', (NOW() AT TIME ZONE 'UTC') - INTERVAL '200 seconds',
     'transporting', '(37.66, 55.71)',
     2, 0, 'finished', 'econom', 'moscow',
     FALSE, '(37.66, 55.71)', ''),
    ('order_id5', 'dbid_uuid2', (NOW() AT TIME ZONE 'UTC') - INTERVAL '200 seconds',
     'transporting', '(37.66, 55.71)',
     2, 0, 'finished', 'econom', 'moscow',
     FALSE, '(37.66, 55.71)', '');
