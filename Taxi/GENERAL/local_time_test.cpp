#include <userver/utest/utest.hpp>

#include <string>

#include <models/time_range.hpp>

namespace models {

bool operator==(const models::LocalTime& a, const models::LocalTime& b) {
  return a.hours == b.hours && a.minutes == b.minutes;
}

}  // namespace models

TEST(TestLocalTimes, TestGoodLocalTimes) {
  models::LocalTime loc_time("12");
  ASSERT_EQ(loc_time.hours, 12);
  ASSERT_EQ(loc_time.minutes, 0);

  loc_time = models::LocalTime{"7:22"};

  ASSERT_EQ(loc_time.hours, 7);
  ASSERT_EQ(loc_time.minutes, 22);
}

TEST(TestLocalTimes, TestBadLocalTimes) {
  ASSERT_ANY_THROW(models::LocalTime(""));
  ASSERT_ANY_THROW(models::LocalTime("12:"));
  ASSERT_ANY_THROW(models::LocalTime(":12"));
  ASSERT_ANY_THROW(models::LocalTime("12test"));
  ASSERT_ANY_THROW(models::LocalTime("12:3test"));
  ASSERT_ANY_THROW(models::LocalTime("12:73"));
  ASSERT_ANY_THROW(models::LocalTime("12:-15"));
  ASSERT_ANY_THROW(models::LocalTime("-12"));
  ASSERT_ANY_THROW(models::LocalTime("64:32"));
}

TEST(TestTimeRanges, TestGoodTimeRanges) {
  models::TimeRange range("12");
  ASSERT_EQ(range.from, models::LocalTime("12"));
  ASSERT_EQ(range.to, models::LocalTime("12"));

  range = models::TimeRange{"7-13"};
  ASSERT_EQ(range.from, models::LocalTime("7"));
  ASSERT_EQ(range.to, models::LocalTime("13"));

  range = models::TimeRange{"7:00-18"};
  ASSERT_EQ(range.from, models::LocalTime("7:00"));
  ASSERT_EQ(range.to, models::LocalTime("18"));

  range = models::TimeRange{"18:43-0:12"};
  ASSERT_EQ(range.from, models::LocalTime("18:43"));
  ASSERT_EQ(range.to, models::LocalTime("0:12"));
}

TEST(TestTimeRanges, TestBadTimeRanges) {
  ASSERT_ANY_THROW(models::TimeRange(""));
  ASSERT_ANY_THROW(models::TimeRange("12-13-15"));
  ASSERT_ANY_THROW(models::TimeRange("7:00-"));
  ASSERT_ANY_THROW(models::TimeRange("-7:00"));
}
