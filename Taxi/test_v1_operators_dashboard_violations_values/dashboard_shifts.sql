insert into callcenter_operators.shift_types (id, alias, properties)
values (1, 'common', '{"consider_as_workload": true}'), (2, 'additional', '{"consider_as_workload": true}')
on conflict do nothing;

insert into callcenter_operators.shift_events (id, alias, description)
values (0, 'tutoring', 'tutor tutoring students')
on conflict do nothing;

insert into callcenter_operators.operators_shifts
    (
        id,
        yandex_uid,
        skill,
        start,
        duration_minutes,
        type,
        description,
        operators_schedule_types_id
    )
values
    (
        1,
        'uid1',
        'pokemon',
        '2020-07-26 12:00:00.0 +0000',
        60,
        1,
        'empty',
        1
    ),
    (
        2,
        'uid1',
        'pokemon',
        '2020-07-26 13:00:00.0 +0000',
        60,
        1,
        'empty',
        1
    ),
    (
        3,
        'uid2',
        'pokemon',
        '2020-07-26 13:00:00.0 +0000',
        60,
        1,
        'empty',
        1
    ),
    (
        4,
        'uid3',
        'pokemon',
        '2020-07-26 13:00:00.0 +0000',
        60,
        1,
        'empty',
        1
    );


insert into callcenter_operators.operators_shifts_violations
    (
        yandex_uid,
        state_type,
        start,
        duration_minutes,
        finish,
        shift_id
    )
values
    (
        'uid1',
        'late',
        '2020-07-26 13:00:00.0 +0000',
        15,
        '2020-07-26 13:15:00.0 +0000',
        2
    ),
    (
        'uid1',
        'not_working',
        '2020-07-26 13:45:00.0 +0000',
        60,
        '2020-07-26 14:00:00.0 +0000',
        2
    ),
    (
        'uid2',
        'absent',
        '2020-07-26 13:00:00.0 +0000',
        60,
        '2020-07-26 14:00:00.0 +0000',
        3
    );
