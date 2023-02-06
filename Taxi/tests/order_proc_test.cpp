#include <gtest/gtest.h>

#include "utils/order_proc.hpp"

namespace coupons::utils::order_proc {

namespace {
formats::json::Value GetOrderJson(std::string status, std::string taxi_status,
                                  bool was_coupon_used,
                                  bool has_performer = false) {
  formats::json::ValueBuilder order;
  order["status"] = status;
  order["taxi_status"] = taxi_status;
  order["coupon"] = formats::json::MakeObject("was_used", was_coupon_used);

  formats::json::ValueBuilder result;
  result["order"] = order.ExtractValue();
  if (has_performer) {
    result["performer"] = formats::json::MakeObject("candidate_index", 0);
  }

  return result.ExtractValue();
}

TEST(WasCouponUsed, JustTakeFromCoupon) {
  for (bool was_used : {true, false}) {
    const auto order = GetOrderJson("finished", "complete", was_used);
    EXPECT_EQ(WasCouponUsed(order), was_used);
  }
}

TEST(WasCouponUsed, InconsistentStateStatus) {
  const auto order = GetOrderJson("not_finished", "complete", true);
  EXPECT_THROW(WasCouponUsed(order), InconsistentOrderProcState);
}

TEST(WasCouponUsed, InconsistentStateTaxiStatus) {
  const auto order = GetOrderJson("finished", "not_complete", true);
  EXPECT_THROW(WasCouponUsed(order), InconsistentOrderProcState);
}

TEST(WasCouponUsed, ExpiredOrderWithPerformer) {
  for (bool was_used : {true, false}) {
    const auto order = GetOrderJson("finished", "expired", was_used, true);
    if (was_used) {
      EXPECT_THROW(WasCouponUsed(order), InconsistentOrderProcState);
    } else {
      EXPECT_FALSE(WasCouponUsed(order));
    }
  }
}

TEST(WasCouponUsed, ExpiredOrderWithoutPerformer) {
  for (bool was_used : {true, false}) {
    const auto order = GetOrderJson("finished", "expired", was_used, false);
    EXPECT_FALSE(WasCouponUsed(order));
  }
}

}  // namespace

}  // namespace coupons::utils::order_proc
