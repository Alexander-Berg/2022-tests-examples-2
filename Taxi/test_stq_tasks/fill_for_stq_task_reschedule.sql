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
    is_parser_enabled
)
values (
   '1',
   'place1',
   '1',
   '1',
   true,
   true
),
(
   '2',
   'place2',
   '1',
   '1',
   true,
   true
),
(
   '3',
   'place3',
   '1',
   '1',
   true,
   true
);

insert into eats_nomenclature_collector.nomenclature_brand_tasks(
    id, brand_id, status
)
values (
    'uuid_1',
    '1',
    'created'
),
(
    'uuid_2',
    '1',
    'failed'
),
(
    'uuid_3',
    '1',
    'finished'
);

insert into eats_nomenclature_collector.nomenclature_place_tasks(
    id, place_id, nomenclature_brand_task_id, status, file_path
)
values (
    'uuid_5',
    '1',
    'uuid_3',
    'finished',
    'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/test1.json'
),
(
    'uuid_6',
    '2',
    'uuid_3',
    'finished',
    'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/test2.json'
),
(
    'uuid_7',
    '3',
    'uuid_3',
    'finished',
    'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/test3.json'
);
