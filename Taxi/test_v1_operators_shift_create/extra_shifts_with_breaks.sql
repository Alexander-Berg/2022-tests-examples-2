INSERT INTO callcenter_operators.operators_shifts
(id,
 yandex_uid,
 skill,
 start,
 duration_minutes,
 frozen,
 type,
 description)
VALUES (10,
        'uid2',
        'pokemon',
        '2020-07-27 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'),
       (11,
        'uid1',
        'pokemon',
        '2020-07-27 01:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'),
       (12,
        'uid1',
        'pokemon',
        '2020-07-28 04:00:00.0 +0000',
        600,
        FALSE,
        1,
        'empty');

INSERT INTO callcenter_operators.operators_breaks
(shift_id,
 start,
 duration_minutes,
 type)
VALUES (10,
        '2020-07-27 12:30:00.0 +0000',
        15,
        'technical'),
       (11,
        '2020-07-27 01:30:00.0 +0000',
        15,
        'technical'),
       (12,
        '2020-07-28 05:30:00.0 +0000',
        15,
        'technical'),
       (12,
        '2020-07-28 07:30:00.0 +0000',
        15,
        'technical'),
       (12,
        '2020-07-28 09:45:00.0 +0000',
        15,
        'technical'),
       (12,
        '2020-07-28 11:15:00.0 +0000',
        15,
        'technical'),
       (12,
        '2020-07-28 13:30:00.0 +0000',
        15,
        'technical');