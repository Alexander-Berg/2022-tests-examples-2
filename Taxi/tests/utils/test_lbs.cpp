#include <gtest/gtest.h>

#include "utils/lbs.hpp"

TEST(TestLbs, LbsMac) {
  auto lbs_mac = utils::lbs::LbsMacFromBssid("aabbccddeeff");
  ASSERT_EQ(lbs_mac.value_or(""), "AABBCCDDEEFF");
  lbs_mac = utils::lbs::LbsMacFromBssid("00112233aaff");
  ASSERT_EQ(lbs_mac.value_or(""), "00112233AAFF");
  lbs_mac = utils::lbs::LbsMacFromBssid("00112233aaf");
  ASSERT_EQ(lbs_mac, std::nullopt);
  lbs_mac = utils::lbs::LbsMacFromBssid("0:11:b:33:aa:f");
  ASSERT_EQ(lbs_mac.value_or(""), "00110B33AA0F");
  lbs_mac = utils::lbs::LbsMacFromBssid("0:11:b:33::f");
  ASSERT_EQ(lbs_mac, std::nullopt);
}
