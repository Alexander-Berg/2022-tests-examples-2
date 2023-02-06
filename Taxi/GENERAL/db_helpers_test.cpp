#include "db_helpers.hpp"

#include <gtest/gtest.h>

using models::legacy::NormalizeKeyWord;

TEST(NormalizeKeyWord, One) {
  EXPECT_STREQ("МОСКВА", NormalizeKeyWord("Москва").c_str());
  EXPECT_STREQ("ТУЛА", NormalizeKeyWord("Тула ").c_str());
  EXPECT_STREQ("УЗЛОВАЯ", NormalizeKeyWord(" Узловая ").c_str());
}
