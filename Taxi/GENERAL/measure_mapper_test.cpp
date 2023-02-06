#include <fmt/format.h>
#include <gtest/gtest.h>

#include <models/measure_mapper.hpp>
#include <models/product.hpp>

namespace eats_products::models {

namespace {

const std::string kGram = "GRM";
const std::string kKGram = "KGRM";

}  // namespace

struct TestParams {
  std::string unit;
  int value;
  double price;
  std::optional<double> old_price;
  bool should_round;
  std::optional<handlers::ProductWeightData> expected_result;
  std::string test_name;
};

class TestProductWeightData : public testing::TestWithParam<TestParams> {};

std::string PrintToString(const TestParams& params) { return params.test_name; }

const std::vector<TestParams> kBasicTestParams = {
    {"unknown_units", 100, 100.0, std::nullopt, false, std::nullopt,
     "unknown_units"},
    {"GRM", 0, 100.0, std::nullopt, false, std::nullopt, "value_is_zero"},
    {kGram, 100, 100, std::nullopt, false,
     handlers::ProductWeightData{Money("1000"), std::nullopt, 100},
     "gram_no_promo"},
    {kGram, 250, 90.0, 100.0, false,
     handlers::ProductWeightData{Money("400"), Money("360"), 250},
     "gram_with_promo"},
    {kKGram, 2, 100.0, std::nullopt, false,
     handlers::ProductWeightData{Money("50"), std::nullopt, 2000},
     "kg_no_promo"},
    {kKGram, 3, 90.0, 100.0, false,
     handlers::ProductWeightData{Money("33.33"), Money("30"), 3000},
     "kg_with_promo"},
    {kKGram, 3, 90.0, std::nullopt, true,
     handlers::ProductWeightData{Money("30"), std::nullopt, 3000},
     "kg_no_promo_round"},
    {kKGram, 3, 91.0, 92.0, true,
     handlers::ProductWeightData{Money("31"), Money("31"), 3000},
     "kg_with_promo_round"},
};

TEST_P(TestProductWeightData, BasicTest) {
  const auto params = GetParam();
  const ItemMeasure item_measure{params.value, std::nullopt, params.unit};
  const auto result = ConvertProductWeightData(
      item_measure, params.price, params.old_price, params.should_round);
  EXPECT_EQ(result.has_value(), params.expected_result.has_value());
  if (result) {
    const auto& result_value = result.value();
    const auto& expected_value = params.expected_result.value();
    EXPECT_EQ(result_value.quantim_value_g, expected_value.quantim_value_g);
    EXPECT_EQ(result_value.price_per_kg, expected_value.price_per_kg);
    EXPECT_EQ(result_value.promo_price_per_kg.has_value(),
              expected_value.promo_price_per_kg.has_value());
    if (result_value.promo_price_per_kg) {
      EXPECT_EQ(result_value.promo_price_per_kg.value(),
                expected_value.promo_price_per_kg.value());
    }
  }
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestProductWeightData,
                         testing::ValuesIn(kBasicTestParams),
                         testing::PrintToStringParamName());

}  // namespace eats_products::models
