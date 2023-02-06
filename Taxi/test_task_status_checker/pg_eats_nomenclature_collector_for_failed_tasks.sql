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
    false
),
(
   '2',
   'place2',
   '1',
   '1',
   true,
   true,
   false
);

insert into eats_nomenclature_collector.nomenclature_brand_tasks(
    id, brand_id, status
)
values ('brand_task_id', '1', 'created');

insert into eats_nomenclature_collector.nomenclature_place_tasks(
    id, place_id, nomenclature_brand_task_id, status, file_path, status_synchronized_at
)
values
    ('task_id1', '1', 'brand_task_id', 'started', null, '2021-01-15T00:00:00+00:00'),
    ('task_id2', '1', 'brand_task_id', 'created', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_failed1', '1', 'brand_task_id', 'failed', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_cancelled1', '1', 'brand_task_id', 'cancelled', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_creation_failed1', '1', 'brand_task_id', 'creation_failed', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_finished1', '1', 'brand_task_id', 'finished', 'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/task_id_finished1.json', '2021-01-15T00:00:00+00:00');

insert into eats_nomenclature_collector.price_tasks(
    id, place_id, status, file_path, status_synchronized_at
)
values
    ('task_id3', '1', 'started', null, '2021-01-15T00:00:00+00:00'),
    ('task_id4', '1', 'created', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_failed2', '1', 'failed', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_cancelled2', '1', 'cancelled', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_creation_failed2', '1', 'creation_failed', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_finished2', '1', 'finished', 'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/task_id_finished2.json', '2021-01-15T00:00:00+00:00');

insert into eats_nomenclature_collector.stock_tasks(
    id, place_id, status, file_path, status_synchronized_at
)
values
    ('task_id5', '1', 'started', null, '2021-01-15T00:00:00+00:00'),
    ('task_id6', '2', 'created', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_failed3', '1', 'failed', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_cancelled3', '1', 'cancelled', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_creation_failed3', '1', 'creation_failed', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_finished3', '1', 'finished', 'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/task_id_finished3.json', '2021-01-15T00:00:00+00:00');

insert into eats_nomenclature_collector.availability_tasks(
    id, place_id, status, file_path, status_synchronized_at
)
values
    ('task_id7', '1', 'started', null, '2021-01-15T00:00:00+00:00'),
    ('task_id8', '1', 'created', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_failed4', '1', 'failed', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_cancelled4', '1', 'cancelled', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_creation_failed4', '1', 'creation_failed', null, '2021-01-15T00:00:00+00:00'),
    ('task_id_finished4', '1', 'finished', 'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/task_id_finished4.json', '2021-01-15T00:00:00+00:00');
