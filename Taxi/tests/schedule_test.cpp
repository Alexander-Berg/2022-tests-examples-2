#include <gtest/gtest.h>

#include <schedule/schedule.hpp>

namespace eats_rest_menu_storage::schedule {

TEST(CheckSchedule, CheckSingleScheduleSerializer) {
  const auto true_json = formats::json::FromString(R"(
      [
        {
            "day": 2,
            "from": 720, 
            "to": 1080
        }
    ]
    )");
  const Schedule schedule(std::vector<handlers::Schedule>{{2, 720, 1080}});

  const auto serialized_json =
      Serialize(schedule, formats::serialize::To<formats::json::Value>());

  ASSERT_TRUE(serialized_json == true_json);
}

TEST(CheckSchedule, CheckScheduleSerializer) {
  const auto true_json = formats::json::FromString(R"(
      [
        {
            "day": 2,
            "from": 720, 
            "to": 1080
        },
        {
            "day": 3,
            "from": 0,
            "to" : 1440
        }
    ]
    )");
  const Schedule schedule(
      std::vector<handlers::Schedule>{{2, 720, 1080}, {3, 0, 1440}});

  const auto serialized_json =
      Serialize(schedule, formats::serialize::To<formats::json::Value>());

  ASSERT_TRUE(serialized_json == true_json);
}

TEST(CheckSchedule, CheckSingleScheduleParser) {
  const auto single_schedule_json = formats::json::FromString(R"(
      [
        {
            "day": 2,
            "from": 720, 
            "to": 1080
        }
       ]
    )");

  const Schedule schedule =
      Parse(single_schedule_json, ::formats::parse::To<schedule::Schedule>());
  const Schedule true_schedule(std::vector<handlers::Schedule>{{2, 720, 1080}});

  ASSERT_TRUE(schedule == true_schedule);
}

TEST(CheckSchedule, CheckScheduleParser) {
  const auto single_schedule_json = formats::json::FromString(R"(
      [
        {
            "day": 2,
            "from": 720, 
            "to": 1080
        },
        {
            "day": 3,
            "from": 0, 
            "to": 1440
        }
       ]
    )");

  const Schedule schedule =
      Parse(single_schedule_json, ::formats::parse::To<schedule::Schedule>());
  const Schedule true_schedule(
      std::vector<handlers::Schedule>{{2, 720, 1080}, {3, 0, 1440}});

  ASSERT_TRUE(schedule == true_schedule);
}

TEST(CheckScheduleMatcher, CheckScheduleMatcherTime) {
  Schedule schedule(std::vector<handlers::Schedule>{
      {1, 360, 600}});  // c 6 утра до 10 утра в понедельник

  auto time_point =
      utils::datetime::Stringtime("2021-11-15T06:00:01.854565956+0000");
  ASSERT_TRUE(schedule.Match(time_point));

  //время на cекунду меньше конца
  time_point =
      utils::datetime::Stringtime("2021-11-15T09:59:59.854565956+0000");
  ASSERT_TRUE(schedule.Match(time_point));

  //в середине периода
  time_point =
      utils::datetime::Stringtime("2021-11-15T08:00:00.854565956+0000");
  ASSERT_TRUE(schedule.Match(time_point));

  //на секунду после конца
  time_point =
      utils::datetime::Stringtime("2021-11-15T10:00:01.854565956+0000");
  ASSERT_FALSE(schedule.Match(time_point));

  //время на час дальше
  time_point =
      utils::datetime::Stringtime("2021-11-15T11:00:00.854565956+0000");
  ASSERT_FALSE(schedule.Match(time_point));

  //другой день недели
  time_point =
      utils::datetime::Stringtime("2021-11-12T05:59:59.854565956+0000");
  ASSERT_FALSE(schedule.Match(time_point));

  time_point =
      utils::datetime::Stringtime("2021-11-29T00:00:01.854565956+0000");
  ASSERT_FALSE(schedule.Match(time_point));
}

TEST(CheckScheduleMatcher, CheckMatcherSeveralDays) {
  auto schedule =
      Schedule(std::vector<handlers::Schedule>{{6, 0, 600}, {7, 0, 600}});

  auto time_point =
      utils::datetime::Stringtime("2021-12-10T08:59:59.854565956+0000");
  ASSERT_FALSE(schedule.Match(time_point));

  time_point =
      utils::datetime::Stringtime("2021-12-11T00:00:01.854565956+0000");
  ASSERT_TRUE(schedule.Match(time_point));

  time_point =
      utils::datetime::Stringtime("2021-12-11T09:59:59.854565956+0000");
  ASSERT_TRUE(schedule.Match(time_point));

  time_point =
      utils::datetime::Stringtime("2021-12-12T00:00:01.854565956+0000");
  ASSERT_TRUE(schedule.Match(time_point));

  time_point =
      utils::datetime::Stringtime("2021-12-12T09:59:59.854565956+0000");
  ASSERT_TRUE(schedule.Match(time_point));

  time_point =
      utils::datetime::Stringtime("2021-12-13T00:00:01.854565956+0000");
  ASSERT_FALSE(schedule.Match(time_point));
}
}  // namespace eats_rest_menu_storage::schedule
