insert into callcenter_operators.shift_events (id, alias, description, properties, updated_at)
VALUES (1, 'training', 'no matter train muscles or brain', '{"distribute_breaks_inside": true, "is_training": false}', '2020-11-16 14:10:00.0'),
       (2, 'with_breaks', 'training with its own breaks inside', '{"distribute_breaks_inside": false, "is_training": true}',
        '2020-11-16 14:10:00.0');

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
        1,
        1,
        '2020-07-26 12:30:00.0 +0000',
        30,
        'technical'
    ),
    (
        5,
        2,
        '2020-07-26 16:00:00.0 +0000',
        15,
        'technical'
    );
