#include "orderkit/order_proc.cpp"

#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <models/order2.hpp>
#include <utils/bson_utils.hpp>

namespace {

TEST(OrderProc, CreateEmpty) {
  models::orders::Order order;
  order.Deserialize(bson_utils::Load("order_for_order_proc.json"), {});

  auto actual_order_proc = orderkit::order_proc::Create(order);
  auto expected_order_proc = bson_utils::Load("order_proc_expected_empty.json");

  bson_utils::BSONCompare comparator;
  ASSERT_TRUE(comparator.Compare(expected_order_proc, actual_order_proc));
}

}  // namespace
