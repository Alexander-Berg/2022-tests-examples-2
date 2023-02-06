set foreign_key_checks = 0;

truncate table places;
truncate table countries;
truncate table regions;
truncate table courier_services;
truncate table courier_service_regions;
truncate table suppliers;
truncate table logistic_place_groups;
truncate table logistic_place_groups_places;
truncate table courier_active_shift_state;
truncate table courier_picker_requisites;
truncate table couriers;
truncate table courier_delivery_zones;
truncate table courier_personal_data_identifiers;

INSERT INTO places
(id, price_category_id, name, picture, picture_enabled, rating, updated_at, deleted_at, created_at,
 launched_at, location_latitude, location_longitude, address_city, address_street,
 address_house, address_entrance, address_floor, address_office, address_comment,
 address_reliable, address_full, address_short, average_preparation_time, email, description,
 enabled, slug, address_plot, address_building, bounding_box_left_bottom_latitude,
 bounding_box_left_bottom_longitude, bounding_box_right_top_latitude,
 bounding_box_right_top_longitude, place_group_id, origin_menu_source, payment_method_id,
 crm_comment, company_tin, company_kpp, origin_id, smartomato_user_id, special_menu_origin_id,
 disable_details_comment, disable_details_available_at, disable_details_status,
 disable_details_reason, disable_details_last_call_date, is_updatable_images_on_parsing,
 parser_enabled, popularity_algorithm, place_info_id, promo_available, autocalls_enabled,
 type, couriers_type, average_marketplace_delivery_time, is_fast_food, sort, address_doorcode,
 region_id, footer_description, visibility_mode, average_rating_value, average_rating_count,
 average_rating_created_at, average_rating_show, ads_allowed, contract,
 price_category_autocalculate_enabled, brand_id, avatarnica_identity, courier_delivery_zone_id,
 lpr_email, report_email, accountancy_email, delivery_condition_id, sales_id,
 disable_details_vendor_user_id, legal_name, legal_address, reg_number, salesforce_id,
 bit_settings, availability_strategy, extra_preparation_minutes, extra_preparation_valid_to,
 preparation_time, address_client_comment, onboarding_type)
VALUES (1, 1, 'Магазин Азбука Вкуса 1', '5690fbc0a60191c4a154306926edc074.jpg', 1, 1.00, '2020-06-24 22:24:18',
        null, '2020-04-02 15:47:04', '2020-04-03 10:06:00', 55.766491, 37.622333, 'Москва',
        'Трубная площадь', '2', null, null, null, 'На входе будет стол', 1, 'Россия, Москва, Трубная площадь, 2',
        'Трубная площадь, 2', 22, 'fnikitina@fomiceva.biz', null, 1, 'azbuka_vkusa', null,
        null, 0.000000, 0.000000, 0.000000, 0.000000, 1610, null, 2,
        'Интеграция. ДОБАВОЧНЫЙ НОМЕР ДЛЯ АВТООБЗВОНА 0201', null, null, '30', null, null, null, null, null, null,
        null, 1, 1, 'only_automatic', null, 0, 1, 'native', null, null, 0, 100, null, 1, '', 'on', 4.8125, 48,
        '2020-05-26 01:02:18', 1, 0, 'primary', 1, 24668, '1387779/5690fbc0a60191c4a154306926edc074', 6593,
        'akrasovskiy@azbukavkusa.ru', null, 'ngorbacheva@azbukavkusa.ru', null, 3, null,
        'ООО "Городской супермаркет"', null, '1027705012312', '0013X00002ckVhwQAE', 0, null, 0, null, 5, null,
        'directive'),
       (2, null, 'Retail Shop Test', '13875fd3cca19bb8cc1b8ceb7a191c81.jpeg', 1, 6.00, '2022-02-15 10:07:57', null,
        '2022-02-03 11:28:28', '2022-02-03 12:38:00', 55.766491, 37.622333, 'Москва', 'улица Верхняя Масловка', '22',
        null, null, null, null, 1, 'Россия, Москва, улица Верхняя Масловка, 22', 'улица Верхняя Масловка, 22', 30,
        'shop@test.tt', null, 1, 'retail_shop', null, null, 0.000000, 0.000000, 0.000000, 0.000000, 221094, null, 2,
        null, null, null, '0c237395-fcc2-11e8-a324-0cc47aab7cf9', null, null, null, null, null, null, null, 1, 1,
        'only_automatic', null, 0, 0, 'native', null, null, 0, 100, null, 1, '', 'on', null, 0, null, 0, 1, 'primary',
        1, 111219, '69745/13875fd3cca19bb8cc1b8ceb7a191c81', 6593, 'retail_shop@test.tt', null, null, null, 1228, null,
        null, null, '', null, 0, null, 0, null, 1, null, 'directive');

INSERT INTO place_groups (id, name, updated_at, deleted_at, created_at, integration_engine_id, organization_id, options,
                          menu_parser_enabled, order_sender_enabled, parser_days_of_week, parser_hours,
                          stop_list_aggregator, price_parser_aggregator, price_parser_times, menu_parser_name,
                          menu_parser_options, need_order_email_notification, delay_to_auto_confirm, picture,
                          type_id, vox_implant_enabled, avatarnica_identity, vox_implant_client_permission_delay,
                          immediately_send_orders, place_group_setting_id, is_fast_food, use_integration_kernel,
                          places_stop_list_aggregator, is_duplicate_to_vendor, stock_reset_limit,
                          native_vox_implant_strategy, place_schedule_parser_name,
                          place_schedule_parser_days_of_week, place_schedule_parser_hours,
                          use_nomenclature_service_synchronization,
                          use_client_categories_synchronization_with_menu, updating_to_terminal_status,
                          place_schedule_parser_closing_time_correction, place_schedule_parser_excluded_place_ids,
                          ignore_redis_lock) VALUES
(1610, 'test_place_group', NOW(), NULL, NOW(), NULL, NULL, '[]', 0, 0, '1111111', '8:00', NULL, NULL, NULL, NULL, NULL,
 1, 3, NULL, NULL, 0, NULL, 0, 0, 1, 0, '00000', NULL, 0, 0, 0, NULL, NULL, NULL, 0, 0, 0, NULL, NULL, 0),
(221094, 'picker_spb', NOW(), NULL, NOW(), 120, '1',
 '{"vendorHost":"http:\\/\\/eats-picker-orders.eda.yandex.net\\/api\\/v1","supportCatchweightGoods":true,"orderConfirmationRequired":false,"acceptedByPlaceStatuses":["assigned","picking","picked_up","paid","complete"],"apiVersion":"v2","softChecker":"Magnit","softChequeHost":null,"softChequeToken":"fc1fc11d9e2b01b19e6569f259cd13a05e90e320589eeac8d42d183d3dec923a201cb216328982ad9eed5212a7a026a7314e0eadf4f501d8ac3283ae5f7c2bf2","softChequeConfirmationType":"barcode","softChequeDescription":"","softChequeBarcodeType":"code128","softChequeConfirmationCode":"3232","softChequeShouldSendPhone":false,"softChequeShouldSendPromocode":false}',
 0, 0, '0000000', '9:00', 'retail_availability_aggregator', NULL, NULL,
 'miratorg_retail_menu', '{"clientId":"Yandex","clientSecret":"527a57c3-9616-4ca7-93dd-6f7e840cb2c4","scope":"write","vendorHost":"http:\\/\\/app00000-6.my-miratorg.ru\\/InternetShopTest\\/hs\\/v1","timeouts":null,"limitCCDeep":false,"parseOnlyFromLowLevelCategories":true,"moveDishesToOthersCategory":false,"supportCatchWeightGoods":true,"apiVersion":"v1","priceRoundingStrategy":"floor","imageTransportTimeout":null}',
 0, 2, NULL, NULL, 1, NULL, 0, 0, 1, 0, '00001', NULL, 0, 1, 1, NULL, '1111111', NULL, 0, 1, 0, NULL, NULL, 0);

INSERT INTO place_group_settings (parser_filters, use_dynamic_config, menu_item_sort_source, delivery_zone_parser,
                                  delivery_zone_parser_options, created_at, updated_at) VALUES
(NULL, 0, 0, NULL, NULL, NOW(), NOW());

INSERT INTO integration_engines (id, name, updated_at, deleted_at, created_at, is_hidden) VALUES
(120, 'PickOrders API', NULL , NULL, NOW(), 0);

INSERT INTO countries (id, code, name, name_in_yandex_forms, created_at, updated_at, currency_code,
                       user_agreement_link, promo_codes_agreement_link) VALUES
('1', 'RU', 'Российская Федерация', 'Российская Федерация', NOW(), NULL, 'RUB', NULL, NULL);

INSERT INTO regions (id, is_available, is_default, name, center_location_latitude,
                     center_location_longitude, bounding_box_left_top_latitude,
                     bounding_box_left_top_longitude, bounding_box_right_bottom_latitude,
                     bounding_box_right_bottom_longitude, created_at, vox_implant_code,
                     vox_implant_enabled, slug, prepositional, region_setting_id, timezone,
                     sort, oktmo, billing_subregion_id, country_id, deleted_at, courier_training_type) VALUES
('1', '1', '1', 'test_region_moscow', '55.724266', '37.642806', '56.473673', '35.918658', '54.805858', '39.133684',
 NOW(), NULL, '0', 'moscow', 'в Москве', '1', 'Europe/Moscow', '1', '45000000', '1', '1', NULL, 'offline');

INSERT INTO courier_services
    (id, name, vat, created_at, updated_at, position_of_head, full_name_of_head, full_name_of_chief_accountant,
     disabled_for_cash_orders, test, address, work_schedule, status, post_suffix, country_id) VALUES
(1, 'test', 1, NOW(), NOW(), '1', 'head', 'head_accountant', 0, 0, 'test_address', 'test_schedule', 'active',
 'test_post_suffix', 1);

INSERT INTO courier_service_regions (courier_service_id, region_id) VALUES
(1, 1);

INSERT INTO suppliers (id, logistic_place_group_id, name, external_id, type, subtype, travel_type,
                       region_id, available_until, created_at, updated_at, is_picker,
                       is_special_collector, is_rover) VALUES
(1, 1, 'test', '1', 'eda_courier', 'planned', 'pedestrian', 1, '2100-01-01T00:00:00', NOW(), NOW(), 1, 1, 0),
(2, 1, 'test1', '2', 'eda_courier', 'planned', 'pedestrian', 1, '2100-01-01T00:00:00', NOW(), NOW(), 0, 0, 0),
(3, 2, 'test2', '3', 'eda_courier', 'planned', 'pedestrian', 1, '2100-01-01T00:00:00', NOW(), NOW(), 0, 1, 0);

INSERT INTO logistic_place_groups (id, name, is_enabled, zone_id, meta_group, return_point_latitude,
                                   return_point_longitude, created_at, updated_at) VALUES
(1, 'test', 1, 1, NULL, 55.766491, 37.622333, NOW(), NOW()),
(2, 'test1', 1, NULL, NULL, 55.766491, 37.622333, NOW(), NOW());

INSERT INTO logistic_place_groups_places (logistic_place_group_id, place_id) VALUES
(1, 1), (2, 2);

INSERT INTO courier_active_shift_state (courier_id, shift_id, state, closes_at,
                                        created_at, updated_at, started_at, is_high_priority) VALUES
(1, 1, 'opened', '2100-01-01T00:00:00', NOW(), NOW(), NOW(), 1),
(2, 2, 'opened', '2100-01-01T00:00:00', NOW(), NOW(), NOW(), 1),
(3, 1, 'opened', '2100-01-01T00:00:00', NOW(), NOW(), NOW(), 1);

INSERT INTO courier_picker_requisites (courier_id, type, `value`, created_at, updated_at) VALUES
(1, 'TinkoffCardCode', '1234567890', NOW(), NOW()),
(1, 'TinkoffCardNum', '1234', NOW(), NOW()),
(3, 'TinkoffCardCode', '1234567890098', NOW(), NOW()),
(3, 'TinkoffCardNum', '1234', NOW(), NOW());

INSERT INTO couriers (id, type, username, salt, `password`, phone_number, updated_at,
                      created_at, location_latitude, location_longitude, logged_out_at, blocked_until,
                      courier_zone_id, courier_zone_updated_at, region_id, courier_service_id,
                      identity_document, work_status, billing_type, partner_id, `source`,
                      `comment`, is_order_assign_available, zendesk_task_id, pool_name,
                      is_subscribed_to_push, work_status_updated_at) VALUES
(1, 'pedestrian', 'test', '9kn0yoj93lcsssogo8wc4s8ok8oc0sg',
 '$2y$08$9EdeeuqI1I2bF3B01UahSOFcVXrJQSWpfqr5bkJC40YdZGs9VUriC', '+79999999999', NOW(), NOW(),
 55.766491, 37.622333, null, null, 1, NOW(), 1, 1, '1111 111111', 'active', 'courier_service',
 null, null, '', 1, null, 'eda', 1, NOW()),
(2, 'pedestrian', 'test1', '9kn0yoj93lcsssogo8wc4s8ok8oc0sg',
 '$2y$08$9EdeeuqI1I2bF3B01UahSOFcVXrJQSWpfqr5bkJC40YdZGs9VUriC', '+79999999998', NOW(), NOW(),
  55.766491, 37.622333, null, null, 1, NOW(), 1, 1, '2222 222222', 'active', 'courier_service',
 null, null, '', 1, null, 'eda', 1, NOW()),
(3, 'pedestrian', 'test2', '9kn0yoj93lcsssogo8wc4s8ok8oc0sg',
 '$2y$08$9EdeeuqI1I2bF3B01UahSOFcVXrJQSWpfqr5bkJC40YdZGs9VUriC', '+79006666621', NOW(), NOW(),
 55.766491, 37.622333, null, null, 1, NOW(), 1, 1, '3333 333333', 'active', 'courier_service',
 null, null, '', 1, null, 'eda', 1, NOW());

INSERT INTO courier_billing_data (id, client_id, created_at) VALUES
(1, 123, NOW()),
(2, 223, NOW());

INSERT INTO courier_delivery_zones (id, `name`, region_id, enabled, created_at, updated_at, revision_id) VALUES
(1, 'test', 1, 0, NOW(), NOW(), 1);

INSERT INTO courier_personal_data_identifiers (id, phone_number, email, inn, identity_document, telegram_name,
                                               address, created_at, birth_place, birth_at, migration_card,
                                               migration_card_issued_at, address_registration,
                                               address_registration_at, identity_document_type,
                                               identity_document_series, identity_document_number,
                                               identity_document_issued_at, identity_document_issued_by) VALUES
(1, '68696aae79e7486cb389503778ddf1a0', '6e444832bbb84387a5d9f4e32002c24a', null, '11cedf8bf1074463ab981e8960104e06',
 null, null, NOW(), null, null, null, null, null, null, null, null, null, null, null),
(2, '68696aae79e7486cb389503778ddf1a0', '6e444832bbb84387a5d9f4e32002c24a', null, '11cedf8bf1074463ab981e8960104e06',
 null, null, NOW(), null, null, null, null, null, null, null, null, null, null, null),
(3, '68696aae79e7486cb389503778ddf1a0', '6e444832bbb84387a5d9f4e32002c24a', null, '11cedf8bf1074463ab981e8960104e06',
 null, null, NOW(), null, null, null, null, null, null, null, null, null, null, null);

set foreign_key_checks = 1;
