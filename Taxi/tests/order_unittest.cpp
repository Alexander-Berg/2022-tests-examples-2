#include <models/order.hpp>

#include <gtest/gtest.h>

struct TestCouponData {
  mongo::BSONObj coupon_obj;
  double cost;
  double value_expected;
  double apply_expected;
  bool can_be_applied_expected;
};

// clang-format off
std::vector<TestCouponData> coupon_tests{
  {
    BSON(
      "valid" << false <<
      "was_used" << false <<
      "value" << 100
    ),
    123.,
    0.0,
    123.,
    false
  },
  {
    BSON(
      "valid" << true <<
      "was_used" << false <<
      "value" << 100
    ),
    123.,
    0.0,
    123.,
    false
  },
  {
    BSON(
      "valid" << false <<
      "was_used" << true <<
      "value" << 100
    ),
    123.,
    0.0,
    123.,
    false
  },
  {
    BSON(
      "valid" << true <<
      "was_used" << true <<
      "value" << 100
    ),
    123.,
    100.,
    23.,
    true
  },
  {
    BSON(
      "valid" << true <<
      "was_used" << true <<
      "percent" << 20
    ),
    100.,
    20.,
    80.,
    true
  },
  {
    BSON(
      "valid" << true <<
      "was_used" << true <<
      "percent" << 20 <<
      "limit" << 10
    ),
    100.,
    10.,
    90.,
    true
  },
  {
    BSON(
      "valid" << true <<
      "was_used" << true <<
      "percent" << 20 <<
      "limit" << 0
    ),
    100.,
    0.,
    100.,
    false
  },
};
// clang-format on

class OrderCoupon : public ::testing::TestWithParam<TestCouponData> {};

TEST_P(OrderCoupon, Parametrized) {
  const auto& params = GetParam();
  models::Order::Coupon coupon(params.coupon_obj);
  EXPECT_EQ(coupon.Value(params.cost), params.value_expected);
  EXPECT_EQ(coupon.Apply(params.cost), params.apply_expected);
  EXPECT_EQ(coupon.CanBeApplied(), params.can_be_applied_expected);
}

INSTANTIATE_TEST_CASE_P(OrderCouponTest, OrderCoupon,
                        ::testing::ValuesIn(coupon_tests), );
