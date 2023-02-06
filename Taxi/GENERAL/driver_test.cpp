#include "driver.hpp"

#include <gtest/gtest.h>

TEST(HelpersDriver, GetDriverId) {
  EXPECT_STREQ(utils::helpers::GetDriverId("1", "2").c_str(), "1_2");
}
