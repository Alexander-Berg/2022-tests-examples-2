#include <userver/utest/utest.hpp>

#include "common/common.hpp"

using bank_wallet::common::GetLastPanDigits;

TEST(Common, LastPanDigitsEmpty) {
  const std::string invalid_pan = "";
  EXPECT_EQ(invalid_pan, GetLastPanDigits(invalid_pan));
}

TEST(Common, LastPanDigitsTwo) {
  const std::string invalid_pan = "11";
  EXPECT_EQ(invalid_pan, GetLastPanDigits(invalid_pan));
}

TEST(Common, LastPanDigitsTwoAndMore) {
  std::string invalid_pan = "11";
  while (invalid_pan.size() <= 13) {
    EXPECT_EQ(invalid_pan.substr(invalid_pan.size() - 2),
              GetLastPanDigits(invalid_pan));
    invalid_pan = "*" + invalid_pan;
  }
}

TEST(Common, LastPanDigitsFourteenAndMore) {
  std::string invalid_pan = "**********2211";
  while (invalid_pan.size() <= 20) {
    EXPECT_EQ(invalid_pan.substr(invalid_pan.size() - 4),
              GetLastPanDigits(invalid_pan));
    invalid_pan = "*" + invalid_pan;
  }
}
