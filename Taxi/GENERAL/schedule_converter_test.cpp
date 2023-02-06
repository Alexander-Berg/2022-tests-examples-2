#include <gtest/gtest.h>

#include "schedule_converter.hpp"

#include <userver/utils/datetime.hpp>

#include <schedule/schedule.hpp>

#include <models/place_promo.hpp>

const std::string ARAGUAINA_TZ = "America/Araguaina";
const std::string NORONHA_TZ = "America/Noronha";
const std::string CAPE_VERDE_TZ = "Atlantic/Cape_Verde";
const std::string LAGOS_TZ = "Africa/Lagos";
const std::string TANZANIA_TZ = "Africa/Dar_es_Salaam";
const std::string MOSCOW_TZ = "Europe/Moscow";
const std::string MAURITIUS_TZ = "Indian/Mauritius";
const std::string EKB_TZ = "Asia/Yekaterinburg";

std::chrono::system_clock::time_point operator"" _st(
    const char* const string_time, const size_t size) {
  return utils::datetime::Stringtime(std::string(string_time, size));
}

TEST(Convert, Null) {
  const auto schedule_json = formats::json::FromString(R"(
  {
    "timezone": "LOCAL",
    "intervals": [
      {
        "exclude": false,
        "day": [1,2,3,4,5,6,7]
      }
    ]
  }
  )");

  auto schedule = schedule_json.As<schedule::Schedule>();

  auto converted_null_schedule =
      eats_restapp_promo::utils::ConvertScheduleToSchedule(std::nullopt);

  const auto now = utils::datetime::Now();

  EXPECT_EQ(converted_null_schedule.size(), 1);

  ASSERT_TRUE(converted_null_schedule.front().Match(now));
  ASSERT_TRUE(converted_null_schedule.front().Match(now, LAGOS_TZ));
  ASSERT_TRUE(converted_null_schedule.front().Match(now, TANZANIA_TZ));
  ASSERT_TRUE(converted_null_schedule.front().Match(now, MOSCOW_TZ));
  ASSERT_TRUE(converted_null_schedule.front().Match(now, MAURITIUS_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindNext(
                "2019-11-19T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindNext(
                "2019-11-20T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-21T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindNext(
                "2019-11-21T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-22T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindNext(
                "2019-11-22T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-23T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindNext(
                "2019-11-23T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-24T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindNext(
                "2019-11-24T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-25T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindNext(
                "2019-11-25T20:34:13.000+0000"_st));

  // some crazy cases. UTC is enough.
  ASSERT_EQ(schedule.FindNext("2222-11-17T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindNext(
                "2222-11-17T23:59:59.999999999+0000"_st));
  ASSERT_EQ(schedule.FindNext("2222-11-18T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindNext(
                "2222-11-18T23:59:59.999999999+0000"_st));
  ASSERT_EQ(schedule.FindNext("2222-11-19T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindNext(
                "2222-11-19T23:59:59.999999999+0000"_st));
  ASSERT_EQ(schedule.FindNext("2222-11-20T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindNext(
                "2222-11-20T23:59:59.999999999+0000"_st));
  ASSERT_EQ(schedule.FindNext("2222-11-21T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindNext(
                "2222-11-21T23:59:59.999999999+0000"_st));
  ASSERT_EQ(schedule.FindNext("2222-11-22T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindNext(
                "2222-11-22T23:59:59.999999999+0000"_st));
  ASSERT_EQ(schedule.FindNext("2222-11-23T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindNext(
                "2222-11-23T23:59:59.999999999+0000"_st));

  ASSERT_EQ(schedule.FindPrev("2019-11-19T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2019-11-19T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-20T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2019-11-20T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-21T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2019-11-21T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-22T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2019-11-22T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-23T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2019-11-23T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-24T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2019-11-24T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-25T20:34:13.000+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2019-11-25T20:34:13.000+0000"_st));

  // some crazy cases. UTC is enough.
  ASSERT_EQ(schedule.FindPrev("2222-11-17T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2222-11-17T23:59:59.999999999+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2222-11-18T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2222-11-18T23:59:59.999999999+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2222-11-19T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2222-11-19T23:59:59.999999999+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2222-11-20T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2222-11-20T23:59:59.999999999+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2222-11-21T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2222-11-21T23:59:59.999999999+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2222-11-22T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2222-11-22T23:59:59.999999999+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2222-11-23T23:59:59.999999999+0000"_st),
            converted_null_schedule.front().FindPrev(
                "2222-11-23T23:59:59.999999999+0000"_st));
}

TEST(Convert, WithGroup) {
  const auto promo_schedules =
      std::vector<eats_restapp_promo::models::PromoSchedule>{
          {1, 720, 780},   {3, 720, 780},   {5, 720, 780},
          {2, 1020, 1080}, {4, 1020, 1080}, {6, 1020, 1080}};
  auto converted_schedules =
      eats_restapp_promo::utils::ConvertScheduleToSchedule(promo_schedules);

  EXPECT_EQ(converted_schedules.size(), 2);

  const auto time_point_monday = "2021-10-18T12:30:00.000+0300"_st;
  const auto time_point_tuesday = "2021-10-19T17:30:00.000+0300"_st;

  ASSERT_FALSE(converted_schedules[0].Match(time_point_monday));  // UTC
  ASSERT_FALSE(converted_schedules[0].Match(time_point_monday, LAGOS_TZ));
  ASSERT_TRUE(converted_schedules[0].Match(time_point_monday, TANZANIA_TZ));
  ASSERT_TRUE(converted_schedules[0].Match(time_point_monday, MOSCOW_TZ));
  ASSERT_FALSE(converted_schedules[0].Match(time_point_monday, MAURITIUS_TZ));

  ASSERT_FALSE(converted_schedules[0].Match(time_point_tuesday));
  ASSERT_FALSE(converted_schedules[0].Match(time_point_tuesday, LAGOS_TZ));
  ASSERT_FALSE(converted_schedules[0].Match(time_point_tuesday, TANZANIA_TZ));
  ASSERT_FALSE(converted_schedules[0].Match(time_point_tuesday, MOSCOW_TZ));
  ASSERT_FALSE(converted_schedules[0].Match(time_point_tuesday, MAURITIUS_TZ));

  ASSERT_FALSE(converted_schedules[1].Match(time_point_tuesday));  // UTC
  ASSERT_FALSE(converted_schedules[1].Match(time_point_tuesday, LAGOS_TZ));
  ASSERT_TRUE(converted_schedules[1].Match(time_point_tuesday, TANZANIA_TZ));
  ASSERT_TRUE(converted_schedules[1].Match(time_point_tuesday, MOSCOW_TZ));
  ASSERT_FALSE(converted_schedules[1].Match(time_point_tuesday, MAURITIUS_TZ));

  ASSERT_FALSE(converted_schedules[1].Match(time_point_monday));
  ASSERT_FALSE(converted_schedules[1].Match(time_point_monday, LAGOS_TZ));
  ASSERT_FALSE(converted_schedules[1].Match(time_point_monday, TANZANIA_TZ));
  ASSERT_FALSE(converted_schedules[1].Match(time_point_monday, MOSCOW_TZ));
  ASSERT_FALSE(converted_schedules[1].Match(time_point_monday, MAURITIUS_TZ));
}

TEST(Convert, WithoutGroup) {
  const auto schedule_json1 = formats::json::FromString(R"(
  {
    "timezone": "LOCAL",
    "intervals": [
      {
        "exclude": false,
        "day": [3]
      },
      {
        "exclude": false,
        "daytime": [
          {
            "from": "12:00:00",
            "to": "13:00:00"
          }
        ]
      }
    ]
  }
  )");

  const auto schedule_json2 = formats::json::FromString(R"(
  {
    "timezone": "LOCAL",
    "intervals": [
      {
        "exclude": false,
        "day": [4]
      },
      {
        "exclude": false,
        "daytime": [
          {
            "from": "17:00:00",
            "to": "18:00:00"
          }
        ]
      }
    ]
  }
  )");

  auto schedules =
      std::vector<schedule::Schedule>{schedule_json1.As<schedule::Schedule>(),
                                      schedule_json2.As<schedule::Schedule>()};

  const auto promo_schedules =
      std::vector<eats_restapp_promo::models::PromoSchedule>{{3, 720, 780},
                                                             {4, 1020, 1080}};
  auto converted_schedules =
      eats_restapp_promo::utils::ConvertScheduleToSchedule(promo_schedules);

  EXPECT_EQ(converted_schedules.size(), 2);

  const auto time_point_wednesday = "2021-10-20T12:30:00.000+0300"_st;
  const auto time_point_thursday = "2021-10-21T17:30:00.000+0300"_st;

  ASSERT_FALSE(converted_schedules[0].Match(time_point_wednesday));  // UTC
  ASSERT_FALSE(converted_schedules[0].Match(time_point_wednesday, LAGOS_TZ));
  ASSERT_TRUE(converted_schedules[0].Match(time_point_wednesday, TANZANIA_TZ));
  ASSERT_TRUE(converted_schedules[0].Match(time_point_wednesday, MOSCOW_TZ));
  ASSERT_FALSE(
      converted_schedules[0].Match(time_point_wednesday, MAURITIUS_TZ));

  ASSERT_FALSE(converted_schedules[0].Match(time_point_thursday));
  ASSERT_FALSE(converted_schedules[0].Match(time_point_thursday, LAGOS_TZ));
  ASSERT_FALSE(converted_schedules[0].Match(time_point_thursday, TANZANIA_TZ));
  ASSERT_FALSE(converted_schedules[0].Match(time_point_thursday, MOSCOW_TZ));
  ASSERT_FALSE(converted_schedules[0].Match(time_point_thursday, MAURITIUS_TZ));

  ASSERT_FALSE(converted_schedules[1].Match(time_point_thursday));  // UTC
  ASSERT_FALSE(converted_schedules[1].Match(time_point_thursday, LAGOS_TZ));
  ASSERT_TRUE(converted_schedules[1].Match(time_point_thursday, TANZANIA_TZ));
  ASSERT_TRUE(converted_schedules[1].Match(time_point_thursday, MOSCOW_TZ));
  ASSERT_FALSE(converted_schedules[1].Match(time_point_thursday, MAURITIUS_TZ));

  ASSERT_FALSE(converted_schedules[1].Match(time_point_wednesday));
  ASSERT_FALSE(converted_schedules[1].Match(time_point_wednesday, LAGOS_TZ));
  ASSERT_FALSE(converted_schedules[1].Match(time_point_wednesday, TANZANIA_TZ));
  ASSERT_FALSE(converted_schedules[1].Match(time_point_wednesday, MOSCOW_TZ));
  ASSERT_FALSE(
      converted_schedules[1].Match(time_point_wednesday, MAURITIUS_TZ));

  ASSERT_EQ(schedules[0].FindPrev("2021-10-20T12:30:00.000+0000"_st),
            converted_schedules[0].FindPrev("2021-10-20T12:30:00.000+0000"_st));
  ASSERT_EQ(schedules[1].FindPrev("2021-10-21T17:30:00.000+0000"_st),
            converted_schedules[1].FindPrev("2021-10-21T17:30:00.000+0000"_st));
}
