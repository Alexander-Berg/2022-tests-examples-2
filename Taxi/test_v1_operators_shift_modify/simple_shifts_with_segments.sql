insert into callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"consider_as_workload": true}'), (2, 'additional', '{"consider_as_workload": true}')
on conflict do nothing;

INSERT INTO callcenter_operators.operators_shifts
(id,
 yandex_uid,
 skill,
 start,
 duration_minutes,
 frozen,
 type,
 description)
VALUES (0,
        'uid1',
        NULL,
        '2020-07-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty'),
       (1,
        'uid2',
        'pokemon',
        '2020-08-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty');

INSERT INTO callcenter_operators.operators_shifts_segments
(id,
 shift_id,
 start,
 duration_minutes,
 skill,
 description)
VALUES (0,
        0,
        '2020-07-26 12:00:00.0 +0000',
        30,
        'pokemon',
        'awesome description'),
       (1,
        0,
        '2020-07-26 12:30:00.0 +0000',
        30,
        'pokemon',
        NULL)
