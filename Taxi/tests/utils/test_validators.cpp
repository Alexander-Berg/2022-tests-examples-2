#include <gtest/gtest.h>

#include <utils/validators.hpp>

namespace uu = user_api::utils;

TEST(ValidatorsTest, ValidPhones) {
  using std::string_literals::operator""s;
  EXPECT_TRUE(uu::ValidatePhone("+71111111111"s));
  EXPECT_TRUE(uu::ValidatePhone("+7"s));
}

TEST(ValidatorsTest, InvalidPhones) {
  using std::string_literals::operator""s;
  EXPECT_FALSE(uu::ValidatePhone("81111111111"));
  EXPECT_FALSE(uu::ValidatePhone("++71111111111"));
  EXPECT_FALSE(uu::ValidatePhone("+"));
  EXPECT_FALSE(uu::ValidatePhone("+7111111+11"));
  EXPECT_FALSE(uu::ValidatePhone("+7111111a11"));
  EXPECT_FALSE(uu::ValidatePhone("+711111111111111111"));  // Too long
  EXPECT_FALSE(uu::ValidatePhone(" +71111111111"s));       // No trailing spaces
  EXPECT_FALSE(uu::ValidatePhone("+71111111111 "s));       // No trailing spaces
}
