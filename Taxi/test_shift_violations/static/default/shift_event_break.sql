INSERT INTO callcenter_operators.operators_shifts
    (
        id,
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
        10,
        'uid1',
        'pokemon',
        '2020-07-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        'empty',
        1
    );

insert into callcenter_operators.shift_events (id, alias, description)
VALUES (1, 'training', 'no matter train muscles or brain')
on conflict do nothing;

insert into callcenter_operators.operators_shifts_events
    (
        shift_id,
        event_id,
        start,
        duration_minutes,
        description
    )
values
    (
        10,
        1,
        '2020-07-26 12:00:00.0 +0000',
        30,
        'technical'
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
        10,
        '2020-07-26 12:30:00.0 +0000',
        30,
        'technical'
    );
