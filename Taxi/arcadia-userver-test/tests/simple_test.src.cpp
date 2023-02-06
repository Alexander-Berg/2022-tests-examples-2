#include <gtest/gtest.h>

TEST(TestsFromTests, Test1) {
  auto str = "Some string";
  EXPECT_STREQ(str, "Some string");
}
