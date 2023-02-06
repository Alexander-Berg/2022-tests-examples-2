insert into callcenter_operators.shift_types (id, alias, properties)
values (1, 'common', '{"consider_as_workload": true}'), (2, 'additional', '{"consider_as_workload": true}')
on conflict do nothing;

insert into callcenter_operators.shift_events (id, alias, description)
values (1, 'tutoring', 'tutor tutoring students'),
(2, 'training', 'no matter train muscles or brain');


insert into callcenter_operators.additional_shifts_jobs
    (
        datetime_from,
        datetime_to,
        skill,
        status,
        ttl_time,
        extra_job_data,
        shifts_distributed
    )
values
    (
        '2020-07-25 00:00:00.0+00',
        '2020-07-27 10:00:00.0+00',
        'pokemon',
        2,
        '2020-07-27 00:00:00.0+00',
        '{"dry_run": false, "author_yandex_uid": "uid1", "additional_shifts_count": 1}'::JSONB,
        0
    );


insert into callcenter_operators.operators_shifts
    (
        id,
        yandex_uid,
        skill,
        start,
        duration_minutes,
        frozen,
        type,
        job_id,
        description
    )
values
    (
        1,
        'uid1',
        'pokemon',
        '2020-07-26 12:00:00.0 +0000',
        60,
        FALSE,
        1,
        1,
        'empty'
    );

insert into callcenter_operators.operators_breaks
    (
        shift_id,
        start,
        duration_minutes,
        type
    )
values
    (
        1,
        '2020-07-26 12:00:00.0 +0000',
        30,
        'technical'
    );

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
    );
