#include <gtest/gtest.h>

#include <handlers/create_transaction.hpp>

using handlers::CheckAndNormalizeAmount;

TEST(CheckAndNormalizeAmount, OK) {
  EXPECT_EQ("1.0000", CheckAndNormalizeAmount("    1"));
  EXPECT_EQ("1.0000", CheckAndNormalizeAmount("1    "));
  EXPECT_EQ("1.0000", CheckAndNormalizeAmount("  1  "));
  EXPECT_EQ("1.0000", CheckAndNormalizeAmount("1"));
  EXPECT_EQ("1.0000", CheckAndNormalizeAmount("1."));
  EXPECT_EQ("1.0000", CheckAndNormalizeAmount("+1."));
  EXPECT_EQ("-1.0000", CheckAndNormalizeAmount("-1."));
  EXPECT_EQ("0.1000", CheckAndNormalizeAmount(".1"));
  EXPECT_EQ("0.0001", CheckAndNormalizeAmount("0.0000501"));
  EXPECT_EQ("12345.7890", CheckAndNormalizeAmount("12345.7890000"));
  EXPECT_EQ("1000000.0000", CheckAndNormalizeAmount("1000000"));
  EXPECT_EQ("-1000000.0000", CheckAndNormalizeAmount("-1000000"));
}

TEST(CheckAndNormalizeAmount, Fail) {
  using handlers::BadRequestError;

  EXPECT_THROW(CheckAndNormalizeAmount(""), BadRequestError);
  EXPECT_THROW(CheckAndNormalizeAmount("-"), BadRequestError);
  EXPECT_THROW(CheckAndNormalizeAmount("+"), BadRequestError);
  EXPECT_THROW(CheckAndNormalizeAmount("."), BadRequestError);
  EXPECT_THROW(CheckAndNormalizeAmount("0"), BadRequestError);
  EXPECT_THROW(CheckAndNormalizeAmount(".0"), BadRequestError);
  EXPECT_THROW(CheckAndNormalizeAmount("0."), BadRequestError);
  EXPECT_THROW(CheckAndNormalizeAmount("1000000000.0001"), BadRequestError);
  EXPECT_THROW(CheckAndNormalizeAmount("-1000000000.0001"), BadRequestError);
  EXPECT_THROW(CheckAndNormalizeAmount("i  1"), BadRequestError);
  EXPECT_THROW(CheckAndNormalizeAmount("1  i"), BadRequestError);
  EXPECT_THROW(CheckAndNormalizeAmount("1a"), BadRequestError);
  EXPECT_THROW(CheckAndNormalizeAmount("10a"), BadRequestError);
  EXPECT_THROW(CheckAndNormalizeAmount("1,000.000"), BadRequestError);
}
