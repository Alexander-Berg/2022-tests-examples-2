INSERT INTO callcenter_operators.additional_shifts_jobs
    (
        id,
        datetime_from,
        datetime_to,
        skill,
        status,
        ttl_time,
        shifts_distributed,
        extra_job_data
    )
VALUES
     (
        8,
        '2020-07-02 00:00:00.0+00',
        '2020-07-02 10:00:00.0+00',
        'hokage',
        1,
        '2020-07-02 00:00:00.0+00',
        7,
        '{"dry_run": false, "author_yandex_uid": "uid3", "additional_shifts_count": 7}'
    ),
    (
        9,
        '2020-07-26 12:00:00.0 +0000',
        '2020-07-26 18:00:00.0 +0000',
        'hokage',
        1,
        '2020-07-02 00:00:00.0+00',
        0,
        '{"dry_run": false, "author_yandex_uid": "uid3", "additional_shifts_count": 1}'
    );



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
        1, 'uid2', 2, 'offered', ARRAY['{"date": "2020-07-02T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-04T00:00:00.0 +0000", "status": "offered"}'::JSONB]
    ),
    (
        8, 'uid1', 1, 'offered', ARRAY['{"date": "2020-07-02T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-04T00:00:00.0 +0000", "status": "offered"}'::JSONB]
    ),
    (
        8, 'uid2', 2, 'accepted', ARRAY['{"date": "2020-07-02T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-04T00:00:00.0 +0000", "status": "offered"}'::JSONB,
            '{"date": "2020-07-04T00:00:00.0 +0000", "status": "accepted"}'::JSONB]
    ),
    (
        9, 'uid1', 1, 'offered', ARRAY['{"date": "2020-07-02T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-04T00:00:00.0 +0000", "status": "offered"}'::JSONB]
    );
