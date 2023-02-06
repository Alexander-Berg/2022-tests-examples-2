#include <gtest/gtest.h>

#include "continuous_price.hpp"

namespace helpers {

namespace {

const std::string kCurrencySign = "$";

ThresholdInfoSettings MakeSettings() {
  ThresholdInfoSettings result{};
  result.message_tmpl = "Цена ниже за каждые 50 {currency_sign} в заказе";
  result.low_threshold_tmpl = "Заказ от 0 {currency_sign}";
  result.high_threshold_tmpl = "Заказ от {last_order_price} {currency_sign}";
  return result;
}

::handlers::ContinuousFees MakeContinuousFees() {
  ::handlers::ContinuousFees result{};
  result.min_price = 25;
  result.points = {
      {20, 1000},
      {500, 100},
  };
  return result;
}

NativeDeliveryLimit MakeNativeDeliveryLimit() {
  return NativeDeliveryLimit(1, handlers::ZoneInfoZonetype::kPedestrian,
                             nullptr, {}, nullptr);
}

}  // namespace

TEST(MakeThresholdsInfo, Generic) {
  const auto settings = MakeSettings();
  const auto continuous_fees = MakeContinuousFees();
  const auto native_delivery_fee_limit = MakeNativeDeliveryLimit();
  const auto result = MakeThresholdsInfo(continuous_fees, kCurrencySign,
                                         settings, native_delivery_fee_limit);

  const auto& info = result.thresholds_info;
  ASSERT_EQ(info.thresholds.size(), 3);

  const auto& first = info.thresholds.at(0);
  ASSERT_EQ(first.name, "Цена ниже за каждые 50 $ в заказе");
  ASSERT_EQ(first.value, " ");

  const auto& second = info.thresholds.at(1);
  ASSERT_EQ(second.name, "Заказ от 0 $");
  ASSERT_EQ(second.value, "500 $");

  const auto& third = info.thresholds.at(2);
  ASSERT_EQ(third.name, "Заказ от 1000 $");
  ASSERT_EQ(third.value, "25 $");

  ASSERT_EQ(info.thresholds_fees.size(), 2);

  const auto& first_fees = info.thresholds_fees.front();
  ASSERT_EQ(first_fees.order_price, models::Money{100});
  ASSERT_EQ(first_fees.delivery_cost, models::Money{500});

  const auto& last_fees = info.thresholds_fees.back();
  ASSERT_EQ(last_fees.order_price, models::Money{1000});
  ASSERT_EQ(last_fees.delivery_cost, models::Money{25});

  const auto& thresholds = result.thresholds;
  ASSERT_EQ(thresholds.size(), 2);
  const auto& first_threshold = thresholds.front();
  ASSERT_EQ(first_threshold.order_price, 0);
  ASSERT_EQ(first_threshold.delivery_cost, 500);

  const auto& last_threshold = thresholds.back();
  ASSERT_EQ(last_threshold.order_price, 1000);
  ASSERT_EQ(last_threshold.delivery_cost, 25);
}

TEST(MakeThresholdsInfo, WithRegionLimit) {
  // Проверяем что если первая точка нарушает региональный лимит
  // то сдвигается order_price, а не ограничивается delivery_cost

  constexpr const int kLimit = 399;

  const auto settings = MakeSettings();
  const auto continuous_fees = MakeContinuousFees();

  auto region_settings = std::make_shared<models::RegionSettingsByRegionId>();
  (*region_settings)[1].native_max_delivery_fee = kLimit;
  NativeDeliveryLimit native_delivery_fee_limit(
      1, handlers::ZoneInfoZonetype::kPedestrian, region_settings, {}, nullptr);

  const auto result = MakeThresholdsInfo(continuous_fees, kCurrencySign,
                                         settings, native_delivery_fee_limit);

  const auto& info = result.thresholds_info;
  ASSERT_EQ(info.thresholds.size(), 3);

  const auto& second = info.thresholds.at(1);
  ASSERT_EQ(second.name, "Заказ от 0 $");
  ASSERT_EQ(second.value, "399 $");

  ASSERT_EQ(info.thresholds_fees.size(), 2);

  const auto& first_fees = info.thresholds_fees.front();
  // ASSERT_EQ(first_fees.order_price, models::Money{289.38});
  ASSERT_EQ(first_fees.delivery_cost, models::Money{399});

  const auto& last_fees = info.thresholds_fees.back();
  ASSERT_EQ(last_fees.order_price, models::Money{1000});
  ASSERT_EQ(last_fees.delivery_cost, models::Money{25});

  const auto& thresholds = result.thresholds;
  ASSERT_EQ(thresholds.size(), 2);
  const auto& first_threshold = thresholds.front();
  ASSERT_EQ(first_threshold.order_price, 0);
  ASSERT_EQ(first_threshold.delivery_cost, kLimit);

  const auto& last_threshold = thresholds.back();
  ASSERT_EQ(last_threshold.order_price, 1000);
  ASSERT_EQ(last_threshold.delivery_cost, 25);
}

}  // namespace helpers
