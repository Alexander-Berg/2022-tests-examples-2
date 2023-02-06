#include <userver/utest/utest.hpp>

#include "driver_profile_text_preparation.hpp"

TEST(DriverProfileTextPreparation, PrepareDriverLicense) {
  using utils::text::PrepareDriverLicense;

  EXPECT_EQ("", PrepareDriverLicense("    "));
  EXPECT_EQ("123", PrepareDriverLicense(" 1 2 3 "));
  EXPECT_EQ("АБ,ЪЪЯ", PrepareDriverLicense(" А б, ъъ я\n"));
  EXPECT_EQ("АБВ123WER", PrepareDriverLicense("Абв 1 2 3 wer"));
}
