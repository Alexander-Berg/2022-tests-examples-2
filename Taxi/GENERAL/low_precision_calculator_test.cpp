#include "low_precision_calculator.hpp"

#include <gtest/gtest.h>
#include <taxi_config/variables/EATS_ETA_CALCULATOR_SETTINGS.hpp>
#include <testing/taxi_config.hpp>

namespace eats_eta::impl {

using CalculatorSettings =
    taxi_config::eats_eta_calculator_settings::EatsEtaCalculatorSettings;

namespace {
using WeightUnit = libraries::eats_shared::WeightUnit;
using Weight = libraries::eats_shared::Weight;

Cart MockCart() {
  return {
      {{1, Money{100}, "", "", 1, {Weight{"500"}, WeightUnit::kG}},
       {2, Money{100}, "", "", 5, {Weight{"500"}, WeightUnit::kG}},
       {3, Money{100}, "", "", 10, {Weight{"100"}, WeightUnit::kG}}}  // items
  };
}

Place MockPlace() {
  return {
      1,                           // place_id
      2,                           // brand_id
      3,                           // region_id
      DeliveryType::kNative,       // delivery_type
      Business::kRestaurant,       // business
      {},                          // position
      std::chrono::minutes{20},    // avg_preparation
      std::chrono::minutes{5},     // delay
      {std::chrono::minutes{15}},  // fixed
      4,                           // zone_id
      CourierType::kPedestrian,    // courier_type
      {MockCart()},                // cart
      {Precision::kLow},           // options
  };
}

CalculatorSettings MockCalculatorSettings() {
  return dynamic_config::GetDefaultSnapshot()
      [taxi_config::EATS_ETA_CALCULATOR_SETTINGS];
}

}  // namespace

TEST(LowPrecisionCalculator, GetLowPrecisionEstimation) {
  ::geometry::Distance distance{7487.669462709577 * geometry::meters};

  const auto estimation = GetLowPrecisionEstimation(
      {
          std::nullopt,           // distance
          3,                      // tempo
          20,                     // fixtme
      },                          // settings
      distance,                   // distance
      std::chrono::minutes{0},    // delay
      std::chrono::minutes{17},   // preparation
      std::chrono::minutes{-10},  // offset,
      std::chrono::minutes{5},    // weight
      std::chrono::minutes{5},    // quantity
      5                           // ceil
  );

  EXPECT_EQ(estimation.interval.min.count(), 60);
  EXPECT_EQ(estimation.interval.max.count(), 70);
  EXPECT_EQ(estimation.interval.offset.count(), -10);
  EXPECT_EQ(estimation.total.count(), 69);
  EXPECT_EQ(estimation.travel.count(), 42);
  EXPECT_EQ(estimation.preparation.count(), 17);
  EXPECT_EQ(estimation.delay.count(), 0);
  EXPECT_EQ(estimation.weight.count(), 5);
  EXPECT_EQ(estimation.quantity.count(), 5);
  EXPECT_EQ(estimation.distance, distance);
}

TEST(LowPrecisionCalculator, CalculateWeightTime) {
  const auto place = MockPlace();
  const auto settings = MockCalculatorSettings();

  const auto weight = CalculateWeightTime(place, settings);
  EXPECT_EQ(weight.count(), 15);
}

TEST(LowPrecisionCalculator, CalculateQuantityTime) {
  const auto place = MockPlace();
  const auto settings = MockCalculatorSettings();

  const auto quantity = CalculateQuantityTime(place, settings);
  EXPECT_EQ(quantity.count(), 55);
}

}  // namespace eats_eta::impl
