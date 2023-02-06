#include <gtest/gtest.h>

#include <userver/utils/mock_now.hpp>

#include <defs/definitions.hpp>

#include <cart_delivery_fee/threshold_cart_delivery_price.hpp>

#include "utils.hpp"

namespace cart_delivery_fee::tests {

ThresholdCartDeliveryPrice MakeThresholdCartDeliveryPrice(
    const std::vector<handlers::Threshold>& thresholds,
    const std::vector<handlers::WeightThreshold>& weight_thresholds = {},
    const surge::PlaceSurge& place_surge = {},
    const std::optional<models::Money>& region_limit = std::nullopt) {
  return ThresholdCartDeliveryPrice{thresholds, weight_thresholds, place_surge,
                                    region_limit};
}

class ThresholdDeliveryFeeTest : public ::testing::TestWithParam<CartFeePair> {
};

TEST_P(ThresholdDeliveryFeeTest, ThresholdDeliveryFee) {
  // Проверяет расчет цены при разных входных параметрах

  // {delivery_cost, order_price}
  const auto [subtotal, delivery_fee] = GetParam();
  const std::vector<::handlers::Threshold> thresholds{
      {300, 0},
      {100, 500},
      {0, 1000},
  };

  const auto price = MakeThresholdCartDeliveryPrice(thresholds);
  const auto result = price.GetDeliveryFeeInfo(subtotal).delivery_fee;
  ASSERT_EQ(result, delivery_fee);
}

INSTANTIATE_TEST_SUITE_P(
    ThresholdDeliveryFee, ThresholdDeliveryFeeTest,
    ::testing::Values(CartFeePair{models::Money{0}, models::Money{0}},
                      CartFeePair{models::Money{1}, models::Money{300}},
                      CartFeePair{models::Money{250}, models::Money{300}},
                      CartFeePair{models::Money{500}, models::Money{100}},
                      CartFeePair{models::Money{501}, models::Money{100}},
                      CartFeePair{models::Money{750}, models::Money{100}},
                      CartFeePair{models::Money{1000}, models::Money{0}},
                      CartFeePair{models::Money{1001}, models::Money{0}}),
    [](const auto& v) { return v.param.GetName(); });

class ThresholdSurgeTest : public ::testing::TestWithParam<CartFeePair> {};

TEST_P(ThresholdSurgeTest, ThresholdSurge) {
  // Проверяем, что при сурже независимо от
  // корзины цена будет фиксированной

  // {delivery_cost, order_price}
  const auto [subtotal, delivery_fee] = GetParam();
  const std::vector<::handlers::Threshold> thresholds{
      {300, 0},
      {100, 500},
      {0, 1000},
  };
  surge::PlaceSurge place_surge{};
  auto& surge = place_surge.nativeinfo.emplace();
  surge.surgelevel = 1;
  surge.deliveryfee = 299;

  const auto price =
      MakeThresholdCartDeliveryPrice(thresholds, {}, place_surge);
  const auto result = price.GetDeliveryFeeInfo(subtotal).delivery_fee;
  ASSERT_EQ(result, delivery_fee);
}

INSTANTIATE_TEST_SUITE_P(
    ThresholdSurge, ThresholdSurgeTest,
    ::testing::Values(CartFeePair{models::Money{0}, models::Money{0}},
                      CartFeePair{models::Money{250}, models::Money{399}},
                      CartFeePair{models::Money{750}, models::Money{399}},
                      CartFeePair{models::Money{1001}, models::Money{399}}),
    [](const auto& v) { return v.param.GetName(); });

TEST(GetThresholdDeliveryFee, EmptyThresholds) {
  const std::vector<::handlers::Threshold> thresholds{};
  const surge::PlaceSurge place_surge{};

  const auto price =
      MakeThresholdCartDeliveryPrice(thresholds, {}, place_surge);
  const auto result = price.GetDeliveryFeeInfo(models::Money{100}).delivery_fee;
  ASSERT_EQ(result, models::Money{0});
}

class OneThreshol : public ::testing::TestWithParam<CartFeePair> {};

TEST_P(OneThreshol, OneThreshold) {
  // Проверяет расчет цены в случае если список трешхолдов содержит 1 элемент

  const auto [subtotal, delivery_fee] = GetParam();
  const std::vector<::handlers::Threshold> thresholds{
      {100, 500},
  };
  const surge::PlaceSurge place_surge{};

  const auto price =
      MakeThresholdCartDeliveryPrice(thresholds, {}, place_surge);
  const auto result = price.GetDeliveryFeeInfo(subtotal).delivery_fee;
  ASSERT_EQ(result, delivery_fee);
}

INSTANTIATE_TEST_SUITE_P(
    OneThreshol, OneThreshol,
    ::testing::Values(CartFeePair{models::Money{250}, models::Money{100}},
                      CartFeePair{models::Money{750}, models::Money{100}}),
    [](const auto& v) { return v.param.GetName(); });

TEST(ThresholdCartDeliveryPrice, GetSumToFreeDelivery) {
  // Проверяем расчет суммы до бесплатной доставки в случае трешхолдов

  // empty thresholds
  std::vector<::handlers::Threshold> thresholds{};
  const surge::PlaceSurge place_surge{};
  auto result = MakeThresholdCartDeliveryPrice(thresholds, {}, place_surge)
                    .GetSumToFreeDelivery(models::Money{100});
  ASSERT_FALSE(result.has_value());

  // last non free
  thresholds = {
      {100, 100},
      {50, 500},
  };
  result = MakeThresholdCartDeliveryPrice(thresholds, {}, place_surge)
               .GetSumToFreeDelivery(models::Money{100});
  ASSERT_FALSE(result.has_value());

  // greater then last point
  thresholds = {
      {100, 100},
      {0, 500},
  };
  result = MakeThresholdCartDeliveryPrice(thresholds, {}, place_surge)
               .GetSumToFreeDelivery(models::Money{600});
  ASSERT_FALSE(result.has_value());

  // ok
  result = MakeThresholdCartDeliveryPrice(thresholds, {}, place_surge)
               .GetSumToFreeDelivery(models::Money{250});
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value(), models::Money{250});
}

TEST(ThresholdCartDeliveryPrice, GetNextDeliveryThreshold) {
  // Проверяем расчет суммы до бесплатной доставки в случае трешхолдов

  // empty thresholds
  std::vector<::handlers::Threshold> thresholds{};
  const surge::PlaceSurge place_surge{};
  auto result = MakeThresholdCartDeliveryPrice(thresholds, {}, place_surge)
                    .GetSumToFreeDelivery(models::Money{100});
  ASSERT_FALSE(result.has_value());

  // last non free
  thresholds = {
      {100, 100},
      {50, 500},
  };
  result = MakeThresholdCartDeliveryPrice(thresholds, {}, place_surge)
               .GetSumToFreeDelivery(models::Money{100});
  ASSERT_FALSE(result.has_value());

  // greater then last point
  thresholds = {
      {100, 100},
      {0, 500},
  };
  result = MakeThresholdCartDeliveryPrice(thresholds, {}, place_surge)
               .GetSumToFreeDelivery(models::Money{600});
  ASSERT_FALSE(result.has_value());

  // ok
  result = MakeThresholdCartDeliveryPrice(thresholds, {}, place_surge)
               .GetSumToFreeDelivery(models::Money{250});
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value(), models::Money{250});
}

TEST(ThresholdCartDeliveryPrice, GetNextDeliveryThresholdEmpty) {
  const std::vector<::handlers::Threshold> thresholds{};

  const auto result = MakeThresholdCartDeliveryPrice(thresholds, {}, {})
                          .GetNextDeliveryThreshold(models::Money{100});
  ASSERT_FALSE(result.has_value());
}

TEST(ThresholdCartDeliveryPrice, GetNextDeliveryThresholdNextThreshold) {
  const std::vector<::handlers::Threshold> thresholds{
      {100, 100},
      {50, 500},
      {0, 1000},
  };

  const auto result = MakeThresholdCartDeliveryPrice(thresholds, {}, {})
                          .GetNextDeliveryThreshold(models::Money{200});
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value().amount_need, models::Money{300});
  ASSERT_EQ(result.value().next_cost, models::Money{50});
}

TEST(ThresholdCartDeliveryPrice, GetNextDeliveryThresholdNextFree) {
  const std::vector<::handlers::Threshold> thresholds{
      {100, 100},
      {50, 500},
      {0, 1000},
  };

  const auto result = MakeThresholdCartDeliveryPrice(thresholds, {}, {})
                          .GetNextDeliveryThreshold(models::Money{900});
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value().amount_need, models::Money{100});
  ASSERT_EQ(result.value().next_cost, models::kZeroMoney);
}

TEST(ThresholdCartDeliveryPrice, NextDeliveryThresholdNextFreeAlreadyFree) {
  const std::vector<::handlers::Threshold> thresholds{
      {100, 100},
      {50, 500},
      {0, 1000},
  };

  const auto result = MakeThresholdCartDeliveryPrice(thresholds, {}, {})
                          .GetNextDeliveryThreshold(models::Money{1500});
  ASSERT_FALSE(result.has_value());
}

TEST(ThresholdDeliveryFee, GetDeliveryFeeRange) {
  // Проверяет поиск минимума и максимума

  const std::vector<::handlers::Threshold> thresholds{
      {300, 0},
      {100, 500},
      {0, 1000},
  };
  const surge::PlaceSurge place_surge{};

  auto price =
      MakeThresholdCartDeliveryPrice(thresholds, {}, place_surge, std::nullopt);
  const auto result = price.GetDeliveryFeeRange();
  ASSERT_EQ(result.min, models::Money{0});
  ASSERT_EQ(result.max, models::Money{300});
}

TEST_P(OneThreshol, DeliveryFeeWithWeightFees) {
  const std::vector<::handlers::Threshold> thresholds{
      {100, 500},
      {50, 1000},
  };
  const std::vector<::handlers::WeightThreshold> weight_thresholds{
      {0, 0},
      {40, 8000},
      {80, 15000},
  };

  auto price = MakeThresholdCartDeliveryPrice(thresholds, weight_thresholds);
  const auto result_delivery_info =
      price.GetDeliveryFeeInfo(models::Money{600});
  const auto result_weight_fee = price.GetWeightFee(9000);
  ASSERT_EQ(result_delivery_info.delivery_fee, models::Money{100});
  ASSERT_EQ(result_weight_fee, models::Money{40});
}

}  // namespace cart_delivery_fee::tests
