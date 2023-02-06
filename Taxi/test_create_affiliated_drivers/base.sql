INSERT INTO rent.affiliations
    (record_id,
     park_id, local_driver_id,
     original_driver_park_id, original_driver_id,
     creator_uid, created_at_tz,
     state)
VALUES ('a1',
        'park', NULL,
        'odp1', 'od1',
        'c', NOW(),
        'accepted'),
       ('a2',
        'park', 'ld1',
        'odp2', 'od2',
        'c', NOW(),
        'active')
