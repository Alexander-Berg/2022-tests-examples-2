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
),
(
    '3',
    'brand3'
),
(
    '4',
    'brand4'
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
    'place_group1',
    '1111111',
    '0:00',
    true,
    false
),
(
    '3',
    'place_group1',
    '1111111',
    '0:00',
    true,
    false
),
(
    '4',
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
),
(
   '4',
   '4',
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
),
(
   '4',
   'place4',
   '1',
   '1',
   true,
   true
),
(
   '5',
   'place5',
   '2',
   '2',
   true,
   true
),
(
   '6',
   'place6',
   '3',
   '3',
   true,
   true
),
(
   '7',
   'place7',
   '4',
   '4',
   true,
   true
),
(
   '8',
   'place8',
   '4',
   '4',
   true,
   true
);

insert into eats_nomenclature_collector.nomenclature_brand_tasks(
    id, brand_id, status
)
values (
    'brand_task_1_created',
    '1',
    'created'
),
(
    'brand_task_1_failed',
    '1',
    'failed'
),
(
    'brand_task_1_finished',
    '1',
    'finished'
),
(
    'brand_task_2_finished',
    '2',
    'finished'
),
(
    'brand_task_3_will_fail_all_parsing',
    '3',
    'finished'
),
(
    'brand_task_4_finished',
    '4',
    'finished'
);

insert into eats_nomenclature_collector.nomenclature_place_tasks(
    id, place_id, nomenclature_brand_task_id, status, file_path
)
values (
    'place_task_1_finished',
    '1',
    'brand_task_1_finished',
    'finished',
    'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/test1.json'
),
(
    'place_task_2_finished',
    '2',
    'brand_task_1_finished',
    'finished',
    'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/test2.json'
),
(
    -- failed place task, won't be taken
    'place_task_2_failed',
    '2',
    'brand_task_1_finished',
    'failed',
    null
),
(
    'place_task_3_finished',
    '3',
    'brand_task_1_finished',
    'finished',
    'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/test3.json'
),
(
    'place_task_6_will_fail_unknown_path',
    '6',
    'brand_task_3_will_fail_all_parsing',
    'finished',
    'https:\/\/eda-integration.s3.mdst.yandex.net\/path_unknown\/test.json'
),
(
    'place_task_7_will_fail_parsing',
    '7',
    'brand_task_4_finished',
    'finished',
    'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/test6.json'
),
(
    'place_task_8_finished',
    '8',
    'brand_task_4_finished',
    'finished',
    'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/test7.json'
),
(
    'place_task_5_finished',
    '5',
    'brand_task_2_finished',
    'finished',
    'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/test5.json'
),
(
    'place_task_3_linked_to_created',
    '3',
    'brand_task_1_created',
    'finished',
    'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/test5.json'
),
(
    'place_task_3_linked_to_failed',
    '3',
    'brand_task_1_failed',
    'finished',
    'https:\/\/eda-integration.s3.mdst.yandex.net\/some_path\/test5.json'
);