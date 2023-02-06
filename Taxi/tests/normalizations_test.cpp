#include <gtest/gtest.h>

#include <utils/normalizations.hpp>

namespace pu = personal::utils;

TEST(NormalizationsTest, NormalizeDriverLicense) {
  EXPECT_EQ(pu::NormalizeDriverLicense(u8"1234567890"), u8"1234567890");
  EXPECT_EQ(pu::NormalizeDriverLicense(u8"ABCEHKMOPTXY"), u8"ABCEHKMOPTXY");
  EXPECT_EQ(pu::NormalizeDriverLicense(u8"abcehkmoptxy"), u8"ABCEHKMOPTXY");
  EXPECT_EQ(pu::NormalizeDriverLicense(u8"АВСЕНКМОРТХУ"), u8"ABCEHKMOPTXY");
  EXPECT_EQ(pu::NormalizeDriverLicense(u8"авсенкмортху"), u8"ABCEHKMOPTXY");
  EXPECT_EQ(pu::NormalizeDriverLicense(u8"äвсенкмортху"), u8"ÄBCEHKMOPTXY");
  EXPECT_EQ(pu::NormalizeDriverLicense(u8"qwerty123"), u8"QWERTY123");
  EXPECT_EQ(pu::NormalizeDriverLicense(u8"эюя123"), u8"ЭЮЯ123");
  EXPECT_EQ(pu::NormalizeDriverLicense(u8"   YУYУYУ    "), u8"YYYYYY");
  EXPECT_EQ(pu::NormalizeDriverLicense(u8"YУ   YУ\tYУ"), u8"YYYYYY");
  EXPECT_EQ(pu::NormalizeDriverLicense(u8"\n   YУ\rYУ  YУ"), u8"YYYYYY");
  EXPECT_EQ(pu::NormalizeDriverLicense(u8"YУ\t\r\nYУYУ"), u8"YYYYYY");
}

TEST(NormalizationsTest, NormalizeDriverLicenseSpaces) {
  // ''.join([
  //   unichr(ch).encode('utf-8')
  //   for ch in xrange(sys.maxunicode + 1)
  //   if not hlp.clean_driver_license(unichr(ch))
  // ])
  const auto kSpacesUtf8 =
      u8"\t\n\x0b\x0c\r\x1c\x1d\x1e\x1f \xc2\x85\xc2\xa0\xe1\x9a\x80\xe1\xa0"
      u8"\x8e\xe2\x80\x80\xe2\x80\x81\xe2\x80\x82\xe2\x80\x83\xe2\x80\x84\xe2"
      u8"\x80\x85\xe2\x80\x86\xe2\x80\x87\xe2\x80\x88\xe2\x80\x89\xe2\x80\x8a"
      u8"\xe2\x80\xa8\xe2\x80\xa9\xe2\x80\xaf\xe2\x81\x9f\xe3\x80\x80";
  EXPECT_EQ(pu::NormalizeDriverLicense(kSpacesUtf8), "");

  // ' a'.join([
  //    unichr(ch).encode('utf-8')
  //    for ch in xrange(sys.maxunicode + 1)
  //    if not hlp.clean_driver_license(unichr(ch))
  // ])
  const auto kSpacesWithDataUtf8 =
      u8"\t a\n a\x0b a\x0c a\r a\x1c a\x1d a\x1e a\x1f a  a\xc2\x85 a\xc2\xa0 "
      u8"a\xe1\x9a\x80 a\xe1\xa0\x8e a\xe2\x80\x80 a\xe2\x80\x81 a\xe2\x80\x82 "
      u8"a\xe2\x80\x83 a\xe2\x80\x84 a\xe2\x80\x85 a\xe2\x80\x86 a\xe2\x80\x87 "
      u8"a\xe2\x80\x88 a\xe2\x80\x89 a\xe2\x80\x8a a\xe2\x80\xa8 a\xe2\x80\xa9 "
      u8"a\xe2\x80\xaf a\xe2\x81\x9f a\xe3\x80\x80";
  EXPECT_EQ(pu::NormalizeDriverLicense(kSpacesWithDataUtf8),
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAA");
}
