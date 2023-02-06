#include <gtest/gtest.h>

#include <userver/utest/utest.hpp>

#include <format_balance_impl.hpp>

UTEST(BankFormatterTest, FormatBalance) {
  // test is_fixed and precision params
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(10000.04, false, 0, "ru_RU.UTF-8"),
      "10 000");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(10000.09, true, 1, "ru_RU.UTF-8"),
      "10 000,1");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(10000.04, false, 1, "ru_RU.UTF-8"),
      "10 000");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(10000.04, false, 2, "ru_RU.UTF-8"),
      "10 000,04");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(10000.04, false, 4, "ru_RU.UTF-8"),
      "10 000,04");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(10000.04, true, 4, "ru_RU.UTF-8"),
      "10 000,0400");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(1000.00, false, 4, "ru_RU.UTF-8"),
      "1000");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(1000.05, false, 1, "ru_RU.UTF-8"),
      "1000,1");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(-1500, false, 1, "ru_RU.UTF-8"),
      "\u22121500");

  // test four numbers without space
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(9998.999, true, 0, "ru_RU.UTF-8"),
      "9999");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(9998.999, true, 2, "ru_RU.UTF-8"),
      "9999,00");

  // test other system locales
  EXPECT_EQ(bank_localization::impl::FormatAmount(10000000.04, false, 4,
                                                  "en_US.UTF-8"),
            "10,000,000.04");
  EXPECT_EQ(bank_localization::impl::FormatAmount(10000000.04, false, 4,
                                                  "de_DE.UTF-8"),
            "10.000.000,04");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(1000.04, false, 4, "de_DE.UTF-8"),
      "1.000,04");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(0.005, false, 2, "de_DE.UTF-8"),
      "0,01");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(-10.03, false, 2, "de_DE.UTF-8"),
      "\u221210,03");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(-0.006, false, 2, "de_DE.UTF-8"),
      "\u22120,01");
  EXPECT_EQ(
      bank_localization::impl::FormatAmount(-0.004, false, 2, "de_DE.UTF-8"),
      "0");
}
