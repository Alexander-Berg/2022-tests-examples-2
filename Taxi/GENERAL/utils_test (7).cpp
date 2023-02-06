#include <trackstory/utils.hpp>

#include <gtest/gtest.h>

TEST(trackstory, TestBucketHourAndMinutes) {
  // 2011-10-25T00:00:00+00:00
  auto hour_and_minutes = trackstory::utils::GetBucketHourAndMinutes(
      std::chrono::system_clock::from_time_t(1319500800));
  ASSERT_EQ(hour_and_minutes.first, 0);
  ASSERT_EQ(hour_and_minutes.second, 0);

  // 2011-10-25T23:05:00+00:00
  hour_and_minutes = trackstory::utils::GetBucketHourAndMinutes(
      std::chrono::system_clock::from_time_t(1319583900));
  ASSERT_EQ(hour_and_minutes.first, 23);
  ASSERT_EQ(hour_and_minutes.second, 1);

  // 2011-10-25T23:55:00+00:00
  hour_and_minutes = trackstory::utils::GetBucketHourAndMinutes(
      std::chrono::system_clock::from_time_t(1319586900));
  ASSERT_EQ(hour_and_minutes.first, 23);
  ASSERT_EQ(hour_and_minutes.second, 11);

  // 2011-10-25T23:59:59+00:00
  hour_and_minutes = trackstory::utils::GetBucketHourAndMinutes(
      std::chrono::system_clock::from_time_t(1319587199));
  ASSERT_EQ(hour_and_minutes.first, 23);
  ASSERT_EQ(hour_and_minutes.second, 11);

  // 2011-10-26T00:04:59+00:00
  hour_and_minutes = trackstory::utils::GetBucketHourAndMinutes(
      std::chrono::system_clock::from_time_t(1319501099));
  ASSERT_EQ(hour_and_minutes.first, 0);
  ASSERT_EQ(hour_and_minutes.second, 0);
}
