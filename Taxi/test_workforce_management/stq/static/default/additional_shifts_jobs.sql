INSERT INTO callcenter_operators.additional_shifts_jobs
    (
        datetime_from,
        datetime_to,
        skill,
        status,
        ttl_time,
        extra_job_data,
        shifts_distributed,
        updated_at
    )
VALUES
    (
        '2020-08-02 00:00:00.0+00',
        '2020-08-02 10:00:00.0+00',
        'hokage',
        1,
        '2020-08-02 00:00:00.0+00',
        '{"dry_run": false, "author_yandex_uid": "uid1", "additional_shifts_count": 1, "candidates_count": 2}'::JSONB,
        0,
        '2020-08-02 00:00:00.0+00'
    ),
    (
        '2020-09-02 00:00:00.0+00',
        '2020-09-02 10:00:00.0+00',
        'hokage',
        1,
        '2020-09-02 00:00:00.0+00',
        '{"dry_run": false, "author_yandex_uid": "uid1", "additional_shifts_count": 1, "candidates_count": 1, "shifts_distributed":1}'::JSONB,
        0,
        '2020-09-02 00:00:00.0+00'
    );

INSERT INTO callcenter_operators.additional_shift_candidates
    (
        job_id,
        yandex_uid,
        status,
        status_updates,
        updated_at
    )
VALUES
    (
        1, 'uid1', 'picked', ARRAY['{"date": "2020-08-01T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-08-02T00:00:00.0 +0000", "status": "offered"}'::JSONB], '2020-08-02T00:00:00 +0000'
    ),
    (
        2, 'uid1', 'accepted', ARRAY['{"date": "2020-09-01T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-09-02T00:00:00.0 +0000", "status": "offered"}'::JSONB,
            '{"date": "2020-09-02T00:00:00.0 +0000", "status": "accepted"}'::JSONB], '2020-09-02T00:00:00 +0000'
    );
