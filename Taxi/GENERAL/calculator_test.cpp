#include "calculator.hpp"

#include <gtest/gtest.h>

using AmountType = helpers::AmountType;
TEST(CALCULATOR, DefaultOrder) {
  auto calculator = helpers::calculator::Calculator();
  AmountType result = calculator.Calculate(AmountType(562), AmountType(10),
                                           AmountType(50), AmountType(5));
  AmountType exp_result("134.3");
  ASSERT_EQ(result, exp_result);
}

TEST(CALCULATOR, RoundCheck) {
  auto calculator = helpers::calculator::Calculator();
  AmountType result = calculator.Calculate(AmountType("562.5"), AmountType(10),
                                           AmountType(50), AmountType(5));
  AmountType exp_result("134.38");  // real answer 134.375
  ASSERT_EQ(result, exp_result);
}

TEST(getPlaceCashlessCommissionCalculator, DefaultOrder) {
  auto calculator = helpers::calculator::GetCorrespondingCalculator(
      helpers::calculator::PaymentType::Cashless,
      helpers::calculator::Counteragent::Place,
      helpers::calculator::DeliveryType::None);
  AmountType result = calculator->Calculate(AmountType(562), AmountType(10),
                                            AmountType(50), AmountType(5));
  AmountType exp_result("134.3");

  ASSERT_EQ(result, exp_result);

  ASSERT_EQ(calculator->OutputType(), "PlaceCashlessCommissionCalculator");
}

TEST(getPlaceCashCommissionCalculator, DefaultOrder) {
  auto calculator = helpers::calculator::GetCorrespondingCalculator(
      helpers::calculator::PaymentType::Cash,
      helpers::calculator::Counteragent::Place,
      helpers::calculator::DeliveryType::None);
  AmountType result =
      calculator->Calculate(AmountType(562), AmountType(10), AmountType(50));
  AmountType exp_result("106.2");

  ASSERT_EQ(result, exp_result);

  ASSERT_EQ(calculator->OutputType(), "PlaceCashCommissionCalculator");
}

TEST(getDeliveryCashlessNativeCommissionCalculator, DefaultOrder) {
  auto calculator = helpers::calculator::GetCorrespondingCalculator(
      helpers::calculator::PaymentType::Cashless,
      helpers::calculator::Counteragent::Delivery,
      helpers::calculator::DeliveryType::Native);
  AmountType result = calculator->Calculate(AmountType(562), AmountType(10),
                                            AmountType(50), AmountType(5));
  AmountType exp_result("134.3");

  ASSERT_EQ(result, exp_result);

  ASSERT_EQ(calculator->OutputType(),
            "DeliveryCashlessNativeCommissionCalculator");
}

TEST(getDeliveryCashNativeCommissionCalculator, DefaultOrder) {
  auto calculator = helpers::calculator::GetCorrespondingCalculator(
      helpers::calculator::PaymentType::Cash,
      helpers::calculator::Counteragent::Delivery,
      helpers::calculator::DeliveryType::Native);
  AmountType result =
      calculator->Calculate(AmountType(562), AmountType(10), AmountType(50));
  AmountType exp_result("106.2");
  ASSERT_EQ(result, exp_result);

  ASSERT_EQ(calculator->OutputType(), "DeliveryCashNativeCommissionCalculator");
}

TEST(getMarket, DefaultOrder) {
  auto calculator = helpers::calculator::GetCorrespondingCalculator(
      helpers::calculator::PaymentType::Cash,
      helpers::calculator::Counteragent::Delivery,
      helpers::calculator::DeliveryType::Marketplace);
  AmountType result = calculator->Calculate(AmountType(562), AmountType(10),
                                            AmountType(50), AmountType(5));
  AmountType exp_result(0);
  ASSERT_EQ(result, exp_result);

  ASSERT_EQ(calculator->OutputType(),
            "DeliveryMarketplaceCommissionCalculator");
}
