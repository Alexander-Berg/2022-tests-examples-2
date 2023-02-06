#include <cmath>

#include <clients/models/place_product.hpp>
#include <clients/models/product_cache.hpp>
#include <models/money.hpp>

#include <userver/utest/utest.hpp>

namespace nmn = eats_nomenclature;

namespace {

struct GenerateProductPricesFromTestParam {
  std::optional<double> price_opt;
  std::optional<double> old_price_opt;
  std::optional<double> full_price_opt;
  std::optional<double> old_full_price_opt;
  bool is_catch_weight;
  double quantum;
  bool should_include_pennies_in_price;
};

class GenerateProductPricesFromTestBase
    : public ::testing::TestWithParam<GenerateProductPricesFromTestParam> {
 public:
  void SetUp() override {}
  void TearDown() override {}
};

class PriceFromFullPriceWithQuantumTest
    : public GenerateProductPricesFromTestBase {};

class PriceFromFullPriceTest : public GenerateProductPricesFromTestBase {};

class PriceFromPriceTest : public GenerateProductPricesFromTestBase {};

class ZeroPriceTest : public GenerateProductPricesFromTestBase {};

class RoundPriceFromFullPriceWithQuantumTest
    : public GenerateProductPricesFromTestBase {};

class RoundPriceFromFullPriceTest : public GenerateProductPricesFromTestBase {};

class RoundPriceFromPriceTest : public GenerateProductPricesFromTestBase {};

}  // namespace

namespace {

std::optional<Money> ConvertToMoneyOpt(const std::optional<double>& value) {
  if (!value) {
    return std::nullopt;
  }
  return Money::FromFloatInexact(*value);
}

std::pair<double, std::optional<double>> GenerateProductPricesFrom(
    const GenerateProductPricesFromTestParam& test_param) {
  const auto [price, old_price] =
      nmn::clients::models::GenerateProductPricesFrom(
          ConvertToMoneyOpt(test_param.price_opt),
          ConvertToMoneyOpt(test_param.old_price_opt),
          ConvertToMoneyOpt(test_param.full_price_opt),
          ConvertToMoneyOpt(test_param.old_full_price_opt),
          nmn::clients::models::IsCatchWeight{test_param.is_catch_weight},
          nmn::clients::models::Quantum{test_param.quantum},
          test_param.should_include_pennies_in_price);
  return {price.ToDoubleInexact(),
          old_price ? old_price->ToDoubleInexact() : std::optional<double>{}};
}

}  // namespace

namespace eats_nomenclature::partners::processing::tests {

TEST_P(PriceFromFullPriceWithQuantumTest, Test) {
  const auto param = GetParam();
  const auto [price, old_price] = ::GenerateProductPricesFrom(param);
  ASSERT_EQ(price, *param.full_price_opt * param.quantum);
  ASSERT_EQ(old_price, param.old_full_price_opt
                           ? *param.old_full_price_opt * param.quantum
                           : std::optional<double>{});
}

INSTANTIATE_TEST_SUITE_P(PriceFromFullPriceWithQuantumInst,
                         PriceFromFullPriceWithQuantumTest,
                         // is_catch_weight is true, full_price is not null
                         ::testing::Values(
                             // old_full_price is not null
                             GenerateProductPricesFromTestParam{
                                 10.1, 20.2, 100.34, 283.67, true, 1.5, true},
                             // old_full_price is null
                             GenerateProductPricesFromTestParam{
                                 10.1, 20.2, 100.34, std::nullopt, true, 1.5,
                                 true}));

TEST_P(PriceFromFullPriceTest, Test) {
  const auto param = GetParam();
  const auto [price, old_price] = ::GenerateProductPricesFrom(param);
  ASSERT_EQ(price, *param.full_price_opt);
  ASSERT_EQ(old_price, param.old_full_price_opt);
}

INSTANTIATE_TEST_SUITE_P(PriceFromFullPriceInst, PriceFromFullPriceTest,
                         // is_catch_weight is false, full_price is not null
                         ::testing::Values(
                             // old_full_price is not null
                             GenerateProductPricesFromTestParam{
                                 10.1, 20.2, 100.34, 283.67, false, 1.5, true},
                             // old_full_price is null
                             GenerateProductPricesFromTestParam{
                                 10.1, 20.2, 100.34, std::nullopt, false, 1.5,
                                 true}));

TEST_P(PriceFromPriceTest, Test) {
  const auto param = GetParam();
  const auto [price, old_price] = ::GenerateProductPricesFrom(param);
  ASSERT_EQ(price, *param.price_opt);
  ASSERT_EQ(old_price, param.old_price_opt);
}

INSTANTIATE_TEST_SUITE_P(
    PriceFromPriceInst, PriceFromPriceTest,
    // full_price is null
    ::testing::Values(
        // is_catch_weight is true, old_price is not null
        GenerateProductPricesFromTestParam{10.1, 20.2, std::nullopt, 283.67,
                                           true, 1.5, true},
        // is_catch_weight is false, old_price is not null
        GenerateProductPricesFromTestParam{10.1, 20.2, std::nullopt, 283.67,
                                           false, 1.5, true},
        // is_catch_weight is true, old_price null
        GenerateProductPricesFromTestParam{10.1, std::nullopt, std::nullopt,
                                           283.67, true, 1.5, true},
        // is_catch_weight is false, old_price is null
        GenerateProductPricesFromTestParam{10.1, std::nullopt, std::nullopt,
                                           283.67, false, 1.5, true}));

TEST_P(ZeroPriceTest, Test) {
  const auto param = GetParam();
  const auto [price, old_price] = ::GenerateProductPricesFrom(param);
  ASSERT_EQ(price, 0);
}

INSTANTIATE_TEST_SUITE_P(
    ZeroPriceInst, ZeroPriceTest,
    // full_price is null, price is null
    ::testing::Values(
        // is_catch_weight is false
        GenerateProductPricesFromTestParam{std::nullopt, 20.2, std::nullopt,
                                           283.67, false, 1.5, true},
        // is_catch_weight is true
        GenerateProductPricesFromTestParam{std::nullopt, 20.2, std::nullopt,
                                           283.67, true, 1.5, true}));

TEST_P(RoundPriceFromFullPriceWithQuantumTest, Test) {
  const auto param = GetParam();
  const auto [price, old_price] = ::GenerateProductPricesFrom(param);
  ASSERT_EQ(price, std::round(*param.full_price_opt * param.quantum));
  ASSERT_EQ(old_price, std::round(*param.old_full_price_opt * param.quantum));
}

INSTANTIATE_TEST_SUITE_P(RoundPriceFromFullPriceWithQuantumTestInst,
                         RoundPriceFromFullPriceWithQuantumTest,
                         // should_include_pennies_in_price is false
                         ::testing::Values(GenerateProductPricesFromTestParam{
                             10.1, 20.2, 100.34, 283.67, true, 1.5, false}));

TEST_P(RoundPriceFromFullPriceTest, Test) {
  const auto param = GetParam();
  const auto [price, old_price] = ::GenerateProductPricesFrom(param);
  ASSERT_EQ(price, std::round(*param.full_price_opt));
  ASSERT_EQ(old_price, std::round(*param.old_full_price_opt));
}

INSTANTIATE_TEST_SUITE_P(RoundPriceFromFullPriceTestInst,
                         RoundPriceFromFullPriceTest,
                         // should_include_pennies_in_price is false
                         ::testing::Values(GenerateProductPricesFromTestParam{
                             10.1, 20.2, 100.34, 283.67, false, 1.5, false}));

TEST_P(RoundPriceFromPriceTest, Test) {
  const auto param = GetParam();
  const auto [price, old_price] = ::GenerateProductPricesFrom(param);
  ASSERT_EQ(price, std::round(*param.price_opt));
  ASSERT_EQ(old_price, std::round(*param.old_price_opt));
}

INSTANTIATE_TEST_SUITE_P(RoundPriceFromPriceTestInst, RoundPriceFromPriceTest,
                         // should_include_pennies_in_price is false
                         ::testing::Values(GenerateProductPricesFromTestParam{
                             10.1, 20.2, std::nullopt, 283.67, false, 1.5,
                             false}));

}  // namespace eats_nomenclature::partners::processing::tests
