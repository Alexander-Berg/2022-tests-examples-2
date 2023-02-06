#include <userver/utest/utest.hpp>
#include <userver/utils/datetime/date.hpp>

#include <cctz/civil_time.h>

#include <utils/time_range.hpp>

TEST(GoalSummaryUtils, ToCivilDay) {
  auto date = utils::datetime::DateFromRFC3339String("2021-11-23");
  EXPECT_EQ(utils::ToCivilDay(date), cctz::civil_day(2021, 11, 23));
}
