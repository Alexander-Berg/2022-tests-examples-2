#include <gtest/gtest.h>

#include "route.hpp"

TEST(CalcDueTimeTest, SecondsTest) {
  const int32_t urgency_sec = 180;
  const int32_t threshold_sec = 30;
  const std::chrono::system_clock::time_point now =
      std::chrono::system_clock::from_time_t(1507569206);

  const time_t due =
      dispatch::kit::CalcDueTime(std::chrono::seconds{urgency_sec},
                                 std::chrono::seconds{threshold_sec}, now);

  EXPECT_EQ(due % threshold_sec, 0);
  EXPECT_EQ(due, 1507569390);
}

TEST(CalcDueTimeTest, MinutesTest) {
  const int32_t urgency_sec = 180;
  const int32_t threshold_min = 2;
  const std::chrono::system_clock::time_point now =
      std::chrono::system_clock::from_time_t(1507569206);

  const time_t due =
      dispatch::kit::CalcDueTime(std::chrono::seconds{urgency_sec},
                                 std::chrono::minutes{threshold_min}, now);

  EXPECT_EQ(due % (threshold_min * 60), 0);
  EXPECT_EQ(due, 1507569480);
}
