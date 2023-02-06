INSERT INTO callcenter_operators.additional_shift_candidates
    (
        job_id,
        yandex_uid,
        unique_operator_id,
        status,
        status_updates
    )
VALUES
    (
        11, 'uid1', 1, 'offered', ARRAY['{"date": "2020-07-02T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-04T00:00:00.0 +0000", "status": "offered"}'::JSONB]
    ),
    (
        11, 'uid2', 2, 'offered', ARRAY['{"date": "2020-07-02T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-04T00:00:00.0 +0000", "status": "offered"}'::JSONB]
    ),
    (
        11, 'uid3', 3, 'offered', ARRAY['{"date": "2020-07-02T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-04T00:00:00.0 +0000", "status": "offered"}'::JSONB]
    ),

    (
        12, 'uid1', 1, 'offered', ARRAY['{"date": "2020-07-02T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-04T00:00:00.0 +0000", "status": "offered"}'::JSONB]
    ),
    (
        12, 'uid3', 3, 'offered', ARRAY['{"date": "2020-07-02T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-04T00:00:00.0 +0000", "status": "offered"}'::JSONB]
    ),
    (
        13, 'uid3', 3, 'offered', ARRAY['{"date": "2020-07-02T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-04T00:00:00.0 +0000", "status": "offered"}'::JSONB]
    ),
    (
        14, 'uid1', 1, 'offered', ARRAY['{"date": "2020-07-02T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-04T00:00:00.0 +0000", "status": "offered"}'::JSONB]
    );
