#include <gtest/gtest.h>

#include "money.hpp"

namespace models {

struct TestCasePram {
  models::Money input;
  models::Money expected;
};

class MoneyFloorTest : public ::testing::TestWithParam<TestCasePram> {};

TEST_P(MoneyFloorTest, Floor) {
  const auto [input, expected] = GetParam();
  const auto result = Floor(input);
  ASSERT_EQ(result, expected);
}

INSTANTIATE_TEST_SUITE_P(
    Floor, MoneyFloorTest,
    ::testing::Values(TestCasePram{models::Money{0}, models::Money{0}},
                      TestCasePram{models::Money::FromFloatInexact(-1.4),
                                   models::Money::FromFloatInexact(-2.0)},
                      TestCasePram{models::Money::FromFloatInexact(1.4),
                                   models::Money::FromFloatInexact(1.0)}));

class MoneyCeilTest : public ::testing::TestWithParam<TestCasePram> {};

TEST_P(MoneyCeilTest, Ceil) {
  const auto [input, expected] = GetParam();
  const auto result = Ceil(input);
  ASSERT_EQ(result, expected);
}

INSTANTIATE_TEST_SUITE_P(
    Ceil, MoneyCeilTest,
    ::testing::Values(TestCasePram{models::Money{0}, models::Money{0}},
                      TestCasePram{models::Money::FromFloatInexact(-1.4),
                                   models::Money::FromFloatInexact(-1.0)},
                      TestCasePram{models::Money::FromFloatInexact(1.4),
                                   models::Money::FromFloatInexact(2.0)}));

}  // namespace models
