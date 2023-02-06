#include <gmock/gmock.h>

#include <memory>

#include <accounting/driver_fix/usecases.hpp>
#include <accounting/time_events_repository.hpp>
#include <common/types.hpp>
#include <common/utils/time.hpp>
#include <models/subvention_rule.hpp>

namespace accounting = billing_time_events::accounting;
namespace models = billing_time_events::models;
namespace types = billing_time_events::types;

namespace billing_time_events::accounting {
bool operator==(const AggregateByIntervalsQuery& lhs,
                const AggregateByIntervalsQuery& rhs) {
  if (lhs.driver != rhs.driver) return false;
  if (lhs.created_at_boundaries != rhs.created_at_boundaries) return false;
  if (lhs.event_at_intervals.size() != rhs.event_at_intervals.size()) {
    return false;
  }
  return std::equal(lhs.event_at_intervals.begin(),
                    lhs.event_at_intervals.end(),
                    rhs.event_at_intervals.begin());
}
}  // namespace billing_time_events::accounting

namespace {

auto MakeTimePoint(const std::string& stringtime) {
  return ::utils::datetime::Stringtime(stringtime, "UTC");
}

class MockTimeEventsRepository : public accounting::TimeEventsRepository {
 public:
  MOCK_METHOD(std::vector<accounting::IntervalAndEvent>, AggregateByIntervals,
              (const accounting::AggregateByIntervalsQuery&), (override));
};

class DriverFixUsecaseTest : public ::testing::Test {
  void SetUp() override {
    // rule
    data_.currency = "USD";
    data_.tariff_classes = {"econom", "comfort"};
    data_.payment_type_restrictions = models::PaymentTypeRestrictions::kOnline;
    data_.geoarea = "kursk";
    data_.validity = {MakeTimePoint("2020-08-01T22:00:00Z"),
                      MakeTimePoint("2020-08-02T01:00:00Z")};
    data_.rates.insert({{1, 0, 10, types::Numeric{1}},
                        {2, 1, 20, types::Numeric{2}},
                        {3, 2, 30, types::Numeric{3}},
                        {4, 3, 40, types::Numeric{4}},
                        {5, 4, 50, types::Numeric{5}},
                        {6, 5, 59, types::Numeric{6}},
                        {7, 6, 10, types::Numeric{7}}});
    data_.timezone_id = "Europe/Moscow";

    // event
    event_.payload.tariff_classes = {"econom"};
    event_.payload.payment_type_restrictions =
        models::ToString(models::PaymentTypeRestrictions::kOnline);
    event_.payload.geoareas = {"kursk"};
    event_.amount = std::chrono::minutes{6};
    event_.event_at = MakeTimePoint("2020-08-01T23:00:00Z");

    // interval
    boundaries_ = {MakeTimePoint("2020-08-01T22:00:00Z"),
                   MakeTimePoint("2020-08-02T01:00:00Z")};

    // daily_shift
    daily_shift_.shift_close_time = std::chrono::hours{23};
    daily_shift_.validity = {MakeTimePoint("2020-08-01T22:00:00Z"),
                             MakeTimePoint("2020-08-02T01:00:00Z")};
    mock_time_events_repository_.reset(new MockTimeEventsRepository{});
  }

 protected:
  models::driver_fix::RuleCalcBasis data_{};
  models::DailyShift daily_shift_{};
  models::Event event_{};
  types::TimeRange boundaries_{};
  std::shared_ptr<MockTimeEventsRepository> mock_time_events_repository_{};
};
}  // namespace

TEST_F(DriverFixUsecaseTest, HonorShifts) {
  accounting::AggregateByIntervalsQuery expect_query{};
  expect_query.created_at_boundaries = boundaries_;
  auto shift_close_time = MakeTimePoint("2020-08-01T23:00:00Z");
  expect_query.event_at_intervals = {{boundaries_.lower(), shift_close_time},
                                     {shift_close_time, boundaries_.upper()}};
  expect_query.driver = "1000_FFFFFFFFFFF";
  EXPECT_CALL(*mock_time_events_repository_,
              AggregateByIntervals(expect_query));
  accounting::driver_fix::CalculateJournals(
      mock_time_events_repository_, data_,
      {daily_shift_, "1000_FFFFFFFFFFF", boundaries_, {boundaries_}});
}

TEST_F(DriverFixUsecaseTest, HonorMultipleEventAtRanges) {
  daily_shift_.shift_close_time = std::chrono::hours{1};

  std::vector<types::TimeRange> event_at_ranges{};
  auto from = boundaries_.lower();
  for (auto to : {MakeTimePoint("2020-08-01T22:30:00Z"),
                  MakeTimePoint("2020-08-01T23:00:00Z"),
                  MakeTimePoint("2020-08-01T23:30:00Z"),
                  MakeTimePoint("2020-08-02T00:00:00Z"),
                  MakeTimePoint("2020-08-02T00:30:00Z"), boundaries_.upper()}) {
    event_at_ranges.push_back({from, to});
    from = to;
  }

  accounting::AggregateByIntervalsQuery expect_query{};
  expect_query.created_at_boundaries = boundaries_;
  expect_query.event_at_intervals = event_at_ranges;

  expect_query.driver = "1000_FFFFFFFFFFF";
  EXPECT_CALL(*mock_time_events_repository_,
              AggregateByIntervals(expect_query));

  accounting::driver_fix::CalculateJournals(
      mock_time_events_repository_, data_,
      {daily_shift_, "1000_FFFFFFFFFFF", boundaries_, event_at_ranges});
}
