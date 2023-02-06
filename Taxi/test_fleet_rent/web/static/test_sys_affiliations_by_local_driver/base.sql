INSERT INTO rent.affiliations
(record_id, state,
 park_id, local_driver_id,
 original_driver_park_id, original_driver_id,
 creator_uid, created_at_tz,
 modified_at_tz)
VALUES ('record_id1', 'park_recalled',
        'park_id', 'local_driver_id1',
        'original_driver_park_id1', 'original_driver_id1',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00'),
       ('record_id2', 'new',
        'park_id', 'local_driver_id1',
        'original_driver_park_id2', 'original_driver_id2',
        'creator_uid', '2020-01-02+00',
        '2020-01-02+00')
