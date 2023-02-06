INSERT INTO callcenter_operators.schedule_types
    (
        schedule_alias,
        schedule,
        schedule_by_minutes,
        first_weekend,
        start,
        duration_minutes,
        updated_at,
        domain,
        offset_settings,
        rotation_type,
        absolute_start
    )
VALUES
    (
        '5\/2 (СБ,ВС) 4Ч | 20-01',
        '{5,2}',
        '{1020,300,1140,300,1140,300,1140,300,1140,300,3000}',
        FALSE,
        '14:00:00.000+00:00',
        300,
        '2022-04-16T11:27:16.452+00:00',
        'taxi',
        '[{"offset": 0, "oebs_alias": "5\/2 (СБ,ВС) 4Ч", "offset_alias": "1"}]',
        'weekly',
        '2022-01-31T21:00:00.000+00:00'
    );


INSERT INTO callcenter_operators.operators
    (
        yandex_uid,
        rate,
        updated_at,
        tags
    )
VALUES
    (
        'uid1',
        0.5,
        '2020-08-26 00:00:00.0',
        ARRAY['naruto']
    );

INSERT INTO callcenter_operators.skills
    (
        name,
        description,
        active,
        domain
    )
VALUES
    (
        'pokemon',
        '',
        True,
        'taxi'
    )
ON CONFLICT (name) DO NOTHING;

INSERT INTO callcenter_operators.operators_schedule_types
    (
        yandex_uid,
        schedule_type_id,
        starts_at,
        expires_at,
        updated_at,
        schedule_offset
    )
VALUES
    (
        'uid1',
        1,
        '2022-05-01 00:00:00.0+03',
        NULL,
        '2022-05-02 22:10:43.4+03',
        0
    );


INSERT INTO callcenter_operators.operators_schedule_type_skills
    (
        skill,
        operators_schedule_types_id,
        updated_at
    )
VALUES
    (
        'pokemon',
        1,
        '2022-06-26 00:00:00.0+00'
    );
