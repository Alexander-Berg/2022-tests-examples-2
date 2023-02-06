#include <gtest/gtest.h>

#include <userver/utils/mock_now.hpp>

#include <cart_delivery_fee/continuous_cart_delivery_price.hpp>

#include "utils.hpp"

namespace cart_delivery_fee::tests {

namespace {

::handlers::ContinuousFees MakeContinuousFees(
    std::vector<::handlers::Threshold>&& points) {
  ::handlers::ContinuousFees result{};
  result.points = std::move(points);
  result.middle_point = 1500;
  result.min_price = 0;
  result.round_up = false;
  return result;
}

ContinuousCartDeliveryPrice MakeContinuousCartDeliveryPrice(
    const ::handlers::ContinuousFees& continuous_fees,
    const std::vector<handlers::WeightThreshold>& weight_thresholds = {},
    const std::optional<::handlers::ContinuousFees>& continuous_surge =
        std::nullopt,
    const models::Money carrot_step = models::Money{200},
    const std::optional<models::Money> region_limit = std::nullopt) {
  return ContinuousCartDeliveryPrice{continuous_fees,  weight_thresholds,
                                     continuous_surge, carrot_step,
                                     RoundCeil,        region_limit};
}

}  // namespace

class ContinuousCartDeliveryPriceTest
    : public ::testing::TestWithParam<CartFeePair> {};

TEST_P(ContinuousCartDeliveryPriceTest, ContiniusDeliveryFee) {
  // Проверяет расчет цены при разных входных параметрах

  // {delivery_cost, order_price}
  const auto [subtotal, delivery_fee] = GetParam();
  const auto continious_fees = MakeContinuousFees({
      {300, 100},
      {200, 500},
      {100, 1000},
      {0, 1500},
  });
  const auto price = MakeContinuousCartDeliveryPrice(continious_fees);
  const auto result = price.GetDeliveryFeeInfo(subtotal).delivery_fee;
  ASSERT_EQ(result, delivery_fee);
}

INSTANTIATE_TEST_SUITE_P(
    ContinuousCartDeliveryPrice, ContinuousCartDeliveryPriceTest,
    // {order_price, delivery_cost}
    ::testing::Values(CartFeePair{models::Money{0}, models::Money{0}},
                      CartFeePair{models::Money{20}, models::Money{300}},
                      CartFeePair{models::Money{100}, models::Money{300}},
                      CartFeePair{models::Money{300}, models::Money{250}},
                      CartFeePair{models::Money{750}, models::Money{150}},
                      CartFeePair{models::Money{1250}, models::Money{50}}),
    [](const auto& v) { return v.param.GetName(); });

class ContinuousCartDeliveryPriceSurgeTest
    : public ::testing::TestWithParam<CartFeeSurge> {};

TEST_P(ContinuousCartDeliveryPriceSurgeTest, ContiniusDeliveryFeeSurge) {
  // Проверяет расчет цены при разных входных параметрах
  // и сурже

  // {delivery_cost, order_price}
  const auto [subtotal, delivery_fee, surge_part] = GetParam();
  const auto continious_fees = MakeContinuousFees({
      {300, 100},
      {200, 500},
      {100, 1000},
      {0, 1500},
  });

  const auto continious_surge = MakeContinuousFees({
      {100, 1000},
      {0, 1500},
  });
  const auto price =
      MakeContinuousCartDeliveryPrice(continious_fees, {}, continious_surge);
  const auto result = price.GetDeliveryFeeInfo(subtotal);
  ASSERT_EQ(result.delivery_fee, delivery_fee);
  ASSERT_EQ(result.surge_part, surge_part);
}

INSTANTIATE_TEST_SUITE_P(
    ContinuousCartDeliveryPriceSurge, ContinuousCartDeliveryPriceSurgeTest,
    // {order_price, delivery_cost}
    ::testing::Values(
        CartFeeSurge{models::Money{0}, models::Money{0}, models::Money{0}},
        CartFeeSurge{models::Money{20}, models::Money{400}, models::Money{100}},
        CartFeeSurge{models::Money{100}, models::Money{400},
                     models::Money{100}},
        CartFeeSurge{models::Money{300}, models::Money{350},
                     models::Money{100}},
        CartFeeSurge{models::Money{750}, models::Money{250},
                     models::Money{100}},
        CartFeeSurge{models::Money{1250}, models::Money{100},
                     models::Money{50}},
        CartFeeSurge{models::Money{2000}, models::Money{0}, models::Money{0}}),
    [](const auto& v) { return v.param.GetName(); });

TEST(ContinuousCartDeliveryPrice, EmptyThresholds) {
  const auto continious_fees = MakeContinuousFees({});

  const auto price = MakeContinuousCartDeliveryPrice(continious_fees);
  const auto result = price.GetDeliveryFeeInfo(models::Money{100}).delivery_fee;
  ASSERT_EQ(result, models::Money{0});
}

TEST(ContinuousCartDeliveryPrice, MinPrice) {
  // Проверяем, что если мы выходим за прямую,
  // то берется цена из поля min_price
  auto continious_fees = MakeContinuousFees({
      {100, 100},
  });

  continious_fees.min_price = 500;

  const auto price = MakeContinuousCartDeliveryPrice(continious_fees);
  const auto result = price.GetDeliveryFeeInfo(models::Money{200}).delivery_fee;
  ASSERT_EQ(result, models::Money::FromFloatInexact(continious_fees.min_price));
}

TEST(ContinuousCartDeliveryPrice, HighPrecisionMoney) {
  // Проверяем, что если провести прямую через
  // (100, 100) и (1000, 0) она будет
  // проходить через точки через которые проведена
  auto continious_fees = MakeContinuousFees({
      {100, 100},
      {0, 1000},
  });

  const auto price = MakeContinuousCartDeliveryPrice(continious_fees);
  ASSERT_EQ(price.GetDeliveryFeeInfo(models::Money{100}).delivery_fee,
            models::Money{100});
  ASSERT_EQ(price.GetDeliveryFeeInfo(models::Money{1000}).delivery_fee,
            models::Money{0});
}

TEST(ContinuousCartDeliveryPrice, RoundUp) {
  // Проверяем округление до 9-ок
  auto continious_fees = MakeContinuousFees({
      {100, 0},
      {0, 100},
  });
  continious_fees.round_up = true;
  const models::Money kCarrotStep{200};

  ContinuousCartDeliveryPrice price{
      continious_fees, {}, std::nullopt, kCarrotStep, RoundToNine};
  const auto result = price.GetDeliveryFeeInfo(models::Money{20}).delivery_fee;
  ASSERT_EQ(result, models::Money{89});
}

TEST(ContinuousCartDeliveryPrice, Ceil) {
  // Проверяем округление до целых
  auto continious_fees = MakeContinuousFees({
      {50, 0},
      {0, 100},
  });
  continious_fees.round_up = false;

  const auto price = MakeContinuousCartDeliveryPrice(continious_fees);
  const auto result = price.GetDeliveryFeeInfo(models::Money{65}).delivery_fee;
  ASSERT_EQ(result, models::Money{18});  // ceil(17.5)
}

TEST(ContinuousCartDeliveryPrice, GetSumToFreeDelivery) {
  // Проверяем расчет суммы до бесплатной доставки в случае трешхолдов
  ::handlers::ContinuousFees continuous_fees{};

  // non zero min price
  continuous_fees.min_price = 100;
  auto result = MakeContinuousCartDeliveryPrice(continuous_fees)
                    .GetSumToFreeDelivery(models::Money{100});
  ASSERT_FALSE(result.has_value());

  // empty points
  continuous_fees.min_price = 0;
  result = MakeContinuousCartDeliveryPrice(continuous_fees)
               .GetSumToFreeDelivery(models::Money{100});
  ASSERT_FALSE(result.has_value());

  // greater then last point
  continuous_fees.points = {
      {100, 100},
      {0, 500},
  };
  result = MakeContinuousCartDeliveryPrice(continuous_fees)
               .GetSumToFreeDelivery(models::Money{600});
  ASSERT_FALSE(result.has_value());

  // ok
  result = MakeContinuousCartDeliveryPrice(continuous_fees)
               .GetSumToFreeDelivery(models::Money{250});
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value(), models::Money{250});

  // surge
  continuous_fees.points = {
      {100, 100},
      {0, 500},
  };

  ::handlers::ContinuousFees continuous_surge{};
  continuous_surge.points = {
      {100, 1000},
  };
  result =
      MakeContinuousCartDeliveryPrice(continuous_fees, {}, continuous_surge)
          .GetSumToFreeDelivery(models::Money{600});
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value(), models::Money{400});
}

TEST(ContinuousCartDeliveryPrice, GetCarrotNextDeliveryThreshold) {
  // Логику GetCarrotNextDeliveryThreshold

  ::handlers::ContinuousFees continuous_fees{};
  continuous_fees.middle_point = 500;
  continuous_fees.points = {
      {100, 100},
      {0, 1000},
  };
  continuous_fees.min_price = 0;

  ::handlers::ContinuousFees continuous_surge{};
  // Добавляем +100 к каждой цене до корзины в 1000
  continuous_surge.points = {
      {100, 1500},
  };
  continuous_surge.min_price = 0;

  const models::Money kCarrotStep{200};

  ContinuousCartDeliveryPrice price{
      continuous_fees, {}, continuous_surge, kCarrotStep, RoundCeil};

  // на константной части
  auto result = price.GetNextDeliveryThreshold(models::Money{50});
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value().amount_need, models::Money{250});
  ASSERT_EQ(result.value().next_cost, models::Money{178});

  // на наклонной части
  result = price.GetNextDeliveryThreshold(models::Money{200});
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value().amount_need, kCarrotStep);
  ASSERT_EQ(result.value().next_cost, models::Money{167});

  // приблажаемся к бесплатной доставке,
  // nead_amount должен уменьшаться
  result = price.GetNextDeliveryThreshold(models::Money{1400});
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value().amount_need, models::Money{100});  // 1500 - 1400
  ASSERT_EQ(result.value().next_cost, models::Money{0});

  // за прямой
  result = price.GetNextDeliveryThreshold(models::Money{3000});
  ASSERT_FALSE(result.has_value());

  // с региональным лимитом
  ContinuousCartDeliveryPrice limited_price{
      continuous_fees, {},        continuous_surge,
      kCarrotStep,     RoundCeil, models::Money{150}};
  // константа до 550
  result = limited_price.GetNextDeliveryThreshold(models::Money{300});
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result.value().amount_need, models::Money{450});
  ASSERT_EQ(result.value().next_cost, models::Money{128});
}

TEST(ContinuousCartDeliveryPrice, GetDeliveryFeeRange) {
  // Логику GetCarrotNextDeliveryThreshold

  ::handlers::ContinuousFees continuous_fees{};
  continuous_fees.middle_point = 500;
  continuous_fees.points = {
      {100, 100},
      {0, 1000},
  };
  continuous_fees.min_price = 0;

  ::handlers::ContinuousFees continuous_surge{};
  // Добавляем +100 к каждой цене до корзины в 1000
  continuous_surge.points = {
      {100, 1500},
  };
  continuous_surge.min_price = 0;
  const models::Money kCarrotStep{200};

  ContinuousCartDeliveryPrice price{
      continuous_fees, {}, continuous_surge, kCarrotStep, RoundCeil};

  const auto result = price.GetDeliveryFeeRange();
  ASSERT_EQ(result.min, models::Money{0});
  ASSERT_EQ(result.max, models::Money{200});
}

TEST(ContinuousCartDeliveryPrice, EmptyThresholdsWithWeightFees) {
  const auto continious_fees = MakeContinuousFees({});
  const std::vector<::handlers::WeightThreshold> weight_thresholds{
      {0, 0},
      {10, 5000},
      {20, 10000},
  };

  const auto price =
      MakeContinuousCartDeliveryPrice(continious_fees, weight_thresholds);
  const auto result = price.GetWeightFee(7000);
  ASSERT_EQ(result, models::Money{10});
}

}  // namespace cart_delivery_fee::tests
