INSERT INTO dispatch_airport_partner_protocol.parking_drivers AS drivers (driver_id,
                                                                          parking_id,
                                                                          created_ts,
                                                                          updated_ts,
                                                                          heartbeated,
                                                                          latitude,
                                                                          longitude)
VALUES ('dbid_uuid1',
        'parking_lot1',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        0,
        0)
        ,
       ('dbid_uuid2',
        'parking_lot1',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        '2020-02-02T00:00:00+00:00',
        10,
        20)
;
