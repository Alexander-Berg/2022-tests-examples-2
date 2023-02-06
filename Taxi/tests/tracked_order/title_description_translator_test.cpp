#include <gtest/gtest.h>
#include <userver/utils/mock_now.hpp>

#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/utils/datetime.hpp>

#include <taxi_config/variables/EATS_ORDERS_TRACKING_MCDONALDS_PICKUP_DISPOSAL.hpp>
#include <taxi_config/variables/EATS_RETAIL_ALCOHOL_SHOPS.hpp>
#include <test_stubs/translations_test.hpp>
#include <tracked_order/widget_text_translator.hpp>

namespace {

namespace impl = eats_orders_tracking::tracked_order::impl;
namespace tests = eats_orders_tracking::tests;

using defs::internal::pg_order::OrderShippingType;
using eats_orders_tracking::models::OrderEta;
using eats_orders_tracking::utils::TrackedOrderPayload;
using eats_orders_tracking::utils::localization::L10nTranslationsPtr;
using eats_orders_tracking::utils::localization::TranslationContext;

struct RetailAlcoDisposalTimeTestParams {
  int brand_id = 0;
  std::optional<std::chrono::system_clock::time_point> moved_to_delivery_at;
  std::string expected_result;
};

struct RetailAlcoDisposalTimeTest
    : public ::testing::TestWithParam<RetailAlcoDisposalTimeTestParams> {};

const std::vector<RetailAlcoDisposalTimeTestParams>
    kRetailAlcoDisposalTimeTestParams{
        {1,
         ::utils::datetime::Stringtime("2022-01-02T10:20:00", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "10:20, 04.01.22"},
        {1,
         ::utils::datetime::Stringtime("2021-12-30T10:20:00", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "10:20, 01.01.22"},
        {1,
         ::utils::datetime::Stringtime("2022-01-02T21:20:00", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "21:20, 04.01.22"},
        {1,
         ::utils::datetime::Stringtime("2022-01-02T10:20:40", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "10:20, 04.01.22"},
        {1,
         ::utils::datetime::Stringtime("2022-01-02T10:24:59", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "10:20, 04.01.22"},
        {1,
         ::utils::datetime::Stringtime("2022-01-02T10:25:00", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "10:25, 04.01.22"},
        {2,
         ::utils::datetime::Stringtime("2022-01-02T10:20:00", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         ""},
        {1, {}, ""},
        {2, {}, ""}};

constexpr const char* const kAllTankerArgs[] = {
    impl::kTankerArgCourierName,
    impl::kTankerArgPlaceName,
    impl::kTankerArgPlaceAddressComment,
    impl::kTankerArgEtaTime,
    impl::kTankerArgEtaTimeRounded,
    impl::kTankerArgPreOrderDateTime,
    impl::kTankerArgPickupTime,
    impl::kTankerArgOrderNr,
    impl::kTankerArgShortOrderNr,
    impl::kTankerArgEtaMinutes,
    impl::kTankerArgEtaMinutesRoundedDown,
    impl::kTankerArgEtaMinutesRoundedDownPlus5m,
    impl::kTankerArgPromiseTime,
    impl::kTankerArgPromiseTimeMinus15,
    impl::kTankerArgPromiseTimeMinus10,
    impl::kTankerArgPromiseTimeMinus7p5,
    impl::kTankerArgPromiseTimePlus7p5,
    impl::kTankerArgCarModel,
    impl::kTankerArgDeliverySlotFrom,
    impl::kTankerArgDeliverySlotTo,
    impl::kTankerArgMcdonaldsDisposalTtlMinutes,
    impl::kTankerArgMinutesToMcdonaldsDisposal,
    impl::kTankerArgMcdonaldsDisposalTime,
    impl::kTankerArgRetailAlcoDisposalTime};

dynamic_config::KeyValue CreateMcdonaldsDisposalConfig(
    int minutes_to_disposal) {
  return {taxi_config::EATS_ORDERS_TRACKING_MCDONALDS_PICKUP_DISPOSAL,
          {std::chrono::minutes(minutes_to_disposal)}};
}

dynamic_config::KeyValue CreateRetailAlcoholConfig(int brand_id,
                                                   int storage_time) {
  return {taxi_config::EATS_RETAIL_ALCOHOL_SHOPS,
          {{{std::to_string(brand_id),
             {"", "", "", {"", {"", ""}}, storage_time, "", ""}}}}};
}

void CheckAllParametersAreAdded(const TranslationContext& translation_context) {
  ASSERT_EQ(translation_context.size(), std::size(kAllTankerArgs));

  for (const char* tanker_arg_name : kAllTankerArgs) {
    ASSERT_NE(translation_context.find(tanker_arg_name),
              translation_context.end());
  }
}

void CheckBuilderOfTranslationContext(
    const TrackedOrderPayload& payload,
    const TranslationContext& expected_values) {
  // Build translation context.
  L10nTranslationsPtr translations =
      std::make_shared<const tests::Translations>();
  const dynamic_config::StorageMock kConfigStorage{
      CreateMcdonaldsDisposalConfig(15 /* minutes_to_disposal */),
      CreateRetailAlcoholConfig(1 /* brand_id */,
                                48 /* storage_time in hours*/)};
  const auto& config = kConfigStorage.GetSnapshot();
  const auto translation_context = impl::BuildTranslationContext(
      payload, l10n::locales::kDefault, translations, config);

  // All parameters must be added in any case.
  CheckAllParametersAreAdded(translation_context);

  // Check exact values that are expected in the current test.
  for (const auto& [name, value] : expected_values) {
    ASSERT_EQ(value, translation_context.at(name));
  }
}

}  // namespace

// TODO: add tests for TranslateTodayTomorrow().

TEST(TitleDescriptionTranslator, EmptyPayload) {
  const TrackedOrderPayload payload;

  CheckBuilderOfTranslationContext(payload, {});
}

TEST(TitleDescriptionTranslator, ArgumentsWithoutFormatting) {
  // Test values.
  constexpr const char* kCourierName = "TestValueCourierName";
  constexpr const char* kPlaceName = "TestValuePlaceName";
  constexpr const char* kPlaceAddressComment = "TestValuePlaceAddressComment";
  constexpr const char* kOrderNr = "TestValueOrderNr";
  constexpr const char* kCarModel = "TestValueCarModel";

  // Init payload.
  TrackedOrderPayload payload;

  payload.order_courier_assignment.emplace();
  payload.order_courier_assignment->performer_info.name = kCourierName;
  payload.order_courier_assignment->waybill_info.car_model = kCarModel;

  payload.place.payload.name = kPlaceName;
  payload.place.payload.address_comment = kPlaceAddressComment;

  payload.order.order_nr = kOrderNr;

  // Check builder.
  CheckBuilderOfTranslationContext(
      payload, {{impl::kTankerArgCourierName, kCourierName},
                {impl::kTankerArgPlaceName, kPlaceName},
                {impl::kTankerArgPlaceAddressComment, kPlaceAddressComment},
                {impl::kTankerArgOrderNr, kOrderNr},
                {impl::kTankerArgCarModel, kCarModel}});
}

TEST(TitleDescriptionTranslator, ShortOrderNr) {
  TrackedOrderPayload payload;
  payload.order.order_nr = "210211-123456";

  CheckBuilderOfTranslationContext(payload,
                                   {{impl::kTankerArgShortOrderNr, "3456"}});
}

TEST(TitleDescriptionTranslator, GroceryShortOrderNr) {
  TrackedOrderPayload payload;
  payload.order.order_nr = "210211-123456";
  payload.order.payload.short_order_nr = "000000-111-6543";

  CheckBuilderOfTranslationContext(payload,
                                   {{impl::kTankerArgShortOrderNr, "6543"}});
}

TEST(TitleDescriptionTranslator, PromiseTime) {
  TrackedOrderPayload payload;

  constexpr const char* kTimezone = "Europe/Moscow";

  payload.order.payload.promise = ::utils::datetime::Stringtime(
      "2021-02-12 11:17:00", kTimezone, "%Y-%m-%d %H:%M:%S");
  payload.order.payload.region.timezone = kTimezone;

  CheckBuilderOfTranslationContext(payload,
                                   {{impl::kTankerArgPromiseTime, "11:17"}});
}

TEST(TitleDescriptionTranslator, FlowWithPreOrderDate) {
  TrackedOrderPayload payload;
  payload.order.payload.pre_order_date = ::utils::datetime::Now();

  CheckBuilderOfTranslationContext(payload, {});
}

TEST(TitleDescriptionTranslator, FlowWithPickup) {
  TrackedOrderPayload payload;
  payload.order.payload.shipping_type = OrderShippingType::kPickup;

  CheckBuilderOfTranslationContext(payload, {});
}

TEST(TitleDescriptionTranslator, RoundTimeUpToFiveMin) {
  TrackedOrderPayload payload;

  constexpr const char* kTimezone = "Europe/Moscow";

  payload.order.payload.shipping_type = OrderShippingType::kPickup;
  payload.order.payload.promise = ::utils::datetime::Stringtime(
      "2021-02-12 11:17:00", kTimezone, "%Y-%m-%d %H:%M:%S");
  payload.order.payload.region.timezone = kTimezone;

  CheckBuilderOfTranslationContext(payload,
                                   {{impl::kTankerArgPickupTime, "11:20"}});

  payload.order.payload.promise = ::utils::datetime::Stringtime(
      "2021-02-12 11:13:00", kTimezone, "%Y-%m-%d %H:%M:%S");

  CheckBuilderOfTranslationContext(payload,
                                   {{impl::kTankerArgPickupTime, "11:15"}});

  payload.order.payload.promise = ::utils::datetime::Stringtime(
      "2021-02-12 11:10:00", kTimezone, "%Y-%m-%d %H:%M:%S");

  CheckBuilderOfTranslationContext(payload,
                                   {{impl::kTankerArgPickupTime, "11:10"}});

  payload.order.payload.promise = ::utils::datetime::Stringtime(
      "2021-02-12 11:15:00", kTimezone, "%Y-%m-%d %H:%M:%S");

  CheckBuilderOfTranslationContext(payload,
                                   {{impl::kTankerArgPickupTime, "11:15"}});
}

TEST(TitleDescriptionTranslator, DeliverySlot) {
  TrackedOrderPayload payload;

  constexpr const char* kTimezone = "Europe/Moscow";

  payload.order.payload.delivery_slot.emplace();
  payload.order.payload.delivery_slot->from = ::utils::datetime::Stringtime(
      "2021-02-12 11:17:00", kTimezone, "%Y-%m-%d %H:%M:%S");
  payload.order.payload.delivery_slot->to = ::utils::datetime::Stringtime(
      "2021-02-12 12:17:00", kTimezone, "%Y-%m-%d %H:%M:%S");
  payload.order.payload.region.timezone = kTimezone;

  CheckBuilderOfTranslationContext(payload,
                                   {{impl::kTankerArgDeliverySlotFrom, "11:17"},
                                    {impl::kTankerArgDeliverySlotTo, "12:17"}});
}

TEST_P(RetailAlcoDisposalTimeTest, RetailAlcoDisposalTimeTest) {
  TrackedOrderPayload payload;

  constexpr const char* kTimezone = "UTC";

  payload.place.payload.brand_id = GetParam().brand_id;
  payload.order.payload.status_history.moved_to_delivery_at =
      GetParam().moved_to_delivery_at;
  payload.order.payload.region.timezone = kTimezone;

  CheckBuilderOfTranslationContext(
      payload,
      {{impl::kTankerArgRetailAlcoDisposalTime, GetParam().expected_result}});
}

INSTANTIATE_TEST_SUITE_P(TitleDescriptionTranslator, RetailAlcoDisposalTimeTest,
                         testing::ValuesIn(kRetailAlcoDisposalTimeTestParams));

struct RoundedEtaMinutesRangeTestParams {
  std::chrono::system_clock::time_point eta;
  std::string expected_rounded_down_eta_minutes;
  std::string expected_rounded_down_plus_5m_eta_minutes;
};

struct RoundedEtaMinutesRangeTest
    : public ::testing::TestWithParam<RoundedEtaMinutesRangeTestParams> {};

const std::vector<RoundedEtaMinutesRangeTestParams>
    kRoundedEtaMinutesRangeTestParams{
        {::utils::datetime::Stringtime("2022-01-01T12:01:00", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "1", "5"},
        {::utils::datetime::Stringtime("2022-01-01T12:00:59", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "1", "5"},
        {::utils::datetime::Stringtime("2022-01-01T12:01:01", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "1", "5"},
        {::utils::datetime::Stringtime("2022-01-01T12:02:00", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "1", "5"},
        {::utils::datetime::Stringtime("2022-01-01T11:59:00", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "1", "5"},
        {::utils::datetime::Stringtime("2022-01-01T12:04:59", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "1", "5"},
        {::utils::datetime::Stringtime("2022-01-01T12:05:00", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "5", "10"},
        {::utils::datetime::Stringtime("2022-01-01T12:10:00", "UTC",
                                       "%Y-%m-%dT%H:%M:%S"),
         "10", "15"},
    };

TEST_P(RoundedEtaMinutesRangeTest, RoundedEtaMinutesRangeTest) {
  const std::chrono::system_clock::time_point kNow =
      ::utils::datetime::Stringtime("2022-01-01T12:00:00", "UTC",
                                    "%Y-%m-%dT%H:%M:%S");
  constexpr const char* kTimezone = "Europe/Moscow";
  ::utils::datetime::MockNowSet(kNow);

  TrackedOrderPayload payload;
  payload.order_dynamic_data.estimates.courier_arriving_to_client.expected_at =
      GetParam().eta;
  payload.order.payload.region.timezone = kTimezone;

  CheckBuilderOfTranslationContext(
      payload, {{impl::kTankerArgEtaMinutesRoundedDown,
                 GetParam().expected_rounded_down_eta_minutes},
                {impl::kTankerArgEtaMinutesRoundedDownPlus5m,
                 GetParam().expected_rounded_down_plus_5m_eta_minutes}});
}

INSTANTIATE_TEST_SUITE_P(TitleDescriptionTranslator, RoundedEtaMinutesRangeTest,
                         testing::ValuesIn(kRoundedEtaMinutesRangeTestParams));
