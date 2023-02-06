#include "datetime.hpp"
#include <userver/utest/utest.hpp>

namespace grocery_depots::datetime {

TEST(Datetime, StartOfDay) {
  auto tp = cctz::civil_minute(2019, 12, 16, 21, 21);
  EXPECT_EQ(StartOfDay(tp), cctz::civil_minute(2019, 12, 16, 0, 0));
}

TEST(Datetime, AddDays) {
  auto tp = cctz::civil_minute(2019, 12, 16, 21, 21);
  EXPECT_EQ(AddDays(tp, 1), cctz::civil_minute(2019, 12, 17, 21, 21));
}

TEST(Datetime, AddDaysMonthSplit) {
  auto tp = cctz::civil_minute(2019, 12, 31, 21, 21);
  EXPECT_EQ(AddDays(tp, 1), cctz::civil_minute(2020, 1, 1, 21, 21));
}

TEST(Datetime, RoundUpMinutes) {
  auto tp = cctz::civil_minute(2019, 12, 31, 21, 21);
  EXPECT_EQ(RoundUpMinutes(tp, 30), cctz::civil_minute(2019, 12, 31, 21, 30));
}

}  // namespace grocery_depots::datetime
