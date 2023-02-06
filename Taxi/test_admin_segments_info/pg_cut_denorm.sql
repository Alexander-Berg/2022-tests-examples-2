ALTER TABLE cargo_claims.additional_info DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.cargo_finance_claim_estimating_results DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_audit DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_changes DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_custom_context DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_estimating_results DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_features DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_point_time_intervals DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_points DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_segment_points DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_segment_points_change_log DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_segments DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_warnings DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claims DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claims_c2c DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.courier_manual_dispatch DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.documents DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.items DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.items_exchange DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.items_fiscalization DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.matched_cars DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.matched_items DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.payment_on_delivery DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.points DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.points_ready_for_interact_notifications DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.taxi_order_changes DISABLE TRIGGER ALL;
ALTER TABLE cargo_claims.taxi_performer_info DISABLE TRIGGER ALL;

INSERT INTO cargo_claims.additional_info
SELECT *
FROM json_populate_record (NULL::cargo_claims.additional_info,
'{
 "assign_robot": true,
 "cargo_loaders": 2,
 "cargo_options": ["cargo_options"],
 "cargo_type": "lcv_l",
 "claim_id": 1,
 "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
 "extra_requirements": {
   "extra_requirement": 123
 },
 "id": 189000,
 "pro_courier": true,
 "recipient_address": "adress",
 "recipient_is_individual": true,
 "recipient_name": "name",
 "recipient_phone_number_pd_id": "pd_id",
 "shipment_details": "shipment_details",
 "shipment_name": "shipment_name",
 "shipping_document": "smth",
 "taxi_class": "courier",
 "taxi_classes": ["courier"],
 "updated_ts": "2021-01-01T00:00:04+00:00",
 "vehicle_requirements": "vehicle_requirements"
}'
);

INSERT INTO cargo_claims.cargo_finance_claim_estimating_results
SELECT *
FROM json_populate_record (NULL::cargo_claims.cargo_finance_claim_estimating_results,
   '{
     "cardstorage_id": "card-x9f185f4d7c685a5db1fc1654",
     "cargo_claim_id": "9756ae927d7b42dc9bbdcbb832924343",
     "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
     "id": 1,
     "owner_yandex_uid": "4079315220"
   }'
);

INSERT INTO cargo_claims.claim_audit
SELECT *
FROM json_populate_record (NULL::cargo_claims.claim_audit,
'{
 "claim_id": 1,
 "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
 "comment": "Заказ закрыт автоматически по факту прихода исполнителя в точку Б",
 "corp_client_id": "798838e4b169456eb023595801bbb366",
 "event_time": "2021-01-01T00:00:04+00:00",
 "id": 1,
 "is_delayed": false,
 "new_current_point": 1,
 "new_status": "pickuped",
 "old_current_point": 1,
 "old_status": "delivery_arrived",
 "ticket": "CHATTERBOX-74946",
 "zone_id": "moscow"
}'
);

INSERT INTO cargo_claims.claim_changes
SELECT *
FROM json_populate_record (NULL::cargo_claims.claim_changes,
'{
 "claim_id": "9756ae927d7b42dc9bbdcbb832924343",
 "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
 "created_ts": "2021-01-01T00:00:04+00:00",
 "error_code":  "some_error",
 "error_params":  {
   "additional_error_code": "second_error_code"
 },
 "id": 93292,
 "kind": "change_comment",
 "last_known_revision": "1",
 "request_id": "210705-045523-60e30365334b1",
 "status": "applied"
}'
);

INSERT INTO cargo_claims.claim_custom_context
SELECT *
FROM json_populate_record (NULL::cargo_claims.claim_custom_context,
'{
 "claim_id": 1,
 "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
 "context": {
   "brand_id": 3529,
   "brand_name": "Макдоналдс"
 },
 "id": 1,
 "updated_ts": "2021-01-01T00:00:04+00:00"
}'
);

INSERT INTO cargo_claims.claim_estimating_results
SELECT *
FROM json_populate_record (NULL::cargo_claims.claim_estimating_results,
'{
 "cargo_claim_id": "9756ae927d7b42dc9bbdcbb832924343",
 "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
 "created_ts": "2021-01-01T00:00:04+00:00",
 "failure_reason": "estimating.too_large_linear_size",
 "id": 1,
 "status": "succeed",
 "taxi_classes_substitution": [
   "courier",
   "express"
 ],
 "taxi_offer_id": "cargo-pricing/v1/d2144396-9a93-4ab1-bf02-545d3988ec72",
 "taxi_offer_price": "285.0000",
 "taxi_offer_price_mult": "342.0000",
 "taxi_offer_price_raw": 285,
 "updated_ts": "2021-01-01T00:00:04+00:00",
 "valid_until": "2021-01-01T00:00:04+00:00"
}'
);

INSERT INTO cargo_claims.claim_features
SELECT *
FROM json_populate_record (NULL::cargo_claims.claim_features,
'{
 "claim_id": 1,
 "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
 "feature_name": "limited_paid_waiting",
 "id": 1,
 "updated_ts": "2021-01-01T00:00:04+00:00"
}'
);

INSERT INTO cargo_claims.claim_points
SELECT *
FROM json_populate_record (NULL::cargo_claims.claim_points,
'{
  "claim_id": 1,
  "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
  "id": 1,
  "last_status_change_ts": "2021-01-01T00:00:04+00:00",
  "leave_under_door": true,
  "meet_outside": true,
  "no_door_call": true,
  "modifier_age_check": true,
  "pickup_code": "5555",
  "pickup_code_receipt_timestamp": "2021-01-01T00:00:04+00:00",
  "point_id": 2,
  "return_comment": "Груз больше нормы",
  "return_reasons": ["return_reasons"],
  "sharing_key": "3e6bfd3d290c49dc9f67824c415a62ba",
  "skip_confirmation": true,
  "type": "source",
  "updated_ts": "2021-01-01T00:00:04+00:00",
  "uuid": "03c7fb984afa42a4a2f1bf5a8a5c9842",
  "visit_order": 1,
  "visit_status": "visited"
}'
);

INSERT INTO cargo_claims.claim_segment_points
SELECT *
FROM json_populate_record (NULL::cargo_claims.claim_segment_points,
'{
 "claim_point_id": 1,
 "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
 "created_ts": "2021-01-01T00:00:04.000000+00:00",
 "id": 1,
 "is_fixed_visit_order": false,
 "last_status_change_ts": "2021-01-01T00:00:04.000000+00:00",
 "location_id": "03c7fb984afa42a4a2f1bf5a8a5c9842",
 "revision": 3,
 "segment_id": 7,
 "type": "destination",
 "updated_ts": "2021-01-01T00:00:04.000000+00:00",
 "uuid": "64870b88-414f-4688-bf58-b21127baf9a9",
 "visit_order": 1,
 "visit_status": "visited",
 "visited_times": 0
}'
);

INSERT INTO cargo_claims.claim_segment_points_change_log
SELECT *
FROM json_populate_record (NULL::cargo_claims.claim_segment_points_change_log,
'{
 "cargo_order_id": "2901eaff-9a7a-4799-9cdd-e6a8d0a727ad",
 "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
 "driver_id": "11ff3c0b6e484370ac94473f997eb8b3",
 "event_time": "2021-01-01T00:00:04.000000+00:00",
 "id": 1,
 "new_visit_status": "visited",
 "old_visit_status": "arrived",
 "point_uuid": "64870b88-414f-4688-bf58-b21127baf9a9",
 "segment_point_id": 1,
 "updated_ts": "2021-01-01T00:00:04.000000+00:00"
}'
);

INSERT INTO cargo_claims.claim_segments
SELECT *
FROM json_populate_record (NULL::cargo_claims.claim_segments,
'{
 "autoreorder_flow": "newway",
 "cargo_order_id": "25705ef6-e3e7-46fc-8126-863fc4e88ff6",
 "allow_batch": true,
 "claim_id": 1,
 "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
 "created_ts": "2021-01-01T00:00:05.000000+00:00",
 "current_point": 1,
 "dispatch_requirements": {
   "soft_requirements": [{
     "type": "performer_group",
     "meta_group": "lavka",
     "logistic_group": "140",
     "performers_restriction_type": "group_only"
   }]
 },
 "dispatch_revision": 5,
 "id": 7,
 "paper_act": false,
 "perform_order": 1,
 "points_user_version": 1,
 "provider_order_id": "69b88e9887cb432facdc274e0a237fcd",
 "resolution": "finished",
 "resolved_at": "2021-01-01T00:00:05.000000+00:00",
 "revision": 15,
 "special_requirements": {
   "virtual_tariffs": []
 },
 "status": "delivered_finish",
 "updated_ts": "2021-01-01T00:00:05.000000+00:00",
 "uuid": "9756ae927d7b42dc9bbdcbb832924343"
}'
);

INSERT INTO cargo_claims.claim_warnings
SELECT *
FROM json_populate_record (NULL::cargo_claims.claim_warnings,
'{
  "claim_id": 1,
  "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
  "code": "not_fit_in_car",
  "details_args": {
      "item_title": "Биг Тейсти МакКомбо Большой"
  },
  "details_code": "estimating.warning.too_large_item",
  "id": 5380711,
  "source": "client_requirements",
  "updated_ts": "2021-01-01T00:00:00.000000+00:00"
}'
);

INSERT INTO cargo_claims.claims
SELECT *
FROM json_populate_record (NULL::cargo_claims.claims,
'{
  "admin_cancel_reason": "customer_mistake.point_off",
  "api_kind": "api",
  "autocancel_reason": "performer_not_found_after_support_autoreorder",
  "callback_url": "https://courier.foodfox.ru",
  "cargo_pricing_price": "231",
  "claim_kind": "delivery_service",
  "claim_taxi_requirements": {
    "some_requirement": "str"
  },
  "comment": "Доставка из магазина \"ВкусВилл\"",
  "corp_client_id": "798838e4b169456eb023595801bbb366",
  "created_ts": "2021-01-01T00:00:00.000000+00:00",
  "currency": "RUB",
  "currency_rules": {
      "code": "RUB",
      "sign": "RUB",
      "text": "RUB",
      "template": "RUB"
  },
  "current_point": 1,
  "customer_ip": "127.0.0.1",
  "dispatch_requirements": {
      "soft_requirements": [{
          "type": "performer_group",
          "meta_group": "lavka",
          "logistic_group": "2565",
          "performers_restriction_type": "no_restrictions"
      }]
  },
  "due": "2021-01-02T00:00:00.000000+00:00",
  "emergency_fullname": "Контакт-центр",
  "emergency_personal_phone_id": "4e243e5adea44cedacb69ef833315b29",
  "eta": 30,
  "final_price": "231.0000",
  "final_price_mult": "277.2000",
  "final_pricing_calc_id": "cargo-pricing/v1/72cbc66d8f68412fa2719e8ffd808f58",
  "id": 1,
  "idempotency_token": "9edcfca2d5354161b6564a0bac69dabd",
  "is_delayed": false,
  "is_new_logistic_contract": false,
  "just_client_payment": true,
  "last_status_change_ts": "2021-01-01T00:00:50.000000+00:00",
  "mpc_billing_rev": "claim/order/04c86eb6f01c458099033eb22bbb7b6f/2",
  "mpc_comment": "cargo_claims.manual_price_correction.reasons.other",
  "mpc_corrections_count": 6,
  "mpc_reason": "03fc3781ab7a45d689665f30c6bf9ed1",
  "mpc_source": "",
  "mpc_yandex_login": "user",
  "mpc_yandex_uuid": "1120000000222563",
  "optional_return": false,
  "paper_act": false,
  "price_multiplier": "1.2000",
  "processing_create_event": "create",
  "processing_flow": "enabled",
  "referral_source": "bitrix",
  "return_comment": "Коментарий о возврате",
  "revision": 1,
  "skip_act": false,
  "skip_client_notify": false,
  "skip_door_to_door": false,
  "skip_emergency_notify": false,
  "status": "new",
  "taxi_order_id": "5bef015c4d344936b9a0747462098c89",
  "taxi_user_id": "a11bc7128d9a4f2da0ea216274a39fe8",
  "updated_ts": "2021-01-01T00:00:04.000000+00:00",
  "user_locale": "ru",
  "uuid_id": "9756ae927d7b42dc9bbdcbb832924343",
  "version": 1,
  "yandex_login": "user_yandex",
  "zone_id": "irkutsk"
}'
);

INSERT INTO cargo_claims.claims_c2c
SELECT *
FROM json_populate_record (NULL::cargo_claims.claims_c2c,
'{
  "cargo_c2c_order_id": "953bdb0d8a784e7aa472f1f94d16b09e",
  "claim_id": 1,
  "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
  "created_ts": "2021-01-01T00:00:04+00:00",
  "id": 1,
  "idempotency_token": "d4e2ae26647649bc9bb755d7e856aeb1",
  "partner_tag": "some_partner_tag",
  "payment_method_id": "card-xb534d9bc86cbc48fd82ae4d6",
  "payment_type": "card",
  "updated_ts": "2021-01-01T00:00:04+00:00",
  "yandex_uid": "1306848605"
}'
);

INSERT INTO cargo_claims.courier_manual_dispatch
SELECT *
FROM json_populate_record (NULL::cargo_claims.courier_manual_dispatch,
'{
  "claim_id": "9756ae927d7b42dc9bbdcbb832924343",
  "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
  "corp_client_id": "smth",
  "courier_id": "7ad36bc7560449998acbe2c57a75c293_c2c06341661838d48dffc39f529e8ea7",
  "id": 1,
  "is_processed": true,
  "revision": 1
}'
);

INSERT INTO cargo_claims.documents
SELECT *
FROM json_populate_record (NULL::cargo_claims.documents,
'{
  "claim_id": "9756ae927d7b42dc9bbdcbb832924343",
  "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
  "claim_status": "delivered",
  "document_type": "act",
  "driver_id": "471f13434c3f4458bd458ba2ad3443f5",
  "id": 1,
  "is_deleted": false,
  "last_fail_reason": "signed_contract_not_found",
  "mds_path": "documents/1279f465d72e4292a1044eb8880f7a77",
  "park_id": "e7d6f9ae35c94422a4a86abec9d4b4e3",
  "updated_ts": "2021-01-01T00:00:04+00:00"
}'
);

INSERT INTO cargo_claims.items
SELECT *
FROM json_populate_record (NULL::cargo_claims.items,
'{
 "claim_id": 1,
 "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
 "cost_currency": "RUB",
 "cost_value": 39,
 "created_ts": "2021-01-01T00:00:04+00:00",
 "delivery_status": "pending",
 "droppof_point": 1,
 "extra_id": "5_9018",
 "id": 1,
 "pickup_point": 1,
 "quantity": 1,
 "return_point": 1,
 "size_h": 0.3,
 "size_l": 0.45,
 "size_w": 0.45,
 "title": "Соус 1000 островов",
 "updated_ts": "2021-01-01T00:00:04+00:00",
 "uuid": "215126a264cb49b6986d111240da7914",
 "weight": 0.025
}'
);

INSERT INTO cargo_claims.items_exchange
SELECT *
FROM json_populate_record (NULL::cargo_claims.items_exchange,
'{
  "claim_id": 1,
  "claim_point_id": 1,
  "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
  "id": 1,
  "item_id": 1,
  "quantity": 1,
  "updated_ts": "2021-01-01T00:00:04+00:00"
}'
);

INSERT INTO cargo_claims.items_fiscalization
SELECT *
FROM json_populate_record (NULL::cargo_claims.items_fiscalization,
'{
  "article": "20ML50OWKY4FC86",
  "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
  "country_of_origin_code": "РОССИЯ",
  "created_ts": "2021-01-01T00:00:04+00:00",
  "customs_declaration_number": "0",
  "excise": "0.0000",
  "id": 1,
  "item_id": 1,
  "item_type": "service",
  "payment_mode": "full_payment",
  "payment_subject": "commodity",
  "product_code": "some_product_code",
  "supplier_inn": "5260465923",
  "updated_ts": "2021-01-01T00:00:04+00:00",
  "vat_code": 1,
  "vat_code_str": "vat0"
}'
);

INSERT INTO cargo_claims.matched_cars
SELECT *
FROM json_populate_record (NULL::cargo_claims.matched_cars,
'{
 "cargo_claim_id": "9756ae927d7b42dc9bbdcbb832924343",
 "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
 "cargo_loaders": 2,
 "cargo_points": [1, 1],
 "cargo_points_field": "fake_middle_point_cargocorp_lcv_l",
 "cargo_type": "lcv_l",
 "cargo_type_int": 3,
 "client_taxi_class": "cargo",
 "door_to_door": true,
 "id": 166988,
 "pro_courier": true,
 "taxi_class": "express",
 "updated_ts": "2021-01-01T00:00:04+00:00"
}'
);

INSERT INTO cargo_claims.matched_items
SELECT *
FROM json_populate_record (NULL::cargo_claims.matched_items,
'{
  "car_id": 1,
  "cargo_claim_id": "9756ae927d7b42dc9bbdcbb832924343",
  "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
  "comment": "matched_item_comment",
  "id": 1,
  "item_id": 1,
  "quantity": 1,
  "status": "succeed",
  "updated_ts": "2021-01-01T00:00:04+00:00"
}'
);

INSERT INTO cargo_claims.points
SELECT *
FROM json_populate_record (NULL::cargo_claims.points,
'{
  "building": "3А ",
  "building_name": "name",
  "city": "Москва",
  "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
  "comment": "Магазин: Азбука вкуса, номер заказа: 210210-523891.\n",
  "contact_name": "Азбука вкуса",
  "contact_personal_email_id": "f1009bd5b5a648de84ae107ce9046d49",
  "contact_personal_phone_id": "3e684088c55f4f29bd0fa59cb163966f",
  "contact_phone_additional_code": "602 17 500",
  "country": "Российская Федерация",
  "created_ts": "2021-01-01T00:00:04+00:00",
  "description": "description",
  "diagnostics": {
    "geocoder": {
      "uri": null,
      "shortname": null,
      "description": null,
      "distance_from_origin": 5578849.840437059
    }
  },
  "door_code": "не работает",
  "door_code_extra": "K",
  "doorbell_name": "K",
  "external_order_cost_currency": "RUB",
  "external_order_cost_sign": "P",
  "external_order_cost_value": "100",
  "external_order_id": "210406-074879",
  "flat": 148,
  "floor": 3,
  "fullname": "Россия, Санкт-Петербург, Ново-Александровская улица, 3А",
  "id": 2,
  "latitude": 0.0,
  "longitude": 0.0,
  "porch": "10",
  "ready_for_interact": "2021-01-01T00:00:04+00:00",
  "sflat": "148",
  "sfloor": "3",
  "shortname": "проспект Энгельса, 154",
  "street": "улица Сергея Макеева",
  "time_interval_from": "2021-01-01T00:00:04+00:00",
  "time_interval_to": "2021-01-01T00:00:04+00:00",
  "updated_ts": "2021-01-01T00:00:04+00:00",
  "uri": "ymapsbm1://geo?ll=30.335%2C60.059&spn=0.001%2C0.001&text="
}'
);

INSERT INTO cargo_claims.taxi_order_changes
SELECT *
FROM json_populate_record (NULL::cargo_claims.taxi_order_changes,
'{
  "claim_id": 1,
  "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
  "created_ts": "2021-01-01T00:00:04+00:00",
  "id": 1,
  "new_claim_status": "delivered_finish",
  "reason": "taxi_order_complete",
  "taxi_order_id": "b68b2eb2d3f7c7a581f55bebfea74488",
  "updated_ts": "2021-01-01T00:00:04+00:00"
}'
);

INSERT INTO cargo_claims.taxi_performer_info
SELECT *
FROM json_populate_record (NULL::cargo_claims.taxi_performer_info,
'{
 "car_color": "blue",
 "car_color_hex": "some_code",
 "car_id": "bc2eb90af7ae1d78bfadada3102948ed",
 "car_model": "Hyundai Solaris",
 "car_number": "А777МР777",
 "claim_id": 1,
 "claim_uuid": "9756ae927d7b42dc9bbdcbb832924343",
 "created_ts": "2021-01-01T00:00:04+00:00",
 "dispatch_revision": 1,
 "driver_id": "6938e2a1d918cdc1ae2c4b1ec25e3294",
 "id": 3089477,
 "ip": "2a02:6b8:c0b:6a1c:0:42d5:198e:0",
 "lookup_version": 12,
 "name": "Пешев Пеш19 Пешевич",
 "order_alias_id": "88782cd70644c7e99f7bbfef610536ca",
 "park_clid": "12345678910",
 "park_id": "0253f79a86d14b7ab9ac1d5d3017be47",
 "park_name": "Тест-Курьер ООО",
 "park_org_name": "Тест-Курьер ООО",
 "phone_pd_id": "debc244580cd48759e5d1764b759f9d6",
 "segment_id": 46697,
 "tariff_class": "econom",
 "taxi_order_id": "9293457ef0ef3629a51b1de72c0fca01",
 "transport_type": "car",
 "updated_ts": "2021-01-01T00:00:04+00:00"
}'
);

ALTER TABLE cargo_claims.additional_info ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.cargo_finance_claim_estimating_results ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_audit ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_changes ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_custom_context ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_estimating_results ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_features ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_point_time_intervals ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_points ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_segment_points ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_segment_points_change_log ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_segments ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claim_warnings ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claims ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.claims_c2c ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.courier_manual_dispatch ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.documents ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.items ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.items_exchange ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.items_fiscalization ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.matched_cars ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.matched_items ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.payment_on_delivery ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.points ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.points_ready_for_interact_notifications ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.taxi_order_changes ENABLE TRIGGER ALL;
ALTER TABLE cargo_claims.taxi_performer_info ENABLE TRIGGER ALL;
