insert into eats_nomenclature_collector.brands(
    id,
    slug
)
values (
    '1',
    'brand1'
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
    false
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
   '1',
   '1',
   true,
   true,
   true
);

insert into eats_nomenclature_collector.price_tasks(
    id, place_id, status, file_path
)
values (
    'uuid_1',
    '1',
    'created',
    null
),
(
    'uuid_2',
    '1',
    'failed',
    null
)
