#include <gtest/gtest.h>

#include <subvention-rule-utils/models/daytime.hpp>

namespace sru = subvention_rule_utils;

TEST(Daytime, Datetime) {
  EXPECT_EQ(sru::models::Daytime(9, 17),
            sru::models::Daytime(9 * 3600 + 17 * 60));
  EXPECT_EQ(sru::models::Daytime(24, 0), sru::models::Daytime(0, 0));

  EXPECT_LT(sru::models::Daytime(9, 17), sru::models::Daytime(9, 18));
  EXPECT_LT(sru::models::Daytime(9, 17), sru::models::Daytime(10, 19));
  EXPECT_LT(sru::models::Daytime(9, 17), sru::models::Daytime(10, 3));
}

TEST(Daytime, DatetimeRange) {
  const sru::models::DaytimeRange r1 = {sru::models::Daytime(10, 12),
                                        sru::models::Daytime(11, 03)};
  EXPECT_TRUE(r1.Contains(sru::models::Daytime(10, 12)));
  EXPECT_TRUE(r1.Contains(sru::models::Daytime(11, 02)));
  EXPECT_FALSE(r1.Contains(sru::models::Daytime(11, 03)));

  const sru::models::DaytimeRange r2 = {sru::models::Daytime(11, 11),
                                        sru::models::Daytime(11, 11)};
  EXPECT_TRUE(r2.Contains(sru::models::Daytime(11, 11)));
  EXPECT_TRUE(r2.Contains(sru::models::Daytime(11, 12)));

  const sru::models::DaytimeRange r3 = {sru::models::Daytime(11, 11),
                                        sru::models::Daytime(11, 12)};
  EXPECT_TRUE(r3.Contains(sru::models::Daytime(11, 11)));
  EXPECT_FALSE(r3.Contains(sru::models::Daytime(11, 12)));

  const sru::models::DaytimeRange r4 = {sru::models::Daytime(12, 05),
                                        sru::models::Daytime(12, 00)};
  EXPECT_TRUE(r4.Contains(sru::models::Daytime(12, 05)));
  EXPECT_TRUE(r4.Contains(sru::models::Daytime(12, 10)));
  EXPECT_TRUE(r4.Contains(sru::models::Daytime(11, 59)));
  EXPECT_FALSE(r4.Contains(sru::models::Daytime(12, 00)));
  EXPECT_FALSE(r4.Contains(sru::models::Daytime(12, 04)));
}
