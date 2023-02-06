#include <gtest/gtest.h>

TEST(TestsFromSrc, Test1) {
  auto number = 1;
  EXPECT_EQ(number, 1);
}

int main(int argc, char** argv) {
  printf("Running main() from sample1\n");
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
