INSERT INTO signal_device_api.last_tags_deleted
(last_deleted_tag_at, updated_at)
VALUES
('2020-12-12 00:00:00+00:00', CURRENT_TIMESTAMP);

INSERT INTO signal_device_api.statuses (
    id,
    cpu_temperature,
    disk_bytes_free_space,
    disk_bytes_total_space,
    root_bytes_free_space,
    root_bytes_total_space,
    ram_bytes_free_space,
    software_version,
    uptime_ms,
    status_at,
    created_at,
    updated_at
)
VALUES
(1, 2, 2, 8, 2, 2, 8, '12', 30, '2019-11-12 00:00:00+00:00', '2019-11-12 00:00:00+00:00',
 '2020-12-11 23:59:59+00:00'
),
(2, 2, 2, 8, 2, 2, 8, '12', 30, '2019-11-12 00:00:00+00:00', '2019-11-12 00:00:00+00:00',
 '2020-12-12 00:00:00+00:00'
),
(3, 2, 2, 8, 2, 2, 8, '12', 30, '2019-11-12 00:00:00+00:00', '2019-11-12 00:00:00+00:00',
 '2020-12-12 00:02:00+00:00'
),
(4, 2, 2, 8, 2, 2, 8, '12', 30, '2019-11-12 00:00:00+00:00', '2019-11-12 00:00:00+00:00',
 '2020-12-12 00:03:00+00:00'
),
(5, 2, 2, 8, 2, 2, 8, '12', 30, '2019-11-12 00:00:00+00:00', '2019-11-12 00:00:00+00:00',
 '2020-12-12 00:05:00+00:00'
),
(6, 2, 2, 8, 2, 2, 8, '12', 30, '2019-11-12 00:00:00+00:00', '2019-11-12 00:00:00+00:00',
 '2020-12-12 00:10:00+00:00'
);

INSERT INTO signal_device_api.park_device_profiles
(
    park_id,
    device_id,
    created_at,
    updated_at,
    is_active
)
VALUES
(
 'p1', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 'p4', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, FALSE
),
(
 'p2', 4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 'p3', 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 'p5', 6, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 'p7', 7, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 'p8', 8, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 'p8', 9, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 'p8', 10, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 'p9', 11, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 'p10', 12, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 'p11', 13, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 'p12', 14, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
);

INSERT INTO signal_device_api.car_device_bindings (
    id,
    park_id,
    car_id,
    device_id,
    created_at,
    updated_at,
    is_tag_active
)
VALUES
(
 '1', 'p1', 'c1', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 '2', 'p4', 'c1', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 '4', 'p2', 'c2', 4, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, FALSE
),
(
 '5', 'p3', 'c3', 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 '6', 'p5', 'c5', 6, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 '7', 'p7', 'c7', 7, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 '8', 'p8', 'c8', 8, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 '9', 'p8', 'c9', 9, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 '10', 'p8', 'c10', 10, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 '11', 'p9', 'c11', 11, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 '12', 'p10', 'c12', 12, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 '13', 'p11', 'c13', 13, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE
),
(
 '14', 'p12', 'c14', 14, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, FALSE
);

INSERT INTO signal_device_api.events
(
    id,
    device_id,
    created_at,
    updated_at,
    event_id,
    public_event_id,
    event_at,
    event_type,
    gnss_latitude,
    gnss_longitude,
    park_id
)
VALUES
-- driver_lost < curr - 5min && driver_found < driver_lost
(
    1,
    7,
    '2020-02-27T13:00:00',
    '2020-02-27T13:00:00',
    'fafs6e6e1331b3a7d35c585983076a',
    'fasfd7ec-30f6-43cf-94a8-911bc8fe404c',
    '2020-12-12T00:14:59+00:00',
    'sleep',
    54.99250000,
    73.36861111,
    'p7'
),
(
    2,
    7,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    '5e9afs6e5963785801eed76c4322b394',
    '54b3d7ec-30f6-43cf-94a8-afs6e8fe404c',
    '2020-12-12T00:11:59+00:00',
    'driver_lost',
    54.99550072,
    72.94622044,
    'p7'
),
(
    3,
    7,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    '5afs6e875963785801eed76c4322b394',
    '54b38580-30f6-8580-94a8-911bc8fe404c',
    '2020-12-12T00:10:58+00:00',
    'driver_found',
    54.99550072,
    72.94622044,
    'p7'
),
-- driver_lost >= curr - 5min && driver_found < driver_lost
(
    4,
    8,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    '85800875963785801eed76c4322b394',
    '54b3d7ec-30f6-43cf-8580-911bc8fe404c',
    '2020-12-12T00:15:02+00:00',
    'driver_lost',
    54.99550072,
    72.94622044,
    'p8'
),
(
    5,
    8,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    '5e94c0875963785801eed858022b394',
    '546378ec-6378-43cf-94a8-911bc8fe404c',
    '2020-12-01T23:55:00+00:00',
    'driver_lost',
    54.99550072,
    72.94622044,
    'p8'
),
(
    6,
    8,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    '63780875963785801eed76c4322b394',
    '54b3d7ec-6378-43cf-94a8-911bc8fe404c',
    '2020-12-12T00:15:01+00:00',
    'driver_found',
    54.99550072,
    72.94622044,
    'p8'
),
-- driver_found > driver_lost
(
    7,
    9,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    '5e94c087596322b301eed76c4322b394',
    '54b3d7ec-22b3-43cf-94a8-911bc8fe404c',
    '2020-02-26T23:55:00',
    'driver_lost',
    54.99550072,
    72.94622044,
    'p8'
),
(
    8,
    9,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    '5e94c22b3637858022b36c4322b394',
    '54b3d7ec-22b3-22b3-22b3-911bc8fe404c',
    '2020-02-27T23:55:00',
    'driver_found',
    54.99550072,
    72.94622044,
    'p8'
),
-- no driver_lost
(
    9,
    10,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    '5e94c0lllll3785801eed76c4322b394',
    '54b3d7ec-llll-43cf-94a8-911bc8fe404c',
    '2020-02-26T23:55:00',
    'driver_found',
    54.99550072,
    72.94622044,
    'p8'
),
-- no driver_found, driver_lost >= curr - 5min
(
    10,
    11,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    'llll0875963785801eed76c4322b394',
    '54b3d7ec-llll-llll-llll-911bc8fe404c',
    '2020-12-12T00:18:00+00:00',
    'driver_lost',
    54.99550072,
    72.94622044,
    'p9'
),
-- no driver_found, driver_lost < curr - 5min
(
    11,
    12,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    '5kkkk0875963785801eed76c4322b394',
    '54b3d7ec-kkkk-43cf-94a8-911bc8fe404c',
    '2020-12-12T00:10:00+00:00',
    'driver_lost',
    54.99550072,
    72.94622044,
    'p10'
),
-- no driver_found, no driver_lost
(
    12,
    13,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    '1e94cta75963xze801eed76c4322b394',
    '54b3d7ec-tttt-43cf-94a8-911bc8fe404c',
    '2020-12-12T00:17:00+00:00',
    'fart',
    54.99550072,
    72.94622044,
    'p11'
),
-- tag is not active
(
    13,
    14,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    '1e94cta7596xzar01eed76c4322b394',
    'xzard7ec-tttt-43cf-94a8-911bc8fe404c',
    '2020-12-12T00:10:00+00:00',
    'driver_lost',
    54.99550072,
    72.94622044,
    'p12'
),
-- no record in car_device_bindings
(
    14,
    15,
    '2020-02-27T23:55:00',
    '2020-02-27T23:55:00',
    'kslgcta7596xzar01eed76c4322b394',
    'pstsd7ec-tttt-43cf-94a8-911bc8fe404c',
    '2020-12-12T00:10:00+00:00',
    'driver_lost',
    54.99550072,
    72.94622044,
    'p13'
);
