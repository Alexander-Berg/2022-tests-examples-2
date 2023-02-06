#include <gtest/gtest.h>
#include <models/order2.hpp>
#include <utils/bson_utils.hpp>

namespace {

TEST(Orders, FixPrice) {
  // parse order with fixed price
  models::orders::Order order;
  order.Deserialize(bson_utils::Load("order_fix_price.json"), {});
  ASSERT_TRUE((bool)order.fixed_price->price);

  // parse order without fixed price
  models::orders::Order order2;
  order2.Deserialize(bson_utils::Load("order_no_fix_price.json"), {});
  ASSERT_TRUE(!order2.fixed_price);

  // parse order with fixed price, but with changed destination.
  // so no more 'price' field in 'fixed_price' structure.
  models::orders::Order order3;
  order3.Deserialize(bson_utils::Load("order_fix_price_changed_dest.json"), {});
  ASSERT_TRUE(!order3.fixed_price->price);
}

}  //  namespace
