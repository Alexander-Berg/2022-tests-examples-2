#include <gtest/gtest.h>

#include "misc.hpp"

namespace persey_core::models {

TEST(models, ParseExternalDecimal) {
  EXPECT_EQ(ToString(ParseExternalDecimal("1e1")), "10");
  EXPECT_EQ(ToString(ParseExternalDecimal("1e2")), "100");
  EXPECT_EQ(ToString(ParseExternalDecimal("1.5e2")), "150");
  EXPECT_EQ(ToString(ParseExternalDecimal("1.5e+2")), "150");
  EXPECT_EQ(ToString(ParseExternalDecimal("1.2345e+2")), "123.45");
  EXPECT_EQ(ToString(ParseExternalDecimal("-1.2345e+2")), "-123.45");
  EXPECT_EQ(ToString(ParseExternalDecimal("1.5")), "1.5");
  EXPECT_EQ(ToString(ParseExternalDecimal("-1.5")), "-1.5");
  EXPECT_EQ(ToString(ParseExternalDecimal("1e10")), "10000000000");
  EXPECT_ANY_THROW(ParseExternalDecimal("1e"));
  EXPECT_ANY_THROW(ParseExternalDecimal("1e+"));
  EXPECT_ANY_THROW(ParseExternalDecimal("1e-1"));
  EXPECT_ANY_THROW(ParseExternalDecimal("1e+999999999"));
  EXPECT_ANY_THROW(ParseExternalDecimal("1.2345e+2x"));
  EXPECT_ANY_THROW(ParseExternalDecimal("1.2345e+"));
}

}  // namespace persey_core::models
