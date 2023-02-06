#pragma once

#include <userver/formats/json/serialize.hpp>

namespace test_constants {

constexpr auto kGroceryCustomContextWithoutType = R"(
{"weight": 10000.0, "created": "2022-07-11T09:09:44.144268+00:00", "depot_id": "476361", "order_id": "a8bd4a31d8104f2c9ea54720f132615d-grocery", "region_id": 213, "brand_name": "Лавка", "dispatch_id": "73646213-e517-45a3-a7e0-7d0164e2af7a", "dispatch_type": "pull-dispatch", "dispatch_wave": 0, "delivery_flags": {"assign_rover": false, "is_forbidden_to_be_in_batch": false}, "personal_phone_id": "d456aa09c5704a0ab7e9aa30b9129d57", "external_feature_prices": {"external_order_created_ts": 1657530584}, "lavka_has_market_parcel": false}
)";

constexpr auto kGroceryCustomContextWithType = R"(
{"cargo_custom_context_type": "grocery", "weight": 10000.0, "created": "2022-07-11T09:09:44.144268+00:00", "depot_id": "476361", "order_id": "a8bd4a31d8104f2c9ea54720f132615d-grocery", "region_id": 213, "brand_name": "Лавка", "dispatch_id": "73646213-e517-45a3-a7e0-7d0164e2af7a", "dispatch_type": "pull-dispatch", "dispatch_wave": 0, "delivery_flags": {"assign_rover": false, "is_forbidden_to_be_in_batch": false}, "personal_phone_id": "d456aa09c5704a0ab7e9aa30b9129d57", "external_feature_prices": {"external_order_created_ts": 1657530584}, "lavka_has_market_parcel": false}
)";

constexpr auto kEatsCustomContextWithoutType = R"(
{"region_id": 1, "place_id": 1873, "brand_id": 151272, "brand_name": "place_native__yuiene110225", "delivery_flags": { "is_forbidden_to_be_second_in_batch": false, "is_forbidden_to_be_in_batch": false, "is_forbidden_to_be_in_taxi_batch": false, "assign_rover": false }, "overwrites_for_courier": [ { "tariff": "eda", "comment": "Ресторан Теремок_test1, номер заказа: 220715-235767, сумма заказа: 1155₽." }, { "tariff": "lavka", "comment": "" } ], "zone_type": "pedestrian", "weight_restrictions": [ { "moving_behavior": "pedestrian", "weight_gr": 15000 }, { "moving_behavior": "bicycle", "weight_gr": 22000 }, { "moving_behavior": "electrobike", "weight_gr": 22000 }, { "moving_behavior": "auto", "weight_gr": 52000 }, { "moving_behavior": "motorcycle", "weight_gr": 22000 } ], "batch_weight_restrictions": [ { "moving_behavior": "pedestrian", "weight_gr": 20000 }, { "moving_behavior": "bicycle", "weight_gr": 20000 }, { "moving_behavior": "electrobike", "weight_gr": 20000 }, { "moving_behavior": "auto", "weight_gr": 50000 }, { "moving_behavior": "motorcycle", "weight_gr": 20000 } ], "order_id": 275366550, "order_confirmed_at": "2022-07-15T17:13:59+03:00", "promise_min_at": "2022-07-15T17:28:59+03:00", "promise_max_at": "2022-07-15T17:38:59+03:00", "cooking_time": 420, "order_cancel_at": "2022-07-15T17:24:00+03:00", "order_flow_type": "native", "delivery_flow_type": "courier", "is_asap": true, "is_fast_food": true, "has_slot": false, "user_device_id": "l58151bm-rkyjmpfuz2r-3sgdu4pyr02-tn705ouad1q", "items_cost": { "value": 115500, "currency": "RUB", "decimal_places": 2 }, "delivery_cost": { "value": 17300, "currency": "RUB", "decimal_places": 2 }, "weight": 1372, "route_to_client": { "pedestrian": { "distance": 159, "time": 114, "is_precise": true }, "transit": { "distance": 159, "time": 148, "is_precise": true }, "auto": { "distance": 154, "time": 28, "is_precise": true } }, "order_price": 115500, "user_tags": [], "route_finish_delta_mul": 1, "approach_duration_nowait_add": 0, "entrances_photo_urls": [ "https://avatars.mds.yandex.net/get-altay/5477999/2a0000017eaa175a5a795343ee1c90e493c8/XXXL", "https://avatars.mds.yandex.net/get-altay/5480011/2a0000017da3cad8a88dabe590161143890f/XXXL", "https://avatars.mds.yandex.net/get-altay/5469293/2a0000017ef25a9fa1171e8f73efae82ba6c/XXXL", "https://avatars.mds.yandex.net/get-altay/5265775/2a0000017ba25f70413c63622e31aebb63bf/XXXL" ], "sender_is_picker": false}
)";

constexpr auto kEatsCustomContextWithType = R"(
{"cargo_custom_context_type": "eats", "region_id": 1, "place_id": 1873, "brand_id": 151272, "brand_name": "place_native__yuiene110225", "delivery_flags": { "is_forbidden_to_be_second_in_batch": false, "is_forbidden_to_be_in_batch": false, "is_forbidden_to_be_in_taxi_batch": false, "assign_rover": false }, "overwrites_for_courier": [ { "tariff": "eda", "comment": "Ресторан Теремок_test1, номер заказа: 220715-235767, сумма заказа: 1155₽." }, { "tariff": "lavka", "comment": "" } ], "zone_type": "pedestrian", "weight_restrictions": [ { "moving_behavior": "pedestrian", "weight_gr": 15000 }, { "moving_behavior": "bicycle", "weight_gr": 22000 }, { "moving_behavior": "electrobike", "weight_gr": 22000 }, { "moving_behavior": "auto", "weight_gr": 52000 }, { "moving_behavior": "motorcycle", "weight_gr": 22000 } ], "batch_weight_restrictions": [ { "moving_behavior": "pedestrian", "weight_gr": 20000 }, { "moving_behavior": "bicycle", "weight_gr": 20000 }, { "moving_behavior": "electrobike", "weight_gr": 20000 }, { "moving_behavior": "auto", "weight_gr": 50000 }, { "moving_behavior": "motorcycle", "weight_gr": 20000 } ], "order_id": 275366550, "order_confirmed_at": "2022-07-15T17:13:59+03:00", "promise_min_at": "2022-07-15T17:28:59+03:00", "promise_max_at": "2022-07-15T17:38:59+03:00", "cooking_time": 420, "order_cancel_at": "2022-07-15T17:24:00+03:00", "order_flow_type": "native", "delivery_flow_type": "courier", "is_asap": true, "is_fast_food": true, "has_slot": false, "user_device_id": "l58151bm-rkyjmpfuz2r-3sgdu4pyr02-tn705ouad1q", "items_cost": { "value": 115500, "currency": "RUB", "decimal_places": 2 }, "delivery_cost": { "value": 17300, "currency": "RUB", "decimal_places": 2 }, "weight": 1372, "route_to_client": { "pedestrian": { "distance": 159, "time": 114, "is_precise": true }, "transit": { "distance": 159, "time": 148, "is_precise": true }, "auto": { "distance": 154, "time": 28, "is_precise": true } }, "order_price": 115500, "user_tags": [], "route_finish_delta_mul": 1, "approach_duration_nowait_add": 0, "entrances_photo_urls": [ "https://avatars.mds.yandex.net/get-altay/5477999/2a0000017eaa175a5a795343ee1c90e493c8/XXXL", "https://avatars.mds.yandex.net/get-altay/5480011/2a0000017da3cad8a88dabe590161143890f/XXXL", "https://avatars.mds.yandex.net/get-altay/5469293/2a0000017ef25a9fa1171e8f73efae82ba6c/XXXL", "https://avatars.mds.yandex.net/get-altay/5265775/2a0000017ba25f70413c63622e31aebb63bf/XXXL" ], "sender_is_picker": false}
)";

static const auto kGroceryCustomContextWithoutTypeJson =
    formats::json::FromString(kGroceryCustomContextWithoutType);

static const auto kGroceryCustomContextWithTypeJson =
    formats::json::FromString(kGroceryCustomContextWithType);

static const auto kEatsCustomContextWithoutTypeJson =
    formats::json::FromString(kEatsCustomContextWithoutType);

static const auto kEatsCustomContextWithTypeJson =
    formats::json::FromString(kEatsCustomContextWithType);

}  // namespace test_constants
