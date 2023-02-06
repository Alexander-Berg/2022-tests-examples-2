#include <gtest/gtest.h>

#include <clients/yamaps.cpp>

TEST(Yamaps, CleanLocale) {
  auto response1 = clients::yamaps::CleanLocale("_%Hans");
  EXPECT_EQ("en_GB", response1);

  auto response2 = clients::yamaps::CleanLocale("ru_%Hans");
  EXPECT_EQ("ru", response2);

  auto response3 = clients::yamaps::CleanLocale("haw_%Hans");
  EXPECT_EQ("haw", response3);

  auto response4 = clients::yamaps::CleanLocale("ru_RU_%Hans");
  EXPECT_EQ("ru_RU", response4);

  auto response5 = clients::yamaps::CleanLocale("haw_US_%Hans");
  EXPECT_EQ("haw_US", response5);

  auto response6 = clients::yamaps::CleanLocale("hz_Hans_%Hans");
  EXPECT_EQ("hz_Hans", response6);

  auto response7 = clients::yamaps::CleanLocale("tzm_Latn_%Hans");
  EXPECT_EQ("tzm_Latn", response7);

  auto response8 = clients::yamaps::CleanLocale("hz_Hans_CN_%Hans");
  EXPECT_EQ("hz_Hans_CN", response8);

  auto response9 = clients::yamaps::CleanLocale("tzm_Latn_MA_%Hans");
  EXPECT_EQ("tzm_Latn_MA", response9);
}
