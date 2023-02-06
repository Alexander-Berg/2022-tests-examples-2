
#include "order2.hpp"

#include <gtest/gtest.h>

using namespace models;
using namespace models::orders;

TEST(Order2, Smoke) {
  Order order;
  // must be
  order.id = "hello";
  order.type = types::Soon;
  order.request.payment.type = payment_types::Cash;
  order.status = statuses::Draft;
  order.user_phone_id = mongo::OID("5714f45e98956f06baaae3d4");
  order.payment_tech.type = payment_types::Cash;

  Order order_clone;

  ASSERT_NO_THROW(order_clone.Deserialize(order.Serialize(), {}));

  EXPECT_EQ(order.id, order_clone.id);
  EXPECT_EQ(order.type, order_clone.type);
  EXPECT_EQ(order.request.payment.type, order_clone.request.payment.type);
  EXPECT_EQ(order.status, order_clone.status);
}
