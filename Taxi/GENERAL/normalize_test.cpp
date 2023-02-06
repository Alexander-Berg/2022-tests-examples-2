#include <gtest/gtest.h>

#include "normalize.hpp"

TEST(DeptransUtils, NormalizeDriverLicense) {
  EXPECT_EQ("ABCEHKMOPTXY",
            utils::deptrans::NormalizeDriverLicense("АВСЕНКМОРТХУ"));
  EXPECT_EQ("Y123Y", utils::deptrans::NormalizeDriverLicense("У123Y"));
  EXPECT_EQ("Y123Y", utils::deptrans::NormalizeDriverLicense("Y123У"));
  EXPECT_EQ("1Y2Y3", utils::deptrans::NormalizeDriverLicense("1Y2У3"));
  EXPECT_EQ("HBAA123124",
            utils::deptrans::NormalizeDriverLicense("нвAA123124"));
  EXPECT_EQ("HBAA123124",
            utils::deptrans::NormalizeDriverLicense("нвaa123124"));
  EXPECT_EQ("HPTCCMM", utils::deptrans::NormalizeDriverLicense("нртCCмм"));
  EXPECT_EQ("ЯЯ", utils::deptrans::NormalizeDriverLicense("яЯ"));
}

TEST(DeptransUtils, NormalizeString) {
  std::string before("Мамин ё - Сибиряк ");
  std::string expected("МАМИНЕСИБИРЯК");
  ASSERT_EQ(utils::deptrans::NormalizeDriverLastName(before), expected);
}

TEST(DeptransUtils, HashDriverLicenseRus) {
  ASSERT_EQ(
      utils::deptrans::GetDriverLicenseHash("0123456", "Мамин - Сибиряк "),
      utils::deptrans::GetDriverLicenseHash("0123456", "МАМИНСИБИРЯК"));
  ASSERT_EQ("LICENSE_NUMBER1",
            utils::deptrans::NormalizeDriverLicense("license_number1"));
  ASSERT_EQ("dfe10ceb8a402ea518d8e89126044a1e8a30c1d4db37d5941fcdb7dd3c2dd166",
            utils::deptrans::GetDriverLicenseHash("license_number1", "Иванов"));
}

TEST(DeptransUtils, HashDriverLicenseRusYo) {
  ASSERT_EQ(utils::deptrans::GetDriverLicenseHash("0123456", "Маминё-Сибиряк"),
            utils::deptrans::GetDriverLicenseHash("0123456", "МАМИНЕСИБИРЯК"));
}

TEST(DeptransUtils, HashDriverLicenseEn) {
  ASSERT_EQ(utils::deptrans::GetDriverLicenseHash("0123456", "Smith"),
            utils::deptrans::GetDriverLicenseHash("0123456", "SMITH"));
}
