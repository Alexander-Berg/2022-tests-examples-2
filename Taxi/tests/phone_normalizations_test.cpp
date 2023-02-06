#include <gtest/gtest.h>

namespace personal::utils {
std::string LeftOnlyPlusAndDigits(const std::string& value);
}

namespace pu = personal::utils;

TEST(PhoneNormalizationTest, NormalizePhone) {
  EXPECT_EQ(pu::LeftOnlyPlusAndDigits("1234567890"), "1234567890");
  EXPECT_EQ(pu::LeftOnlyPlusAndDigits("+1234567890"), "+1234567890");
  EXPECT_EQ(pu::LeftOnlyPlusAndDigits("+1-2-3(4)5+6=7#8 9~0__"), "+1234567890");
  EXPECT_EQ(pu::LeftOnlyPlusAndDigits(" +1234567890 "), "+1234567890");
  EXPECT_EQ(pu::LeftOnlyPlusAndDigits("123+4567890"), "1234567890");
  EXPECT_EQ(pu::LeftOnlyPlusAndDigits(""), "");
  EXPECT_EQ(pu::LeftOnlyPlusAndDigits("!@#$%^&*()_+"), "+");
  EXPECT_EQ(pu::LeftOnlyPlusAndDigits("!@#$%^&*()_"), "");
  EXPECT_EQ(pu::LeftOnlyPlusAndDigits("abdsd+rert"), "+");
}
