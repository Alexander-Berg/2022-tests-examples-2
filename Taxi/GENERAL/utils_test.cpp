#include <gtest/gtest.h>

#include "utils.hpp"

TEST(UserArchiveUtils, DelayAfterJob) {
  auto time = utils::datetime::Now();
  auto res = geohistory::archive::DelayAfterJob(
      time, time + std::chrono::nanoseconds(20),
      time + std::chrono::nanoseconds(520), 10, 499, 10,
      std::chrono::minutes(5));
  EXPECT_EQ(res.count(), 66);
  res = geohistory::archive::DelayAfterJob(time,
                                           time + std::chrono::nanoseconds(20),
                                           time + std::chrono::nanoseconds(500),
                                           15, 500, 6, std::chrono::minutes(5));
  EXPECT_EQ(res.count(), 61);
  res = geohistory::archive::DelayAfterJob(
      time, time + std::chrono::nanoseconds(20),
      time + std::chrono::minutes(500), 500, 1, 20, std::chrono::minutes(5));
  EXPECT_EQ(res.count(), 300000000000);
  res = geohistory::archive::DelayAfterJob(
      time, time + std::chrono::nanoseconds(20),
      time + std::chrono::nanoseconds(30), 0, 0, 20, std::chrono::minutes(5));
  EXPECT_EQ(res.count(), 10);
  res = geohistory::archive::DelayAfterJob(
      time, time + std::chrono::minutes(20), time + std::chrono::minutes(500),
      0, 0, 20, std::chrono::minutes(5));
  EXPECT_EQ(res.count(), 300000000000);
}

TEST(UserArchiveUtils, GetDeadline) {
  //  2018-10-01T15:45:00+00:00
  const int answer = 1538408700;
  //  2018-10-01T15:20:13+00:00
  EXPECT_EQ(
      std::chrono::system_clock::to_time_t(geohistory::archive::GetDeadline(
          std::chrono::system_clock::from_time_t(1538407213))),
      answer);
  //  2018-10-01T14:52:00+00:00
  EXPECT_EQ(
      std::chrono::system_clock::to_time_t(geohistory::archive::GetDeadline(
          std::chrono::system_clock::from_time_t(1538405520))),
      answer);
}
