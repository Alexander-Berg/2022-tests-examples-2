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
);

insert into eats_nomenclature_collector.nomenclature_brand_tasks(
    id, brand_id, status
)
values (
    'uuid-1',
    '1',
    'created'
),
(
    'uuid-2',
    '1',
    'failed'
),
(
    'uuid-3',
    '1',
    'finished'
);

insert into eats_nomenclature_collector.nomenclature_place_tasks(
    id, place_id, nomenclature_brand_task_id, status, file_path
)
values (
    'uuid_5',
    '1',
    'uuid-3',
    'finished',
    'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/test1.json'
);

insert into eats_nomenclature_collector.client_categories (
    brand_id, name, origin_id, parent_origin_id
)
values 
    ('1', 'Курица', '33333333-d00c-11ea-98c6-001e676a98dc', '0535c142-d00c-11ea-98c6-001e676a98dc'),
    ('1', 'Фрукты', '55555555-d00c-11ea-98c6-001e676a98dc', null),
    ('1', 'Яблоки', '66666666-d00c-11ea-98c6-001e676a98dc', '55555555-d00c-11ea-98c6-001e676a98dc'),
    ('1', 'Помидоры', '77777777-d00c-11ea-98c6-001e676a98dc', '11111111-1111-1111-1111-111111111111');
