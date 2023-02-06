#include <gmock/gmock.h>

#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <defs/all_definitions.hpp>
#include <suggests/eater_to_support/eater_data_requester.hpp>
#include <suggests/eater_to_support/predicate_kwarg_builder.hpp>

namespace {
using clients::eats_catalog_storage::PlacesItem;
using defs::internal::suggests_tree::ActionType;
using eats_messenger::suggests::eater_to_support::EaterData;
using eats_messenger::suggests::eater_to_support::PredicateKwargBuilder;
using experiments3::models::KwargsMap;

clients::eats_support_misc::v1_get_support_meta::get::Response
BuildSupportMiscResponse() {
  auto eats_support_misc_response_json = formats::json::FromString(R"({
    "metadata": {
      "eater_id": "some_id",
      "eater_decency": "good",
      "eater_passport_uid": "1234",
      "is_first_order": true,
      "is_blocked_user": false,
      "order_status": "delivered",
      "order_type": "native",
      "delivery_type": "native",
      "is_fast_food": false,
      "app_type": "eats",
      "country_code": "RU",
      "country_label": "Russia",
      "city_label": "Moscow",
      "order_created_at": "2020-04-28T12:00:00+03:00",
      "order_promised_at": "2020-04-28T12:59:00+03:00",
      "order_delivered_at": "2020-04-28T13:00:00+03:00",
      "is_surge": false,
      "is_promocode_used": false,
      "persons_count": 1,
      "payment_method": "card",
      "order_total_amount": 150.15,
      "place_id": "10",
      "place_name": "some_place_name",
      "is_sent_to_restapp": false,
      "is_sent_to_integration": true,
      "integration_type": "native",
      "place_eta": "2020-04-28T12:20:00.100000+03:00",
      "eater_eta": "2020-04-28T12:30:00.000000+03:00",
      "courier_type": "car",
      "readable_order_created_at": "01.01.2021 02:00",
      "readable_order_promised_at": "01.01.2021 02:00",
      "readable_place_eta": "13:20",
      "readable_eater_eta": "13:30",
      "has_receipts": true,
      "receipt_urls": ["ofd_receipt_url", "another_ofd_url"],
      "courier_arrived_to_customer_planned_time": "2020-04-28T00:16:30+03:00",
      "readable_courier_arrived_to_customer_planned_time": "01:16",
      "courier_arrived_to_customer_from": 10,
      "courier_arrived_to_customer_to": 15,
      "local_time": "01:10",
      "local_date": "28.04.2020"
    }
  })");

  auto response = Parse(
      eats_support_misc_response_json,
      formats::parse::To<
          clients::eats_support_misc::v1_get_support_meta::get::Response>());
  return response;
}

clients::eats_ordershistory::v2_get_orders::post::Response
BuildEatsOrdershistoryResponse() {
  auto eats_ordershistory_response_json = formats::json::FromString(R"({
    "orders": [
      {
        "order_id": "111111-000000",
        "place_id": 1337,
        "status": "taken",
        "source": "eda",
        "delivery_location": {"lat": 0, "lon": 0},
        "total_amount": "123",
        "is_asap": false,
        "created_at": "2020-09-04T15:26:43+0000"
      },
      {
        "order_id": "111111-000001",
        "place_id": 1337,
        "status": "finished",
        "source": "eda",
        "delivery_location": {"lat": 0, "lon": 0},
        "total_amount": "123",
        "is_asap": false,
        "created_at": "2020-09-04T15:26:43+0000",
        "delivered_at": "2020-09-04T15:36:43+0000"
      }
    ]
  })");
  auto response =
      Parse(eats_ordershistory_response_json,
            formats::parse::To<
                clients::eats_ordershistory::v2_get_orders::post::Response>());
  return response;
}

clients::eats_eaters::v1_eaters_find_by_passport_uid::post::Response
BuildEatsEatersResponse() {
  auto eats_eaters_response_json = formats::json::FromString(R"({
    "eater": {
      "personal_phone_id": "phone_id",
      "id": "123456",
      "uuid": "eater-uuid-1",
      "created_at": "2021-06-01T00:00:00+00:00",
      "updated_at": "2021-06-01T00:00:00+00:00"
    }
  })");
  auto response = Parse(
      eats_eaters_response_json,
      formats::parse::To<clients::eats_eaters::v1_eaters_find_by_passport_uid::
                             post::Response>());
  return response;
}
}  // namespace

TEST(PredicateKwarg, JustAuthorized) {
  PredicateKwargBuilder builder{};
  EaterData data;
  data.passport_uid = "1234";

  std::string puid = "1234";
  KwargsMap expected_context;
  expected_context.Update("is_authorized", true);
  expected_context.Update("passport_uid", puid);

  KwargsMap actual_context = builder.Build(data);
  ASSERT_EQ(actual_context.GetMap(), expected_context.GetMap());
}

TEST(PredicateKwarg, EatsEatersKwargs) {
  PredicateKwargBuilder builder{};
  EaterData data;
  data.eats_eaters_response = BuildEatsEatersResponse();

  std::string eater_id = "123456";
  std::string personal_phone_id = "phone_id";
  KwargsMap expected_context;
  expected_context.Update("is_authorized", false);
  expected_context.Update("personal_phone_id", personal_phone_id);
  expected_context.Update("eater_id", eater_id);

  KwargsMap actual_context = builder.Build(data);
  ASSERT_EQ(actual_context.GetMap(), expected_context.GetMap());
}

TEST(PredicateKwarg, EatsOrdershistoryKwargs) {
  PredicateKwargBuilder builder{};
  EaterData data;
  data.eats_ordershistory_response = BuildEatsOrdershistoryResponse();

  KwargsMap expected_context;
  expected_context.Update("is_authorized", false);
  expected_context.Update("number_of_orders_for_period", (std::int64_t)2);
  expected_context.Update("number_of_active_orders", (std::int64_t)1);

  KwargsMap actual_context = builder.Build(data);
  ASSERT_EQ(actual_context.GetMap(), expected_context.GetMap());
}

TEST(PredicateKwarg, EatsSupportMiscKwargs) {
  utils::datetime::MockNowSet(utils::datetime::GuessStringtime(
      "2020-04-28T13:01:00+03:00", utils::datetime::kDefaultDriverTimezone));
  PredicateKwargBuilder builder{};
  EaterData data;
  data.eats_support_misc_response = BuildSupportMiscResponse();
  std::string order_type = "native";
  std::string delivery_type = "native";
  std::string order_status = "delivered";
  KwargsMap expected_context;
  expected_context.Update("order_status", order_status);
  expected_context.Update("has_planned_lateness", false);
  expected_context.Update("planned_lateness_minutes", (std::int64_t)-29);
  expected_context.Update("is_eta_available", true);
  expected_context.Update("has_lateness", true);
  expected_context.Update("minutes_to_promise", (std::int64_t)-1);
  expected_context.Update("minutes_from_finished", (std::int64_t)1);
  expected_context.Update("is_authorized", false);
  expected_context.Update("is_fast_food", false);
  expected_context.Update("order_type", order_type);
  expected_context.Update("delivery_type", delivery_type);
  expected_context.Update("persons_count", (std::int64_t)1);
  expected_context.Update("is_order_finished", true);
  expected_context.Update("is_order_active", false);

  KwargsMap actual_context = builder.Build(data);
  ASSERT_EQ(actual_context.GetMap(), expected_context.GetMap());
}
