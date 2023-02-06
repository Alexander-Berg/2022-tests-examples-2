#include <gtest/gtest.h>

#include <cart_delivery_fee/round.hpp>

namespace cart_delivery_fee::tests {

struct TestCase {
  models::Money input{};
  models::Money expected{};

  inline std::string GetName() const {
    auto str = fmt::format("{}_{}", input, expected);
    std::replace(str.begin(), str.end(), '.', '_');
    return str;
  }
};

class RoundToNineTest : public ::testing::TestWithParam<TestCase> {};

TEST_P(RoundToNineTest, RoundToNine) {
  const auto [input, expected] = GetParam();
  const auto result = RoundToNine(input);
  ASSERT_EQ(result, expected) << "Input: " << input;
}

INSTANTIATE_TEST_SUITE_P(
    RoundToNine, RoundToNineTest,
    // {order_price, delivery_cost}
    ::testing::Values(
        TestCase{models::Money{0}, models::Money{0}},
        TestCase{models::Money{7}, models::Money{9}},
        TestCase{models::Money{9}, models::Money{9}},
        TestCase{models::Money{11}, models::Money{19}},
        TestCase{models::Money{15}, models::Money{19}},
        TestCase{models::Money{17}, models::Money{19}},
        TestCase{models::Money{20}, models::Money{29}},
        TestCase{models::Money::FromFloatInexact(15.1), models::Money{19}},
        TestCase{models::Money::FromFloatInexact(15.5), models::Money{19}},
        TestCase{models::Money::FromFloatInexact(15.9), models::Money{19}},
        TestCase{models::Money::FromFloatInexact(18.9), models::Money{19}},
        TestCase{models::Money{19}, models::Money{19}},
        TestCase{models::Money::FromFloatInexact(19.1), models::Money{29}},
        TestCase{models::Money::FromFloatInexact(19.9), models::Money{29}},
        TestCase{models::Money{100}, models::Money{109}},
        TestCase{models::Money{290}, models::Money{299}}),
    [](const auto& v) { return v.param.GetName(); });

}  // namespace cart_delivery_fee::tests
