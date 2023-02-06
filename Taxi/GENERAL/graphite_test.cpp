#include "graphite.hpp"

#include <gtest/gtest.h>

TEST(Graphite, GetRequestTypeName) {
  const clients::Graphite graphite;

  EXPECT_THROW(graphite.GetRequestTypeName(1000), std::out_of_range);

  const uint16_t hw_id_0 = graphite.GetDynamicRequestType("hello_world");
  EXPECT_LE(utils::external_request::kCount, hw_id_0);
  EXPECT_STREQ("hello_world", graphite.GetRequestTypeName(hw_id_0).c_str());

  const uint16_t hw_id_1 = graphite.GetDynamicRequestType("hello_world");
  EXPECT_EQ(hw_id_0, hw_id_1);

  const uint16_t q_id = graphite.GetDynamicRequestType("qwerty");
  EXPECT_LE(utils::external_request::kCount, q_id);
  EXPECT_NE(hw_id_0, q_id);
  EXPECT_STREQ("qwerty", graphite.GetRequestTypeName(q_id).c_str());
}
