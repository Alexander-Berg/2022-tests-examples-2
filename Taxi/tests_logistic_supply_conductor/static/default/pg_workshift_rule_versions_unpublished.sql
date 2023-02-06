INSERT INTO logistic_supply_conductor.workshift_rule_versions
(rule_id, "version", publish_at, published_since, dispatch_priority, tags_on_subscription,
 order_source, employer_names, schedule, availability_courier_requirements, descriptive_items,
 free_time)
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
    interval '60 seconds'
),
(
    2,
    1,
    (current_timestamp - interval '30 days'),
    (current_timestamp - interval '30 days'),
    interval '60 seconds',
    '{}',
    '{}',
    ARRAY['vkusvill'],
    '{}',
    '{}',
    '{}',
    interval '60 seconds'
),
(
    2,
    2,
    (current_timestamp - interval '30 minutes'),
    (current_timestamp - interval '30 minutes'),
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
    interval '1 hour'
),
(
    2,
    3,
    (current_timestamp - interval '10 minutes'),
    NULL,
    interval '120 seconds',
    ARRAY['foo', 'bar', 'baz'],
    '{}',
    '{}',
    ARRAY[
        (
            1,
            (
                ARRAY['wednesday'],
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
    interval '1 hour'
);

UPDATE logistic_supply_conductor.workshift_rules
SET
    actual_version = 2,
    display_version = 2,
    last_known_version = 2
WHERE
    id = 2;
