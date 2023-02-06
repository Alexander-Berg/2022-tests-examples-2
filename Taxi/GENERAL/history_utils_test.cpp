#include <gtest/gtest.h>

#include "history_utils.hpp"

TEST(GeohistoryUtils, HoursCount) {
  // Time.at(1483243200) => 2017-01-01 07:00:00 +0300
  std::chrono::system_clock::time_point t =
      std::chrono::system_clock::from_time_t(1483243200);
  const auto r1 = geohistory::utils::GetHourCount(t);
  ASSERT_EQ(r1, 4);
}

TEST(GeohistoryUtils, SplitTime) {
  // Time.at(1483318800) => 2017-01-02 04:00:00 +0300
  std::chrono::system_clock::time_point t =
      std::chrono::system_clock::from_time_t(1483318800);
  std::string date, time;
  std::tie(date, time) = geohistory::utils::SplitTime(t);
  EXPECT_EQ(date, "20170102");
  EXPECT_EQ(time, "1483318800000000");
  std::tie(date, time) = geohistory::utils::SplitTime(t, true);
  EXPECT_EQ(date, "20170102");
  EXPECT_EQ(time, "1483318800");
}
