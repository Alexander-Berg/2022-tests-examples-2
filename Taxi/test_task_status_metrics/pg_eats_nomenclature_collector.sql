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
   false,
   true,
   true
);

insert into eats_nomenclature_collector.nomenclature_brand_tasks(
    id, brand_id, status, updated_at
)
values ('brand_task_id', '1', 'created', now() - interval '1 days'),
       ('brand_task_id_finished', '1', 'finished', now() - interval '1 days'),
       ('brand_task_id_finished_new', '1', 'finished', now()),
       ('brand_task_id_failed', '1', 'failed', now()),
       ('brand_task_id_creating1', '1', 'creating', now() - interval '1 days'),
       ('brand_task_id_creating2', '1', 'creating', now() - interval '1 days'),
       ('brand_task_id_failed2', '1', 'failed', now() - interval '1 days'),
       ('brand_task_id_without_enabled_places', '1', 'created', now() - interval '1 days'),
       ('brand_task_id_with_enabled_places', '1', 'created', now() - interval '1 days');

insert into eats_nomenclature_collector.nomenclature_place_tasks(
    id, place_id, nomenclature_brand_task_id, status, status_synchronized_at
)
values
    ('task_id1', '1', 'brand_task_id', 'started', now() - interval '1 days'),
    ('task_id2', '1', 'brand_task_id', 'created', now() - interval '1 days'),
    ('task_id_failed1', '1', 'brand_task_id', 'failed', now()),
    ('task_id_failed2', '1', 'brand_task_id', 'failed', now()),
    ('task_id_creation_failed1', '1', 'brand_task_id', 'creation_failed', now()),
    ('task_id_started1', '1', 'brand_task_id', 'started', now() - interval '1 days'),
    ('task_id_creation_failed2', '1', 'brand_task_id', 'creation_failed', now() - interval '1 days'),
    ('task_id_finished1', '1', 'brand_task_id', 'finished', now() - interval '1 days'),
    ('task_id_finished_new', '1', 'brand_task_id', 'finished', now()),
    ('task_id_processed1', '1', 'brand_task_id', 'processed', now() - interval '1 days'),
    ('task_id_processed_new', '1', 'brand_task_id', 'processed', now()),
    ('task_id1_disabled_place', '2', 'brand_task_id_without_enabled_places', 'created', now() - interval '1 days'),
    ('task_id2_disabled_place', '2', 'brand_task_id_with_enabled_places', 'created', now() - interval '1 days'),
    ('task_id3_enabled_place', '1', 'brand_task_id_with_enabled_places', 'created', now() - interval '1 days');

insert into eats_nomenclature_collector.price_tasks(
    id, place_id, status, status_synchronized_at
)
values
    ('task_id3', '1', 'started', now() - interval '1 days'),
    ('task_id4', '1', 'created', now() - interval '1 days'),
    ('task_id_created_new', '1', 'created', now()),
    ('task_id_failed2', '1', 'failed', now()),
    ('task_id_failed3', '1', 'failed', now()),
    ('task_id_failed4', '1', 'failed', now() - interval '1 days');

insert into eats_nomenclature_collector.stock_tasks(
    id, place_id, status, status_synchronized_at
)
values
    ('task_id5', '1', 'started', now() - interval '1 days'),
    ('task_id6', '1', 'created', now() - interval '1 days'),
    ('task_id_failed3', '1', 'failed', now()),
    ('task_id_creation_failed3', '1', 'creation_failed', now()),
    ('task_id_finished3', '1', 'finished', now() - interval '1 days'),
    ('task_id_finished_new', '1', 'finished', now()),
    ('task_id_processed', '1', 'processed', now() - interval '1 days');

insert into eats_nomenclature_collector.availability_tasks(
    id, place_id, status, status_synchronized_at
)
values
    ('task_id7', '1', 'started', now() - interval '1 days'),
    ('task_id_started_new', '1', 'started', now()),
    ('task_id_creation_failed4', '1', 'creation_failed', now()),
    ('task_id_finished4', '1', 'finished', now() - interval '1 days'),
    ('task_id_failed', '1', 'failed', now() - interval '1 days');
