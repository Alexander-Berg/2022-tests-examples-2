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
        '09-21 / 2/2/3 11Ч',
        '{1,2,3,2,2,3,1}',
        '{1800,720,720,720,5040,720,720,720,3600,720,720,720,720,720,1800}',
        TRUE,
        '03:00:00+00:00',
        720,
        '2022-03-15T15:14:17.477+00:00',
        'taxi',
        '[{"offset": 0, "oebs_alias": "2/2/3-1 11Ч", "offset_alias": "1"}, {"offset": 2, "oebs_alias": "2/2/3-3 11Ч", "offset_alias": "3"}, {"offset": 7, "oebs_alias": "2/2/3-2 11Ч", "offset_alias": "2"}, {"offset": 9, "oebs_alias": "2/2/3-10 11Ч", "offset_alias": "10"}]',
        'sequentially',
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
        '2022-02-01 00:00:00.000+03',
        NULL,
        '2022-02-23 14:11:20.167+03',
        7
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
