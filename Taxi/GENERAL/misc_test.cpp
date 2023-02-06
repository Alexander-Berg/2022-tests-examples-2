#include <userver/utest/utest.hpp>

#include <helpers/misc.hpp>

using fleet_financial_statements::helpers::IsNumber;

TEST(HelpersMiscTest, IsNumber) {
  EXPECT_TRUE(IsNumber("0"));
  EXPECT_TRUE(IsNumber("1234567890"));

  EXPECT_FALSE(IsNumber(""));
  EXPECT_FALSE(IsNumber(" 1234567890"));
  EXPECT_FALSE(IsNumber("1234567890 "));
}
