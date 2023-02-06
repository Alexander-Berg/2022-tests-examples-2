#include <gtest/gtest.h>

#include <data_types/phone_type.hpp>

namespace market_personal_normalizer::data_types::phone_type {
std::string LeftOnlyPlusAndDigits(const std::string& value);
}

namespace pt = market_personal_normalizer::data_types::phone_type;

TEST(PhoneNormalizationTest, NormalizePhone) {
  EXPECT_EQ(pt::LeftOnlyPlusAndDigits("1234567890"), "1234567890");
  EXPECT_EQ(pt::LeftOnlyPlusAndDigits("+1234567890"), "+1234567890");
  EXPECT_EQ(pt::LeftOnlyPlusAndDigits("+1-2-3(4)5+6=7#8 9~0__"), "+1234567890");
  EXPECT_EQ(pt::LeftOnlyPlusAndDigits(" +1234567890 "), "+1234567890");
  EXPECT_EQ(pt::LeftOnlyPlusAndDigits("123+4567890"), "1234567890");
  EXPECT_EQ(pt::LeftOnlyPlusAndDigits(""), "");
  EXPECT_EQ(pt::LeftOnlyPlusAndDigits("!@#$%^&*()_+"), "+");
  EXPECT_EQ(pt::LeftOnlyPlusAndDigits("!@#$%^&*()_"), "");
  EXPECT_EQ(pt::LeftOnlyPlusAndDigits("abdsd+rert"), "+");
}
