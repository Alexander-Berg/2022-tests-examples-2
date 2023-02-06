#include <gmock/gmock.h>

#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <defs/all_definitions.hpp>
#include <suggests/eater_to_support/eater_data_requester.hpp>
#include <suggests/eater_to_support/translation_context_builder.hpp>

namespace {
using eats_messenger::localization::ILocalization;
using TranslationContext = std::unordered_map<std::string, std::string>;
using clients::eats_catalog_storage::PlacesItem;
using defs::internal::suggests_tree::ActionType;
using eats_messenger::suggests::eater_to_support::EaterData;
using eats_messenger::suggests::eater_to_support::
    GroceryTranslationContextBuilder;
using eats_messenger::suggests::eater_to_support::TranslationContextBuilder;

formats::json::Value BuildSupportMiscResponse() {
  formats::json::ValueBuilder builder;
  defs::internal::support_misc::Metadata meta;
  meta.eater_name = "eater";
  meta.eater_eta = utils::datetime::GuessStringtime(
      "2020-04-28T13:00:00+03:00", utils::datetime::kDefaultDriverTimezone);
  meta.order_created_at = utils::datetime::GuessStringtime(
      "2020-04-28T12:00:00+03:00", utils::datetime::kDefaultDriverTimezone);
  meta.order_promised_at = utils::datetime::GuessStringtime(
      "2020-04-28T12:50:00+03:00", utils::datetime::kDefaultDriverTimezone);
  builder["metadata"] = meta;
  return builder.ExtractValue();
}

clients::eats_catalog_storage::
    internal_eats_catalog_storage_v1_places_retrieve_by_ids::post::Response
    BuildEatsCatalogStorageResponse() {
  auto eats_catalog_storage_response_json = formats::json::FromString(R"({
    "places": [
      {
          "id": 1337,
          "revision_id": 1,
          "updated_at": "2020-04-28T12:00:00+03:00",
          "name": "kfc",
          "business": "restaurant",
          "region": {
              "geobase_ids": [213, 216],
              "id": 1,
              "name": "region_name",
              "time_zone": "Europe/Moscow"
          }
      }
    ],
    "not_found_place_ids": []
  })");

  auto response =
      Parse(eats_catalog_storage_response_json,
            formats::parse::To<
                clients::eats_catalog_storage::
                    internal_eats_catalog_storage_v1_places_retrieve_by_ids::
                        post::Response>());
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
        "created_at": "2020-04-28T09:00:00+0000"
      }
    ]
  })");
  auto response =
      Parse(eats_ordershistory_response_json,
            formats::parse::To<
                clients::eats_ordershistory::v2_get_orders::post::Response>());
  return response;
}

clients::grocery_eats_gateway::grocery_eats_gateway_v1_latest::post::Response
BuildGroceryEatsGatewayResponse() {
  clients::grocery_eats_gateway::grocery_eats_gateway_v1_latest::post::Response
      response;
  response.body.resize(1);
  response.body[0].timezone = "Europe/Moscow";
  response.body[0].created_at = utils::datetime::GuessStringtime(
      "2020-04-28T12:00:00+03:00", utils::datetime::kDefaultDriverTimezone);
  response.body[0].order_nr = "111111-000000";
  return response;
}
}  // namespace

class MockLocalization : public ILocalization {
 public:
  MOCK_METHOD(std::string, GetTranslation,
              (const std::string& key,
               const TranslationContext& translation_context, const int count),
              (const, override));
  MOCK_METHOD(std::string, GetTranslation, (const std::string& key),
              (const, override));
};

TEST(TranslationContext, EmptyInput) {
  MockLocalization localization;
  TranslationContextBuilder builder{localization};
  EaterData data;
  TranslationContext expected_context{};

  TranslationContext actual_context = builder.Build(data, std::nullopt);
  ASSERT_EQ(actual_context, expected_context);
}

TEST(TranslationContext, SelectedOrderNrWithoutPlaceInfo) {
  MockLocalization localization;
  TranslationContextBuilder builder{localization};
  EaterData data;
  TranslationContext expected_context{{"order_nr", "111111-000000"},
                                      {"pickup_order_nr", "0000"}};

  TranslationContext actual_context = builder.Build(data, "111111-000000");
  ASSERT_EQ(actual_context, expected_context);
}

TEST(TranslationContext, SelectedOrderNrWithPlaceInfo) {
  utils::datetime::MockNowSet(utils::datetime::GuessStringtime(
      "2020-04-28T12:30:00+03:00", utils::datetime::kDefaultDriverTimezone));
  MockLocalization localization;
  TranslationContextBuilder builder{localization};
  EaterData data;
  data.eats_ordershistory_response = BuildEatsOrdershistoryResponse();
  data.eats_catalog_storage_response = BuildEatsCatalogStorageResponse();

  TranslationContext expected_context{{"order_place_type_from", "ресторана"},
                                      {"order_place_name", "kfc"},
                                      {"order_nr", "111111-000000"},
                                      {"pickup_order_nr", "0000"},
                                      {"pickup_order_nr", "0000"},
                                      {"order_date_time", "12:00"},
                                      {"order_date_day", "сегодня"},
                                      {"order_date_day_month", "28 апреля"},
                                      {"order_date_short", "Сегодня в 12.00"}};

  TranslationContext today_translation_context{{"time", "12:00"}};
  EXPECT_CALL(localization, GetTranslation("suggests.default.today_at",
                                           today_translation_context, 1))
      .WillOnce(testing::Return("Сегодня в 12.00"));
  EXPECT_CALL(localization,
              GetTranslation("suggests.default.restaurant_genitive"))
      .WillOnce(testing::Return("ресторана"));
  EXPECT_CALL(localization, GetTranslation("suggests.default.month_april"))
      .WillOnce(testing::Return("апреля"));
  EXPECT_CALL(localization, GetTranslation("suggests.default.today"))
      .WillRepeatedly(testing::Return("сегодня"));

  TranslationContext actual_context = builder.Build(data, "111111-000000");
  ASSERT_EQ(actual_context, expected_context);
}

TEST(TranslationContext, SupportMiscResponse) {
  utils::datetime::MockNowSet(utils::datetime::GuessStringtime(
      "2020-04-28T12:30:00+03:00", utils::datetime::kDefaultDriverTimezone));

  MockLocalization localization;
  TranslationContextBuilder builder{localization};
  EaterData data;
  data.selected_order_nr = "111111-000000";
  data.eats_support_misc_response.emplace();
  data.eats_support_misc_response->extra = BuildSupportMiscResponse();

  TranslationContext expected_context{{"eta_minutes", "через ещё 30 минут"},
                                      {"eta", "30"},
                                      {"order_nr", "111111-000000"},
                                      {"pickup_order_nr", "0000"},
                                      {"eater_name", "eater"}};

  TranslationContext eta_translation_context{{"eta", "30"}};
  EXPECT_CALL(localization, GetTranslation("suggests.default.eta_minutes",
                                           eta_translation_context, 30))
      .WillOnce(testing::Return("через ещё 30 минут"));

  TranslationContext actual_context = builder.Build(data, "111111-000000");
  ASSERT_EQ(actual_context, expected_context);
}

TEST(TranslationContext, GreenFlow) {
  utils::datetime::MockNowSet(utils::datetime::GuessStringtime(
      "2020-04-28T12:30:00+03:00", utils::datetime::kDefaultDriverTimezone));

  MockLocalization localization;
  TranslationContextBuilder builder{localization};

  EaterData data;
  data.selected_order_nr = "111111-000000";
  data.eats_support_misc_response.emplace();
  data.eats_support_misc_response->extra = BuildSupportMiscResponse();
  data.eats_ordershistory_response = BuildEatsOrdershistoryResponse();
  data.eats_catalog_storage_response = BuildEatsCatalogStorageResponse();

  TranslationContext expected_context{{"order_date_short", "Сегодня в 12.00"},
                                      {"order_place_type_from", "ресторана"},
                                      {"order_place_name", "kfc"},
                                      {"order_date_day_month", "28 апреля"},
                                      {"order_nr", "111111-000000"},
                                      {"pickup_order_nr", "0000"},
                                      {"eta_minutes", "через ещё 30 минут"},
                                      {"eta", "30"},
                                      {"eater_name", "eater"},
                                      {"promise_date_time", "12:50"},
                                      {"promise_date_day", "сегодня"},
                                      {"order_date_time", "12:00"},
                                      {"order_date_day", "сегодня"}};
  TranslationContext eta_translation_context{{"eta", "30"}};
  EXPECT_CALL(localization, GetTranslation("suggests.default.eta_minutes",
                                           eta_translation_context, 30))
      .WillOnce(testing::Return("через ещё 30 минут"));

  TranslationContext today_translation_context{{"time", "12:00"}};
  EXPECT_CALL(localization, GetTranslation("suggests.default.today_at",
                                           today_translation_context, 1))
      .WillOnce(testing::Return("Сегодня в 12.00"));
  EXPECT_CALL(localization, GetTranslation("suggests.default.today"))
      .WillRepeatedly(testing::Return("сегодня"));

  EXPECT_CALL(localization,
              GetTranslation("suggests.default.restaurant_genitive"))
      .WillOnce(testing::Return("ресторана"));
  EXPECT_CALL(localization, GetTranslation("suggests.default.month_april"))
      .WillOnce(testing::Return("апреля"));

  TranslationContext actual_context = builder.Build(data, "111111-000000");
  ASSERT_EQ(actual_context, expected_context);
}

TEST(GroceryTranslationContext, GreenFlow) {
  utils::datetime::MockNowSet(utils::datetime::GuessStringtime(
      "2020-04-28T12:30:00+03:00", utils::datetime::kDefaultDriverTimezone));

  MockLocalization localization;
  GroceryTranslationContextBuilder builder{localization};

  EaterData data;
  data.selected_order_nr = "111111-000000";
  data.grocery_eats_gateway_response = BuildGroceryEatsGatewayResponse();

  TranslationContext expected_context{{"order_date_short", "Сегодня в 12.00"},
                                      {"order_date_time", "12:00"},
                                      {"order_date_day", "сегодня"},
                                      {"order_date_day_month", "28 апреля"},
                                      {"order_nr", "111111-000000"}};

  TranslationContext today_translation_context{{"time", "12:00"}};
  EXPECT_CALL(localization, GetTranslation("suggests.default.today_at",
                                           today_translation_context, 1))
      .WillOnce(testing::Return("Сегодня в 12.00"));
  EXPECT_CALL(localization, GetTranslation("suggests.default.today"))
      .WillRepeatedly(testing::Return("сегодня"));

  EXPECT_CALL(localization, GetTranslation("suggests.default.month_april"))
      .WillOnce(testing::Return("апреля"));

  TranslationContext actual_context = builder.Build(data, "111111-000000");
  ASSERT_EQ(actual_context, expected_context);
}
