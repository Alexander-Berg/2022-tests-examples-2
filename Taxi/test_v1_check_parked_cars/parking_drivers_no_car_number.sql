INSERT INTO dispatch_airport_partner_protocol.parking_drivers AS drivers (driver_id,
                                                                          parking_id,
                                                                          created_ts,
                                                                          updated_ts,
                                                                          heartbeated,
                                                                          car_number_normalized,
                                                                          latitude,
                                                                          longitude,
                                                                          has_allowed_provider)
VALUES ('dbid_uuid1',
        'parking_lot1',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        'A111AA',
        0,
        0,
        TRUE),
       ('dbid_uuid2',
        'parking_lot1',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        NULL,
        0,
        0,
        TRUE),
       ('dbid_uuid3',
        'parking_lot1',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        'C112CC',
        0,
        0,
        TRUE),
       ('dbid_uuid4',
        'parking_lot1',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        NULL,
        0,
        0,
        TRUE),
       ('dbid_uuid4',
        'parking_lot2',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        NULL,
        0,
        0,
        TRUE),
       ('dbid_uuid5',
        'parking_lot2',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        NULL,
        0,
        0,
        TRUE)
;
