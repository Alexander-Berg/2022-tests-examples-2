#include "value.hpp"

#include <gtest/gtest.h>

TEST(ValueZoneClassMap, Empty) {
  config::ValueZoneClassMap<int> map;

  map.Add(0);

  int res;
  ASSERT_NO_THROW(res = map("hello", "world"));
  EXPECT_EQ(0, res);

  ASSERT_NO_THROW(res = map(std::string(), std::string()));
  EXPECT_EQ(0, res);

  ASSERT_NO_THROW(res = map.Get("hello", "world"));
  EXPECT_EQ(0, res);

  ASSERT_NO_THROW(res = map.Get(std::string(), std::string()));
  EXPECT_EQ(0, res);
}
