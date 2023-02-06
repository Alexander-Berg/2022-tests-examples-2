#include "parse_number.hpp"

#include <gtest/gtest.h>

using utils::TryParse;

TEST(ParseNumber, TryParseTimeT) {
  time_t val;

  EXPECT_TRUE(TryParse("0", val));
  EXPECT_EQ(0, val);

  EXPECT_TRUE(TryParse("123", val));
  EXPECT_EQ(123, val);

  EXPECT_TRUE(TryParse("-123", val));
  EXPECT_EQ(-123, val);

  EXPECT_FALSE(TryParse("", val));
  EXPECT_FALSE(TryParse("abc", val));
  EXPECT_FALSE(TryParse("42group", val));
}
