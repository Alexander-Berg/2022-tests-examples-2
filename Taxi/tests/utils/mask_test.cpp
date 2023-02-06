#include "utils/mask.hpp"

#include <gtest/gtest.h>

namespace utils {

TEST(MaskPhone, Basic) { EXPECT_EQ(MaskPhone("+79991234567"), "+799******67"); }

TEST(MaskPhone, StartAndEnd) {
  EXPECT_EQ(MaskPhone("+79991234567", 0, 0), "************");
  EXPECT_EQ(MaskPhone("+79991234567", 5, 5), "+7999**34567");
  EXPECT_EQ(MaskPhone("+79991234567", 12, 0), "+79991234567");
  EXPECT_EQ(MaskPhone("+79991234567", 0, 12), "+79991234567");
}

TEST(MaskPhone, TooMuch) {
  EXPECT_EQ(MaskPhone("+7999"), "***");
  EXPECT_EQ(MaskPhone("+7"), "***");
  EXPECT_EQ(MaskPhone("+79991234567", 0, 13), "***");
  EXPECT_EQ(MaskPhone("+79991234567", 0, 9001), "***");
  EXPECT_EQ(MaskPhone("+79991234567", 13, 0), "***");
  EXPECT_EQ(MaskPhone("+79991234567", 9001, 0), "***");
}

}  // namespace utils
