INSERT INTO callcenter_operators.schedule_types
    (
        schedule_type_id,
        schedule_alias,
        schedule_by_minutes,
        rotation_type,
        updated_at,
        domain
    )
VALUES
    (
        10,
        '10:00-19:00',
        '{600, 540, 300}',
        'sequentially',
        '2021-06-01 00:00:00.0',
        'taxi'
    );
