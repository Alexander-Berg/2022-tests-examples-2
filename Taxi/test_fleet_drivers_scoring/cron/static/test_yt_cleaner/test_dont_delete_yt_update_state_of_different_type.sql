INSERT INTO fleet_drivers_scoring.yt_update_states
(
    id, operation_id, name, type, status, src_path, dst_path, src_cluster,
    dst_cluster, created_at, updated_at, parent_id, revision
)
VALUES
(
    3,
    'r0',
    'high_speed_driving',
    'calc',
    'done',
    'some_path0',
    'some_path0',
    'hahn',
    'seneca-man',
    '2020-05-08 02:20:00',
    '2020-05-08 02:30:00',
    1,
    '2020-05-04 02:00:00'
),
(
    4,
    'r1',
    'high_speed_driving',
    'copy',
    'done',
    'some_path0',
    'some_path0',
    'hahn',
    'seneca-man',
    '2020-05-08 02:20:00',
    '2020-05-08 02:30:00',
    1,
    '2020-05-04 02:00:00'
),
(
    5,
    'r2',
    'high_speed_driving',
    'convert',
    'done',
    'some_path0',
    'some_path0',
    'hahn',
    'seneca-man',
    '2020-05-08 02:20:00',
    '2020-05-08 02:30:00',
    1,
    '2020-05-04 02:00:00'
),
(
    51,
    'r00',
    'high_speed_driving',
    'calc',
    'done',
    'some_path1',
    'some_path1',
    'hahn',
    'seneca-vla',
    '2020-05-08 02:20:00',
    '2020-05-08 02:30:00',
    1,
    '2020-05-05 02:00:00'
),
(
    52,
    'r01',
    'high_speed_driving',
    'copy',
    'done',
    'some_path1',
    'some_path1',
    'hahn',
    'seneca-vla',
    '2020-05-08 02:20:00',
    '2020-05-08 02:30:00',
    1,
    '2020-05-05 02:00:00'
),
(
    53,
    'r02',
    'high_speed_driving',
    'convert',
    'done',
    'some_path1',
    'some_path1',
    'hahn',
    'seneca-vla',
    '2020-05-08 02:20:00',
    '2020-05-08 02:30:00',
    1,
    '2020-05-05 02:00:00'
),
(
    71,
    'r11',
    'passenger_tags',
    'calc',
    'done',
    'some_path2',
    'some_path2',
    'hahn',
    'seneca-vla',
    '2020-05-08 02:20:00',
    '2020-05-08 02:30:00',
    1,
    '2020-05-04 02:00:00'
),
(
    72,
    'r12',
    'passenger_tags',
    'copy',
    'done',
    'some_path2',
    'some_path2',
    'hahn',
    'seneca-vla',
    '2020-05-08 02:20:00',
    '2020-05-08 02:30:00',
    1,
    '2020-05-04 02:00:00'
),
(
    73,
    'r13',
    'passenger_tags',
    'convert',
    'done',
    'some_path2',
    'some_path2',
    'hahn',
    'seneca-vla',
    '2020-05-08 02:20:00',
    '2020-05-08 02:30:00',
    1,
    '2020-05-04 02:00:00'
);

INSERT INTO fleet_drivers_scoring.yt_updates
(
    id,
    name,
    path,
    revision,
    created_at
)
VALUES
(
    1,
    'high_speed_driving',
    'some_path0',
    '2020-05-04 02:00:00',
    '2020-05-04 02:00:00'
),
(
    2,
    'high_speed_driving',
    'some_path1',
    '2020-05-05 02:00:00',
    '2020-05-05 02:00:00'
),
(
    3,
    'passenger_tags',
    'some_path2',
    '2020-05-04 02:00:00',
    '2020-05-04 02:00:00'
);
