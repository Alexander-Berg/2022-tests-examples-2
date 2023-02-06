#include <gtest/gtest.h>

#include "limit_native_delivery_fee.hpp"

namespace helpers {

namespace {

std::shared_ptr<const models::RegionSettingsByRegionId> MakeRegionSettings(
    const int region_id,
    const std::optional<double>& native_max_delivery_fee = std::nullopt,
    const std::optional<double>& taxi_max_delivery_fee = std::nullopt) {
  models::RegionSettingsByRegionId result;
  auto& settings = result[region_id];
  settings.native_max_delivery_fee = native_max_delivery_fee;
  settings.taxi_max_delivery_fee = taxi_max_delivery_fee;
  return std::make_shared<const models::RegionSettingsByRegionId>(result);
}

surge::PlaceSurge GenerateSurge(double fee) {
  surge::PlaceSurge surge;
  surge.nativeinfo = surge::NativeInfo{1, 1, fee};
  return surge;
}

}  // namespace

TEST(LimitNativeDeliveryFee, FeeLessThanLimit) {
  // Проверяем, что если текущая стоимость меньше максимальной
  // ограничение не сработает
  const double kFee = 100.0;
  const int kRegionId = 1;
  const double kNativeLimit = 1000.0;

  const auto settings = MakeRegionSettings(kRegionId, kNativeLimit);
  const auto limit =
      NativeDeliveryLimit(kRegionId, handlers::ZoneInfoZonetype::kPedestrian,
                          settings, {}, nullptr);
  const double result = limit.Limit(kFee);
  ASSERT_EQ(result, kFee);
}

TEST(LimitNativeDeliveryFeeSurge, FeeLessThanLimit) {
  // Проверяем, что если текущая стоимость меньше максимальной
  // ограничение не сработает
  const double kFee = 100.0;
  const int kRegionId = 1;
  const double kNativeLimit = 1000.0;

  const double kSurgeFee = 50.0;
  auto surge = GenerateSurge(kSurgeFee);

  const auto settings = MakeRegionSettings(kRegionId, kNativeLimit);
  const auto limit =
      NativeDeliveryLimit(kRegionId, handlers::ZoneInfoZonetype::kPedestrian,
                          settings, {}, nullptr);
  const auto result = limit.LimitNativeDeliveryFeeSurge(kFee, surge);
  ASSERT_EQ(result, kFee);
  ASSERT_EQ(surge.nativeinfo->deliveryfee, kSurgeFee);
}

TEST(LimitNativeDeliveryFeeSurge, NativeLimit) {
  // Проверяем, что если текущая стоимость
  // больше макисмально и зона пешая, возьмется
  // ограничение из настроек и уменьшит сурж
  const double kFee = 100.0;
  const int kRegionId = 1;
  const double kNativeLimit = 50.0;
  const double kTaxiLimit = 70.0;

  const double kSurgeFee = 60.0;
  auto surge = GenerateSurge(kSurgeFee);

  const auto settings = MakeRegionSettings(kRegionId, kNativeLimit, kTaxiLimit);
  const auto limit =
      NativeDeliveryLimit(kRegionId, handlers::ZoneInfoZonetype::kPedestrian,
                          settings, {}, nullptr);
  const auto result = limit.LimitNativeDeliveryFeeSurge(kFee, surge);
  ASSERT_EQ(result, kNativeLimit);
  ASSERT_EQ(surge.nativeinfo->deliveryfee, 10.0);
  ASSERT_EQ(surge.nativeinfo->surgelevel, 1);
}

TEST(LimitNativeDeliveryFeeSurge, NativeLimitZero) {
  // Проверяем, что если текущая стоимость
  // больше макисмально и зона пешая, возьмется
  // ограничение из настроек и обнулит сурж
  const double kFee = 100.0;
  const int kRegionId = 1;
  const double kNativeLimit = 50.0;
  const double kTaxiLimit = 70.0;

  const double kSurgeFee = 10.0;
  auto surge = GenerateSurge(kSurgeFee);

  const auto settings = MakeRegionSettings(kRegionId, kNativeLimit, kTaxiLimit);
  const auto limit =
      NativeDeliveryLimit(kRegionId, handlers::ZoneInfoZonetype::kPedestrian,
                          settings, {}, nullptr);
  const auto result = limit.LimitNativeDeliveryFeeSurge(kFee, surge);
  ASSERT_EQ(result, kNativeLimit);
  ASSERT_EQ(surge.nativeinfo->deliveryfee, 0.0);
  ASSERT_EQ(surge.nativeinfo->surgelevel, 1);
}

TEST(LimitNativeDeliveryFee, NativeLimit) {
  // Проверяем, что если текущая стоимость
  // больше макисмально и зона пешая, возьмется
  // ограничение из настроек
  const double kFee = 100.0;
  const int kRegionId = 1;
  const double kNativeLimit = 50.0;
  const double kTaxiLimit = 70.0;

  const auto settings = MakeRegionSettings(kRegionId, kNativeLimit, kTaxiLimit);
  const auto limit =
      NativeDeliveryLimit(kRegionId, handlers::ZoneInfoZonetype::kPedestrian,
                          settings, {}, nullptr);
  const double result = limit.Limit(kFee);
  ASSERT_EQ(result, kNativeLimit);
}

TEST(LimitNativeDeliveryFee, TaxiLimit) {
  // Проверяем, что если текущая стоимость
  // больше макисмально и зона такси, возьмется
  // ограничение из настроек для такси
  const double kFee = 100.0;
  const int kRegionId = 1;
  const double kNativeLimit = 50.0;
  const double kTaxiLimit = 70.0;

  const auto settings = MakeRegionSettings(kRegionId, kNativeLimit, kTaxiLimit);
  const auto limit = NativeDeliveryLimit(
      kRegionId, handlers::ZoneInfoZonetype::kTaxi, settings, {}, nullptr);
  const auto result = limit.Limit(kFee);
  ASSERT_EQ(result, kTaxiLimit);
}

TEST(LimitNativeDeliveryFeeSurge, TaxiLimit) {
  // Проверяем, что если текущая стоимость
  // больше макисмально и зона такси, возьмется
  // ограничение из настроек для такси а сурж не будет меняться
  const double kFee = 100.0;
  const int kRegionId = 1;
  const double kNativeLimit = 50.0;
  const double kTaxiLimit = 70.0;

  const double kSurgeFee = 10.0;
  auto surge = GenerateSurge(kSurgeFee);

  const auto settings = MakeRegionSettings(kRegionId, kNativeLimit, kTaxiLimit);
  const auto limit = NativeDeliveryLimit(
      kRegionId, handlers::ZoneInfoZonetype::kTaxi, settings, {}, nullptr);
  const auto result = limit.LimitNativeDeliveryFeeSurge(kFee, surge);
  ASSERT_EQ(result, kTaxiLimit);

  ASSERT_EQ(surge.nativeinfo->deliveryfee, kSurgeFee);
  ASSERT_EQ(surge.nativeinfo->surgelevel, 1);
}

TEST(LimitNativeDeliveryFee, UnknowRegion) {
  // Проверяем, что для неизвестного региона
  // ограничение не срабатывает

  const double kFee = 100.0;
  const int kRegionId = 1;

  const auto settings =
      std::make_shared<const models::RegionSettingsByRegionId>();
  const auto limit =
      NativeDeliveryLimit(kRegionId, handlers::ZoneInfoZonetype::kPedestrian,
                          settings, {}, nullptr);
  const double result = limit.Limit(kFee);
  ASSERT_EQ(result, kFee);
}

TEST(LimitNativeDeliveryFeeSurge, UnknowRegion) {
  // Проверяем, что для неизвестного региона
  // ограничение не срабатывает

  const double kFee = 100.0;
  const int kRegionId = 1;

  const double kSurgeFee = 10.0;
  auto surge = GenerateSurge(kSurgeFee);

  const auto settings =
      std::make_shared<const models::RegionSettingsByRegionId>();
  const auto limit =
      NativeDeliveryLimit(kRegionId, handlers::ZoneInfoZonetype::kPedestrian,
                          settings, {}, nullptr);
  const auto result = limit.LimitNativeDeliveryFeeSurge(kFee, surge);
  ASSERT_EQ(result, kFee);
  ASSERT_EQ(surge.nativeinfo->deliveryfee, kSurgeFee);
  ASSERT_EQ(surge.nativeinfo->surgelevel, 1);
}

}  // namespace helpers
