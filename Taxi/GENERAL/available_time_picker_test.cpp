#include "available_time_picker.hpp"
#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

namespace overlord_catalog::models::catalog {

TEST(AvailableTimePicker, Default) {
  auto tp = ::utils::datetime::Stringtime("2019-12-16 20:00:00",
                                          "Europe/Moscow", "%Y-%m-%d %H:%M:%S");
  utils::datetime::MockNowSet(tp);
  cctz::time_zone tz;
  load_time_zone("Europe/Moscow", &tz);
  auto result = GetAvailableTimePicker(tz);
  EXPECT_EQ(result.size(), 2);
  auto today = result[0];
  EXPECT_EQ(today.size(), 7);
  EXPECT_EQ(today[0], cctz::civil_minute(2019, 12, 16, 20, 30));
  EXPECT_EQ(today[6], cctz::civil_minute(2019, 12, 16, 23, 30));

  auto tomorrow = result[1];
  EXPECT_EQ(tomorrow.size(), 34);
  EXPECT_EQ(tomorrow[0], cctz::civil_minute(2019, 12, 17, 0, 0));
  EXPECT_EQ(tomorrow[1], cctz::civil_minute(2019, 12, 17, 7, 30));
}

TEST(AvailableTimePicker, AvaialbleFromMidnight) {
  auto tp = ::utils::datetime::Stringtime("2019-12-16 23:35:00",
                                          "Europe/Moscow", "%Y-%m-%d %H:%M:%S");
  utils::datetime::MockNowSet(tp);
  cctz::time_zone tz;
  load_time_zone("Europe/Moscow", &tz);
  auto result = GetAvailableTimePicker(tz);
  EXPECT_EQ(result.size(), 2);
  auto today = result[0];
  EXPECT_EQ(today.size(), 0);

  auto tomorrow = result[1];
  EXPECT_EQ(tomorrow.size(), 34);
  EXPECT_EQ(tomorrow[0], cctz::civil_minute(2019, 12, 17, 0, 0));
  EXPECT_EQ(tomorrow[1], cctz::civil_minute(2019, 12, 17, 7, 30));
}

TEST(AvailableTimePicker, AvaialbleFromNextMorning) {
  auto tp = ::utils::datetime::Stringtime("2019-12-16 23:55:00",
                                          "Europe/Moscow", "%Y-%m-%d %H:%M:%S");
  utils::datetime::MockNowSet(tp);
  cctz::time_zone tz;
  load_time_zone("Europe/Moscow", &tz);
  auto result = GetAvailableTimePicker(tz);
  EXPECT_EQ(result.size(), 2);
  auto today = result[0];
  EXPECT_EQ(today.size(), 0);

  auto tomorrow = result[1];
  EXPECT_EQ(tomorrow.size(), 33);
  EXPECT_EQ(tomorrow[0], cctz::civil_minute(2019, 12, 17, 7, 30));
}

TEST(AvailableTimePicker, AvaialbleWholeDay) {
  auto tp = ::utils::datetime::Stringtime("2019-12-16 00:55:00",
                                          "Europe/Moscow", "%Y-%m-%d %H:%M:%S");
  utils::datetime::MockNowSet(tp);
  cctz::time_zone tz;
  load_time_zone("Europe/Moscow", &tz);
  auto result = GetAvailableTimePicker(tz);
  EXPECT_EQ(result.size(), 2);
  auto today = result[0];
  EXPECT_EQ(today.size(), 33);
  EXPECT_EQ(today[0], cctz::civil_minute(2019, 12, 16, 7, 30));

  auto tomorrow = result[1];
  EXPECT_EQ(tomorrow.size(), 34);
  EXPECT_EQ(tomorrow[0], cctz::civil_minute(2019, 12, 17, 0, 0));
}

}  // namespace overlord_catalog::models::catalog
