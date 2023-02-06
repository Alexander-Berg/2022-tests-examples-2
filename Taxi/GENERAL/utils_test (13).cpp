#include <gtest/gtest.h>

#include <utils/utils.hpp>

std::string MaskCode(const std::string& code) {
  std::string result = code;
  esignature_issuer::utils::MaskCode(result);
  return result;
}

TEST(Utils, MaskCode) {
  EXPECT_EQ("", MaskCode(""));
  EXPECT_EQ("*", MaskCode("1"));
  EXPECT_EQ("**", MaskCode("12"));
  EXPECT_EQ("1**", MaskCode("123"));
  EXPECT_EQ("12**", MaskCode("1234"));
  EXPECT_EQ("12**5", MaskCode("12345"));
  EXPECT_EQ("12**56", MaskCode("123456"));
  EXPECT_EQ("12***67", MaskCode("1234567"));
}
