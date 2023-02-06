INSERT INTO callcenter_operators.schedule_types
    (
         schedule_type_id,
        schedule_alias,
        schedule,
        first_weekend,
        start,
        duration_minutes,
        updated_at,
        active
    )
VALUES
    (
        10,
        '5x2/10:00-00:00',
        '{5, 2}',
        FALSE,
        '10:00',
        14 * 60,
        '2023-08-01 00:00:00.0',
        false
    );
