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
   false
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
),
(
   '2',
   'place_group2',
   '1111111',
   '0:00',
   true,
   false
),
(
   '3',
   'place_group3',
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
),
(
   '2',
   '2',
   true
),
(
   '3',
   '3',
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
),
(
   '4',
   'place4',
   '1',
   '1',
   true,
   true,
   true
),
(
   '5',
   'place5',
   '1',
   '1',
   true,
   true,
   true
),
(
   '6',
   'place6',
   '2',
   '2',
   true,
   true,
   true
),
(
   '7',
   'place7',
   '2',
   '2',
   true,
   true,
   true
),
(
   '8',
   'place8',
   '2',
   '2',
   true,
   true,
   true
),
(
   '9',
   'place9',
   '2',
   '2',
   false,
   true,
   true
),
(
   '10',
   'place10',
   '2',
   '2',
   true,
   true,
   true
),
(
   '11',
   'place11',
   '2',
   '2',
   true,
   true,
   true
),
(
   '12',
   'place12',
   '2',
   '2',
   true,
   true,
   true
),
(
   '13',
   'place13',
   '2',
   '2',
   true,
   true,
   true
),
(
   '14',
   'place14',
   '2',
   '2',
   true,
   true,
   true
),
(
   '15',
   'place15',
   '2',
   '2',
   true,
   true,
   true
),
(
   '16',
   'place16',
   '2',
   '2',
   true,
   true,
   true
),
(
   '17',
   'place17',
   '3',
   '3',
   true,
   true,
   true
),
(
   '18',
   'place18',
   '2',
   '2',
   true,
   true,
   true
);

insert into eats_nomenclature_collector.nomenclature_brand_tasks(
    id, brand_id, status, updated_at
)
values
    ('brand1_task_id', '1', 'created', now() - interval '1 days'),
    ('brand2_task_id', '2', 'created', now() - interval '1 days');

insert into eats_nomenclature_collector.place_tasks_last_status(
    place_id,
    task_type,
    status,
    task_error,
    task_warnings,
    status_or_text_changed_at
)
values
    ('1', 'nomenclature', 'processed', null, null, now() - interval '1 hours'),
    ('1', 'price', 'processed', null, null, now() - interval '1 hours'),
    ('1', 'stock', 'processed', null, null, now() - interval '1 hours'),
    ('1', 'availability', 'processed', null, null, now() - interval '1 hours'),
    ('2', 'nomenclature', 'failed', 'Connection timeout while fetch menu', null, now() - interval '5 minutes'),
    ('2', 'price', 'failed', 'Connection timeout while fetch menu', null, now() - interval '5 minutes'),
    ('2', 'stock', 'failed', 'Connection timeout while fetch menu', null, now() - interval '5 minutes'),
    ('2', 'availability', 'failed', 'Connection timeout while fetch menu', null, now() - interval '5 minutes'),
    ('3', 'nomenclature', 'failed', 'Fetch menu fail', null, now() - interval '1 hours'),
    ('3', 'price', 'failed', 'Fetch menu fail', null, now() - interval '1 hours'),
    ('3', 'stock', 'failed', 'Fetch menu fail', null, now() - interval '1 hours'),
    ('3', 'availability', 'failed', 'Fetch menu fail', null, now() - interval '1 hours'),
    ('4', 'nomenclature', 'failed', 'Another reason', null, now() - interval '1 hours'),
    ('4', 'price', 'failed', 'Another reason', null, now() - interval '1 hours'),
    ('4', 'stock', 'failed', 'Another reason', null, now() - interval '1 hours'),
    ('4', 'availability', 'failed', 'Another reason', null, now() - interval '1 hours'),
    ('5', 'nomenclature', 'failed', null, null, now() - interval '1 hours'),
    ('5', 'price', 'failed', null, null, now() - interval '1 hours'),
    ('5', 'stock', 'failed', null, null, now() - interval '1 hours'),
    ('5', 'availability', 'failed', null, null, now() - interval '1 hours'),
    ('6', 'nomenclature', 'failed', 'No categories in nomenclature', null, now() - interval '1 hours'),
    ('6', 'price', 'failed', 'No prices', null, now() - interval '1 hours'),
    ('6', 'stock', 'failed', 'No stocks', null, now() - interval '1 hours'),
    ('6', 'availability', 'failed', 'No availability', null, now() - interval '1 hours'),
    ('7', 'nomenclature', 'failed', 'No products in nomenclature', null, now() - interval '1 hours'),
    ('7', 'price', 'failed', 'All prices are zero', null, now() - interval '1 hours'),
    ('7', 'stock', 'failed', 'All stocks are zero', null, now() - interval '1 hours'),
    ('7', 'availability', 'failed', 'All availability false', null, now() - interval '1 hours'),
    ('8', 'nomenclature', 'failed', 'Negative weight in nomenclature', null, now() - interval '1 hours'),
    ('8', 'price', 'failed', 'Has negative prices', null, now() - interval '1 hours'),
    ('9', 'nomenclature', 'failed', 'Empty menu in place', null, now() - interval '1 hours'),
    ('9', 'availability', 'failed', 'Unsupported availability aggregator', null, now() - interval '1 hours'),
    ('10', 'stock', 'failed', 'Empty stop list', null, now() - interval '1 hours'),
    ('11', 'nomenclature', 'processed', null, 'Client category without origin id|Non existing parent client category|No client category for origin id', now() - interval '1 hours'),
    ('11', 'price', 'failed', 'All prices are zero', null, now() - interval '1 hours'),
    ('11', 'stock', 'processed', null, null, now() - interval '1 hours'),
    ('12', 'nomenclature', 'processed', null, 'Client category without origin id|Skipped items with no client categories|Items with non existing category', now() - interval '1 hours'),
    ('13', 'nomenclature', 'processed', null, 'Mismatched items with same origin id', now() - interval '1 hours'),
    ('14', 'nomenclature', 'failed', 'New menu is much smaller than previous', null, now() - interval '1 hours'),
    ('15', 'nomenclature', 'failed', 'Fail menu synchronization', null, now() - interval '1 hours'),
    ('15', 'stock', 'failed', 'Incorrect data from partner', null, now() - interval '1 hours'),
    ('15', 'price', 'failed', 'Fetch data fail 400', null, now() - interval '1 hours'),
    ('15', 'availability', 'failed', 'New error from partner', null, now() - interval '1 hours'),
    ('16', 'stock', 'failed', 'Stock value is too big', null, now() - interval '1 hours'),
    ('17', 'stock', 'failed', 'Stock value is too big', null, now() - interval '1 hours'),
    ('18', 'nomenclature', 'failed', 'Not found parser name to processing', null, now() - interval '1 hours');
