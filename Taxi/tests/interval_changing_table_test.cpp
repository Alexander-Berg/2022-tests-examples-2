#include <userver/utest/utest.hpp>

#include <testing/taxi_config.hpp>

#include <taxi_config/variables/SUBVENTIONS_ACTIVITY_PRODUCER_AGGREGATION_INTERVAL.hpp>

#include <models/interval_changing_table.hpp>

namespace {
std::chrono::system_clock::time_point MakeTimePoint(
    const std::string& rfc3339s) {
  return utils::datetime::FromRfc3339StringSaturating(rfc3339s);
}

using taxi_config::subventions_activity_producer_aggregation_interval::
    IntervalChangePoint;

dynamic_config::StorageMock MakeConfig(
    std::initializer_list<IntervalChangePoint> il) {
  return dynamic_config::MakeDefaultStorage(
      {{taxi_config::SUBVENTIONS_ACTIVITY_PRODUCER_AGGREGATION_INTERVAL, il}});
}
}  // namespace

TEST(IntervalChangingTable, InteravlChangingTable) {
  const auto config = MakeConfig({
      {MakeTimePoint("2020-01-20T12:00:00+03:00"), std::chrono::minutes(5)},
      {MakeTimePoint("2020-01-20T12:11:00+03:00"), std::chrono::minutes(2)},
      {MakeTimePoint("2020-01-20T12:14:00+03:00"), std::chrono::minutes(3)},
      {MakeTimePoint("2020-01-20T12:20:00+03:00"), std::chrono::minutes(1)},
  });

  const std::vector<IntervalChangePoint> expected_table = {
      {MakeTimePoint("2020-01-20T11:59:00+03:00"), std::chrono::minutes(1)},
      {MakeTimePoint("2020-01-20T12:00:00+03:00"), std::chrono::minutes(5)},
      {MakeTimePoint("2020-01-20T12:01:00+03:00"), std::chrono::minutes(5)},
      {MakeTimePoint("2020-01-20T12:11:00+03:00"), std::chrono::minutes(5)},
      {MakeTimePoint("2020-01-20T12:15:00+03:00"), std::chrono::minutes(5)},
      {MakeTimePoint("2020-01-20T12:15:00+03:00"), std::chrono::minutes(5)},
      {MakeTimePoint("2020-01-20T12:16:00+03:00"), std::chrono::minutes(5)},
      {MakeTimePoint("2020-01-20T12:20:00+03:00"), std::chrono::minutes(2)},
      {MakeTimePoint("2020-01-20T12:21:00+03:00"), std::chrono::minutes(1)},
      {MakeTimePoint("2020-01-20T12:22:00+03:00"), std::chrono::minutes(1)},
  };

  models::IntervalChangingTable table(config.GetSnapshot());

  for (const auto& [time_point, expected] : expected_table) {
    const auto tested = table.GetIntervalLengthFor(time_point);
    EXPECT_EQ(expected, tested)
        << "at " << utils::datetime::Timestring(time_point);
  }
}
