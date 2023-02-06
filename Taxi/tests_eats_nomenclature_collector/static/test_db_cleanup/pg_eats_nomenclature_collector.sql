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
);

insert into eats_nomenclature_collector.nomenclature_brand_tasks(
    id, brand_id, status, updated_at
)
values ('brand_task_id', '1', 'created', now()),
       ('brand_task_id1', '1', 'failed', now() - interval '1 month'),
       ('brand_task_id2', '1', 'finished', now() - interval '1 month'),
       ('brand_task_id3', '1', 'cancelled', now());

insert into eats_nomenclature_collector.nomenclature_place_tasks(
    id, place_id, nomenclature_brand_task_id, status, status_synchronized_at, updated_at
)
values
    ('task_id_started1', '1', 'brand_task_id', 'started', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_created1', '1', 'brand_task_id', 'created', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_failed1', '1', 'brand_task_id', 'failed', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_cancelled1', '1', 'brand_task_id', 'cancelled', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_creation_failed1', '1', 'brand_task_id', 'creation_failed', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_finished1', '1', 'brand_task_id', 'finished', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_processed1', '1', 'brand_task_id', 'processed', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_processed_new', '1', 'brand_task_id', 'processed', now(), now());

insert into eats_nomenclature_collector.price_tasks(
    id, place_id, status, status_synchronized_at, updated_at
)
values
    ('task_id_started2', '1', 'started', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_created2', '1', 'created', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_failed2', '1', 'failed', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_cancelled2', '1', 'cancelled', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_creation_failed2', '1', 'creation_failed', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_finished2', '1', 'finished', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_processed2', '1', 'processed', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_failed_new', '1', 'failed', now(), now());

insert into eats_nomenclature_collector.stock_tasks(
    id, place_id, status, status_synchronized_at, updated_at
)
values
    ('task_id_started3', '1', 'started', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_created3', '1', 'created', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_failed3', '1', 'failed', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_cancelled3', '1', 'cancelled', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_creation_failed3', '1', 'creation_failed', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_finished3', '1', 'finished', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_processed3', '1', 'processed', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_creation_failed_new', '1', 'creation_failed', now(), now());

insert into eats_nomenclature_collector.availability_tasks(
    id, place_id, status, status_synchronized_at, updated_at
)
values
    ('task_id_started4', '1', 'started', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_created4', '1', 'created', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_failed4', '1', 'failed', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_cancelled4', '1', 'cancelled', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_creation_failed4', '1', 'creation_failed', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_finished4', '1', 'finished', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_processed4', '1', 'processed', now() - interval '1 month', now() - interval '1 month'),
    ('task_id_cancelled_new', '1', 'cancelled', now(), now());
