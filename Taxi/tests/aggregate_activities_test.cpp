#include <utils/utils.hpp>

#include <gtest/gtest.h>

#include <common/aggregate_activities.hpp>

#include <fmt/format.h>

namespace handlers {
std::ostream& operator<<(std::ostream& os, const handlers::Activity& activity) {
  return os << fmt::format(
             "(geo: [{}], start: {}, end: {}, status: {}, classes: [{}], tags: "
             "[{}], pt_restrictions: {}, activity_points: {})",
             fmt::join(activity.geoareas, ","),
             utils::datetime::Timestring(activity.start),
             utils::datetime::Timestring(activity.end),
             ToString(activity.status),
             fmt::join(activity.available_tariff_classes, ","),
             fmt::join(activity.tags, ","),
             activity.profile_payment_type_restrictions,
             activity.activity_points);
}
}  // namespace handlers

namespace {
using handlers::TimestampWithGeozone;
using models::IncompleteEventGroup;
using models::RawEventGroup;

std::chrono::system_clock::time_point MakeTimePoint(
    const std::string& rfc3339s) {
  return utils::datetime::FromRfc3339StringSaturating(rfc3339s);
}

RawEventGroup MakeEventGroup(
    std::initializer_list<TimestampWithGeozone> timestamps) {
  models::RawEventGroup gr;
  gr.id = 1;
  gr.begin = MakeTimePoint("2020-01-20T12:00:00+03:00");
  gr.end = MakeTimePoint("2020-01-20T12:01:00+03:00");
  for (const auto& ts : timestamps) {
    gr.timestamps.push_back(ts);
  }
  models::DriverEventData driver_data;
  driver_data.activity_points = 0.0;
  gr.driver_data = driver_data;
  return gr;
}

handlers::Activity BuildActivity(::std::chrono::system_clock::time_point start,
                                 ::std::chrono::system_clock::time_point end,
                                 ::handlers::ActivityStatus status,
                                 ::std::vector<std::string> geoareas) {
  return handlers::Activity{start, end, status, geoareas, {}, {}, {}, {}};
}

struct Params {
  std::string name;
  models::RawEventGroup input;
  std::vector<handlers::Activity> expected_output;
};

std::ostream& operator<<(std::ostream& os, const Params& params) {
  return os << params.name;
}

}  // namespace

class AggregateActivitiesP : public ::testing::TestWithParam<Params> {};

TEST_P(AggregateActivitiesP, AggregateActivitiesTest) {
  using ActivityStatus = handlers::ActivityStatus;

  const std::chrono::seconds kEventMaxTimediff(10);
  const ActivityStatus kDriverStatus = ActivityStatus::kFree;

  const auto& params = GetParam();

  const std::vector<handlers::Activity> output = common::AggregateActivities(
      params.input, kDriverStatus, kEventMaxTimediff);

  ASSERT_EQ(output, params.expected_output);
}

// clang-format off
INSTANTIATE_TEST_SUITE_P(
    AggregateActivities, AggregateActivitiesP,
    ::testing::Values(
      Params{
        "one activity",
        MakeEventGroup({
            {MakeTimePoint("2020-01-20T12:00:00+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:09+03:00"), "zone1"}
        }),
        {
          BuildActivity(
            MakeTimePoint("2020-01-20T12:00:00+03:00"),
            MakeTimePoint("2020-01-20T12:00:09+03:00"),
            handlers::ActivityStatus::kFree,
            {"zone1"}
          )
        }
      },

      Params{
        "zero length second activity",
        MakeEventGroup({
            {MakeTimePoint("2020-01-20T12:00:11+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:20+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:18+03:00"), "zone2"}
        }),
        {
          BuildActivity(
            MakeTimePoint("2020-01-20T12:00:11+03:00"),
            MakeTimePoint("2020-01-20T12:00:20+03:00"),
            handlers::ActivityStatus::kFree,
            {"zone1"}
          )
        }
      },

      Params{
        "same activities",
        MakeEventGroup({
            {MakeTimePoint("2020-01-20T12:00:00+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:09+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:00+03:00"), "zone2"},
            {MakeTimePoint("2020-01-20T12:00:09+03:00"), "zone2"}
        }),
        {
          BuildActivity(
            MakeTimePoint("2020-01-20T12:00:00+03:00"),
            MakeTimePoint("2020-01-20T12:00:09+03:00"),
            handlers::ActivityStatus::kFree,
            {"zone1", "zone2"}
          )
        }
      },

      Params{
        "included activity",
        MakeEventGroup({
            {MakeTimePoint("2020-01-20T12:00:10+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:19+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:26+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:14+03:00"), "zone2"},
            {MakeTimePoint("2020-01-20T12:00:20+03:00"), "zone2"}
        }),
        {
          BuildActivity(
            MakeTimePoint("2020-01-20T12:00:10+03:00"),
            MakeTimePoint("2020-01-20T12:00:14+03:00"),
            handlers::ActivityStatus::kFree,
            {"zone1"}
          ),
          BuildActivity(
            MakeTimePoint("2020-01-20T12:00:14+03:00"),
            MakeTimePoint("2020-01-20T12:00:20+03:00"),            
            handlers::ActivityStatus::kFree,
            {"zone1", "zone2"}
          ),
          BuildActivity(
            MakeTimePoint("2020-01-20T12:00:20+03:00"),
            MakeTimePoint("2020-01-20T12:00:26+03:00"),            
            handlers::ActivityStatus::kFree,
            {"zone1"}
          )
        }
      },

      Params{
        "secluded activities",
        MakeEventGroup({
            {MakeTimePoint("2020-01-20T12:00:10+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:19+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:26+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:44+03:00"), "zone2"},
            {MakeTimePoint("2020-01-20T12:00:51+03:00"), "zone2"}
        }),
        {
          BuildActivity(
            MakeTimePoint("2020-01-20T12:00:10+03:00"),
            MakeTimePoint("2020-01-20T12:00:26+03:00"),            
            handlers::ActivityStatus::kFree,
            {"zone1"}
          ),
          BuildActivity(
            MakeTimePoint("2020-01-20T12:00:44+03:00"),
            MakeTimePoint("2020-01-20T12:01:00+03:00"),            
            handlers::ActivityStatus::kFree,
            {"zone2"}
          )
        }
      },

      Params{
        "linked activities",
        MakeEventGroup({
            {MakeTimePoint("2020-01-20T12:00:10+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:19+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:26+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:26+03:00"), "zone2"},
            {MakeTimePoint("2020-01-20T12:00:34+03:00"), "zone2"}
        }),
        {
          BuildActivity(
            MakeTimePoint("2020-01-20T12:00:10+03:00"),
            MakeTimePoint("2020-01-20T12:00:26+03:00"),            
            handlers::ActivityStatus::kFree,
            {"zone1"}
          ),
          BuildActivity(
            MakeTimePoint("2020-01-20T12:00:26+03:00"),
            MakeTimePoint("2020-01-20T12:00:34+03:00"),
            handlers::ActivityStatus::kFree,
            {"zone2"}
          )
        }
      },

      Params{
        "crossing activities",
        MakeEventGroup({
            {MakeTimePoint("2020-01-20T12:00:10+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:19+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:26+03:00"), "zone1"},
            {MakeTimePoint("2020-01-20T12:00:22+03:00"), "zone2"},
            {MakeTimePoint("2020-01-20T12:00:30+03:00"), "zone2"}
        }),
        {
          BuildActivity(
            MakeTimePoint("2020-01-20T12:00:10+03:00"),
            MakeTimePoint("2020-01-20T12:00:22+03:00"),
            handlers::ActivityStatus::kFree,
            {"zone1"}
          ),
          BuildActivity(
            MakeTimePoint("2020-01-20T12:00:22+03:00"),
            MakeTimePoint("2020-01-20T12:00:26+03:00"),
            handlers::ActivityStatus::kFree,
            {"zone1", "zone2"}
          ),
          BuildActivity(
            MakeTimePoint("2020-01-20T12:00:26+03:00"),
            MakeTimePoint("2020-01-20T12:00:30+03:00"),
            handlers::ActivityStatus::kFree,
            {"zone2"}
          )
        }
      }
    )
);
// clang-format on
