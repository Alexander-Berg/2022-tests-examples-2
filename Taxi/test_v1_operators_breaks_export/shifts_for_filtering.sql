insert into callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"consider_as_workload": true}'), (2, 'additional', '{"consider_as_workload": true}')
on conflict do nothing;

insert into callcenter_operators.shift_events (id, alias, description)
VALUES (0, 'tutoring', 'tutor tutoring students')
on conflict do nothing;

INSERT INTO callcenter_operators.operators_schedule_types
    (
        yandex_uid,
        schedule_type_id,
        starts_at,
        expires_at,
        updated_at
    )
VALUES
    (
        'uid2',
        1,
        '2020-07-01 00:00:00.0+03',
        '2020-07-02 00:00:00.0+03',
        '2020-06-26 00:00:00.0'
    ),
    (
        'uid1',
        1,
        '2020-07-01 00:00:00.0+03',
        '2020-08-02 00:00:00.0+03',
        '2020-06-26 00:00:00.0'
    ),
    (
        'uid2',
        1,
        '2020-08-01 00:00:00.0+03',
        '2020-08-02 00:00:00.0+03',
        '2020-06-26 00:00:00.0'
    ),
    (
        'uid1',
        2,
        '2020-08-26 00:00:00.0+03',
        '2020-08-27 00:00:00.0+03',
        '2020-06-26 00:10:00.0'
    );


INSERT INTO callcenter_operators.operators_shifts
    (
        yandex_uid,
        skill,
        start,
        duration_minutes,
        frozen,
        type,
        description,
        operators_schedule_types_id
    )
VALUES
    (
        'uid1',
        'pokemon',
        '2020-07-26 12:00:00.0 +0300',
        60,
        FALSE,
        1,
        'empty',
        2
    ),
    (
        'uid2',
        'pokemon',
        '2020-08-01 09:00:00.0 +0300',
        60,
        FALSE,
        1,
        'empty',
        Null
    ),
    (
        'uid1',
        'order',
        '2020-08-26 12:00:00.0 +0300',
        360,
        FALSE,
        1,
        'empty',
        4
    );


INSERT INTO callcenter_operators.operators_breaks
    (
        shift_id,
        start,
        duration_minutes,
        type
    )
VALUES
    (
        1,
        '2020-07-26 12:10:00.0 +0300',
        30,
        'technical'
    ),
    (
        2,
        '2020-08-01 09:45:00.0 +0300',
        15,
        'technical'
    ),
    (
        2,
        '2020-08-01 09:15:00.0 +0300',
        15,
        'technical'
    ),
    (
        3,
        '2020-08-26 14:15:00.0 +0300',
        15,
        'technical'
    )
