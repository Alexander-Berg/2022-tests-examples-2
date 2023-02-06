#include <gtest/gtest.h>

#include <cart_delivery_fee/continuous_algo.hpp>

namespace cart_delivery_fee::tests {

namespace {

std::string ToString(const std::vector<Threshold>& points) {
  std::string result;
  bool is_first = true;
  for (const auto& point : points) {
    if (!is_first) {
      result.push_back(',');
    }
    result.append(
        fmt::format("({},{})", point.delivery_cost, point.order_price));
  }
  return result;
}

}  // namespace

TEST(FindTwoLinesMinMax, Empty) {
  ::handlers::ContinuousFees lhs{};
  ::handlers::ContinuousFees rhs{};
  const auto [min, max] =
      FindTwoLinesMinMax(cart_delivery_fee::ContinuousFeeCalculator{lhs},
                         cart_delivery_fee::ContinuousFeeCalculator{rhs});
  ASSERT_EQ(min.delivery_cost, models::Money{0});
  ASSERT_EQ(min.order_price, models::Money{0});
  ASSERT_EQ(max.delivery_cost, models::Money{0});
  ASSERT_EQ(max.order_price, models::Money{0});
}

TEST(FindTwoLinesMinMax, OnlyLhs) {
  ::handlers::ContinuousFees lhs{};
  lhs.points = {
      {100, 100},
      {0, 1000},
  };
  ::handlers::ContinuousFees rhs{};
  const auto [min, max] =
      FindTwoLinesMinMax(cart_delivery_fee::ContinuousFeeCalculator{lhs},
                         cart_delivery_fee::ContinuousFeeCalculator{rhs});
  ASSERT_EQ(min.delivery_cost, models::Money{0});
  ASSERT_EQ(min.order_price, models::Money{1000});
  ASSERT_EQ(max.delivery_cost, models::Money{100});
  ASSERT_EQ(max.order_price, models::Money{100});
}

TEST(FindTwoLinesMinMax, OnlyRhs) {
  ::handlers::ContinuousFees lhs{};
  ::handlers::ContinuousFees rhs{};
  rhs.points = {
      {100, 100},
      {0, 1000},
  };
  const auto [min, max] =
      FindTwoLinesMinMax(cart_delivery_fee::ContinuousFeeCalculator{lhs},
                         cart_delivery_fee::ContinuousFeeCalculator{rhs});
  ASSERT_EQ(min.delivery_cost, models::Money{0});
  ASSERT_EQ(min.order_price, models::Money{1000});
  ASSERT_EQ(max.delivery_cost, models::Money{100});
  ASSERT_EQ(max.order_price, models::Money{100});
}

TEST(FindTwoLinesMinMax, Generic) {
  ::handlers::ContinuousFees lhs{};
  lhs.points = {
      {100, 100},
      {0, 1000},
  };
  ::handlers::ContinuousFees rhs{};
  rhs.points = {
      {50, 1000},
  };
  const auto [min, max] =
      FindTwoLinesMinMax(cart_delivery_fee::ContinuousFeeCalculator{lhs},
                         cart_delivery_fee::ContinuousFeeCalculator{rhs});
  ASSERT_EQ(min.delivery_cost, models::Money{0});
  ASSERT_EQ(min.order_price, models::Money{1000});
  ASSERT_EQ(max.delivery_cost, models::Money{150});
  ASSERT_EQ(max.order_price, models::Money{100});
}

TEST(FindTwoLinesMinMax, DifferentPoints) {
  ::handlers::ContinuousFees lhs{};
  lhs.points = {
      {100, 100},
      {0, 1000},
  };
  ::handlers::ContinuousFees rhs{};
  rhs.points = {
      {50, 500},
      {25, 2000},
  };
  rhs.min_price = 25;
  const auto [min, max] =
      FindTwoLinesMinMax(cart_delivery_fee::ContinuousFeeCalculator{lhs},
                         cart_delivery_fee::ContinuousFeeCalculator{rhs});
  ASSERT_EQ(min.delivery_cost, models::Money{25});
  ASSERT_EQ(min.order_price, models::Money{2000});
  ASSERT_EQ(max.delivery_cost, models::Money{150});
  ASSERT_EQ(max.order_price, models::Money{100});
}

TEST(FindTwoLinesMinMax, BreakingPoint) {
  ::handlers::ContinuousFees lhs{};
  lhs.points = {
      {100, 100},
      {10, 1000},
  };
  ::handlers::ContinuousFees rhs{};
  rhs.points = {
      {50, 1000},
  };
  rhs.min_price = 20;
  const auto [min, max] =
      FindTwoLinesMinMax(cart_delivery_fee::ContinuousFeeCalculator{lhs},
                         cart_delivery_fee::ContinuousFeeCalculator{rhs});
  ASSERT_EQ(min.delivery_cost, models::Money{20});
  ASSERT_EQ(min.order_price, models::Money{1000});
  ASSERT_EQ(max.delivery_cost, models::Money{150});
  ASSERT_EQ(max.order_price, models::Money{100});
}

TEST(FindTwoLinesMinMax, MinPriceSum) {
  ::handlers::ContinuousFees lhs{};
  lhs.points = {
      {100, 100},
      {30, 1000},
  };
  lhs.min_price = 20;
  ::handlers::ContinuousFees rhs{};
  rhs.points = {
      {50, 500},
  };
  rhs.min_price = 20;
  const auto [min, max] =
      FindTwoLinesMinMax(cart_delivery_fee::ContinuousFeeCalculator{lhs},
                         cart_delivery_fee::ContinuousFeeCalculator{rhs});
  ASSERT_EQ(min.delivery_cost, models::Money{40});
  ASSERT_EQ(min.order_price, models::Money{1000});
  ASSERT_EQ(max.delivery_cost, models::Money{150});
  ASSERT_EQ(max.order_price, models::Money{100});
}

TEST(FindTwoLinesMinMax, MinInLastPoint) {
  ::handlers::ContinuousFees lhs{};
  lhs.points = {
      {100, 100},
      {10, 1000},
  };
  lhs.min_price = 20;
  ::handlers::ContinuousFees rhs{};
  rhs.points = {
      {50, 500},
  };
  rhs.min_price = 20;
  const auto [min, max] =
      FindTwoLinesMinMax(cart_delivery_fee::ContinuousFeeCalculator{lhs},
                         cart_delivery_fee::ContinuousFeeCalculator{rhs});
  ASSERT_EQ(min.delivery_cost, models::Money{30});
  ASSERT_EQ(min.order_price, models::Money{1000});
  ASSERT_EQ(max.delivery_cost, models::Money{150});
  ASSERT_EQ(max.order_price, models::Money{100});
}

TEST(AddTwoLines, Empty) {
  ContinuousFeeCalculator lhs{::handlers::ContinuousFees{}};
  ContinuousFeeCalculator rhs{::handlers::ContinuousFees{}};
  auto result = AddTwoLines(lhs, rhs);
  ASSERT_TRUE(result.Points().empty());
  ASSERT_EQ(result.MinPrice(), models::kZeroMoney);
}

TEST(AddTwoLines, LhsEmpty) {
  ::handlers::ContinuousFees lhs_fees{};
  ::handlers::ContinuousFees rhs_fees{};
  rhs_fees.points = {
      {100, 100},
  };
  ContinuousFeeCalculator lhs{lhs_fees};
  ContinuousFeeCalculator rhs{rhs_fees};
  auto result = AddTwoLines(lhs, rhs);
  ASSERT_EQ(result.Points(), rhs.Points()) << ToString(result.Points());
  ASSERT_EQ(result.MinPrice(), models::kZeroMoney);
}

TEST(AddTwoLines, Generic) {
  // Общий случай
  ::handlers::ContinuousFees lhs_fees{};
  lhs_fees.points = {
      {100, 100},
      {10, 1000},
  };
  lhs_fees.min_price = 10;
  ::handlers::ContinuousFees rhs_fees{};
  rhs_fees.points = {
      {100, 1500},
  };
  rhs_fees.min_price = 10;
  ContinuousFeeCalculator lhs{lhs_fees};
  ContinuousFeeCalculator rhs{rhs_fees};
  auto result = AddTwoLines(lhs, rhs);

  std::vector<Threshold> expected_points{
      {models::Money{200}, models::Money{100}},
      {models::Money{110}, models::Money{1000}},
      {models::Money{110}, models::Money{1500}},
  };
  ASSERT_EQ(result.Points(), expected_points) << ToString(result.Points());
  ASSERT_EQ(result.MinPrice(), models::Money{20});
}

TEST(AddTwoLines, SecondConst) {
  // Вторая прямая константная
  ::handlers::ContinuousFees lhs_fees{};
  lhs_fees.points = {
      {100, 100},
      {0, 1000},
  };
  lhs_fees.min_price = 0;
  ::handlers::ContinuousFees rhs_fees{};
  rhs_fees.points = {
      {50, 100},
  };
  rhs_fees.min_price = 50;
  ContinuousFeeCalculator lhs{lhs_fees};
  ContinuousFeeCalculator rhs{rhs_fees};
  auto result = AddTwoLines(lhs, rhs);
  std::vector<Threshold> expected_points{
      {models::Money{150}, models::Money{100}},
      {models::Money{50}, models::Money{1000}},
  };
  ASSERT_EQ(result.Points(), expected_points) << ToString(result.Points());
  ASSERT_EQ(result.MinPrice(), models::Money{50});
}

TEST(AddTwoLines, BothSlop) {
  // Обе прямые имеют наклон
  ::handlers::ContinuousFees lhs_fees{};
  lhs_fees.points = {
      {100, 0},
      {0, 100},
  };
  lhs_fees.min_price = 0;
  ::handlers::ContinuousFees rhs_fees{};
  rhs_fees.points = {
      {50, 0},
      {0, 50},
  };
  ContinuousFeeCalculator lhs{lhs_fees};
  ContinuousFeeCalculator rhs{rhs_fees};
  auto result = AddTwoLines(lhs, rhs);
  std::vector<Threshold> expected_points{
      {models::Money{150}, models::Money{0}},
      {models::Money{50}, models::Money{50}},
      {models::Money{0}, models::Money{100}},
  };
  ASSERT_EQ(result.Points(), expected_points) << ToString(result.Points());
  ASSERT_EQ(result.MinPrice(), models::Money{0});
}

}  // namespace cart_delivery_fee::tests
