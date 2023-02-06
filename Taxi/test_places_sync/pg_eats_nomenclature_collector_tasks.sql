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

insert into eats_nomenclature_collector.places(
    id,
    slug,
    brand_id,
    is_enabled,
    is_parser_enabled,
    stop_list_enabled
)
values (
   '1',
   'place1',
   '1',
   true,
   true,
   true
),
(
   '2',
   'place2',
   '2',
   true,
   true,
   true
),
(
   '3',
   'place3',
   '2',
   true,
   true,
   true
),
(
   '4',
   'place4',
   '2',
   true,
   true,
   true
),
(
   '5',
   'place5',
   '2',
   true,
   true,
   true
),
(
   '6',
   'place6',
   '2',
   true,
   true,
   true
);

insert into eats_nomenclature_collector.nomenclature_brand_tasks(
    id, brand_id, status
)
values (
    'brand_task_1',
    '1',
    'created'
),
(
    'brand_task_2',
    '2',
    'created'
);

insert into eats_nomenclature_collector.nomenclature_place_tasks(
    id,
    place_id, 
    nomenclature_brand_task_id,
    status,
    created_at
) 
values ('nomenclature_task1', 1, 'brand_task_1', 'created', now() - interval '1 hour'),
       ('nomenclature_task2', 2, 'brand_task_2', 'started', now() - interval '1 hour'),
       ('nomenclature_task3', 3, 'brand_task_2', 'failed', now() - interval '1 hour'),
       ('nomenclature_task4', 5, 'brand_task_2', 'finished', now() - interval '1 hour'),
       ('nomenclature_task5', 6, 'brand_task_2', 'processed', now() - interval '1 hour');

insert into eats_nomenclature_collector.price_tasks(
    id,
    place_id, 
    status,
    created_at
) 
values ('price_task1', 1, 'created', now() - interval '1 hour'),
       ('price_task2', 2, 'started', now() - interval '1 hour'),
       ('price_task3', 3, 'failed', now() - interval '1 hour'),
       ('price_task4', 5, 'finished', now() - interval '1 hour'),
       ('price_task5', 6, 'processed', now() - interval '1 hour');
