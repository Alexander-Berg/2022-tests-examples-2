insert into eats_nomenclature_collector.brands(
    id,
    slug
)
values (
    '1',
    'brand1'
),
(
    '2',
    'brand2'
);

insert into eats_nomenclature_collector.place_groups(
    id,
    name,
    parser_days_of_week,
    parser_hours,
    stop_list_enabled,
    is_vendor
)
values (
    '1',
    'place_group1',
    '1111111',
    '0:00',
    true,
    true
),
(
    '2',
    'place_group2',
    '1111111',
    '0:00',
    true,
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
   '2',
   '2',
   true
);

insert into eats_nomenclature_collector.places(
    id,
    slug,
    brand_id,
    place_group_id,
    is_enabled,
    is_parser_enabled,
    stop_list_enabled
)
values (
   '1',
   'place1',
   '1',
   '1',
   true,
   true,
   true
),
(
   '2',
   'place2',
   '1',
   '1',
   true,
   true,
   true
),
(
   '3',
   'place3',
   '2',
   '2',
   true,
   true,
   true
),
(
   '4',
   'place4',
   '2',
   '2',
   true,
   true,
   true
);

insert into eats_nomenclature_collector.nomenclature_brand_tasks(
    id, brand_id, status
)
values (
   '1',
   '1',
   'finished'
),
(
   '2',
   '2',
   'finished'
);
