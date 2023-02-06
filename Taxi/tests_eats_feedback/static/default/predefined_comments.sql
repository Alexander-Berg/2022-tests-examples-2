--mysql> select * from predefined_comments;
--+-----+-----------------------------------------------------+---------+----------------+---------------------+--------------------+--------------------------------+----------------------------+---------------------+---------------------+
--| id  | comment                                             | type    | group_code     | created_at          | generate_sorrycode | calculate_average_rating_place | access_mask_for_order_flow | deleted_at          | updated_at          |
--+-----+-----------------------------------------------------+---------+----------------+---------------------+--------------------+--------------------------------+----------------------------+---------------------+---------------------+
--|   1 | Не понравилась еда                                  | dislike | NULL           | 2017-12-15 15:49:46 |                  0 |                              1 |                          1 | NULL                | 2020-03-30 15:32:00 |
--|   3 | Неверно собран заказ                                | dislike | NULL           | 2017-12-15 15:49:46 |                  0 |                              0 |                          1 | NULL                | 2020-03-30 15:32:00 |
--|   5 | Испорчена упаковка                                  | dislike | NULL           | 2017-12-15 15:49:46 |                  0 |                              0 |                          1 | NULL                | 2020-03-30 15:32:00 |
--|   7 | Еда остыла                                          | dislike | NULL           | 2017-12-15 15:49:46 |                  0 |                              0 |                          1 | NULL                | 2020-03-30 15:32:00 |
--|   9 | Опоздали с доставкой                                | dislike | delivery_delay | 2017-12-15 15:49:46 |                  1 |                              0 |                          1 | NULL                | 2020-03-30 15:32:00 |
--|  11 | Вкус и качество блюд                                | like    | NULL           | 2017-12-15 15:49:46 |                  0 |                              1 |                          1 | NULL                | 2020-03-30 15:32:00 |
--|  13 | Удобство упаковки                                   | like    | NULL           | 2017-12-15 15:49:46 |                  0 |                              0 |                          1 | NULL                | 2020-03-30 15:32:00 |
--|  15 | Температура еды                                     | like    | NULL           | 2017-12-15 15:49:46 |                  0 |                              0 |                          1 | NULL                | 2020-03-30 15:32:00 |
--|  17 | Сервис со стороны курьера                           | like    | NULL           | 2017-12-15 15:49:46 |                  0 |                              0 |                          1 | NULL                | 2020-03-30 15:32:00 |
--|  19 | Скорость доставки                                   | like    | delivery_delay | 2017-12-15 15:49:46 |                  1 |                              0 |                          1 | NULL                | 2020-03-30 15:32:00 |
--|  20 | Курьер отдал заказ в руки                           | dislike | NULL           | 2020-03-19 16:04:31 |                  0 |                              0 |                          1 | 2020-03-30 15:32:01 | 2020-03-30 15:32:01 |
--|  25 | Неверно собран заказ                                | dislike | NULL           | 2020-03-25 16:40:18 |                  0 |                              1 |                          2 | NULL                | 2020-03-30 15:32:00 |
--|  30 | Испорчена упаковка                                  | dislike | NULL           | 2020-03-25 16:40:18 |                  0 |                              1 |                          2 | NULL                | 2020-03-30 15:32:00 |
--|  35 | Опоздали с приготовлением                           | dislike | NULL           | 2020-03-25 16:40:18 |                  0 |                              1 |                          2 | NULL                | 2020-03-30 15:32:00 |
--|  40 | Не понравилась еда                                  | dislike | NULL           | 2020-03-25 16:40:18 |                  0 |                              1 |                          2 | NULL                | 2020-03-30 15:32:00 |
--|  45 | Вкус и качество блюд                                | like    | NULL           | 2020-03-25 16:40:18 |                  0 |                              1 |                          2 | NULL                | 2020-03-30 15:32:00 |
--|  50 | Удобство упаковки                                   | like    | NULL           | 2020-03-25 16:40:18 |                  0 |                              1 |                          2 | NULL                | 2020-03-30 15:32:00 |
--|  55 | Сервис со стороны ресторана                         | like    | NULL           | 2020-03-25 16:40:18 |                  0 |                              1 |                          2 | NULL                | 2020-03-30 15:32:00 |
--|  60 | Скорость приготовления                              | like    | NULL           | 2020-03-25 16:40:18 |                  0 |                              1 |                          2 | NULL                | 2020-03-30 15:32:00 |
--|  63 | Не устроил курьер                                   | dislike | NULL           | 2020-05-08 17:18:24 |                  0 |                              0 |                          1 | NULL                | 2020-05-08 17:18:24 |
--|  66 | Сервис со стороны курьера                           | dislike | NULL           | 2020-11-03 18:05:19 |                  0 |                              0 |                          4 | NULL                | 2020-11-03 18:05:19 |
--|  71 | Опоздали с доставкой                                | dislike | delivery_delay | 2020-11-03 18:05:19 |                  0 |                              0 |                          4 | NULL                | 2020-11-03 18:05:19 |
--|  76 | Привезли не всё                                     | dislike | NULL           | 2020-11-03 18:05:19 |                  0 |                              0 |                          4 | NULL                | 2020-11-03 18:05:19 |
--|  81 | Привезли не то                                      | dislike | NULL           | 2020-11-03 18:05:19 |                  0 |                              0 |                          4 | NULL                | 2020-11-03 18:05:19 |
--|  86 | Некачественные продукты                             | dislike | NULL           | 2020-11-03 18:05:19 |                  0 |                              1 |                          4 | NULL                | 2020-11-03 18:05:19 |
--|  91 | Списали неверную сумму                              | dislike | NULL           | 2020-11-03 18:05:19 |                  0 |                              0 |                          4 | NULL                | 2020-11-03 18:05:19 |
--|  96 | Быстро доставили                                    | like    | NULL           | 2020-11-03 18:05:19 |                  0 |                              0 |                          4 | NULL                | 2020-11-03 18:05:19 |
--| 101 | Хорошо упаковали                                    | like    | NULL           | 2020-11-03 18:05:19 |                  0 |                              0 |                          4 | NULL                | 2020-11-03 18:05:19 |
--| 106 | Качественные продукты                               | like    | NULL           | 2020-11-03 18:05:19 |                  0 |                              1 |                          4 | NULL                | 2020-11-03 18:05:19 |
--| 111 | Курьер молодец                                      | like    | NULL           | 2020-11-03 18:05:19 |                  0 |                              0 |                          4 | NULL                | 2020-11-03 18:05:19 |
--+-----+-----------------------------------------------------+---------+----------------+---------------------+--------------------+--------------------------------+----------------------------+---------------------+---------------------+
--30 rows in set (0.02 sec)
INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
1, 'dislike.food', 'DISLIKE_FOOD', 'default', 'dislike', NULL, FALSE, TRUE, 1, 100,
'{native, lavka, shop, pharmacy, bk_logist, retail}', '2017-12-15 15:49:46', NULL,
'{native, lavka, pharmacy, bk_logist}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
3, 'dislike.incorrectly_assembled_order', 'WRONG_SET', 'default', 'dislike', NULL, FALSE, FALSE, 1, 200,
'{native, lavka, shop, pharmacy, bk_logist}', '2017-12-15 15:49:46', NULL,
'{native, lavka, pharmacy, bk_logist}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
5, 'dislike.damaged_packaging', 'CORRUPTED_PACK', 'default', 'dislike', NULL, FALSE, FALSE, 1, 300,
'{}', '2017-12-15 15:49:46', NULL,
'{native, lavka, pharmacy, bk_logist}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
7, 'dislike.food_gets_cold', 'COLD_FOOD', 'default', 'dislike', NULL, FALSE, FALSE, 1, 400,
'{}', '2017-12-15 15:49:46', NULL,
'{native, lavka, pharmacy, bk_logist}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
9, 'dislike.late_delivery', 'LATE', 'default', 'dislike', 'delivery_delay', TRUE, FALSE, 1, 500,
'{}', '2017-12-15 15:49:46', NULL,
'{native, lavka, pharmacy, bk_logist}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
11, 'like.taste_and_quality_of_dishes', 'TASTE_AND_QUALITY', 'default', 'like', NULL, FALSE, TRUE, 1, 100,
'{}', '2017-12-15 15:49:46', NULL,
'{native, lavka, pharmacy, bk_logist}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
13, 'like.convenience_of_packaging', 'COMFORTABLE_PACK', 'default', 'like', NULL, FALSE, FALSE, 1, 200,
'{}', '2017-12-15 15:49:46', NULL,
'{native, lavka, pharmacy, bk_logist}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
15, 'like.food_temperature', 'TEMPERATURE', 'default', 'like', NULL, FALSE, FALSE, 1, 300,
'{}', '2017-12-15 15:49:46', NULL,
'{native, lavka, pharmacy, bk_logist}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
17, 'like.service_of_courier', 'COURIER', 'default', 'like', NULL, FALSE, FALSE, 1, 400,
'{}', '2017-12-15 15:49:46', NULL,
'{native, lavka, pharmacy, bk_logist}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
19, 'like.delivery_speed', 'SPEED', 'default', 'like', 'delivery_delay', TRUE, FALSE, 1, 500,
'{}', '2017-12-15 15:49:46', NULL,
'{native, lavka, pharmacy, bk_logist}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
20, 'dislike.non_contactless_delivery', 'COVID_19', 'default', 'dislike', NULL, FALSE, FALSE, 1, 600,
'{}', '2020-03-19 16:04:31', '2020-03-30 15:32:01',
'{native, lavka, pharmacy, bk_logist}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
25, 'dislike.incorrectly_assembled_order', 'WRONG_SET', 'default', 'dislike', NULL, FALSE, TRUE, 2, 100,
'{native, lavka, shop, pharmacy, bk_logist}', '2020-03-25 16:40:18', NULL,
'{native, lavka, shop, pharmacy, bk_logist, retail}', '{pickup}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
30, 'dislike.damaged_packaging', 'CORRUPTED_PACK', 'default', 'dislike', NULL, FALSE, TRUE, 2, 200,
'{}', '2020-03-25 16:40:18', NULL,
'{native, lavka, shop, pharmacy, bk_logist, retail}', '{pickup}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
35, 'dislike.late_with_cooking', 'LATE_COOK', 'default', 'dislike', NULL, FALSE, TRUE, 2, 300,
'{}', '2020-03-25 16:40:18', NULL,
'{native, lavka, shop, pharmacy, bk_logist, retail}', '{pickup}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
40, 'dislike.food', 'DISLIKE_FOOD', 'default', 'dislike', NULL, FALSE, TRUE, 2, 400,
'{native, lavka, shop, pharmacy, bk_logist, retail}', '2020-03-25 16:40:18', NULL,
'{native, lavka, shop, pharmacy, bk_logist, retail}', '{pickup}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
45, 'like.taste_and_quality_of_dishes', 'TASTE_AND_QUALITY', 'default', 'like', NULL, FALSE, TRUE, 2, 100,
'{}', '2020-03-25 16:40:18', NULL,
'{native, lavka, shop, pharmacy, bk_logist, retail}', '{pickup}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
50, 'like.convenience_of_packaging', 'COMFORTABLE_PACK', 'default', 'like', NULL, FALSE, TRUE, 2, 200,
'{}', '2020-03-25 16:40:18', NULL,
'{native, lavka, shop, pharmacy, bk_logist, retail}', '{pickup}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
55, 'like.restaurant_service', 'RESTAURANT', 'default', 'like', NULL, FALSE, TRUE, 2, 300,
'{}', '2020-03-25 16:40:18', NULL,
'{native, lavka, shop, pharmacy, bk_logist, retail}', '{pickup}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
60, 'like.cooking_speed', 'SPEED_COOK', 'default', 'like', NULL, FALSE, TRUE, 2, 400,
'{}', '2020-03-25 16:40:18', NULL,
'{native, lavka, shop, pharmacy, bk_logist, retail}', '{pickup}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
63, 'dislike.courier', 'BAD_COURIER', 'default', 'dislike', NULL, FALSE, FALSE, 1, 700,
'{}', '2020-05-08 17:18:24', NULL,
'{native, lavka, pharmacy, bk_logist}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
66, 'dislike.service_of_courier', 'COURIER', 'default', 'dislike', NULL, FALSE, FALSE, 4, 100,
'{}', '2020-11-03 18:05:19', NULL,
'{shop, retail}','{marketplace, our_delivery}'

);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
71, 'dislike.late_delivery', 'LATE', 'default', 'dislike', 'delivery_delay', FALSE, FALSE, 4, 200,
'{}', '2020-11-03 18:05:19', NULL,
'{shop, retail}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
76, 'dislike.delivered_not_all', 'NOT_ALL', 'default', 'dislike', NULL, FALSE, FALSE, 4, 300,
'{native, lavka, shop, pharmacy, bk_logist}', '2020-11-03 18:05:19', NULL,
'{shop, retail}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
81, 'dislike.delivered_wrong', 'NOT_IT', 'default', 'dislike', NULL, FALSE, FALSE, 4, 400,
'{native, lavka, shop, pharmacy, bk_logist}', '2020-11-03 18:05:19', NULL,
'{shop, retail}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
86, 'dislike.poor_quality_products', 'PRODUCT_QUALITY', 'default', 'dislike', NULL, FALSE, TRUE, 4, 500,
'{native, lavka, shop, pharmacy, bk_logist, retail}', '2020-11-03 18:05:19', NULL,
'{shop, retail}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
91, 'dislike.wrong_amount_written_off', 'WRONG_AMOUNT', 'default', 'dislike', NULL, FALSE, FALSE, 4, 600,
'{}', '2020-11-03 18:05:19', NULL,
'{shop, retail}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
96, 'like.delivered_quickly', 'SPEED_DELIVERY', 'default', 'like', NULL, FALSE, FALSE, 4, 100,
'{}', '2020-11-03 18:05:19', NULL,
'{shop, retail}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
101, 'like.packed_well', 'GOOD_PACK', 'default', 'like', NULL, FALSE, FALSE, 4, 200,
'{}', '2020-11-03 18:05:19', NULL,
'{shop, retail}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
106, 'like.quality_products', 'GOOD_PRODUCTS', 'default', 'like', NULL, FALSE, TRUE, 4, 300,
'{}', '2020-11-03 18:05:19', NULL,
'{shop, retail}','{marketplace, our_delivery}'
);

INSERT INTO eats_feedback.predefined_comments (
id,tanker_key,code,version,type,group_code,generate_sorrycode,
calculate_average_rating_place,access_mask_for_order_flow,
show_position,rating_flow_types,
created_at,deleted_at,flow_types,delivery_types) VALUES (
111, 'like.courier_well_done', 'COURIER_MOLODETS', 'default', 'like', NULL, FALSE, FALSE, 4, 400,
'{}', '2020-11-03 18:05:19', NULL,
'{shop, retail}','{marketplace, our_delivery}'
);
