insert into eats_nomenclature_collector.brands(
    id,
    slug,
    is_enabled
)
values (
    '1',
    'brand1',
    true
),
(
    '2',
    'brand2',
    true
),
(
    '3',
    'brand3',
    true
),
(
    '4',
    'disabled_brand',
    false
);

insert into eats_nomenclature_collector.place_groups(
    id,
    name,
    parser_days_of_week,
    parser_hours,
    stop_list_enabled,
    is_vendor,
    is_enabled
)
values (
    '1',
    'place_group1',
    '1111111',
    '0:00',
    true,
    false,
    true
),
(
    '2',
    'place_group2',
    '1111111',
    '0:00',
    true,
    false,
    true
),
(
    '3',
    'place_group3',
    '1111111',
    '0:00',
    true,
    false,
    true
),
(
    '4',
    'place_group4',
    '1111111',
    '0:00',
    true,
    false,
    true
);

insert into eats_nomenclature_collector.brands_place_groups(
    brand_id,
    place_group_id,
    is_enabled
)
values (
   '1',
   '1',
   true
),
(
   '1',
   '2',
   true
),
(
   '2',
   '3',
   true
),
(
   '3',
   '4',
   true
);

insert into eats_nomenclature_collector.places(
    id,
    slug,
    brand_id,
    place_group_id,
    is_enabled,
    is_parser_enabled,
    stop_list_enabled,
    updated_at
)
values (
   '1',
   'place1',
   '1',
   '1',
   true,
   true,
   true,
   '2021-01-01T00:45:00+00:00'
),
(
   '2',
   'place2',
   '2',
   '3',
   false,
   true, 
   true,
   '2021-01-01T00:45:00+00:00'
),
(
   -- will be disabled
   '3',
   'place3',
   '3',
   '4',
   true,
   true,
   true,
   '2021-01-01T00:45:00+00:00'
),
(
   -- will be disabled
   '4',
   'place4',
   '1',
   '1',
   true,
   true,
   true,
   '2021-01-01T00:45:00+00:00'
),
(
   -- is_parser_enabled and is_enabled will be disabled 
   '5',
   'place5',
   '1',
   '1',
   true,
   false,
   true,
   '2021-01-01T00:45:00+00:00'
),
(
   '6',
   'place6',
   '2',
   '3',
   true,
   false,
   true,
   '2021-01-01T00:45:00+00:00'
),
(
   '7',
   'place7',
   '2',
   '3',
   false,
   false,
   true,
   '2021-01-01T00:45:00+00:00'
),
(
   '8',
   'remain_enabled8',
   '2',
   '3',
   true,
   true,
   true,
   '2021-01-01T00:45:00+00:00'
),
(
   '9',
   'enabled9',
   '2',
   '3',
   false,
   false,
   false,
   '2021-01-01T00:45:00+00:00'
),
(
   '10',
   'remain_disabled10',
   '2',
   '3',
   false,
   false,
   false,
   '2021-01-01T00:45:00+00:00'
);

-- add these tasks just to see that deleting them does not cause errors
insert into eats_nomenclature_collector.nomenclature_place_task_creation_attempts(
    place_id,
    last_creation_attempt_at,
    attempts_count,
    last_attempt_was_successful
)
values (
    '1',
    '2021-01-15T00:01:00+00:00',
    3,
    true
);

insert into eats_nomenclature_collector.nomenclature_place_task_creation_attempts(
    place_id,
    last_creation_attempt_at,
    attempts_count,
    last_attempt_was_successful
)
values (
    '4',
    '2021-01-15T00:01:00+00:00',
    3,
    true
);

insert into eats_nomenclature_collector.price_task_creation_attempts(
    place_id,
    last_creation_attempt_at,
    attempts_count,
    last_attempt_was_successful
)
values (
    '1',
    '2021-01-15T00:01:00+00:00',
    3,
    true
);

insert into eats_nomenclature_collector.price_task_creation_attempts(
    place_id,
    last_creation_attempt_at,
    attempts_count,
    last_attempt_was_successful
)
values (
    '3',
    '2021-01-15T00:01:00+00:00',
    3,
    true
);
