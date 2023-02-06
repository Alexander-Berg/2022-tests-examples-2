#include "array.hpp"

#include <gtest/gtest.h>

TEST(Array, Length) {
  int arr[] = {1, 2, 3, 4};
  EXPECT_EQ(4u, Length(arr));
}
