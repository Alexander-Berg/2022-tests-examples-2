#include "views/umlaas-dispatch/v1/preorder_available/post/config.hpp"

#include <gtest/gtest.h>

#include <fstream>

namespace handlers::umlaas_dispatch_v1_preorder_available::post {

bool CheckWithinDaylyRange(const std::string& begin_str,
                           const std::string& end_str,
                           const std::string& moment_str) {
  static const std::string kDailyTimeFormat = "%H:%M:%S";

  auto begin = utils::datetime::Stringtime(begin_str, "UTC", kDailyTimeFormat);
  auto end = utils::datetime::Stringtime(end_str, "UTC", kDailyTimeFormat);
  auto moment = utils::datetime::Stringtime(moment_str);
  return IsWithinDailyRange(TimePoint2DayMoment(begin),
                            TimePoint2DayMoment(end),
                            TimePoint2DayMoment(moment));
}

TEST(PreorderAvailable, DailyRange) {
  // same day
  ASSERT_TRUE(CheckWithinDaylyRange("10:00:00", "20:00:00",
                                    "2019-04-26T15:21:00.66744+0000"));
  ASSERT_FALSE(CheckWithinDaylyRange("10:00:00", "20:00:00",
                                     "2019-04-26T01:21:00.66744+0000"));
  ASSERT_FALSE(CheckWithinDaylyRange("10:00:00", "20:00:00",
                                     "2019-04-26T22:21:00.66744+0000"));

  // two days
  ASSERT_TRUE(CheckWithinDaylyRange("20:00:00", "04:00:00",
                                    "2019-04-26T21:21:00.66744+0000"));
  ASSERT_TRUE(CheckWithinDaylyRange("20:00:00", "04:00:00",
                                    "2019-04-26T20:21:00.66744+0000"));
  ASSERT_TRUE(CheckWithinDaylyRange("20:00:00", "04:00:00",
                                    "2019-04-26T03:21:00.66744+0000"));
  ASSERT_FALSE(CheckWithinDaylyRange("20:00:00", "04:00:00",
                                     "2019-04-26T18:21:00.66744+0000"));
  ASSERT_TRUE(CheckWithinDaylyRange("20:00:00", "04:00:00",
                                    "2019-04-26T04:00:00.66744+0000"));
}

}  // namespace handlers::umlaas_dispatch_v1_preorder_available::post
