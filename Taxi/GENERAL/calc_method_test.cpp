
#include "calc_method.hpp"

#include <gtest/gtest.h>

using namespace models;

TEST(CalcMethod, FromInt) {
  EXPECT_EQ(CalcMethodFromInt(0), CalcMethod::Unknown);
  EXPECT_EQ(CalcMethodFromInt(1), CalcMethod::FreeRoute);
  EXPECT_EQ(CalcMethodFromInt(2), CalcMethod::FixedPrice);
  EXPECT_EQ(CalcMethodFromInt(3), CalcMethod::Other);
  EXPECT_EQ(CalcMethodFromInt(4), CalcMethod::OrderCost);
  EXPECT_EQ(CalcMethodFromInt(5), CalcMethod::Pool);
  EXPECT_EQ(CalcMethodFromInt(6), CalcMethod::Unknown);
  EXPECT_EQ(CalcMethodFromInt(7), CalcMethod::Unknown);
  EXPECT_EQ(CalcMethodFromInt(-1), CalcMethod::Unknown);
}

TEST(CalcMethod, ToString) {
  EXPECT_EQ(CalcMethodToString(CalcMethod::Unknown), "unknown");
  EXPECT_EQ(CalcMethodToString(CalcMethod::FreeRoute), "taximeter");
  EXPECT_EQ(CalcMethodToString(CalcMethod::FixedPrice), "fixed");
  EXPECT_EQ(CalcMethodToString(CalcMethod::Other), "other");
  EXPECT_EQ(CalcMethodToString(CalcMethod::OrderCost), "order-cost");
  EXPECT_EQ(CalcMethodToString(CalcMethod::Pool), "pool");
  EXPECT_EQ(CalcMethodToString(CalcMethod::MaxValue), "");
}
