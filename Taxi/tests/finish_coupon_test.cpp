#include <gtest/gtest.h>

#include "stq/tasks/finish_coupon.hpp"

namespace stq_tasks::finish_coupon {

namespace {
Args GetArgs(bool was_used = true, std::optional<double> cost = 100,
             std::optional<double> coupon_value = 100) {
  stq_tasks::definitions::Coupon coupon{"id", was_used, coupon_value,
                                        /* percent */ std::nullopt,
                                        /* limit */ std::nullopt};

  Args args{"order_id", "yandex_uid",        "application", coupon,
            "phone_id", "personal_phone_id", cost,          "token"};
  return args;
}

TEST(CheckAreArgsValid, OkForSuccessfultUsage) {
  const auto& args = GetArgs();
  EXPECT_TRUE(AreArgsValid(args));
}

TEST(CheckAreArgsValid, OkForUnsuccessfulUsageAndCostNull) {
  const auto& args = GetArgs(false, std::nullopt);
  EXPECT_TRUE(AreArgsValid(args));
}

TEST(CheckAreArgsValid, OkForSuccessfulUsageAndCostNull) {
  const auto& args = GetArgs(true, std::nullopt);
  EXPECT_TRUE(AreArgsValid(args));
}

TEST(CheckAreArgsValid, OkForUnsuccessfulUsageAndCouponValueNull) {
  const auto& args = GetArgs(false);
  EXPECT_TRUE(AreArgsValid(args));
}

TEST(CheckAreArgsValid, ErrorForSuccessfulUsageAndCouponValueNull) {
  const auto& args = GetArgs(true, 100, std::nullopt);
  EXPECT_FALSE(AreArgsValid(args));
}
}  // namespace

}  // namespace stq_tasks::finish_coupon
