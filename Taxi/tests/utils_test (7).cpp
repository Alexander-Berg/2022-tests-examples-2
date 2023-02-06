#include <gtest/gtest.h>

#include "utils.hpp"

TEST(UniqueDriversUtils, NormalizeDriverLicense) {
  EXPECT_EQ("KIA", unique_drivers::utils::NormalizeDriverLicense("KIA  "));
  EXPECT_EQ("ABCEHKMOPTXY",
            unique_drivers::utils::NormalizeDriverLicense("АВСЕНКМОРТХУ"));
  EXPECT_EQ("Y123Y", unique_drivers::utils::NormalizeDriverLicense("У123Y"));
  EXPECT_EQ("Y123Y", unique_drivers::utils::NormalizeDriverLicense("Y123У"));
  EXPECT_EQ("1Y2Y3", unique_drivers::utils::NormalizeDriverLicense("1Y2У3"));
  EXPECT_EQ("HBAA123124",
            unique_drivers::utils::NormalizeDriverLicense("нвAA123124"));
  EXPECT_EQ("HBAA123124",
            unique_drivers::utils::NormalizeDriverLicense("нвaa123124"));
  EXPECT_EQ("HPTCCMM",
            unique_drivers::utils::NormalizeDriverLicense("нртCCмм"));
  EXPECT_EQ("ЯЯ", unique_drivers::utils::NormalizeDriverLicense("яЯ"));
}
