#include "common/datetime.hpp"
#include <gtest/gtest.h>

TEST(MLCommon, ParseDatetime) {
  std::string datetime("2005-08-09T18:31:42+0300");
  auto civil_second = ml::common::ParseDatetime(datetime);

  ASSERT_EQ(18, civil_second.hour());
  ASSERT_EQ(9, civil_second.day());
}

TEST(MLCommon, ParseTimezone) {
  std::string datetime("2005-08-09T18:31:42+0300");
  auto tz = ml::common::GetTimezone(datetime);
  auto offset = tz.lookup(std::chrono::system_clock::now()).offset;

  ASSERT_EQ(10800, offset);
}

TEST(MLCommon, ParseTimezoneError) {
  ASSERT_THROW(ml::common::GetTimezone(""), std::runtime_error);
}

TEST(MLCommon, GetLocalTime) {
  cctz::time_zone tz;
  cctz::load_time_zone("Europe/Moscow", &tz);
  const auto& local_time =
      ml::common::GetLocalTime("2018-02-22T23:37:00-0300", tz);
  ASSERT_EQ(local_time.hour(), 5);
  ASSERT_EQ(local_time.day(), 23);
}
