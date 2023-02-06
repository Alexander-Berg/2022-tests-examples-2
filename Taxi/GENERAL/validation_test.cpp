#include <gtest/gtest.h>

#include "validation.hpp"

using eats_layout_constructor::utils::colors::IsValidHexColor;

TEST(IsValidHexColor, EmptyInput) { ASSERT_FALSE(IsValidHexColor("")); }

TEST(IsValidHexColor, WrongLength) { ASSERT_FALSE(IsValidHexColor("#aa")); }

TEST(IsValidHexColor, DoubleHash) { ASSERT_FALSE(IsValidHexColor("##aa")); }

TEST(IsValidHexColor, NoHash) { ASSERT_FALSE(IsValidHexColor("aa")); }

TEST(IsValidHexColor, InValidShort) { ASSERT_FALSE(IsValidHexColor("#aaa")); }

TEST(IsValidHexColor, ValidLong) { ASSERT_TRUE(IsValidHexColor("#ababab")); }

TEST(IsValidHexColor, ValidMultiCase) {
  ASSERT_TRUE(IsValidHexColor("#aFBBCf"));
}

TEST(IsValidHexColor, NonHexDigit) { ASSERT_FALSE(IsValidHexColor("#aFBZCf")); }
