INSERT INTO callcenter_operators.additional_shifts_jobs
    (
        datetime_from,
        datetime_to,
        skill,
        status,
        ttl_time,
        extra_job_data,
        shifts_distributed
    )
VALUES
    (
        '2020-07-02 00:00:00.0+00',
        '2020-07-02 10:00:00.0+00',
        'hokage',
        1,
        '2020-07-02 00:00:00.0+00',
        '{"dry_run": false, "author_yandex_uid": "uid3", "additional_shifts_count": 1}'::JSONB,
        0
    ),
    (
        '2020-08-02 00:00:00.0+00',
        '2020-08-02 10:00:00.0+00',
        'tatarin',
        1,
        '2020-08-02 00:00:00.0+00',
        '{"dry_run": true, "author_yandex_uid": "uid3", "additional_shifts_count": 1, "operators_filter": {"tag_filter": {"tags": ["новичок"], "ownership_policy": "include", "connection_policy": "conjunction"}, "nearest_shift_filter": {"threshold_minutes": {"left": 180, "right": 180}}}}'::JSONB,
        0
    ),
    (
        '2020-08-02 00:00:00.0+00',
        '2020-08-02 10:00:00.0+00',
        'tatarin',
        1,
        '2020-08-02 00:00:00.0+00',
        '{"dry_run": true, "author_yandex_uid": "uid2", "additional_shifts_count": 1}'::JSONB,
        1
    );

INSERT INTO callcenter_operators.additional_shift_candidates
    (
        job_id,
        yandex_uid,
        unique_operator_id,
        status,
        status_updates,
        updated_at
    )
VALUES
    (
        1, 'uid1', 1, 'picked', ARRAY['{"date": "2020-07-01T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-02T00:00:00.0 +0000", "status": "offered"}'::JSONB], '2020-07-02T00:00:00 +0000'
    ),
    (
        2, 'uid2', 2, 'offered', ARRAY['{"date": "2020-07-01T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-02T00:00:00.0 +0000", "status": "offered"}'::JSONB], '2020-07-02T00:00:00 +0000'
    ),
    (
        3, 'uid2', 2, 'offered', ARRAY['{"date": "2020-07-01T00:00:00.0 +0000", "status": "picked"}'::JSONB,
            '{"date": "2020-07-02T00:00:00.0 +0000", "status": "offered"}'::JSONB], '2020-07-02T00:00:00 +0000'
    );

