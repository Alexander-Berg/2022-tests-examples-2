INSERT INTO dispatch_airport_partner_protocol.parking_drivers AS drivers (driver_id,
                                                                          parking_id,
                                                                          created_ts,
                                                                          updated_ts,
                                                                          heartbeated,
                                                                          latitude,
                                                                          longitude,
                                                                          driver_diagnostics_updated_ts)
VALUES ('dbid1_uuid1',
        'parking_lot1',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        0,
        0,
        NULL),
       ('dbid2_uuid2',
        'parking_lot1',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        0,
        0,
        '2020-02-02T00:00:00+00:00'),
       ('dbid3_uuid3',
        'parking_lot1',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        0,
        0,
        '2020-02-01T00:00:00+00:00');
