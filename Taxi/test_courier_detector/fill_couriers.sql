INSERT INTO eats_proactive_support.courier_on_orders
(order_nr, driver_profile_id, claim_id, waybill_ref, corp_client_id,
 place_location, autostatus_config)
VALUES
    ('123', 'driver_profile_id_1', 'claim_id_123', 'waybill_ref_123',
     'corp_client_id_1', point(30.1,50.1), '{}'
    ),
    ('124', 'driver_profile_id_2', 'claim_id_123', 'waybill_ref_123',
     'corp_client_id_1', point(30.1,50.1), '{}'
    ),
    ('125', 'driver_profile_id_1', 'claim_id_125', 'waybill_ref_125',
     'corp_client_id_1', point(30.1,50.1), '{}'
    ),
    ('126', 'driver_profile_id_3', 'claim_id_125', 'waybill_ref_125',
     'corp_client_id_1', point(30.1,50.1), '{}'
    ),
    ('127', 'driver_profile_id_4', 'claim_id_123', 'waybill_ref_125',
     'corp_client_id_1', point(30.1,50.1), '{}'
    ),
    ('128', 'driver_profile_id_5', 'claim_id_123', 'waybill_ref_125',
     'corp_client_id_1', point(30.1,50.1), '{}'
    );

INSERT INTO eats_proactive_support.courier_positions
(driver_profile_id, claim_point_id, location_timestamp, location)
VALUES
    -- near point
    ('driver_profile_id_1', 1000, '1970-01-01T00:00:00+00:00',
     point(30.1000,50.1)),
    ('driver_profile_id_1', 1000, '1970-01-01T00:03:00+00:00',
     point(30.1000,50.1)),
    -- good GPS
    ('driver_profile_id_1', 1000, '1970-01-01T00:03:01+00:00',
     point(30.1006,50.1)),
    ('driver_profile_id_1', 1000, '1970-01-01T00:03:05+00:00',
     point(30.1008,50.1)),
    ('driver_profile_id_1', 1000, '1970-01-01T00:03:10+00:00',
     point(30.1010,50.1)),
    ('driver_profile_id_1', 1000, '1970-01-01T00:03:15+00:00',
     point(30.1012,50.1)),
    ('driver_profile_id_1', 1000, '1970-01-01T00:03:20+00:00',
     point(30.1013,50.1)),
    ('driver_profile_id_1', 1000, '1970-01-01T00:03:25+00:00',
     point(30.1016,50.1)),

    -- near point
    ('driver_profile_id_1', 1010, '1970-01-01T00:00:00+00:00',
     point(30.1000,50.1)),
    ('driver_profile_id_1', 1010, '1970-01-01T00:03:00+00:00',
     point(30.1000,50.1)),
    -- good GPS
    ('driver_profile_id_1', 1010, '1970-01-01T00:03:01+00:00',
     point(30.1006,50.1)),
    ('driver_profile_id_1', 1010, '1970-01-01T00:03:05+00:00',
     point(30.1008,50.1)),
    ('driver_profile_id_1', 1010, '1970-01-01T00:03:10+00:00',
     point(30.1010,50.1)),
    ('driver_profile_id_1', 1010, '1970-01-01T00:03:15+00:00',
     point(30.1012,50.1)),
    ('driver_profile_id_1', 1010, '1970-01-01T00:03:20+00:00',
     point(30.1014,50.1)),
    ('driver_profile_id_1', 1010, '1970-01-01T00:03:25+00:00',
     point(30.1016,50.1)),

    -- near point
    ('driver_profile_id_4', 1000, '1970-01-01T00:00:00+00:00',
     point(30.1000,50.1)),
    ('driver_profile_id_4', 1000, '1970-01-01T00:02:55+00:00',
     point(30.1000,50.1)),
    -- jump
    ('driver_profile_id_4', 1000, '1970-01-01T00:03:00+00:00',
     point(30.1006,50.1)),
    -- good GPS
    ('driver_profile_id_4', 1000, '1970-01-01T00:03:05+00:00',
     point(30.1008,50.1)),
    ('driver_profile_id_4', 1000, '1970-01-01T00:03:10+00:00',
     point(30.1010,50.1)),
    ('driver_profile_id_4', 1000, '1970-01-01T00:03:15+00:00',
     point(30.1012,50.1)),
    ('driver_profile_id_4', 1000, '1970-01-01T00:03:20+00:00',
     point(30.1013,50.1)),
    ('driver_profile_id_4', 1000, '1970-01-01T00:03:25+00:00',
     point(30.1016,50.1)),

    -- near point
    ('driver_profile_id_5', 1000, '1970-01-01T00:00:00+00:00',
     point(30.1000,50.1)),
    ('driver_profile_id_5', 1000, '1970-01-01T00:03:00+00:00',
     point(30.1000,50.1)),
    -- good GPS
    ('driver_profile_id_5', 1000, '1970-01-01T00:03:01+00:00',
     point(30.1006,50.1)),
    ('driver_profile_id_5', 1000, '1970-01-01T00:03:05+00:00',
     point(30.1008,50.1)),
    ('driver_profile_id_5', 1000, '1970-01-01T00:03:10+00:00',
     point(30.1010,50.1)),
    ('driver_profile_id_5', 1000, '1970-01-01T00:03:15+00:00',
     point(30.1012,50.1)),
    -- very far
    ('driver_profile_id_5', 1000, '1970-01-01T00:03:20+00:00',
     point(30.1022,50.1)),
    ('driver_profile_id_5', 1000, '1970-01-01T00:03:25+00:00',
     point(30.1032,50.1));


INSERT INTO eats_proactive_support.courier_analyzes
(driver_profile_id, claim_point_id)
VALUES
    ('driver_profile_id_1', 1001);
