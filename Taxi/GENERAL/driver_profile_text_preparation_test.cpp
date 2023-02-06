#include <gtest/gtest.h>

#include "driver_profile_text_preparation.hpp"

TEST(DriverProfileTextPreparation, PrepareDriverLicense) {
  using utils::PrepareDriverLicense;
  EXPECT_EQ("", PrepareDriverLicense(u8"    "));
  EXPECT_EQ("123", PrepareDriverLicense(u8" 1 2 3 "));
  EXPECT_EQ(u8"АБ,ЪЪЯ", PrepareDriverLicense(u8" А б, ъъ я\n"));
  EXPECT_EQ(u8"АБВ123WER", PrepareDriverLicense(u8"Абв 1 2 3 wer"));
}

TEST(DriverProfileTextPreparation, PrepareNormalizedDriverLicense) {
  using utils::PrepareNormalizedDriverLicense;
  EXPECT_EQ("", PrepareNormalizedDriverLicense(u8"    "));
  EXPECT_EQ("123", PrepareNormalizedDriverLicense(u8" 1 2 3 "));
  EXPECT_EQ("ABCEHKMOPTXY", PrepareNormalizedDriverLicense(u8"АВСЕНКМОРТХУ"));
  EXPECT_EQ("0123456789", PrepareNormalizedDriverLicense(u8"0123456789"));
  EXPECT_EQ(u8"Я123Я", PrepareNormalizedDriverLicense(u8"я123Я"));
  EXPECT_EQ(u8"AБЪЪЯ", PrepareNormalizedDriverLicense(u8" А б, ъъ я "));
}
