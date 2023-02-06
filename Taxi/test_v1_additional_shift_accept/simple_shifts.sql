insert into callcenter_operators.shift_types (id, alias, properties)
VALUES (1, 'common', '{"consider_as_workload": true}'), (2, 'additional', '{"consider_as_workload": true}')
on conflict do nothing;


INSERT INTO callcenter_operators.operators_shifts
    (
        yandex_uid,
        unique_operator_id,
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
        1,
        'hokage',
        '2020-07-26 12:00:00.0+00',
        60,
        FALSE,
        1,
        'empty',
        1
    );
