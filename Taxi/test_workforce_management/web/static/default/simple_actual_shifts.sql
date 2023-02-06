INSERT INTO callcenter_operators.operators_actual_shifts
(yandex_uid, source, start, duration_minutes, events, shift_id)
VALUES ('uid1',
        'taxi_callcenter',
        '2020-07-26 12:00:00.0 +0000',
        60,
        '[]',
        1),
       ('uid1',
        'taxi_callcenter',
        '2020-07-26 13:00:00.0 +0000',
        60,
        '[]',
        2),
       ('uid1',
        'taxi_callcenter',
        '2020-07-26 14:00:00.0 +0000',
        60,
        '[]',
        3),
       ('uid1',
        'taxi_callcenter',
        '2020-07-26 15:00:00.0 +0000',
        60,
        '[]',
        4),
       ('uid1',
        'taxi_callcenter',
        '2020-07-26 16:00:00.0 +0000',
        60,
        '[]',
        NULL),
       ('uid2',
        'taxi_callcenter',
        '2020-07-26 15:00:00.0 +0000',
        60,
        ('[{"type": "pause", "start": "2020-07-26T15:40:00.608168+00:00", "sub_type": "work_with_rg", ' ||
        '"duration_minutes": 0.5020263166666666}, ' ||
        '{"type": "pause", "start": "2020-07-26T15:43:26.191939+00:00", ' ||
        '"sub_type": "work_with_rg", "duration_minutes": 1.2132323333333335}, ' ||
        '{"type": "pause", "start": "2020-07-26T15:45:08.124016+00:00", "sub_type": null, ' ||
        '"duration_minutes": 0.6532841}]')::jsonb,
        6);
