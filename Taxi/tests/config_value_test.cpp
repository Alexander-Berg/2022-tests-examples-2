#include <config/value.hpp>

#include <gtest/gtest.h>

TEST(ValueDict, Simple) {
  config::ValueDict<int> dict({{"foo", 321}, {"__default__", 123}});

  EXPECT_EQ(dict["foo"], 321);
  EXPECT_EQ(dict["bar"], 123);
}

TEST(ValueDict, Failure) {
  config::ValueDict<int> dict({});

  EXPECT_THROW(dict["foo"], std::runtime_error);
}
