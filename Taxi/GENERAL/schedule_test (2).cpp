#include <gtest/gtest.h>

#include <chrono>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/formats/parse/common_containers.hpp>
#include <userver/utils/datetime.hpp>

#include <schedule/schedule.hpp>

const std::string ARAGUAINA_TZ = "America/Araguaina";
const std::string NORONHA_TZ = "America/Noronha";
const std::string CAPE_VERDE_TZ = "Atlantic/Cape_Verde";
const std::string LAGOS_TZ = "Africa/Lagos";
const std::string JERUSALEM_TZ = "Asia/Jerusalem";
const std::string MOSCOW_TZ = "Europe/Moscow";
const std::string MAURITIUS_TZ = "Indian/Mauritius";
const std::string EKB_TZ = "Asia/Yekaterinburg";

inline std::chrono::system_clock::time_point operator"" _st(
    const char* const string_time, const size_t size) {
  return utils::datetime::Stringtime(std::string(string_time, size));
}

inline std::chrono::system_clock::time_point Next(
    const std::chrono::system_clock::time_point tp) {
  return tp + std::chrono::system_clock::duration{1};
}

inline std::chrono::system_clock::time_point Prev(
    const std::chrono::system_clock::time_point tp) {
  return tp - std::chrono::system_clock::duration{1};
}

TEST(Schedule, EmptySchedule) {
  const auto schedule_json = formats::json::FromString(R"(
  {
  "timezone": "LOCAL",
  "intervals": [ ]
  }
  )");

  const auto schedule = schedule_json.As<schedule::Schedule>();
  const auto now = utils::datetime::Now();

  ASSERT_FALSE(schedule.Match(now));
  ASSERT_FALSE(schedule.Match(now, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(now, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(now, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(now, MAURITIUS_TZ));

  ASSERT_EQ(schedule.FindNext(now), std::nullopt);
  ASSERT_EQ(schedule.FindNext(now, LAGOS_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindNext(now, JERUSALEM_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindNext(now, MOSCOW_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindNext(now, MAURITIUS_TZ), std::nullopt);

  ASSERT_EQ(schedule.FindPrev(now), std::nullopt);
  ASSERT_EQ(schedule.FindPrev(now, LAGOS_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindPrev(now, JERUSALEM_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindPrev(now, MOSCOW_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindPrev(now, MAURITIUS_TZ), std::nullopt);
}

TEST(Schedule, DayFilter) {
  const auto timepoint =
      utils::datetime::Stringtime("2019-11-19T21:34:13.854565956+0000");

  auto schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [2,5,6,7]
    }
  ]
  }
  )");

  auto schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule.Match(timepoint));
  ASSERT_TRUE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MAURITIUS_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st),
            Next("2019-11-19T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T20:34:13.000+0000"_st),
            "2019-11-22T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-21T20:34:13.000+0000"_st),
            "2019-11-22T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-22T20:34:13.000+0000"_st),
            Next("2019-11-22T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-23T20:34:13.000+0000"_st),
            Next("2019-11-23T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-24T20:34:13.000+0000"_st),
            Next("2019-11-24T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-25T20:34:13.000+0000"_st),
            "2019-11-26T00:00:00.000+0000"_st);

  // some crazy cases. UTC is enough.
  ASSERT_EQ(schedule.FindNext("2019-11-17T23:59:59.999999999+0000"_st),
            "2019-11-19T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T23:59:59.999999999+0000"_st),
            "2019-11-22T00:00:00.000+0000"_st);

  ASSERT_EQ(schedule.FindPrev("2019-11-19T20:34:13.000+0000"_st),
            Prev("2019-11-19T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-20T20:34:13.000+0000"_st),
            Prev("2019-11-20T00:00:00.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-21T20:34:13.000+0000"_st),
            Prev("2019-11-20T00:00:00.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-22T20:34:13.000+0000"_st),
            Prev("2019-11-22T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-23T20:34:13.000+0000"_st),
            Prev("2019-11-23T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-24T20:34:13.000+0000"_st),
            Prev("2019-11-24T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-25T20:34:13.000+0000"_st),
            Prev("2019-11-25T00:00:00.000+0000"_st));

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [2,5,6,7]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "start"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindPrev("2019-11-18T20:34:13.000+0000"_st),
            "2019-11-17T23:30:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-19T21:00:00.000+0000"_st),
            "2019-11-19T20:30:00.000+0000"_st);

  ASSERT_EQ(schedule.FindNext("2019-11-20T20:34:13.000+0000"_st),
            "2019-11-22T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:00:00.000+0000"_st),
            "2019-11-19T21:30:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [2,5,6,7]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "end"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindPrev("2019-11-18T20:34:13.000+0000"_st),
            "2019-11-17T23:34:13.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-19T21:00:00.000+0000"_st),
            "2019-11-19T20:30:00.000+0000"_st);

  ASSERT_EQ(schedule.FindNext("2019-11-20T20:34:13.000+0000"_st),
            "2019-11-22T00:04:13.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:00:00.000+0000"_st),
            "2019-11-19T21:30:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": true,
      "day": [2,5,6,7]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match(timepoint));
  ASSERT_FALSE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MAURITIUS_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st),
            "2019-11-20T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-20T20:34:13.000+0000"_st),
            Next("2019-11-20T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-21T20:34:13.000+0000"_st),
            Next("2019-11-21T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-22T20:34:13.000+0000"_st),
            "2019-11-25T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-23T20:34:13.000+0000"_st),
            "2019-11-25T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-24T20:34:13.000+0000"_st),
            "2019-11-25T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T20:34:13.000+0000"_st),
            Next("2019-11-25T20:34:13.000+0000"_st));

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": true,
      "day": [2,5,6,7]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "start"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindPrev("2019-11-18T20:34:13.000+0000"_st),
            "2019-11-18T20:30:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-19T21:00:00.000+0000"_st),
            "2019-11-18T23:30:00.000+0000"_st);

  ASSERT_EQ(schedule.FindNext("2019-11-20T20:34:13.000+0000"_st),
            "2019-11-20T21:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:00:00.000+0000"_st),
            "2019-11-20T00:00:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": true,
      "day": [2,5,6,7]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "end"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindPrev("2019-11-18T20:34:13.000+0000"_st),
            "2019-11-18T20:04:13.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-19T21:00:00.000+0000"_st),
            "2019-11-18T23:30:00.000+0000"_st);

  ASSERT_EQ(schedule.FindNext("2019-11-20T20:34:13.000+0000"_st),
            "2019-11-20T21:04:13.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:00:00.000+0000"_st),
            "2019-11-20T00:00:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "LOCAL",
  "intervals": [
    {
      "exclude": false,
      "day": [2,5,6,7]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule.Match(timepoint));
  ASSERT_TRUE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MAURITIUS_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-19T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T20:34:13.000+0000"_st, JERUSALEM_TZ),
            "2019-11-22T00:00:00.000+0200"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-21T20:34:13.000+0000"_st, MOSCOW_TZ),
            "2019-11-22T00:00:00.000+0300"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-22T20:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-22T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-23T20:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-23T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-24T20:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-24T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-25T20:34:13.000+0000"_st, MOSCOW_TZ),
            "2019-11-26T00:00:00.000+0300"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-26T20:34:13.000+0000"_st, MAURITIUS_TZ),
            "2019-11-29T00:00:00.000+0400"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "LOCAL",
  "intervals": [
    {
      "exclude": true,
      "day": [2,5,6,7]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match("2019-11-23T20:34:13.000+0000"_st));
  ASSERT_FALSE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MAURITIUS_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st, LAGOS_TZ),
            "2019-11-20T00:00:00.000+0100"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-20T20:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-20T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-21T20:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-21T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-22T20:34:13.000+0000"_st, MAURITIUS_TZ),
            "2019-11-25T00:00:00.000+0400"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-23T20:34:13.000+0000"_st, LAGOS_TZ),
            "2019-11-25T00:00:00.000+0100"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-24T20:34:13.000+0000"_st, JERUSALEM_TZ),
            "2019-11-25T00:00:00.000+0200"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T20:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-25T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-26T20:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-27T00:34:13.000+0400"_st));

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "Europe/Moscow",
  "intervals": [
    {
      "exclude": false,
      "day": [2,5,6,7]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match(timepoint));
  ASSERT_FALSE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MAURITIUS_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-19T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T20:34:13.000+0000"_st, JERUSALEM_TZ),
            "2019-11-22T00:00:00.000+0300"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-21T20:34:13.000+0000"_st, MOSCOW_TZ),
            "2019-11-22T00:00:00.000+0300"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-22T20:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-22T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-23T20:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-23T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-24T20:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-24T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-25T20:34:13.000+0000"_st, MOSCOW_TZ),
            "2019-11-26T00:00:00.000+0300"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-26T20:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-26T20:34:13.000+0000"_st));

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "Europe/Moscow",
  "intervals": [
    {
      "exclude": true,
      "day": [2,5,6,7]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule.Match(timepoint));
  ASSERT_TRUE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MAURITIUS_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st, LAGOS_TZ),
            "2019-11-20T00:00:00.000+0300"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-20T20:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-20T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-21T20:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-21T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-22T20:34:13.000+0000"_st, MAURITIUS_TZ),
            "2019-11-25T00:00:00.000+0300"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-23T20:34:13.000+0000"_st, LAGOS_TZ),
            "2019-11-25T00:00:00.000+0300"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-24T20:34:13.000+0000"_st, JERUSALEM_TZ),
            "2019-11-25T00:00:00.000+0300"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T20:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-25T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-26T20:34:13.000+0000"_st, MAURITIUS_TZ),
            "2019-11-27T00:00:00.000+0300"_st);
}

TEST(Schedule, DaytimeFilter) {
  const auto timepoint =
      utils::datetime::Stringtime("2019-11-19T21:34:13.854565956+0000");

  auto schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "00:00:00",
          "to": "02:00:00"
        }
      ]
    }
  ]
  }
  )");

  auto schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match(timepoint));
  ASSERT_FALSE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st),
            "2019-11-20T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-20T21:34:13.000+0000"_st),
            "2019-11-21T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-21T21:34:13.000+0000"_st),
            "2019-11-22T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-22T21:34:13.000+0000"_st),
            "2019-11-23T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-23T21:34:13.000+0000"_st),
            "2019-11-24T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-24T21:34:13.000+0000"_st),
            "2019-11-25T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T21:34:13.000+0000"_st),
            "2019-11-26T00:00:00.000+0000"_st);

  // some crazy cases. UTC is enough.
  ASSERT_EQ(schedule.FindNext("2019-11-19T23:59:59.999999999+0000"_st),
            "2019-11-20T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-20T02:00:00.000+0000"_st),
            "2019-11-21T00:00:00.000+0000"_st);

  ASSERT_EQ(schedule.FindPrev("2019-11-19T21:34:13.000+0000"_st),
            "2019-11-19T02:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-20T21:34:13.000+0000"_st),
            "2019-11-20T02:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-21T21:34:13.000+0000"_st),
            "2019-11-21T02:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-22T21:34:13.000+0000"_st),
            "2019-11-22T02:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-23T21:34:13.000+0000"_st),
            "2019-11-23T02:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-24T21:34:13.000+0000"_st),
            "2019-11-24T02:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-25T21:34:13.000+0000"_st),
            "2019-11-25T02:00:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "00:00:00",
          "to": "02:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "start"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-19T01:34:13.000+0000"_st),
            "2019-11-19T02:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T02:34:13.000+0000"_st),
            "2019-11-26T00:00:00.000+0000"_st);

  ASSERT_EQ(schedule.FindPrev("2019-11-19T02:34:13.000+0000"_st),
            "2019-11-19T02:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-25T01:34:13.000+0000"_st),
            "2019-11-25T01:30:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "00:00:00",
          "to": "02:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "end"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-19T01:34:13.000+0000"_st),
            "2019-11-20T00:04:13.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T02:34:13.000+0000"_st),
            "2019-11-26T00:04:13.000+0000"_st);

  ASSERT_EQ(schedule.FindPrev("2019-11-19T02:34:13.000+0000"_st),
            "2019-11-19T01:34:13.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-25T01:34:13.000+0000"_st),
            "2019-11-25T01:04:13.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": true,
      "daytime": [
        {
          "from": "00:00:00",
          "to": "02:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule.Match(timepoint));
  ASSERT_TRUE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st),
            Next("2019-11-19T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T21:34:13.000+0000"_st),
            Next("2019-11-20T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-21T21:34:13.000+0000"_st),
            Next("2019-11-21T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-22T21:34:13.000+0000"_st),
            Next("2019-11-22T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-23T21:34:13.000+0000"_st),
            Next("2019-11-23T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-24T21:34:13.000+0000"_st),
            Next("2019-11-24T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-25T21:34:13.000+0000"_st),
            Next("2019-11-25T21:34:13.000+0000"_st));

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": true,
      "daytime": [
        {
          "from": "00:00:00",
          "to": "02:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "start"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-19T01:34:13.000+0000"_st),
            "2019-11-19T02:30:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T02:34:13.000+0000"_st),
            "2019-11-25T03:00:00.000+0000"_st);

  ASSERT_EQ(schedule.FindPrev("2019-11-19T02:34:13.000+0000"_st),
            "2019-11-19T02:30:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-25T01:34:13.000+0000"_st),
            "2019-11-24T23:30:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": true,
      "daytime": [
        {
          "from": "00:00:00",
          "to": "02:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "end"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-19T01:34:13.000+0000"_st),
            "2019-11-19T02:04:13.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T02:34:13.000+0000"_st),
            "2019-11-25T03:04:13.000+0000"_st);

  ASSERT_EQ(schedule.FindPrev("2019-11-19T02:34:13.000+0000"_st),
            "2019-11-19T02:04:13.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-25T01:34:13.000+0000"_st),
            "2019-11-24T23:34:13.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "LOCAL",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "00:00:00",
          "to": "02:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match(timepoint));
  ASSERT_FALSE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, LAGOS_TZ),
            "2019-11-20T00:00:00.000+0100"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-20T21:34:13.000+0000"_st, JERUSALEM_TZ),
            "2019-11-21T00:00:00.000+0200"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-21T21:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-21T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-22T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-22T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-23T21:34:13.000+0000"_st, EKB_TZ),
            "2019-11-25T00:00:00.000+0500"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-24T21:34:13.000+0000"_st, LAGOS_TZ),
            "2019-11-25T00:00:00.000+0100"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T21:34:13.000+0000"_st, JERUSALEM_TZ),
            "2019-11-26T00:00:00.000+0200"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-26T21:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-26T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-27T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-27T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-28T21:34:13.000+0000"_st, EKB_TZ),
            "2019-11-30T00:00:00.000+0500"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "LOCAL",
  "intervals": [
    {
      "exclude": true,
      "daytime": [
        {
          "from": "00:00:00",
          "to": "02:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule.Match(timepoint));
  ASSERT_TRUE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-19T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T21:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-20T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-21T21:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-22T02:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-22T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-23T02:00:00.000+0400"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-23T21:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-23T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-24T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-24T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-25T21:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-25T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-26T21:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-27T02:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-27T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-28T02:00:00.000+0400"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-28T21:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-28T21:34:13.000+0000"_st));

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "Europe/Moscow",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "00:00:00",
          "to": "02:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule.Match(timepoint));
  ASSERT_TRUE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-19T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T21:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-20T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-21T21:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-21T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-22T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-22T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-23T21:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-23T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-24T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-24T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-25T21:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-25T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-26T21:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-26T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-27T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-27T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-28T21:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-28T21:34:13.000+0000"_st));

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "Europe/Moscow",
  "intervals": [
    {
      "exclude": true,
      "daytime": [
        {
          "from": "00:00:00",
          "to": "02:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match(timepoint));
  ASSERT_FALSE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-20T02:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T21:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-21T02:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-21T21:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-22T02:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-22T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-23T02:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-23T21:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-24T02:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-24T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-25T02:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-25T21:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-26T02:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-26T21:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-27T02:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-27T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-28T02:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-28T21:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-29T02:00:00.000+0300"_st));

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "Asia/Yekaterinburg",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "00:00:00",
          "to": "02:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match(timepoint));
  ASSERT_FALSE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, LAGOS_TZ),
            "2019-11-21T00:00:00.000+0500"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-20T21:34:13.000+0000"_st, JERUSALEM_TZ),
            "2019-11-22T00:00:00.000+0500"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-21T21:34:13.000+0000"_st, MOSCOW_TZ),
            "2019-11-23T00:00:00.000+0500"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-22T21:34:13.000+0000"_st, MAURITIUS_TZ),
            "2019-11-24T00:00:00.000+0500"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-23T21:34:13.000+0000"_st, EKB_TZ),
            "2019-11-25T00:00:00.000+0500"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-24T21:34:13.000+0000"_st, LAGOS_TZ),
            "2019-11-26T00:00:00.000+0500"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T21:34:13.000+0000"_st, JERUSALEM_TZ),
            "2019-11-27T00:00:00.000+0500"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-26T21:34:13.000+0000"_st, MOSCOW_TZ),
            "2019-11-28T00:00:00.000+0500"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-27T21:34:13.000+0000"_st, MAURITIUS_TZ),
            "2019-11-29T00:00:00.000+0500"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-28T21:34:13.000+0000"_st, EKB_TZ),
            "2019-11-30T00:00:00.000+0500"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "Asia/Yekaterinburg",
  "intervals": [
    {
      "exclude": true,
      "daytime": [
        {
          "from": "00:00:00",
          "to": "02:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule.Match(timepoint));
  ASSERT_TRUE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-19T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T21:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-20T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-21T21:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-21T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-22T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-22T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-23T21:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-23T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-24T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-24T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-25T21:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-25T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-26T21:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-26T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-27T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-27T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-28T21:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-28T21:34:13.000+0000"_st));

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "14:00:00"
        },
        {
          "from": "16:00:00",
          "to": "18:00:00"
        },
        {
          "from": "20:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule.Match(timepoint));
  ASSERT_TRUE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st),
            Next("2019-11-19T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T21:34:13.000+0000"_st),
            Next("2019-11-20T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-21T21:34:13.000+0000"_st),
            Next("2019-11-21T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-22T21:34:13.000+0000"_st),
            Next("2019-11-22T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-23T21:34:13.000+0000"_st),
            Next("2019-11-23T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-24T21:34:13.000+0000"_st),
            Next("2019-11-24T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-25T21:34:13.000+0000"_st),
            Next("2019-11-25T21:34:13.000+0000"_st));

  ASSERT_EQ(schedule.FindPrev("2019-11-19T21:34:13.000+0000"_st),
            Prev("2019-11-19T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-20T21:34:13.000+0000"_st),
            Prev("2019-11-20T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-21T21:34:13.000+0000"_st),
            Prev("2019-11-21T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-22T21:34:13.000+0000"_st),
            Prev("2019-11-22T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-23T21:34:13.000+0000"_st),
            Prev("2019-11-23T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-24T21:34:13.000+0000"_st),
            Prev("2019-11-24T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-25T21:34:13.000+0000"_st),
            Prev("2019-11-25T21:34:13.000+0000"_st));

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "14:00:00"
        },
        {
          "from": "16:00:00",
          "to": "18:00:00"
        },
        {
          "from": "20:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "start"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-19T11:34:13.000+0000"_st),
            "2019-11-19T12:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T12:34:13.000+0000"_st),
            "2019-11-25T13:00:00.000+0000"_st);

  ASSERT_EQ(schedule.FindPrev("2019-11-19T12:34:13.000+0000"_st),
            "2019-11-19T12:30:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-25T11:34:13.000+0000"_st),
            "2019-11-24T23:30:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "14:00:00"
        },
        {
          "from": "16:00:00",
          "to": "18:00:00"
        },
        {
          "from": "20:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "end"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-19T11:34:13.000+0000"_st),
            "2019-11-19T12:04:13.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T12:34:13.000+0000"_st),
            "2019-11-25T13:04:13.000+0000"_st);

  ASSERT_EQ(schedule.FindPrev("2019-11-19T12:34:13.000+0000"_st),
            "2019-11-19T12:04:13.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-25T11:34:13.000+0000"_st),
            "2019-11-24T23:34:13.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": true,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "14:00:00"
        },
        {
          "from": "16:00:00",
          "to": "18:00:00"
        },
        {
          "from": "20:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match(timepoint));
  ASSERT_FALSE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st),
            "2019-11-20T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-20T21:34:13.000+0000"_st),
            "2019-11-21T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-21T21:34:13.000+0000"_st),
            "2019-11-22T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-22T21:34:13.000+0000"_st),
            "2019-11-23T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-23T21:34:13.000+0000"_st),
            "2019-11-24T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-24T21:34:13.000+0000"_st),
            "2019-11-25T00:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T21:34:13.000+0000"_st),
            "2019-11-26T00:00:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": true,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "14:00:00"
        },
        {
          "from": "16:00:00",
          "to": "18:00:00"
        },
        {
          "from": "20:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "start"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-19T11:34:13.000+0000"_st),
            "2019-11-19T14:30:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T12:34:13.000+0000"_st),
            "2019-11-25T14:30:00.000+0000"_st);

  ASSERT_EQ(schedule.FindPrev("2019-11-19T12:34:13.000+0000"_st),
            "2019-11-19T11:30:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-25T11:34:13.000+0000"_st),
            "2019-11-25T11:30:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": true,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "14:00:00"
        },
        {
          "from": "16:00:00",
          "to": "18:00:00"
        },
        {
          "from": "20:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "end"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-19T11:34:13.000+0000"_st),
            "2019-11-19T14:04:13.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T12:34:13.000+0000"_st),
            "2019-11-25T14:04:13.000+0000"_st);

  ASSERT_EQ(schedule.FindPrev("2019-11-19T12:34:13.000+0000"_st),
            "2019-11-19T11:34:13.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-25T11:34:13.000+0000"_st),
            "2019-11-25T11:04:13.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "LOCAL",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "14:00:00"
        },
        {
          "from": "16:00:00",
          "to": "18:00:00"
        },
        {
          "from": "20:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule.Match(timepoint));
  ASSERT_TRUE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-19T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T21:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-20T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-21T21:34:13.000+0000"_st, MOSCOW_TZ),
            "2019-11-22T12:00:00.000+0300"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-22T21:34:13.000+0000"_st, MAURITIUS_TZ),
            "2019-11-23T12:00:00.000+0400"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-23T21:34:13.000+0000"_st, EKB_TZ),
            "2019-11-24T12:00:00.000+0500"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-24T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-24T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-25T21:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-25T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-26T21:34:13.000+0000"_st, MOSCOW_TZ),
            "2019-11-27T12:00:00.000+0300"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-27T21:34:13.000+0000"_st, MAURITIUS_TZ),
            "2019-11-28T12:00:00.000+0400"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-28T21:34:13.000+0000"_st, EKB_TZ),
            "2019-11-29T12:00:00.000+0500"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "LOCAL",
  "intervals": [
    {
      "exclude": true,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "14:00:00"
        },
        {
          "from": "16:00:00",
          "to": "18:00:00"
        },
        {
          "from": "20:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match(timepoint));
  ASSERT_FALSE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, LAGOS_TZ),
            "2019-11-20T00:00:00.000+0100"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-20T21:34:13.000+0000"_st, JERUSALEM_TZ),
            "2019-11-21T00:00:00.000+0200"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-21T21:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-21T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-22T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-22T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-23T21:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-23T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-24T21:34:13.000+0000"_st, LAGOS_TZ),
            "2019-11-25T00:00:00.000+0100"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-25T21:34:13.000+0000"_st, JERUSALEM_TZ),
            "2019-11-26T00:00:00.000+0200"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-26T21:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-26T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-27T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-27T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-28T21:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-28T21:34:13.000+0000"_st));
}

TEST(Schedule, DatetimeFilter) {
  const auto timepoint =
      utils::datetime::Stringtime("2019-11-19T21:34:13.854565956+0000", "UTC",
                                  utils::datetime::kRfc3339Format);

  auto schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        },
        {
          "from": "2019-11-19 23:00:00",
          "to": "2019-11-20 01:00:00"
        }
      ]
    }
  ]
  }
  )");

  auto schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule.Match(timepoint));
  ASSERT_TRUE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-18T21:34:13.000+0000"_st),
            Next("2019-11-18T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T19:34:13.000+0000"_st),
            Next("2019-11-19T19:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st),
            "2019-11-19T21:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st),
            Next("2019-11-19T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T22:34:13.000+0000"_st),
            "2019-11-19T23:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T23:34:13.000+0000"_st),
            Next("2019-11-19T23:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T01:34:13.000+0000"_st), std::nullopt);

  ASSERT_EQ(schedule.FindPrev("2019-11-18T21:34:13.000+0000"_st),
            Prev("2019-11-18T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-19T19:34:13.000+0000"_st),
            Prev("2019-11-19T19:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-19T20:34:13.000+0000"_st),
            "2019-11-19T20:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-19T21:34:13.000+0000"_st),
            Prev("2019-11-19T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-19T22:34:13.000+0000"_st),
            "2019-11-19T21:35:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-19T23:34:13.000+0000"_st),
            Prev("2019-11-19T23:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindPrev("2019-11-20T01:34:13.000+0000"_st),
            "2019-11-20T01:00:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        },
        {
          "from": "2019-11-19 23:00:00",
          "to": "2019-11-20 01:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "start"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-18T21:34:13.000+0000"_st),
            "2019-11-18T22:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-20T01:34:13.000+0000"_st), std::nullopt);

  ASSERT_EQ(schedule.FindPrev("2019-11-18T21:34:13.000+0000"_st),
            "2019-11-18T21:30:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-20T01:34:13.000+0000"_st),
            "2019-11-20T01:00:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        },
        {
          "from": "2019-11-19 23:00:00",
          "to": "2019-11-20 01:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "end"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-18T21:34:13.000+0000"_st),
            "2019-11-18T22:04:13.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-20T01:34:13.000+0000"_st), std::nullopt);

  ASSERT_EQ(schedule.FindPrev("2019-11-18T21:34:13.000+0000"_st),
            "2019-11-18T21:04:13.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-20T01:34:13.000+0000"_st),
            "2019-11-20T00:34:13.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": true,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        },
        {
          "from": "2019-11-19 23:00:00",
          "to": "2019-11-20 01:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match(timepoint));
  ASSERT_FALSE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-18T21:34:13.000+0000"_st),
            Next("2019-11-19T20:00:00.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T19:34:13.000+0000"_st),
            Next("2019-11-19T20:00:00.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st),
            Next("2019-11-19T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st),
            Next("2019-11-19T21:35:00.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T22:34:13.000+0000"_st),
            Next("2019-11-19T22:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T23:34:13.000+0000"_st),
            Next("2019-11-20T01:00:00.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T01:34:13.000+0000"_st),
            Next("2019-11-20T01:34:13.000+0000"_st));

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": true,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        },
        {
          "from": "2019-11-19 23:00:00",
          "to": "2019-11-20 01:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "start"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-18T21:34:13.000+0000"_st),
            "2019-11-19T20:30:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-20T01:34:13.000+0000"_st),
            "2019-11-20T02:00:00.000+0000"_st);

  ASSERT_EQ(schedule.FindPrev("2019-11-18T21:34:13.000+0000"_st), std::nullopt);
  ASSERT_EQ(schedule.FindPrev("2019-11-20T01:34:13.000+0000"_st),
            "2019-11-20T01:30:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": true,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        },
        {
          "from": "2019-11-19 23:00:00",
          "to": "2019-11-20 01:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 1800,
    "origin": "end"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-18T21:34:13.000+0000"_st),
            "2019-11-19T20:04:13.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-20T01:34:13.000+0000"_st),
            "2019-11-20T02:04:13.000+0000"_st);

  ASSERT_EQ(schedule.FindPrev("2019-11-18T21:34:13.000+0000"_st), std::nullopt);
  ASSERT_EQ(schedule.FindPrev("2019-11-20T01:34:13.000+0000"_st),
            "2019-11-20T01:04:13.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "LOCAL",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        },
        {
          "from": "2019-11-19 23:00:00",
          "to": "2019-11-20 01:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule.Match(timepoint));
  ASSERT_FALSE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-18T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-18T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T19:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-19T19:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-19T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, MAURITIUS_TZ),
            std::nullopt);
  ASSERT_EQ(schedule.FindNext("2019-11-19T22:34:13.000+0000"_st, EKB_TZ),
            std::nullopt);
  ASSERT_EQ(schedule.FindNext("2019-11-19T23:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-19T23:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T01:34:13.000+0000"_st, JERUSALEM_TZ),
            std::nullopt);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "LOCAL",
  "intervals": [
    {
      "exclude": true,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        },
        {
          "from": "2019-11-19 23:00:00",
          "to": "2019-11-20 01:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match(timepoint));
  ASSERT_TRUE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-18T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-19T20:00:00.000+0100"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T19:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-19T21:35:00.000+0200"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-20T01:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-19T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T22:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-19T22:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T23:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-20T01:00:00.000+0100"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T01:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-20T01:34:13.000+0000"_st));

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "Asia/Jerusalem",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        },
        {
          "from": "2019-11-19 23:00:00",
          "to": "2019-11-20 01:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule.Match(timepoint));
  ASSERT_TRUE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-18T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-18T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T19:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-19T19:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st, MOSCOW_TZ),
            "2019-11-19T23:00:00.000+0200"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-19T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T22:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-19T22:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T23:34:13.000+0000"_st, LAGOS_TZ),
            std::nullopt);
  ASSERT_EQ(schedule.FindNext("2019-11-20T01:34:13.000+0000"_st, JERUSALEM_TZ),
            std::nullopt);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "Asia/Jerusalem",
  "intervals": [
    {
      "exclude": true,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        },
        {
          "from": "2019-11-19 23:00:00",
          "to": "2019-11-20 01:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match(timepoint));
  ASSERT_FALSE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-18T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-19T20:00:00.000+0200"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T19:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-19T21:35:00.000+0200"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-19T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-20T01:00:00.000+0200"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T22:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-20T01:00:00.000+0200"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T23:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-19T23:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T01:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-20T01:34:13.000+0000"_st));

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "Europe/Moscow",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        },
        {
          "from": "2019-11-19 23:00:00",
          "to": "2019-11-20 01:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule.Match(timepoint));
  ASSERT_TRUE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_TRUE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-18T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-18T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T19:34:13.000+0000"_st, JERUSALEM_TZ),
            "2019-11-19T23:00:00.000+0300"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-19T20:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-19T21:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T22:34:13.000+0000"_st, EKB_TZ),
            std::nullopt);
  ASSERT_EQ(schedule.FindNext("2019-11-19T23:34:13.000+0000"_st, LAGOS_TZ),
            std::nullopt);
  ASSERT_EQ(schedule.FindNext("2019-11-20T01:34:13.000+0000"_st, JERUSALEM_TZ),
            std::nullopt);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "Europe/Moscow",
  "intervals": [
    {
      "exclude": true,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        },
        {
          "from": "2019-11-19 23:00:00",
          "to": "2019-11-20 01:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match(timepoint));
  ASSERT_FALSE(schedule.Match(timepoint, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MOSCOW_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, MAURITIUS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint, EKB_TZ));

  ASSERT_EQ(schedule.FindNext("2019-11-18T21:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-19T20:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T19:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-19T19:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T20:34:13.000+0000"_st, MOSCOW_TZ),
            Next("2019-11-20T01:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:34:13.000+0000"_st, MAURITIUS_TZ),
            Next("2019-11-20T01:00:00.000+0300"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T22:34:13.000+0000"_st, EKB_TZ),
            Next("2019-11-19T22:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-19T23:34:13.000+0000"_st, LAGOS_TZ),
            Next("2019-11-19T23:34:13.000+0000"_st));
  ASSERT_EQ(schedule.FindNext("2019-11-20T01:34:13.000+0000"_st, JERUSALEM_TZ),
            Next("2019-11-20T01:34:13.000+0000"_st));
}

TEST(Schedule, ComplexSchedule) {
  const auto timepoint_a =
      utils::datetime::Stringtime("2019-11-19T21:34:13.854565956+0000", "UTC",
                                  utils::datetime::kRfc3339Format);
  const auto timepoint_b =
      utils::datetime::Stringtime("2019-11-19T23:22:13.854565956+0000", "UTC",
                                  utils::datetime::kRfc3339Format);

  auto schedule_json = formats::json::FromString(R"(
  {
  "timezone": "LOCAL",
  "intervals": [
    {
      "exclude": true,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        }
      ]
    },
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 22:35:00"
        }
      ]
    },
    {
      "exclude": false,
      "day": [2, 5, 7]
    },
    {
      "exclude": true,
      "daytime": [
        {
          "to": "12:00:00"
        },
        {
          "from": "23:00:10"
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "21:00:00",
          "to": "23:00:00"
        }
      ]
    }
  ]
  }
  )");

  auto schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule.Match(timepoint_a, ARAGUAINA_TZ));
  ASSERT_FALSE(schedule.Match(timepoint_a, NORONHA_TZ));
  ASSERT_FALSE(schedule.Match(timepoint_a, CAPE_VERDE_TZ));
  ASSERT_TRUE(schedule.Match(timepoint_a));
  ASSERT_TRUE(schedule.Match(timepoint_a, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint_a, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint_a, MOSCOW_TZ));

  ASSERT_FALSE(schedule.Match(timepoint_a, ARAGUAINA_TZ));
  ASSERT_TRUE(schedule.Match(timepoint_b, NORONHA_TZ));
  ASSERT_TRUE(schedule.Match(timepoint_b, CAPE_VERDE_TZ));
  ASSERT_FALSE(schedule.Match(timepoint_b));
  ASSERT_FALSE(schedule.Match(timepoint_b, LAGOS_TZ));
  ASSERT_FALSE(schedule.Match(timepoint_b, JERUSALEM_TZ));
  ASSERT_FALSE(schedule.Match(timepoint_b, MOSCOW_TZ));

  ASSERT_EQ(schedule.FindNext(timepoint_a, ARAGUAINA_TZ),
            "2019-11-19T21:00:00.000-0300"_st);
  ASSERT_EQ(schedule.FindNext(timepoint_a, NORONHA_TZ),
            "2019-11-19T21:00:00.000-0200"_st);
  ASSERT_EQ(schedule.FindNext(timepoint_a, CAPE_VERDE_TZ),
            "2019-11-19T21:00:00.000-0100"_st);
  ASSERT_EQ(schedule.FindNext(timepoint_a), Next(timepoint_a));
  ASSERT_EQ(schedule.FindNext(timepoint_a, LAGOS_TZ), Next(timepoint_a));
  ASSERT_EQ(schedule.FindNext(timepoint_a, JERUSALEM_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindNext(timepoint_a, MOSCOW_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindNext(timepoint_b, ARAGUAINA_TZ),
            "2019-11-19T21:00:00.000-0300"_st);
  ASSERT_EQ(schedule.FindNext(timepoint_b, NORONHA_TZ), Next(timepoint_b));
  ASSERT_EQ(schedule.FindNext(timepoint_b, CAPE_VERDE_TZ), Next(timepoint_b));
  ASSERT_EQ(schedule.FindNext(timepoint_b), std::nullopt);
  ASSERT_EQ(schedule.FindNext(timepoint_b, LAGOS_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindNext(timepoint_b, JERUSALEM_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindNext(timepoint_b, MOSCOW_TZ), std::nullopt);

  ASSERT_EQ(schedule.FindPrev(timepoint_a, ARAGUAINA_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindPrev(timepoint_a, NORONHA_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindPrev(timepoint_a, CAPE_VERDE_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindPrev(timepoint_a), Prev(timepoint_a));
  ASSERT_EQ(schedule.FindPrev(timepoint_a, LAGOS_TZ), Prev(timepoint_a));
  ASSERT_EQ(schedule.FindPrev(timepoint_a, JERUSALEM_TZ),
            "2019-11-19T22:35:00.000+0200"_st);
  ASSERT_EQ(schedule.FindPrev(timepoint_a, MOSCOW_TZ),
            "2019-11-19T22:35:00.000+0300"_st);
  ASSERT_EQ(schedule.FindPrev(timepoint_b, ARAGUAINA_TZ), std::nullopt);
  ASSERT_EQ(schedule.FindPrev(timepoint_b, NORONHA_TZ), Prev(timepoint_b));
  ASSERT_EQ(schedule.FindPrev(timepoint_b, CAPE_VERDE_TZ), Prev(timepoint_b));
  ASSERT_EQ(schedule.FindPrev(timepoint_b), "2019-11-19T22:35:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev(timepoint_b, LAGOS_TZ),
            "2019-11-19T22:35:00.000+0100"_st);
  ASSERT_EQ(schedule.FindPrev(timepoint_b, JERUSALEM_TZ),
            "2019-11-19T22:35:00.000+0200"_st);
  ASSERT_EQ(schedule.FindPrev(timepoint_b, MOSCOW_TZ),
            "2019-11-19T22:35:00.000+0300"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "LOCAL",
  "intervals": [
    {
      "exclude": true,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        }
      ]
    },
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 22:35:00"
        }
      ]
    },
    {
      "exclude": false,
      "day": [2, 5, 7]
    },
    {
      "exclude": true,
      "daytime": [
        {
          "to": "12:00:00"
        },
        {
          "from": "23:00:10"
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "21:00:00",
          "to": "23:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 900,
    "origin": "start"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-19T20:00:00.000+0000"_st),
            "2019-11-19T21:00:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:00:00.000+0000"_st),
            "2019-11-19T21:15:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T22:20:00.000+0000"_st),
            "2019-11-19T22:30:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T22:30:00.000+0000"_st), std::nullopt);

  ASSERT_EQ(schedule.FindPrev("2019-11-19T20:00:00.000+0000"_st), std::nullopt);
  ASSERT_EQ(schedule.FindPrev("2019-11-19T21:00:00.000+0000"_st), std::nullopt);
  ASSERT_EQ(schedule.FindPrev("2019-11-19T22:20:00.000+0000"_st),
            "2019-11-19T22:15:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-19T22:30:00.000+0000"_st),
            "2019-11-19T22:15:00.000+0000"_st);

  schedule_json = formats::json::FromString(R"(
  {
  "timezone": "LOCAL",
  "intervals": [
    {
      "exclude": true,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        }
      ]
    },
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 22:35:00"
        }
      ]
    },
    {
      "exclude": false,
      "day": [2, 5, 7]
    },
    {
      "exclude": true,
      "daytime": [
        {
          "to": "12:00:00"
        },
        {
          "from": "23:00:10"
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "21:00:00",
          "to": "23:00:00"
        }
      ]
    }
  ],
  "repeat": {
    "interval": 780,
    "origin": "end"
  }
  }
  )");

  schedule = schedule_json.As<schedule::Schedule>();

  ASSERT_EQ(schedule.FindNext("2019-11-19T20:00:00.000+0000"_st),
            "2019-11-19T21:05:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T21:00:00.000+0000"_st),
            "2019-11-19T21:13:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T22:20:00.000+0000"_st),
            "2019-11-19T22:33:00.000+0000"_st);
  ASSERT_EQ(schedule.FindNext("2019-11-19T22:30:00.000+0000"_st), std::nullopt);

  ASSERT_EQ(schedule.FindPrev("2019-11-19T20:00:00.000+0000"_st), std::nullopt);
  ASSERT_EQ(schedule.FindPrev("2019-11-19T21:00:00.000+0000"_st), std::nullopt);
  ASSERT_EQ(schedule.FindPrev("2019-11-19T22:20:00.000+0000"_st),
            "2019-11-19T22:07:00.000+0000"_st);
  ASSERT_EQ(schedule.FindPrev("2019-11-19T22:30:00.000+0000"_st),
            "2019-11-19T22:17:00.000+0000"_st);
}

TEST(Schedule, Overlapping) {
  auto schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": []
  }
  )");

  auto schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": []
  }
  )");

  auto schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  auto schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [1, 2]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "10:00:00",
          "to": "12:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [4, 5]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "14:00:00",
          "to": "16:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [1, 2]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "10:00:00",
          "to": "14:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [4, 5]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "16:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [1, 2, 3]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "10:00:00",
          "to": "14:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [3, 4, 5]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "16:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [1, 2, 3]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "10:00:00",
          "to": "12:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [3, 4, 5]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "14:00:00",
          "to": "16:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "14:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "16:00:00",
          "to": "18:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "14:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "13:00:00",
          "to": "15:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [1, 2, 3]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [4, 5, 6]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [1, 2, 3]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [2, 3, 4]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:40:00",
          "to": "2019-11-19 22:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:30:00",
          "to": "2019-11-19 22:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-20 21:30:00",
          "to": "2019-11-21 13:00:00"
        },
        {
          "from": "2019-11-24 00:00:00",
          "to": "2019-11-25 12:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-20 21:30:00",
          "to": "2019-11-21 13:00:00"
        }
      ]
    }
  ]
  }
  )");

  const auto schedule_gamma_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-24 00:00:00",
          "to": "2019-11-25 12:00:00"
        }
      ]
    }
  ]
  }
  )");

  const auto schedule_delta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-20 21:30:00",
          "to": "2019-11-27 22:00:00"
        }
      ]
    }
  ]
  }
  )");

  const auto schedule_epsilon_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [2]
    }
  ]
  }
  )");

  const auto schedule_zeta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "12:30:00",
          "to": "14:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();
  const auto schedule_gamma = schedule_gamma_json.As<schedule::Schedule>();
  const auto schedule_delta = schedule_delta_json.As<schedule::Schedule>();
  const auto schedule_epsilon = schedule_epsilon_json.As<schedule::Schedule>();
  const auto schedule_zeta = schedule_zeta_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule::Overlaps({schedule_alpha, schedule_beta}));
  ASSERT_TRUE(schedule::Overlaps({schedule_alpha, schedule_gamma}));
  ASSERT_TRUE(schedule::Overlaps({schedule_alpha, schedule_delta}));
  ASSERT_FALSE(schedule::Overlaps({schedule_alpha, schedule_epsilon}));
  ASSERT_TRUE(schedule::Overlaps({schedule_alpha, schedule_zeta}));
  ASSERT_FALSE(schedule::Overlaps({schedule_beta, schedule_gamma}));
  ASSERT_TRUE(schedule::Overlaps({schedule_beta, schedule_delta}));
  ASSERT_FALSE(schedule::Overlaps({schedule_beta, schedule_epsilon}));
  ASSERT_TRUE(schedule::Overlaps({schedule_beta, schedule_zeta}));
  ASSERT_TRUE(schedule::Overlaps({schedule_gamma, schedule_delta}));
  ASSERT_FALSE(schedule::Overlaps({schedule_gamma, schedule_epsilon}));
  ASSERT_TRUE(schedule::Overlaps({schedule_gamma, schedule_zeta}));
  ASSERT_TRUE(schedule::Overlaps({schedule_delta, schedule_epsilon}));
  ASSERT_TRUE(schedule::Overlaps({schedule_delta, schedule_zeta}));
  ASSERT_TRUE(schedule::Overlaps({schedule_epsilon, schedule_zeta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-20 12:00:00",
          "to": "2019-11-24 12:00:00"
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "14:00:00",
          "to": "16:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-21 12:00:00",
          "to": "2019-11-22 12:00:00"
        }
      ]
    },
    {
      "exclude": false,
      "day": [4]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "15:00:00",
          "to": "17:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-20 12:00:00",
          "to": "2019-11-24 12:00:00"
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "14:00:00",
          "to": "16:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-21 12:00:00",
          "to": "2019-11-22 12:00:00"
        }
      ]
    },
    {
      "exclude": false,
      "day": [4]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "18:00:00",
          "to": "20:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-20 12:00:00",
          "to": "2019-11-24 12:00:00"
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "14:00:00",
          "to": "16:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-21 12:00:00",
          "to": "2019-11-21 13:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-20 12:00:00",
          "to": "2019-11-24 12:00:00"
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "14:00:00",
          "to": "16:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-21 12:00:00",
          "to": "2019-11-22 12:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  // example from https://st.yandex-team.ru/EFFICIENCYDEV-6778
  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [1, 2, 3]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "18:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [2, 5]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "17:00:00",
          "to": "20:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_TRUE(schedule::Overlaps({schedule_alpha, schedule_beta}));

  schedule_alpha_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [1, 2, 3]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "18:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_beta_json = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [2, 5]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "19:00:00",
          "to": "20:00:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_alpha = schedule_alpha_json.As<schedule::Schedule>();
  schedule_beta = schedule_beta_json.As<schedule::Schedule>();

  ASSERT_FALSE(schedule::Overlaps({schedule_alpha, schedule_beta}));
}

TEST(Schedule, SerializeOptimize) {
  const auto schedule_json_in = formats::json::FromString(R"(
  {
  "timezone": "Europe/Moscow",
  "intervals": [
    {
      "exclude": true,
      "datetime": [
        {
          "to": "2019-11-19 20:00:00"
        }
      ]
    },
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        }
      ]
    },
    {
      "exclude": false,
      "day": [2, 5, 7]
    },
    {
      "exclude": true,
      "daytime": [
        {
          "to": "12:00:00"
        },
        {
          "from": "23:00:10"
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "21:00:00",
          "to": "22:00:00"
        }
      ]
    }
  ]
  }
  )");

  const auto schedule_json_out_expected = formats::json::FromString(R"(
  {
  "timezone": "Europe/Moscow",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        }
      ]
    },
    {
      "exclude": false,
      "day": [2, 5, 7]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "21:00:00",
          "to": "22:00:00"
        }
      ]
    }
  ]
  }
  )");

  const auto schedule_json_out =
      ::formats::json::ValueBuilder{schedule_json_in.As<schedule::Schedule>()}
          .ExtractValue();

  ASSERT_EQ(schedule_json_out, schedule_json_out_expected);
}

TEST(Schedule, SerializeScheduleIntervalMetaIllformed) {
  const auto schedule_json_in = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00",
          "meta": {
            "whatever": "old"
          }
        },
        {
          "from": "2019-11-19 22:00:00",
          "to": "2019-11-19 22:35:00",
          "meta": true
        }
      ]
    }
  ]
  }
  )");

  ASSERT_THROW(schedule_json_in.As<schedule::Schedule>(),
               formats::json::ParseException);
}

TEST(Schedule, SerializeScheduleIntervalMetaIntersection) {
  const auto schedule_json_no_intersection_meta = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 20:00:00",
          "to": "2019-11-19 21:35:00"
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 22:35:00"
        }
      ]
    }
  ]
  }
  )");

  const auto schedule_json_has_intersection_meta = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 20:00:00",
          "to": "2019-11-19 21:35:00",
          "meta": {
            "whatever": "old"
          }
        },
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 22:35:00",
          "meta": {
            "whatever": "new"
          }
        }
      ]
    }
  ]
  }
  )");

  ASSERT_NO_THROW(schedule_json_no_intersection_meta.As<schedule::Schedule>());
  ASSERT_THROW(schedule_json_has_intersection_meta.As<schedule::Schedule>(),
               std::logic_error);
}

TEST(Schedule, SerializeScheduleIntervalMetaRaw) {
  const auto schedule_json_in = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00",
          "meta": {
            "whatever": "old"
          }
        },
        {
          "from": "2019-11-19 22:00:00",
          "to": "2019-11-19 22:35:00",
          "meta": {
            "whatever": "new"
          }
        }
      ]
    }
  ]
  }
  )");

  const auto schedule_out = schedule_json_in.As<schedule::Schedule>();

  auto match = schedule_out.MatchWithMeta("2019-11-19T21:34:13.000+0000"_st);

  ASSERT_TRUE(match.is_matched);
  ASSERT_TRUE(match.meta);
  ASSERT_EQ(::formats::json::ToString(*match.meta), "{\"whatever\":\"old\"}");

  auto found = schedule_out.FindNextWithMeta("2019-11-19T21:34:13.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);
  ASSERT_EQ(::formats::json::ToString(*found->meta), "{\"whatever\":\"old\"}");

  match = schedule_out.MatchWithMeta("2019-11-19T22:34:13.000+0000"_st);

  ASSERT_TRUE(match.is_matched);
  ASSERT_TRUE(match.meta);
  ASSERT_EQ(::formats::json::ToString(*match.meta), "{\"whatever\":\"new\"}");

  found = schedule_out.FindNextWithMeta("2019-11-19T22:34:13.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);
  ASSERT_EQ(::formats::json::ToString(*found->meta), "{\"whatever\":\"new\"}");
}

TEST(Schedule, SerializeScheduleIntervalMetaTheDeepestDefined) {
  auto schedule_json_in = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00",
          "meta": {
            "from": "datetime"
          }
        }
      ]
    },
    {
      "exclude": false,
      "day": [
        {
          "day": 2,
          "meta": {
            "from": "day"
          }
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "21:20:00",
          "to": "21:30:00",
          "meta": {
            "from": "daytime"
          }
        }
      ]
    }
  ]
  }
  )");

  auto schedule_out = schedule_json_in.As<schedule::Schedule>();

  auto match = schedule_out.MatchWithMeta("2019-11-19T21:25:00.000+0000"_st);

  ASSERT_TRUE(match.is_matched);
  ASSERT_TRUE(match.meta);
  ASSERT_EQ(::formats::json::ToString(*match.meta), "{\"from\":\"daytime\"}");

  auto found = schedule_out.FindNextWithMeta("2019-11-19T21:25:00.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);
  ASSERT_EQ(::formats::json::ToString(*found->meta), "{\"from\":\"daytime\"}");

  schedule_json_in = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00",
          "meta": {
            "from": "datetime"
          }
        }
      ]
    },
    {
      "exclude": false,
      "day": [
        {
          "day": 2,
          "meta": {
            "from": "day"
          }
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "21:20:00",
          "to": "21:30:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_out = schedule_json_in.As<schedule::Schedule>();

  match = schedule_out.MatchWithMeta("2019-11-19T21:25:00.000+0000"_st);

  ASSERT_TRUE(match.is_matched);
  ASSERT_TRUE(match.meta);
  ASSERT_EQ(::formats::json::ToString(*match.meta), "{\"from\":\"day\"}");

  found = schedule_out.FindNextWithMeta("2019-11-19T21:25:00.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);
  ASSERT_EQ(::formats::json::ToString(*found->meta), "{\"from\":\"day\"}");

  schedule_json_in = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00",
          "meta": {
            "from": "datetime"
          }
        }
      ]
    },
    {
      "exclude": false,
      "day": [
        {
          "day": 2
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "21:20:00",
          "to": "21:30:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_out = schedule_json_in.As<schedule::Schedule>();

  match = schedule_out.MatchWithMeta("2019-11-19T21:25:00.000+0000"_st);

  ASSERT_TRUE(match.is_matched);
  ASSERT_TRUE(match.meta);
  ASSERT_EQ(::formats::json::ToString(*match.meta), "{\"from\":\"datetime\"}");

  found = schedule_out.FindNextWithMeta("2019-11-19T21:25:00.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);
  ASSERT_EQ(::formats::json::ToString(*found->meta), "{\"from\":\"datetime\"}");

  schedule_json_in = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00"
        }
      ]
    },
    {
      "exclude": false,
      "day": [
        {
          "day": 2,
          "meta": {
            "from": "day"
          }
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "21:20:00",
          "to": "21:30:00"
        }
      ]
    }
  ]
  }
  )");

  schedule_out = schedule_json_in.As<schedule::Schedule>();

  match = schedule_out.MatchWithMeta("2019-11-19T21:25:00.000+0000"_st);

  ASSERT_TRUE(match.is_matched);
  ASSERT_TRUE(match.meta);
  ASSERT_EQ(::formats::json::ToString(*match.meta), "{\"from\":\"day\"}");

  found = schedule_out.FindNextWithMeta("2019-11-19T21:25:00.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);
  ASSERT_EQ(::formats::json::ToString(*found->meta), "{\"from\":\"day\"}");

  schedule_json_in = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00",
          "meta": {
            "from": "datetime"
          }
        }
      ]
    },
    {
      "exclude": false,
      "day": [
        {
          "day": 2
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "21:20:00",
          "to": "21:30:00",
          "meta": {
            "from": "daytime"
          }
        }
      ]
    }
  ]
  }
  )");

  schedule_out = schedule_json_in.As<schedule::Schedule>();

  match = schedule_out.MatchWithMeta("2019-11-19T21:25:00.000+0000"_st);

  ASSERT_TRUE(match.is_matched);
  ASSERT_TRUE(match.meta);
  ASSERT_EQ(::formats::json::ToString(*match.meta), "{\"from\":\"daytime\"}");

  found = schedule_out.FindNextWithMeta("2019-11-19T21:25:00.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);
  ASSERT_EQ(::formats::json::ToString(*found->meta), "{\"from\":\"daytime\"}");
}

TEST(Schedule, SerializeScheduleIntervalMetaMerge) {
  auto schedule_json_in = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00",
          "meta": {
            "datetime": 13,
            "overridable": "value_0"
          }
        }
      ]
    },
    {
      "exclude": false,
      "day": [
        {
          "day": 2
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "21:20:00",
          "to": "21:30:00",
          "meta": {
            "daytime": 42,
            "overridable": "value_1"
          }
        }
      ]
    }
  ]
  }
  )");

  auto schedule_out = schedule_json_in.As<schedule::Schedule>();

  auto match = schedule_out.MatchWithMeta("2019-11-19T21:25:00.000+0000"_st);

  ASSERT_TRUE(match.is_matched);
  ASSERT_TRUE(match.meta);
  ASSERT_EQ(::formats::json::ToString(*match.meta),
            "{\"datetime\":13,\"overridable\":\"value_1\",\"daytime\":42}");

  auto found = schedule_out.FindNextWithMeta("2019-11-19T21:25:00.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);
  ASSERT_EQ(::formats::json::ToString(*found->meta),
            "{\"datetime\":13,\"overridable\":\"value_1\",\"daytime\":42}");

  match = schedule_out.MatchWithMeta("2000-11-19T21:25:00.000+0000"_st);

  ASSERT_FALSE(match.is_matched);
  ASSERT_FALSE(match.meta);

  found = schedule_out.FindNextWithMeta("2000-11-19T21:25:00.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);
  ASSERT_EQ(::formats::json::ToString(*found->meta),
            "{\"datetime\":13,\"overridable\":\"value_1\",\"daytime\":42}");
}

TEST(Schedule, SerializeScheduleIntervalMetaMergeThrow) {
  auto schedule_json_in = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00",
          "meta": {
            "overridable": 13
          }
        }
      ]
    },
    {
      "exclude": false,
      "day": [
        {
          "day": 2
        }
      ]
    },
    {
      "exclude": false,
      "daytime": [
        {
          "from": "21:20:00",
          "to": "21:30:00",
          "meta": {
            "overridable": 42
          }
        }
      ]
    }
  ]
  }
  )");

  auto schedule_out = schedule_json_in.As<schedule::Schedule>();

  ASSERT_THROW(
      schedule_out.MatchWithMeta("2019-11-19T21:25:00.000+0000"_st, "UTC",
                                 schedule::models::MetaMergePolicy::kThrow),
      schedule::models::MetaMergeException);
  ASSERT_THROW(
      schedule_out.FindNextWithMeta("2019-11-19T21:25:00.000+0000"_st, "UTC",
                                    schedule::models::MetaMergePolicy::kThrow),
      schedule::models::MetaMergeException);
}

struct MetaTest {
  int32_t int32_data;
  std::optional<int32_t> int32_data_opt;
  std::string string_data;
  std::optional<std::string> string_data_opt;

  bool operator==(const MetaTest& rhs) const {
    return std::tie(int32_data, int32_data_opt, string_data, string_data_opt) ==
           std::tie(rhs.int32_data, rhs.int32_data_opt, rhs.string_data,
                    rhs.string_data_opt);
  }

  bool operator!=(const MetaTest& rhs) const { return !(*this == rhs); }
};

MetaTest Parse(const ::formats::json::Value& json,
               formats::parse::To<MetaTest>) {
  return MetaTest{
      json["int32_data"].As<decltype(MetaTest::int32_data)>(),
      json["int32_data_opt"].As<decltype(MetaTest::int32_data_opt)>(),
      json["string_data"].As<decltype(MetaTest::string_data)>(),
      json["string_data_opt"].As<decltype(MetaTest::string_data_opt)>(),
  };
}

TEST(Schedule, SerializeScheduleDatetimeIntervalMeta) {
  const auto schedule_json_in = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "datetime": [
        {
          "from": "2019-11-19 21:00:00",
          "to": "2019-11-19 21:35:00",
          "meta": {
            "int32_data": 42,
            "int32_data_opt": 13,
            "string_data": "whatever",
            "string_data_opt": null
          }
        },
        {
          "from": "2019-11-19 22:00:00",
          "to": "2019-11-19 22:35:00",
          "meta": {
            "int32_data": 13,
            "int32_data_opt": null,
            "string_data": "dead10cc",
            "string_data_opt": "whatever"
          }
        }
      ]
    }
  ]
  }
  )");

  const auto schedule_out = schedule_json_in.As<schedule::Schedule>();

  std::optional<MetaTest> meta = MetaTest{
      42,
      13,
      "whatever",
      std::nullopt,
  };

  auto match =
      schedule_out.MatchWithMetaAs<MetaTest>("2019-11-19T21:34:13.000+0000"_st);

  ASSERT_TRUE(match.is_matched);
  ASSERT_TRUE(match.meta);
  ASSERT_EQ(meta, *match.meta);

  auto found = schedule_out.FindNextWithMetaAs<MetaTest>(
      "2019-11-19T21:34:13.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);
  ASSERT_EQ(meta, found->meta);

  meta = MetaTest{
      13,
      std::nullopt,
      "dead10cc",
      "whatever",
  };

  match =
      schedule_out.MatchWithMetaAs<MetaTest>("2019-11-19T22:34:13.000+0000"_st);

  ASSERT_TRUE(match.is_matched);
  ASSERT_TRUE(match.meta);
  ASSERT_EQ(meta, *match.meta);

  found = schedule_out.FindNextWithMetaAs<MetaTest>(
      "2019-11-19T22:34:13.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);

  ASSERT_EQ(meta, found->meta);
}

TEST(Schedule, SerializeScheduleDayIntervalMeta) {
  const auto schedule_json_in = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "day": [
        {
          "day": 1,
          "meta": {
            "int32_data": 42,
            "int32_data_opt": 13,
            "string_data": "whatever",
            "string_data_opt": null
          }
        },
        {
          "day": 7,
          "meta": {
            "int32_data": 13,
            "int32_data_opt": null,
            "string_data": "dead10cc",
            "string_data_opt": "whatever"
          }
        }
      ]
    }
  ]
  }
  )");

  const auto schedule_out = schedule_json_in.As<schedule::Schedule>();

  auto found = schedule_out.FindNextWithMetaAs<MetaTest>(
      "2019-11-18T21:34:13.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);

  std::optional<MetaTest> meta = MetaTest{
      42,
      13,
      "whatever",
      std::nullopt,
  };

  ASSERT_EQ(meta, found->meta);

  found = schedule_out.FindNextWithMetaAs<MetaTest>(
      "2019-11-17T22:34:13.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);

  meta = MetaTest{
      13,
      std::nullopt,
      "dead10cc",
      "whatever",
  };

  ASSERT_EQ(meta, found->meta);
}

TEST(Schedule, SerializeScheduleDaytimeIntervalMeta) {
  const auto schedule_json_in = formats::json::FromString(R"(
  {
  "timezone": "UTC",
  "intervals": [
    {
      "exclude": false,
      "daytime": [
        {
          "from": "12:00:00",
          "to": "14:00:00",
          "meta": {
            "int32_data": 42,
            "int32_data_opt": 13,
            "string_data": "whatever",
            "string_data_opt": null
          }
        },
        {
          "from": "15:00:00",
          "to": "16:00:00",
          "meta": {
            "int32_data": 13,
            "int32_data_opt": null,
            "string_data": "dead10cc",
            "string_data_opt": "whatever"
          }
        }
      ]
    }
  ]
  }
  )");

  const auto schedule_out = schedule_json_in.As<schedule::Schedule>();

  auto found = schedule_out.FindNextWithMetaAs<MetaTest>(
      "2019-11-18T12:34:13.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);

  std::optional<MetaTest> meta = MetaTest{
      42,
      13,
      "whatever",
      std::nullopt,
  };

  ASSERT_EQ(meta, found->meta);

  found = schedule_out.FindNextWithMetaAs<MetaTest>(
      "2019-11-17T15:34:13.000+0000"_st);

  ASSERT_TRUE(found);
  ASSERT_TRUE(found->meta);

  meta = MetaTest{
      13,
      std::nullopt,
      "dead10cc",
      "whatever",
  };

  ASSERT_EQ(meta, found->meta);
}
