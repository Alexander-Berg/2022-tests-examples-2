#include <helpers/cold_storage_private.hpp>

#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>

#include <grocery-orders-shared/helpers/auth_context.hpp>

namespace grocery_orders_shared::helpers::cold_storage {

namespace {

constexpr auto kItemAuthContext = R"json(
{
  "auth_context_table": [
    {
      "raw_auth_context": "{\"X-Yandex-UID\" : \"345625440\", \"X-YaTaxi-Session\" : \"taxi:8b89bf1d0c7f4553b07bf0b0e7bc3314\", \"X-YaTaxi-User\" : \"personal_phone_id=c08f292160f948fdb2605528210ac156, eats_user_id=81681960\", \"X-YaTaxi-UserId\" : \"8b89bf1d0c7f4553b07bf0b0e7bc3314\", \"X-YaTaxi-PhoneId\" : \"5976e0bfeeaa6309ea23fc96\", \"X-Request-Language\" : \"ru\", \"X-Remote-IP\" : \"2a02:6b8:c14:228b:0:4bb1:e6c0:0\", \"X-Request-Application\" : \"app_brand=yataxi,app_name=web,app_ver1=2\", \"X-YaTaxi-Bound-Sessions\" : [], \"X-AppMetrica-DeviceId\" : [null]}",
      "order_id": "4e46f48ab8f942c1b2592e8783863527-grocery"
    }
  ],
  "order_id": "4e46f48ab8f942c1b2592e8783863527-grocery",
  "item_id": "4e46f48ab8f942c1b2592e8783863527-grocery"
}
)json";

const auto kSavedAuthContext = formats::json::FromString(
    R"({"headers":{"X-Yandex-UID":"345625440","X-YaTaxi-Session":"taxi:8b89bf1d0c7f4553b07bf0b0e7bc3314","X-YaTaxi-User":"personal_phone_id=c08f292160f948fdb2605528210ac156, eats_user_id=81681960","X-YaTaxi-UserId":"8b89bf1d0c7f4553b07bf0b0e7bc3314","X-YaTaxi-PhoneId":"5976e0bfeeaa6309ea23fc96","X-Request-Language":"ru","X-Remote-IP":"2a02:6b8:c14:228b:0:4bb1:e6c0:0","X-Request-Application":"app_brand=yataxi,app_name=web,app_ver1=2"}})");

constexpr auto kItemAdditional = R"json(
{
  "order_id": "9abbdb6d2e2448e98b1b38468cbdfefa-grocery",
  "item_id": "9abbdb6d2e2448e98b1b38468cbdfefa-grocery",
  "additional_table": [
    {
      "app_name": "eda_webview_android",
      "appmetrica_device_id": "818eff0de6cf48b1d7ed2fbf7ad61511",
      "created": "2022-03-18T20:43:53.616104",
      "is_dispatch_request_started": null,
      "order_id": "9abbdb6d2e2448e98b1b38468cbdfefa-grocery",
      "order_settings": "{}",
      "timeslot_end": null,
      "timeslot_request_kind": null,
      "timeslot_start": null,
      "updated": "2022-03-18T20:43:53.616104"
    }
  ]
}
)json";

constexpr auto kItemFeedback = R"json(
{
  "order_id": "eeb5a94576714b479f23fbe6f0c3ba1a-grocery",
  "item_id": "eeb5a94576714b479f23fbe6f0c3ba1a-grocery",
  "feedback_table": [
    {
      "comment": null,
      "feedback_options": [],
      "order_id": "eeb5a94576714b479f23fbe6f0c3ba1a-grocery"
    }
  ]
}
)json";

}  // namespace

TEST(ColdStorage, AuthContext) {
  cold_storage::Field field{
      "auth_context_table",
      cold_storage::FieldType::kArrayOfObjects,
      false /* is_required */,
  };

  Converter::Fields fields;
  fields.emplace(field.name, std::cref(field));

  auto value = formats::json::FromString(kItemAuthContext);

  Converter converter{value, fields};
  auto saved_auth_context = GetSavedAuthContext(converter);
  EXPECT_TRUE(saved_auth_context);
  EXPECT_EQ(helpers::SerializeAuthContext(*saved_auth_context),
            kSavedAuthContext);
}

TEST(ColdStorage, UpdateFeedbackTable) {
  cold_storage::Field field{
      "feedback_table",
      cold_storage::FieldType::kArrayOfObjects,
      false,
  };

  Converter::Fields fields;
  fields.emplace(field.name, std::cref(field));

  auto value = formats::json::parser::ParseToType<
      formats::json::Value, formats::json::parser::JsonValueParser>(
      kItemFeedback);

  Converter converter{value, fields};
  models::Order order;
  UpdateFeedbackTable(converter, order);
  EXPECT_TRUE(order.feedback_options);
  EXPECT_TRUE(order.feedback_options->empty());
  EXPECT_FALSE(order.feedback_comment);
}

TEST(ColdStorage, UpdateAdditionalTable) {
  cold_storage::Field field{
      "additional_table",
      cold_storage::FieldType::kArrayOfObjects,
      false /* is_required */,
  };

  Converter::Fields fields;
  fields.emplace(field.name, std::cref(field));

  auto value = formats::json::parser::ParseToType<
      formats::json::Value, formats::json::parser::JsonValueParser>(
      kItemAdditional);

  Converter converter{value, fields};
  models::Order order;
  UpdateAdditionalTable(converter, order);
  EXPECT_EQ(order.appmetrica_device_id, "818eff0de6cf48b1d7ed2fbf7ad61511");
  EXPECT_TRUE(order.order_settings ==
              grocery_orders_shared::models::OrderSettings{});
  EXPECT_EQ(order.app_name, "eda_webview_android");
  EXPECT_FALSE(order.timeslot_start);
  EXPECT_FALSE(order.timeslot_end);
  EXPECT_FALSE(order.timeslot_request_kind);
  EXPECT_FALSE(order.is_dispatch_request_started);
}

}  // namespace grocery_orders_shared::helpers::cold_storage
