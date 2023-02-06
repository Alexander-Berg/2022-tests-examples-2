#include <vector>

#include <cctz/civil_time.h>
#include <cctz/time_zone.h>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <common/validators/subscription_time/impl/detail.hpp>
#include <utils/utils.hpp>

namespace subscription_time = common::validators::subscription_time::impl;
namespace config = taxi_config::driver_mode_rules_subscription_time_v2;

std::chrono::system_clock::time_point CreateTime(
    int y, int m = 1, int d = 1, int hh = 0, int mm = 0,
    const cctz::time_zone& tz = cctz::utc_time_zone()) {
  return cctz::convert(cctz::civil_minute(y, m, d, hh, mm), tz);
}

const std::string kConfigValueRaw = R"(
{
  "time_zone": "utc",
  "tariff_zones_settings": {
    "__default__": {
      "subscription_schedule": []
    },
    "moscow": {
      "subscription_schedule": [
        {
          "start": {
            "time": "06:00",
            "weekday": "mon"
          },
          "stop": {
            "time": "08:00",
            "weekday": "mon"
          }
        },
        {
          "start": {
            "time": "23:30",
            "weekday": "mon"
          },
          "stop": {
            "time": "05:50",
            "weekday": "wed"
          }
        }
      ]
    },
    "spb": {
      "subscription_schedule": [
        {
          "start": {
            "time": "20:00",
            "weekday": "mon"
          },
          "stop": {
            "time": "04:00",
            "weekday": "mon"
          }
        }
      ]
    },
    "samara": {
      "subscription_schedule": [
        {
          "start": {
            "time": "20:00",
            "weekday": "mon"
          },
          "stop": {
            "time": "20:00",
            "weekday": "mon"
          }
        }
      ]
    }
  }
}
)";

TEST(SubscriptionTime, TestTimeTransformations) {
  // Current time in 06-08 restriction range
  utils::datetime::MockNowSet(
      CreateTime(2020, 8, 3, 10, 20, utils::GetTimezone("Europe/Moscow")));

  EXPECT_EQ(utils::datetime::Timestring(utils::datetime::Now()),
            "2020-08-03T07:20:00+0000");

  cctz::civil_minute current_time =
      subscription_time::GetCurrentTimeInTimezone(utils::GetTimezone("utc"));

  EXPECT_EQ(current_time.year(), 2020);
  EXPECT_EQ(current_time.month(), 8);
  EXPECT_EQ(current_time.day(), 3);
  EXPECT_EQ(current_time.hour(), 7);
  EXPECT_EQ(current_time.minute(), 20);

  const cctz::civil_day current_day{current_time};
  const cctz::civil_minute start_of_day{current_day};

  EXPECT_EQ(start_of_day.year(), 2020);
  EXPECT_EQ(start_of_day.month(), 8);
  EXPECT_EQ(start_of_day.day(), 3);
  EXPECT_EQ(start_of_day.hour(), 0);
  EXPECT_EQ(start_of_day.minute(), 0);

  const unsigned int minute_of_day = current_time - start_of_day;
  EXPECT_EQ(minute_of_day, 440);

  const config::SubscriptionTimeRange time_range{
      {"06:00", config::WeekDay::kMon}, {"08:00", config::WeekDay::kMon}};

  const auto start_offset_minutes =
      utils::datetime::ParseDayTime(time_range.start.time) / 60;
  const auto stop_offset_minutes =
      utils::datetime::ParseDayTime(time_range.stop.time) / 60;

  EXPECT_EQ(start_offset_minutes, 360);
  EXPECT_EQ(stop_offset_minutes, 480);
}

TEST(SubscriptionTime, TestOneDayRange) {
  formats::json::Value config_value_json =
      formats::json::FromString(kConfigValueRaw);

  config::ModeSubscriptionTimeSettings validation_config =
      config::Parse(config_value_json,
                    formats::parse::To<config::ModeSubscriptionTimeSettings>());

  // Current time in 06-08 restriction range
  utils::datetime::MockNowSet(
      CreateTime(2020, 8, 3, 10, 20, utils::GetTimezone("Europe/Moscow")));

  EXPECT_EQ(utils::datetime::Timestring(utils::datetime::Now()),
            "2020-08-03T07:20:00+0000");

  cctz::civil_minute current_time =
      subscription_time::GetCurrentTimeInTimezone(utils::GetTimezone("utc"));

  EXPECT_EQ(current_time.year(), 2020);
  EXPECT_EQ(current_time.month(), 8);
  EXPECT_EQ(current_time.day(), 3);
  EXPECT_EQ(current_time.hour(), 7);
  EXPECT_EQ(current_time.minute(), 20);

  auto check_result = subscription_time::CheckSubscriptionTime(
      current_time,
      validation_config.tariff_zones_settings["moscow"].subscription_schedule);

  EXPECT_TRUE(check_result.is_subscription_available);
  EXPECT_TRUE(check_result.subscription_stop_time.has_value());
  EXPECT_FALSE(check_result.next_available_start_time.has_value());
  EXPECT_EQ(check_result.subscription_stop_time->day(), 3);
  EXPECT_EQ(check_result.subscription_stop_time->hour(), 8);
  EXPECT_EQ(check_result.subscription_stop_time->minute(), 0);

  // Current time not in restriction range
  utils::datetime::MockNowSet(
      CreateTime(2020, 8, 3, 11, 20, utils::GetTimezone("Europe/Moscow")));

  EXPECT_EQ(utils::datetime::Timestring(utils::datetime::Now()),
            "2020-08-03T08:20:00+0000");

  current_time =
      subscription_time::GetCurrentTimeInTimezone(utils::GetTimezone("utc"));

  check_result = subscription_time::CheckSubscriptionTime(
      current_time,
      validation_config.tariff_zones_settings["moscow"].subscription_schedule);

  EXPECT_FALSE(check_result.is_subscription_available);
  EXPECT_FALSE(check_result.subscription_stop_time.has_value());
  EXPECT_TRUE(check_result.next_available_start_time.has_value());
  EXPECT_EQ(check_result.next_available_start_time->day(), 3);
  EXPECT_EQ(check_result.next_available_start_time->hour(), 23);
  EXPECT_EQ(check_result.next_available_start_time->minute(), 30);
}

TEST(SubscriptionTime, TestMultiDayRange) {
  formats::json::Value config_value_json =
      formats::json::FromString(kConfigValueRaw);

  config::ModeSubscriptionTimeSettings validation_config =
      config::Parse(config_value_json,
                    formats::parse::To<config::ModeSubscriptionTimeSettings>());

  // Current time in 23 (mon) - 05 (wed) restriction range
  utils::datetime::MockNowSet(
      CreateTime(2020, 8, 4, 2, 40, utils::GetTimezone("Europe/Moscow")));

  EXPECT_EQ(utils::datetime::Timestring(utils::datetime::Now()),
            "2020-08-03T23:40:00+0000");

  cctz::civil_minute current_time =
      subscription_time::GetCurrentTimeInTimezone(utils::GetTimezone("utc"));

  EXPECT_EQ(current_time.year(), 2020);
  EXPECT_EQ(current_time.month(), 8);
  EXPECT_EQ(current_time.day(), 3);
  EXPECT_EQ(current_time.hour(), 23);
  EXPECT_EQ(current_time.minute(), 40);

  auto check_result = subscription_time::CheckSubscriptionTime(
      current_time,
      validation_config.tariff_zones_settings["moscow"].subscription_schedule);

  EXPECT_TRUE(check_result.is_subscription_available);
  EXPECT_TRUE(check_result.subscription_stop_time.has_value());
  EXPECT_EQ(check_result.subscription_stop_time->day(), 5);
  EXPECT_EQ(check_result.subscription_stop_time->hour(), 5);
  EXPECT_EQ(check_result.subscription_stop_time->minute(), 50);

  // Next utc day
  utils::datetime::MockNowSet(
      CreateTime(2020, 8, 4, 10, 20, utils::GetTimezone("Europe/Moscow")));

  current_time =
      subscription_time::GetCurrentTimeInTimezone(utils::GetTimezone("utc"));

  check_result = subscription_time::CheckSubscriptionTime(
      current_time,
      validation_config.tariff_zones_settings["moscow"].subscription_schedule);

  EXPECT_TRUE(check_result.is_subscription_available);
  EXPECT_TRUE(check_result.subscription_stop_time.has_value());
  EXPECT_EQ(check_result.subscription_stop_time->day(), 5);
  EXPECT_EQ(check_result.subscription_stop_time->hour(), 5);
  EXPECT_EQ(check_result.subscription_stop_time->minute(), 50);
}

TEST(SubscriptionTime, TestCrossWeekSchedule) {
  formats::json::Value config_value_json =
      formats::json::FromString(kConfigValueRaw);

  config::ModeSubscriptionTimeSettings validation_config =
      config::Parse(config_value_json,
                    formats::parse::To<config::ModeSubscriptionTimeSettings>());

  // Tuesday - test start time check
  utils::datetime::MockNowSet(
      CreateTime(2020, 8, 4, 10, 0, utils::GetTimezone("Europe/Moscow")));

  EXPECT_EQ(utils::datetime::Timestring(utils::datetime::Now()),
            "2020-08-04T07:00:00+0000");

  cctz::civil_minute current_time =
      subscription_time::GetCurrentTimeInTimezone(utils::GetTimezone("utc"));

  auto check_result = subscription_time::CheckSubscriptionTime(
      current_time,
      validation_config.tariff_zones_settings["spb"].subscription_schedule);

  EXPECT_TRUE(check_result.is_subscription_available);
  EXPECT_TRUE(check_result.subscription_stop_time.has_value());
  EXPECT_EQ(check_result.subscription_stop_time->day(), 10);
  EXPECT_EQ(check_result.subscription_stop_time->hour(), 4);
  EXPECT_EQ(check_result.subscription_stop_time->minute(), 0);

  // Monday morning - test stop time check
  utils::datetime::MockNowSet(
      CreateTime(2020, 8, 3, 4, 0, utils::GetTimezone("Europe/Moscow")));

  current_time =
      subscription_time::GetCurrentTimeInTimezone(utils::GetTimezone("utc"));

  check_result = subscription_time::CheckSubscriptionTime(
      current_time,
      validation_config.tariff_zones_settings["spb"].subscription_schedule);

  EXPECT_TRUE(check_result.is_subscription_available);
  EXPECT_TRUE(check_result.subscription_stop_time.has_value());
  EXPECT_EQ(check_result.subscription_stop_time->day(), 3);
  EXPECT_EQ(check_result.subscription_stop_time->hour(), 4);
  EXPECT_EQ(check_result.subscription_stop_time->minute(), 0);

  // Not in range
  utils::datetime::MockNowSet(
      CreateTime(2020, 8, 3, 7, 0, utils::GetTimezone("Europe/Moscow")));

  current_time =
      subscription_time::GetCurrentTimeInTimezone(utils::GetTimezone("utc"));

  check_result = subscription_time::CheckSubscriptionTime(
      current_time,
      validation_config.tariff_zones_settings["spb"].subscription_schedule);

  EXPECT_FALSE(check_result.is_subscription_available);
  EXPECT_FALSE(check_result.subscription_stop_time.has_value());
}

TEST(SubscriptionTime, TestFullWeekAllowed) {
  formats::json::Value config_value_json =
      formats::json::FromString(kConfigValueRaw);

  config::ModeSubscriptionTimeSettings validation_config =
      config::Parse(config_value_json,
                    formats::parse::To<config::ModeSubscriptionTimeSettings>());

  // Random day
  utils::datetime::MockNowSet(
      CreateTime(2020, 8, 4, 10, 0, utils::GetTimezone("Europe/Moscow")));

  cctz::civil_minute current_time =
      subscription_time::GetCurrentTimeInTimezone(utils::GetTimezone("utc"));

  auto check_result = subscription_time::CheckSubscriptionTime(
      current_time,
      validation_config.tariff_zones_settings["samara"].subscription_schedule);

  EXPECT_TRUE(check_result.is_subscription_available);
  EXPECT_FALSE(check_result.subscription_stop_time.has_value());

  // Range border - just in case
  utils::datetime::MockNowSet(
      CreateTime(2020, 8, 3, 23, 0, utils::GetTimezone("Europe/Moscow")));

  current_time =
      subscription_time::GetCurrentTimeInTimezone(utils::GetTimezone("utc"));

  check_result = subscription_time::CheckSubscriptionTime(
      current_time,
      validation_config.tariff_zones_settings["samara"].subscription_schedule);

  EXPECT_TRUE(check_result.is_subscription_available);
  EXPECT_FALSE(check_result.subscription_stop_time.has_value());
}

TEST(SubscriptionTime, TestBuildSchedule) {
  using TimeOfDay =
      common::validators::subscription_time::DateSchedule::TimeOfDay;

  // Random wednesday
  utils::datetime::MockNowSet(
      CreateTime(2020, 8, 5, 10, 0, utils::GetTimezone("UTC")));

  cctz::civil_minute current_time =
      subscription_time::GetCurrentTimeInTimezone(utils::GetTimezone("utc"));
  EXPECT_EQ(current_time.hour(), 10);

  cctz::civil_minute local_time = subscription_time::GetCurrentTimeInTimezone(
      utils::GetTimezone("Europe/Samara"));
  EXPECT_EQ(local_time.hour(), 14);

  config::WeekSchedule schedule{
      {{"08:00", config::WeekDay::kTue}, {"10:00", config::WeekDay::kThu}},
      {{"15:00", config::WeekDay::kThu}, {"16:00", config::WeekDay::kThu}},
      {{"20:00", config::WeekDay::kThu}, {"10:00", config::WeekDay::kFri}},
      {{"14:00", config::WeekDay::kFri}, {"18:00", config::WeekDay::kFri}}};

  auto result = subscription_time::GetSubscriptionSchedule(
      schedule, utils::GetTimezone("Europe/Samara"), utils::GetTimezone("UTC"));

  EXPECT_EQ(result.size(), 6);

  // wed - today
  EXPECT_EQ(result[0].date, cctz::civil_day(2020, 8, 5));
  EXPECT_EQ(result[0].time_range.start, TimeOfDay{std::chrono::hours{0}});
  EXPECT_EQ(result[0].time_range.stop, TimeOfDay{std::chrono::hours{0}});

  // thu
  EXPECT_EQ(result[1].date, cctz::civil_day(2020, 8, 6));
  EXPECT_EQ(result[1].time_range.start, TimeOfDay{std::chrono::hours{0}});
  EXPECT_EQ(result[1].time_range.stop, TimeOfDay{std::chrono::hours{14}});

  EXPECT_EQ(result[2].date, cctz::civil_day(2020, 8, 6));
  EXPECT_EQ(result[2].time_range.start, TimeOfDay{std::chrono::hours{19}});
  EXPECT_EQ(result[2].time_range.stop, TimeOfDay{std::chrono::hours{20}});

  // fri
  EXPECT_EQ(result[3].date, cctz::civil_day(2020, 8, 7));
  EXPECT_EQ(result[3].time_range.start, TimeOfDay{std::chrono::hours{0}});
  EXPECT_EQ(result[3].time_range.stop, TimeOfDay{std::chrono::hours{14}});

  EXPECT_EQ(result[4].date, cctz::civil_day(2020, 8, 7));
  EXPECT_EQ(result[4].time_range.start, TimeOfDay{std::chrono::hours{18}});
  EXPECT_EQ(result[4].time_range.stop, TimeOfDay{std::chrono::hours{22}});

  // tue
  EXPECT_EQ(result[5].date, cctz::civil_day(2020, 8, 11));
  EXPECT_EQ(result[5].time_range.start, TimeOfDay{std::chrono::hours{12}});
  EXPECT_EQ(result[5].time_range.stop, TimeOfDay{std::chrono::hours{0}});

  // Move current day to friday
  utils::datetime::MockNowSet(
      CreateTime(2020, 8, 7, 10, 0, utils::GetTimezone("UTC")));

  result = subscription_time::GetSubscriptionSchedule(
      schedule, utils::GetTimezone("Europe/Samara"), utils::GetTimezone("UTC"));

  EXPECT_EQ(result.size(), 6);

  // fri
  EXPECT_EQ(result[0].date, cctz::civil_day(2020, 8, 7));
  EXPECT_EQ(result[0].time_range.start, TimeOfDay{std::chrono::hours{18}});
  EXPECT_EQ(result[0].time_range.stop, TimeOfDay{std::chrono::hours{22}});

  // tue
  EXPECT_EQ(result[1].date, cctz::civil_day(2020, 8, 11));
  EXPECT_EQ(result[1].time_range.start, TimeOfDay{std::chrono::hours{12}});
  EXPECT_EQ(result[1].time_range.stop, TimeOfDay{std::chrono::hours{0}});

  // wed
  EXPECT_EQ(result[2].date, cctz::civil_day(2020, 8, 12));
  EXPECT_EQ(result[2].time_range.start, TimeOfDay{std::chrono::hours{0}});
  EXPECT_EQ(result[2].time_range.stop, TimeOfDay{std::chrono::hours{0}});

  // thu
  EXPECT_EQ(result[3].date, cctz::civil_day(2020, 8, 13));
  EXPECT_EQ(result[3].time_range.start, TimeOfDay{std::chrono::hours{0}});
  EXPECT_EQ(result[3].time_range.stop, TimeOfDay{std::chrono::hours{14}});

  EXPECT_EQ(result[4].date, cctz::civil_day(2020, 8, 13));
  EXPECT_EQ(result[4].time_range.start, TimeOfDay{std::chrono::hours{19}});
  EXPECT_EQ(result[4].time_range.stop, TimeOfDay{std::chrono::hours{20}});

  // fri
  EXPECT_EQ(result[5].date, cctz::civil_day(2020, 8, 14));
  EXPECT_EQ(result[5].time_range.start, TimeOfDay{std::chrono::hours{0}});
  EXPECT_EQ(result[5].time_range.stop, TimeOfDay{std::chrono::hours{14}});
}
