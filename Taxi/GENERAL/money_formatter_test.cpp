#include <gtest/gtest.h>

#include "money_formatter.hpp"

struct MoneyFormatTest
    : ::testing::TestWithParam<std::tuple<std::string, std::string>> {};

INSTANTIATE_TEST_SUITE_P(
    results, MoneyFormatTest,
    ::testing::Values(std::make_tuple("100", "100"),
                      std::make_tuple("100.00000", "100"),
                      std::make_tuple("100.1234", "100.12"),
                      std::make_tuple("100.10", "100.10")));

TEST_P(MoneyFormatTest, Success) {
  const auto [original_money, formatted_money] = GetParam();
  ASSERT_EQ(eats_restapp_promo::utils::MoneyFormat(original_money),
            formatted_money);
}

TEST(MoneyFormat, Fail) {
  ASSERT_THROW(eats_restapp_promo::utils::MoneyFormat("abc"),
               decimal64::ParseError);
}
