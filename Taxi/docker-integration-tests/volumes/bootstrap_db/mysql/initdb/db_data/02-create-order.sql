set foreign_key_checks = 0;

INSERT INTO users
(id, first_name, last_name, email, personal_email_id, uuid, last_login, last_region_id,
 phone_number, personal_phone_id, phone_number_confirmed, payture_password,
 created_at, deactivated_at, updated_at, banned_at, ban_reason, invitecode_id, order_last_delayed_at,
 is_test_account, profile_filled, client_type, settings, last_order_finished_at, passport_uid,
 passport_uid_type, phone_country_code, `type`)
VALUES (3, 'Козьма', 'Прутков', 'cccccc@ccc.ccc', 1, 2, NOW(), 1, '+79682777450', '9aef863cae894bb39a9fabaea851fcd1',
        1, NULL, NOW(), NULL, NOW(), NULL, NULL, NULL, NULL, 0, 0, 'common', 0, NULL,
        333, 1, 'ru', 'native'),
       (4, 'Иван', 'Говнов', 'dddddd@ddd.ddd', 2, 3, NOW(), 1, '+79682777666', '9aef863cae894bb39a9fabaea851fcde',
        1, NULL, NOW(), NULL, NOW(), NULL, NULL, NULL, NULL, 0, 0, 'common', 0, NULL,
        666, 1, 'ru', 'native'),
       (5, 'User', 'Test', 'test@test.ru', 3, 4, NOW(), 1, '+79682777000', '9aef863cae894bb39a9fabaea851fabc',
        1, NULL, NOW(), NULL, NOW(), NULL, NULL, NULL, NULL, 0, 0, 'common', 0, NULL,
        555, 1, 'ru', 'native');

INSERT INTO user_addresses
    (id, updated_at, deleted_at, created_at, city, house, location_latitude, location_longitude, user_id)
VALUES (1, NOW(), NULL, NOW(), 'Moscow', '1', 55.766491, 37.622333, 3),
       (2, NOW(), NULL, NOW(), 'Moscow', '1', 55.766491, 37.622333, 4),
       (3, NOW(), NULL, NOW(), 'Moscow', '1', 55.766491, 37.622333, 5);

INSERT INTO brands
(id, name, created_at, updated_at, notify_emails, category_type, is_stock_supported, surge_ignore, is_store,
 bit_settings, fast_food_notify_time_shift, slug, editorial_verdict, editorial_description, brand_type, business_type)
VALUES
(24668, 'Азбука вкуса', '2019-05-19 17:31:27', '2020-06-24 10:15:09', null, 'client', 1, 0, 0, 9, null,
 'azbuka_vkusa', null, null, 'not_qsr', 'restaurant'),
(111219, 'picker_retail', '2020-11-24 17:46:03', '2021-02-01 13:40:08', null, 'client', 0, 0, 0, 33, null,
 'picker_retail', null, null, 'not_qsr', 'shop');

INSERT INTO brand_additional_settings
(id, brand_id, pickup_type, payment_type, created_at, updated_at) VALUES
(1, 111219, 'our_pickup', 'checkout_dedicated', NOW(), NOW());

INSERT INTO payment_methods
(id, code, enabled, created_at, updated_at)
VALUES (1, 0, 1, NOW(), NOW()),
       (3, 1, 1, NOW(), NOW()),
       (5, 2, 1, NOW(), NOW()),
       (7, 3, 1, NOW(), NOW()),
       (11, 4, 1, NOW(), NOW()),
       (12, 5, 1, NOW(), NOW()),
       (17, 6, 1, NOW(), NOW());

INSERT INTO place_payment_methods
(place_id, payment_method_id, enabled)
VALUES (1, 1, 1),
       (1, 3, 1),
       (1, 5, 1),
       (1, 7, 1),
       (1, 11, 1),
       (1, 12, 1),
       (1, 17, 1),
       (2, 1, 1),
       (2, 3, 1),
       (2, 5, 1),
       (2, 7, 1),
       (2, 11, 1),
       (2, 12, 1),
       (2, 17, 1);

INSERT INTO place_schedule
(id, place_id, weekday, `from`, duration, created_at, updated_at)
VALUES (1, 1, 'monday', '00:00', 1440, NOW(), NOW()),
       (2, 1, 'tuesday', '00:00', 1440, NOW(), NOW()),
       (3, 1, 'wednesday', '00:00', 1440, NOW(), NOW()),
       (4, 1, 'thursday', '00:00', 1440, NOW(), NOW()),
       (5, 1, 'friday', '00:00', 1440, NOW(), NOW()),
       (6, 1, 'saturday', '00:00', 1440, NOW(), NOW()),
       (7, 1, 'sunday', '00:00', 1440, NOW(), NOW()),
       (8, 2, 'monday', '00:00', 1440, NOW(), NOW()),
       (9, 2, 'tuesday', '00:00', 1440, NOW(), NOW()),
       (10, 2, 'wednesday', '00:00', 1440, NOW(), NOW()),
       (11, 2, 'thursday', '00:00', 1440, NOW(), NOW()),
       (12, 2, 'friday', '00:00', 1440, NOW(), NOW()),
       (13, 2, 'saturday', '00:00', 1440, NOW(), NOW()),
       (14, 2, 'sunday', '00:00', 1440, NOW(), NOW());

PREPARE CreatePlaceMenuItem FROM '
INSERT INTO place_menu_items
(id, place_menu_category_id, place_id, name, short_name, description, price, sort, updated_at, deleted_at, created_at,
 available, origin_id, weight, picture, picture_ratio, picture_enabled, reactivate_at, deactivated_at,
 promotional_item_id, ordinary, vat, is_choosable, avatarnica_identity, adult, shipping_type, uuid)
VALUES
(?, ?, ?, ?, null, \'The description\', ?, 100, NOW(), null, NOW(), 1, 1, \'510 г\',
\'0403f7ec7519deb2fb9599c8500285af.jpeg\', 1, 1, null, null, null, 0, 0, 1,
''1368744/0403f7ec7519deb2fb9599c8500285af'', 0, ''all'', null);
';

set @placeId = 1;
set @menuCategoryId = 1;

set @itemId = 1;
set @itemTitle = CONCAT('Item title ', @menuCategoryId, '-', @itemId);
set @itemPrice = 100;
EXECUTE CreatePlaceMenuItem USING @itemId, @menuCategoryId, @placeId, @itemTitle, @itemPrice;
set @itemId = 2;
set @itemTitle = CONCAT('Item title ', @menuCategoryId, '-', @itemId);
set @itemPrice = @itemPrice * 2;
EXECUTE CreatePlaceMenuItem USING @itemId, @menuCategoryId, @placeId, @itemTitle, @itemPrice;
set @itemId = 3;
set @itemTitle = CONCAT('Item title ', @menuCategoryId, '-', @itemId);
set @itemPrice = @itemPrice * 2;
EXECUTE CreatePlaceMenuItem USING @itemId, @menuCategoryId, @placeId, @itemTitle, @itemPrice;

INSERT INTO place_menu_items
(id, place_menu_category_id, place_id, name, short_name, description, price, sort, updated_at, deleted_at, created_at,
 available, origin_id, weight, picture, picture_ratio, picture_enabled, reactivate_at, deactivated_at,
 promotional_item_id, ordinary, vat, is_choosable, avatarnica_identity, adult, shipping_type, uuid)
VALUES
(4, 1, 2, 'Item from retail', null, 'best', 100, 100, NOW(), null, NOW(), 1, 1, '100',
 'fe868b4ec81ec13738a8dd67f85dc7f1.jpeg', 1.0, 1, null, null, null, 0, 10, 1, '3925/fe868b4ec81ec13738a8dd67f85dc7f1',
 0, 'all', null);

INSERT INTO place_menu_item_retail_info
(place_menu_item_id, vendor_code, location, composition, nutritional_value, purpose, storage_requirements,
 expires_in, vendor_country, package_info, vendor_name, barcode_value, barcode_type, barcode_weight_encoding,
 measure_value, measure_quantum, measure_unit, volume_value, volume_unit, is_catch_weight, original_price,
 decimal_original_price, created_at, updated_at)
 VALUES
 (4, 'РН202216', NULL, NULL, 'На 100г. белки: 2,8г., жиры:1,5г., углеводы: 11,8г. Энергетическая ценность: 72 Ккал.',
  NULL, '', '30', NULL, 'Не указано', NULL, '4601662006513', 'code39', 'none', 100, NULL, 'GRM', NULL, NULL, 0, NULL,
  NULL, NOW(), NOW());

PREPARE CreatePlaceMenuCategoryStmt FROM '
INSERT INTO place_menu_categories
(id, place_id, name, is_special_offer, picture, sort, updated_at, created_at, origin_id, deactivated_at,
 use_in_popularity_calculations, available, reactivate_at, schedule_mode, schedule_description,
 is_synced_schedule, uuid)
VALUES
(?, ?, ?, 0, null, 100, \'2020-04-08 12:56:58\', \'2020-04-02 17:20:00\', ?, null, 1, 1, null, \'auto\', null, 1, null)
';

set @originId = 1;
set @categoryStartId = 1;
set @categoryTitlePrefix = 'Category';
set @categoryTitle = CONCAT(@categoryTitlePrefix, ' ', @categoryStartId);
EXECUTE CreatePlaceMenuCategoryStmt USING @categoryStartId, @placeId, @categoryTitle, @originId;

INSERT INTO delivery_zone_vertices
(id, place_id, number, updated_at, deleted_at, created_at, location_latitude, location_longitude)
VALUES
(1, 1, 0, NOW(), null, NOW(), 55.806466, 37.510243),
(2, 1, 1, NOW(), null, NOW(), 55.795621, 37.703824),
(3, 1, 2, NOW(), null, NOW(), 55.715214, 37.711630),
(4, 1, 3, NOW(), null, NOW(), 55.723438, 37.505039),
(5, 2, 0, NOW(), null, NOW(), 55.806466, 37.510243),
(6, 2, 1, NOW(), null, NOW(), 55.795621, 37.703824),
(7, 2, 2, NOW(), null, NOW(), 55.715214, 37.711630),
(8, 2, 3, NOW(), null, NOW(), 55.723438, 37.505039);

INSERT INTO delivery_conditions
(id, name, created_at, updated_at, region_id, place_type)
VALUES
(1, 'test_delivery_condition', NOW(), NOW(), 1, 'native');

INSERT INTO place_delivery_zones
(id, place_id, delivery_condition_id, name, courier_type, average_marketplace_delivery_time, is_synced_schedule,
 created_at, updated_at, deactivated_at, enabled, type, time_of_arrival, shipping_type)
VALUES
(1, 1, 1, 'test_delivery_zone', 'pedestrian', null, 1, NOW(), NOW(), null, 1, 'manual', null, 'delivery'),
(2, 2, 1, 'test_delivery_zone', 'pedestrian', null, 1, NOW(), NOW(), null, 1, 'manual', null, 'delivery');

INSERT INTO place_delivery_zone_vertices
(id, zone_id, number, location_latitude, location_longitude, created_at, updated_at)
VALUES
(1, 1, 0, 55.806466, 37.510243, NOW(), NOW()),
(2, 1, 1, 55.795621, 37.703824, NOW(), NOW()),
(3, 1, 2, 55.715214, 37.711630, NOW(), NOW()),
(4, 1, 3, 55.723438, 37.505039, NOW(), NOW()),
(5, 2, 0, 55.806466, 37.510243, NOW(), NOW()),
(6, 2, 1, 55.795621, 37.703824, NOW(), NOW()),
(7, 2, 2, 55.715214, 37.711630, NOW(), NOW()),
(8, 2, 3, 55.723438, 37.505039, NOW(), NOW());

INSERT INTO place_delivery_zone_working_schedule
(id, zone_id, weekday, `from`, duration, created_at, updated_at)
VALUES (1, 1, 'monday', '00:00', 1440, NOW(), NOW()),
       (2, 1, 'tuesday', '00:00', 1440, NOW(), NOW()),
       (3, 1, 'wednesday', '00:00', 1440, NOW(), NOW()),
       (4, 1, 'thursday', '00:00', 1440, NOW(), NOW()),
       (5, 1, 'friday', '00:00', 1440, NOW(), NOW()),
       (6, 1, 'saturday', '00:00', 1440, NOW(), NOW()),
       (7, 1, 'sunday', '00:00', 1440, NOW(), NOW()),
       (8, 2, 'monday', '00:00', 1440, NOW(), NOW()),
       (9, 2, 'tuesday', '00:00', 1440, NOW(), NOW()),
       (10, 2, 'wednesday', '00:00', 1440, NOW(), NOW()),
       (11, 2, 'thursday', '00:00', 1440, NOW(), NOW()),
       (12, 2, 'friday', '00:00', 1440, NOW(), NOW()),
       (13, 2, 'saturday', '00:00', 1440, NOW(), NOW()),
       (14, 2, 'sunday', '00:00', 1440, NOW(), NOW());

INSERT INTO shipping_type_dictionary
(shipping_type)
VALUES ('all'), ('delivery'), ('pickup');

INSERT INTO price_categories (id, `name`, `value`, updated_at, deleted_at, created_at) VALUES
(1, '₽', 0.00, NOW(), NULL, NOW());

INSERT INTO place_commissions
(id, place_id, fixed_commission, commission, acquiring_commission, available_from, available_to, created_at,
 updated_at, fixed_commission_value, fixed_commission_currency, shipping_type, commission_type)
VALUES (1, 1, null, 0.00, 0.00, NOW(), null, NOW(), NOW(), 0, null, 'delivery', 'delivery');

INSERT INTO legal_info
(id, tin, legal_name, created_at, updated_at)
VALUES (2, '9705114405', 'yandex_eda', NOW(), null);

INSERT INTO order_cancel_reason_groups
(id, name, code, created_at, updated_at, access_mask_for_order_flow)
VALUES (3, 'Курьер', 'courier', NOW(), NOW(), 15),
       (4, 'Сервис', 'service', NOW(), NOW(), 15);

INSERT INTO order_cancel_reasons
(id, group_id, name, code, position, type, created_at, updated_at, deactivated_at, is_system, access_mask_for_order_flow)
VALUES (19, 3, 'Нет курьера на заказ', 'courier.not_found', 301, 'native', NOW(), NOW(), NULL, 0, 5);

INSERT INTO order_cancel_reactions
(id, name, `group`, payload, enabled, created_at, updated_at)
VALUES (21, 'Уведомление и промокод', 'order.cancel.reaction.compensation', '{"situation": "order_cancel.courier"}', 1, NOW(), NOW()),
       (5, 'Разблокировка средств пользователя', 'order.cancel.reaction.unblock', '{}', 1, NOW(), NOW());

INSERT INTO order_cancel_reason_reactions
(id, reason_id, reaction_id, auto, payment_type, created_at, updated_at)
VALUES (1, 19, 21, 1, 1, NOW(), NOW()),
       (2, 19, 21, 1, 0, NOW(), NOW());

INSERT INTO courier_advisor_settings
(id, name, value, updated_at, created_at)
VALUES (381, 'use_taxi_dispatch_fallback', 1, NOW(), NOW()),
       (380, 'logistics_taxi_candidates_usage', 1, NOW(), NOW()),
       (666, 'use_journal_for_cargo_status_flow', 1, NOW(), NOW());

INSERT INTO courier_advisor_region_settings
(id, region_id, name, value, updated_at, created_at)
VALUES (22619, 1, 'use_taxi_dispatch_fallback_region', 1, NOW(), NOW()),
       (22635, 1, 'use_taxi_dispatch_fallback_region_store', 1, NOW(), NOW());

INSERT INTO settings
(id, name, value, updated_at, created_at)
VALUES (55, 'test_phone_confirmation_code', 4827, NOW(), NOW()),
       (355, 'promo_service_enabled', 1, null, NOW()),
       (3, 'fixed_preparation_time_dishes_count', 5, NOW(), NOW()),
       (390, 'pickup_feature_enabled', 1, NOW(), NOW()),
       (4, 'preparation_time_inc_per_dish',  0, NOW(), NOW()),
       (7, 'near_distance', 2.0, NOW(), NOW()),
       (8, 'courier_tempo_near', 15, NOW(), NOW()),
       (10, 'courier_fix_time_near', 6, NOW(), NOW()),
       (9, 'courier_tempo_far', 10, NOW(), NOW()),
       (11, 'courier_fix_time_far', 16, NOW(), NOW()),
       (125, 'vehicle_faraway_distance', 4.0, NOW(), NOW()),
       (127, 'vehicle_tempo_faraway', 3, NOW(), NOW()),
       (129, 'vehicle_fix_time_faraway', 44, NOW(), NOW()),
       (638, 'pickup_cash_enabled', 0, NOW(), NOW()),
       (455, 'eater_eap_login_enabled', 1, NOW(), NOW()),
       (678, 'rest_app_enable_order_editing', 1, NOW(), NOW()),
       (793, 'place_expense_source_disable', 0, NOW(), NOW()),
       (798, 'client_expense_source_disable', 1, NOW(), NOW()),
       (465, 'anti_fraud_enabled', 1, NOW(), NOW()),
       (363, 'google_pay_enabled', 1, NOW(), NOW()),
       (663, 'google_pay_promo_enabled', 1, NOW(), NOW()),
       (739, 'google_pay_ru_enabled', 1, NOW(), NOW()),
       (744, 'google_pay_kz_enabled', 0, NOW(), NOW()),
       (749, 'apple_pay_ru_enabled', 1, NOW(), NOW()),
       (754, 'apple_pay_kz_enabled', 0, NOW(), NOW()),
       (633, 'external_delivery_zone_resolver_enabled', 1, NOW(), NOW()),
       (208, 'nearby_distance', 0.1, NOW(), NOW()),
       (211, 'courier_fix_time_nearby', 1, NOW(), NOW()),
       (57, 'bicycle_near_distance', 2.0, NOW(), NOW()),
       (77, 'enable_logistics_approve', 0, NOW(), NOW()),
       (672, 'enable_3ds_experiment', 1, NOW(), NOW()),
       (348, 'mastercard_promo_setting', 0, NOW(), NOW()),
       (5, 'is_cash_total_limit_enabled', 1, NOW(), NOW()),
       (2, 'cash_total_limit', 3500, NOW(), NOW()),
       (613, 'double_tips_mastercard_promo_enabled', 0, NOW(), NOW()),
       (530, 'elasticsearch_logger_enabled', 0, NOW(), NOW()),
       (6, 'courier_map_timeout', 60, NOW(), NOW()),
       (657, 'expenses_funds_holding_enabled', 0, NOW(), NOW());

INSERT INTO role_permissions
(role_id, permission)
VALUES (1, 'permission.qa.taxi_coords.store') ON DUPLICATE KEY
        UPDATE role_id = 1, permission = 'permission.qa.taxi_coords.store';

set foreign_key_checks = 1;
