#include <gtest/gtest.h>

#include "surge_cost.hpp"

namespace surge {

namespace {

std::vector<::handlers::Threshold> MakeThresholds() {
  std::vector<::handlers::Threshold> thresholds{{
                                                    0.0,  // delivery_cost
                                                    0.0,  // order_price
                                                },
                                                {
                                                    10.0,  // delivery_cost
                                                    10.0,  // order_price
                                                },
                                                {
                                                    20.0,  // delivery_cost
                                                    20.0,  // order_price
                                                }};
  return thresholds;
}

}  // namespace

TEST(GetNativeSurgeCost, Generic) {
  // Проверяем, что при нативном сурже минимальный ненулевой
  // трешхолд складывается с надбавкой за сурж
  const auto thresholds = MakeThresholds();
  surge::PlaceSurge place_surge{};
  auto& native_info = place_surge.nativeinfo.emplace();
  native_info.surgelevel = 100;
  native_info.deliveryfee = 5.0;

  const auto result = GetNativeSurgeCost(thresholds, place_surge, false);
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value(), 15.0);  // 10 + 5
}

TEST(GetNativeSurgeCost, NoNativeInfo) {
  // Проверяем, что если нет информации о нативном
  // сурже, вернется nullopt
  const auto thresholds = MakeThresholds();
  surge::PlaceSurge place_surge{};

  const auto result = GetNativeSurgeCost(thresholds, place_surge, false);
  ASSERT_FALSE(result.has_value());
}

TEST(GetNativeSurgeCost, NoSurgeLvl) {
  // Проверяем, что если surgelevel == 0,
  // то вернется nullopt
  const auto thresholds = MakeThresholds();
  surge::PlaceSurge place_surge{};
  auto& native_info = place_surge.nativeinfo.emplace();
  native_info.surgelevel = 0;
  native_info.deliveryfee = 5.0;

  const auto result = GetNativeSurgeCost(thresholds, place_surge, false);
  ASSERT_FALSE(result.has_value());
}

TEST(GetNativeSurgeCost, ThresholdContainsSurge) {
  // Проверяем, что если передан флаг threshold_contains_surge
  // ничего к трешхолду прибавляться не будет
  const auto thresholds = MakeThresholds();
  surge::PlaceSurge place_surge{};
  auto& native_info = place_surge.nativeinfo.emplace();
  native_info.surgelevel = 100;
  native_info.deliveryfee = 5.0;

  const auto result = GetNativeSurgeCost(thresholds, place_surge, true);
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value(), 10.0);
}

}  // namespace surge
