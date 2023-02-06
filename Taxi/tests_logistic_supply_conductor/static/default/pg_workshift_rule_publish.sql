INSERT INTO logistic_supply_conductor.workshift_rules (workshift_rule_id, created_at)
VALUES ('af31c824-066d-46df-0001-000000000001', (current_timestamp - interval '40 minutes')),
       ('af31c824-066d-46df-0001-000000000002', (current_timestamp - interval '30 minutes')),
       ('af31c824-066d-46df-0001-000000000003', (current_timestamp - interval '20 minutes')),
       ('af31c824-066d-46df-0001-000000000004', (current_timestamp - interval '15 minutes')),
       ('af31c824-066d-46df-0001-000000000005', (current_timestamp - interval '10 minutes'));

INSERT INTO logistic_supply_conductor.workshift_metadata (rule_id, is_visible, visibility_end_date,
                 visibility_duration, alias, visibility_courier_requirements, "state", transport_types)
VALUES(1, True, '2021-04-09T00:00:00Z', interval '90 minutes', 'moscow', '{}', 'pending', '{}'),
      (2, True, '2021-04-09T00:00:00Z', interval '90 minutes', 'kazan', '{}', 'pending', '{}'),
      (3, True, '2021-04-09T00:00:00Z', interval '90 minutes', 'kazan', '{}', 'archiving', '{}'),
      (4, True, '2021-04-09T00:00:00Z', interval '90 minutes', 'kazan', '{}', 'pending', '{}'),
      (5, False, '2021-04-09T00:00:00Z', interval '90 minutes', 'kazan', '{}', 'pending', '{}');

INSERT INTO logistic_supply_conductor.workshift_rule_versions
(rule_id, "version", publish_at, published_since, dispatch_priority, tags_on_subscription,
 order_source, employer_names, schedule, availability_courier_requirements, descriptive_items,
 free_time, removed_at)
VALUES
(
    1,
    1,
    (current_timestamp + interval '90 minutes'),
    NULL,
    interval '60 seconds',
    '{}',
    '{}',
    '{}',
    '{}',
    '{}',
    '{}',
    interval '60 seconds',
    NULL
),
(
    2,
    1,
    (current_timestamp - interval '30 days'),
    NULL,
    interval '60 seconds',
    '{}',
    '{}',
    ARRAY['vkusvill'],
    '{}',
    '{}',
    '{}',
    interval '60 seconds',
    NULL
),
(
    2,
    2,
    (current_timestamp - interval '30 minutes'),
    NULL,
    interval '120 seconds',
    ARRAY['foo', 'bar', 'baz'],
    '{}',
    '{}',
    ARRAY[
        (
            1,
            (
                ARRAY['wednesday', 'friday', 'sunday'],
                '08:30',
                '1 hour'
            )::logistic_supply_conductor.weekdays_time_interval_without_quota__v1
        )
    ]::logistic_supply_conductor.workshift_schedule_siblings_group_without_quota__v1[],
    ARRAY[
        ROW(
            ARRAY['foo', 'bar']
        )::logistic_supply_conductor.handlers__courier_requirement_ref_set__v1
    ],
    ARRAY[
        (
            'name',
            '42'
        )::logistic_supply_conductor.handlers__descriptive_item_ref__v1
    ],
    interval '1 hour',
    current_timestamp
),
(
    2,
    3,
    (current_timestamp - interval '30 minutes'),
    NULL,
    interval '120 seconds',
    ARRAY['foo', 'bar', 'baz'],
    '{}',
    '{}',
    ARRAY[
        (
            1,
            (
                ARRAY['wednesday', 'friday', 'sunday'],
                '08:30',
                '1 hour'
            )::logistic_supply_conductor.weekdays_time_interval_without_quota__v1
        )
    ]::logistic_supply_conductor.workshift_schedule_siblings_group_without_quota__v1[],
    ARRAY[
        ROW(
            ARRAY['foo', 'bar']
        )::logistic_supply_conductor.handlers__courier_requirement_ref_set__v1
    ],
    ARRAY[
        (
            'name',
            '42'
        )::logistic_supply_conductor.handlers__descriptive_item_ref__v1
    ],
    interval '1 hour',
    NULL
),
(
    2,
    4,
    NULL,
    NULL,
    interval '120 seconds',
    ARRAY['foo', 'bar', 'baz'],
    '{}',
    '{}',
    ARRAY[
        (
            1,
            (
                ARRAY['wednesday', 'friday', 'sunday'],
                '08:30',
                '1 hour'
            )::logistic_supply_conductor.weekdays_time_interval_without_quota__v1
        )
    ]::logistic_supply_conductor.workshift_schedule_siblings_group_without_quota__v1[],
    ARRAY[
        ROW(
            ARRAY['foo', 'bar']
        )::logistic_supply_conductor.handlers__courier_requirement_ref_set__v1
    ],
    ARRAY[
        (
            'name',
            '42'
        )::logistic_supply_conductor.handlers__descriptive_item_ref__v1
    ],
    interval '1 hour',
    NULL
),
(
    2,
    5,
    (current_timestamp - interval '15 minutes'),
    NULL,
    interval '120 seconds',
    ARRAY['foo', 'bar', 'baz'],
    '{}',
    '{}',
    ARRAY[
        (
            1,
            (
                ARRAY['wednesday', 'friday', 'sunday'],
                '08:30',
                '1 hour'
            )::logistic_supply_conductor.weekdays_time_interval_without_quota__v1
        )
    ]::logistic_supply_conductor.workshift_schedule_siblings_group_without_quota__v1[],
    ARRAY[
        ROW(
            ARRAY['foo', 'bar']
        )::logistic_supply_conductor.handlers__courier_requirement_ref_set__v1
    ],
    ARRAY[
        (
            'name',
            '42'
        )::logistic_supply_conductor.handlers__descriptive_item_ref__v1
    ],
    interval '1 hour',
    NULL
),
(
    3,
    1,
    (current_timestamp - interval '30 days'),
    NULL,
    interval '60 seconds',
    '{}',
    '{}',
    ARRAY['47d974b0-99fe-4ff7-9862-235922ee2636']::UUID[],
    '{}',
    '{}',
    '{}',
    interval '60 seconds',
    NULL
),
(
    4,
    1,
    (current_timestamp - interval '30 days'),
    NULL,
    interval '60 seconds',
    '{}',
    '{}',
    ARRAY['47d974b0-99fe-4ff7-9862-235922ee2636']::UUID[],
    '{}',
    '{}',
    '{}',
    interval '60 seconds',
    NULL
),
(
    5,
    1,
    (current_timestamp - interval '30 days'),
    NULL,
    interval '60 seconds',
    '{}',
    '{}',
    ARRAY['47d974b0-99fe-4ff7-9862-235922ee2636']::UUID[],
    '{}',
    '{}',
    '{}',
    interval '60 seconds',
    NULL
);
