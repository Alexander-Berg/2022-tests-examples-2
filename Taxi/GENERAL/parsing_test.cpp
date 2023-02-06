#include <gtest/gtest.h>

#include "parsing.hpp"

TEST(View_Common_Parsing, ExtractOauth) {
  EXPECT_STREQ("", views::ExtractOauth("").c_str());
  EXPECT_STREQ("", views::ExtractOauth("test").c_str());
  EXPECT_STREQ("test", views::ExtractOauth("Bearer test").c_str());
}
