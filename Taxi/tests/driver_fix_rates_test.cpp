#include <cctz/civil_time.h>
#include <cctz/time_zone.h>

#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>

#include <accounting/driver_fix/rates.hpp>
#include <common/types.hpp>
#include <common/utils/time.hpp>

namespace driver_fix = billing_time_events::accounting::driver_fix;
namespace models = billing_time_events::models;
namespace types = billing_time_events::types;
namespace dt = ::utils::datetime;
namespace tu = billing_time_events::utils;
namespace {

using PaidIntervals = driver_fix::rates::PaidIntervals;

constexpr auto kMoscowTz = "Europe/Moscow";
constexpr auto kSydneyTz = "Australia/Sydney";
constexpr auto kIsrael = "Israel";
constexpr auto kUtc = "UTC";

constexpr auto kMon = 1;
constexpr auto kTue = 2;
constexpr auto kWed = 3;
constexpr auto kThu = 4;
constexpr auto kFri = 5;
constexpr auto kSat = 6;
constexpr auto kSun = 7;

class DriverFixRates : public ::testing::Test {
  void SetUp() override {
    rates_.insert({{kMon, 0, 10, types::Numeric{1}},
                   {kTue, 1, 20, types::Numeric{2}},
                   {kWed, 2, 30, types::Numeric{3}},
                   {kThu, 3, 40, types::Numeric{4}},
                   {kFri, 4, 50, types::Numeric{5}},
                   {kSat, 5, 59, types::Numeric{6}},
                   {kSun, 6, 10, types::Numeric{7}}});
  }

 protected:
  models::driver_fix::Rates rates_;
};
}  // namespace

namespace std {
std::ostream& operator<<(
    std::ostream& os,
    const billing_time_events::models::driver_fix::RatesEndpoint& what) {
  return os << "{weekday: " << what.weekday << ", hour: " << what.hour
            << ", minute: " << what.minute << ", rpm: " << what.rate_per_minute
            << "}";
}

}  // namespace std

TEST_F(DriverFixRates, GetPaidIntervals) {
  // saturday - sunday
  auto since = dt::Stringtime("2020-08-01T05:50:00Z", kUtc);
  auto till = dt::Stringtime("2020-08-02T06:11:00Z", kUtc);

  auto actual_legacy = driver_fix::rates::GetPaidIntervals(
      rates_, {{since, till}}, kUtc, types::HonorDst::kNo);
  auto actual_modern = driver_fix::rates::GetPaidIntervals(
      rates_, {{since, till}}, kUtc, types::HonorDst::kYes);

  PaidIntervals expected_paid_intervals{
      {{dt::Stringtime("2020-08-01T05:50:00+0000", kUtc),
        dt::Stringtime("2020-08-01T05:59:00+0000", kUtc)},
       {kFri, 4, 50, types::Numeric{5}}},
      {{dt::Stringtime("2020-08-01T05:59:00+0000", kUtc),
        dt::Stringtime("2020-08-02T06:10:00+0000", kUtc)},
       {kSat, 5, 59, types::Numeric{6}}},
      {{dt::Stringtime("2020-08-02T06:10:00+0000", kUtc),
        dt::Stringtime("2020-08-02T06:11:00+0000", kUtc)},
       {kSun, 6, 10, types::Numeric{7}}}};
  EXPECT_EQ(actual_legacy, expected_paid_intervals);
  EXPECT_EQ(actual_modern, expected_paid_intervals);
}

TEST_F(DriverFixRates, WithoutDOL) {
  // saturday - sunday
  types::TimeRange boundaries{
      dt::Stringtime("2020-04-04T15:50:00+03:00", "UTC", dt::kRfc3339Format),
      dt::Stringtime("2020-04-05T15:50:00+03:00", "UTC", dt::kRfc3339Format)};

  auto actual_legacy = driver_fix::rates::GetPaidIntervals(
      rates_, {boundaries}, kMoscowTz, types::HonorDst::kNo);
  auto actual_modern = driver_fix::rates::GetPaidIntervals(
      rates_, {boundaries}, kMoscowTz, types::HonorDst::kYes);

  PaidIntervals expected_paid_intervals{
      {{dt::Stringtime("2020-04-04T12:50:00+0000", kUtc),
        dt::Stringtime("2020-04-05T03:10:00+0000", kUtc)},
       {kSat, 5, 59, types::Numeric{6}}},
      {{dt::Stringtime("2020-04-05T03:10:00+0000", kUtc),
        dt::Stringtime("2020-04-05T12:50:00+0000", kUtc)},
       {kSun, 6, 10, types::Numeric{7}}}};
  EXPECT_EQ(actual_legacy, expected_paid_intervals);
  EXPECT_EQ(actual_modern, expected_paid_intervals);
}

TEST_F(DriverFixRates, DOL) {
  // saturday - sunday
  types::TimeRange boundaries{
      dt::Stringtime("2020-04-04T15:50:00+11:00", kUtc, dt::kRfc3339Format),
      dt::Stringtime("2020-04-05T15:50:00+11:00", kUtc, dt::kRfc3339Format)};

  auto actual_legacy = driver_fix::rates::GetPaidIntervals(
      rates_, {boundaries}, kSydneyTz, types::HonorDst::kNo);
  auto actual_test = driver_fix::rates::GetPaidIntervals(
      rates_, {boundaries}, kSydneyTz, types::HonorDst::kTest);
  auto actual_dst_aware = driver_fix::rates::GetPaidIntervals(
      rates_, {boundaries}, kSydneyTz, types::HonorDst::kYes);

  PaidIntervals expected_dst_aware{
      {{dt::Stringtime("2020-04-04T04:50:00+0000", kUtc),
        dt::Stringtime("2020-04-04T16:00:00+0000", kUtc)},
       {kSat, 5, 59, types::Numeric{6}}},
      {{dt::Stringtime("2020-04-04T16:00:00+0000", kUtc),
        dt::Stringtime("2020-04-04T20:10:00+0000", kUtc)},
       {kSat, 5, 59, types::Numeric{6}}},
      {{dt::Stringtime("2020-04-04T20:10:00+0000", kUtc),
        dt::Stringtime("2020-04-05T04:50:00+0000", kUtc)},
       {kSun, 6, 10, types::Numeric{7}}}};
  EXPECT_EQ(actual_dst_aware, expected_dst_aware);

  PaidIntervals expected_dst_unaware{
      {{dt::Stringtime("2020-04-04T04:50:00+0000", kUtc),
        dt::Stringtime("2020-04-04T20:10:00+0000", kUtc)},
       {kSat, 5, 59, types::Numeric{6}}},
      {{dt::Stringtime("2020-04-04T20:10:00+0000", kUtc),
        dt::Stringtime("2020-04-05T04:50:00+0000", kUtc)},
       {kSun, 6, 10, types::Numeric{7}}}};
  EXPECT_EQ(actual_legacy, expected_dst_unaware);
  EXPECT_EQ(actual_test, expected_dst_unaware);
}

TEST_F(DriverFixRates, TransitionToWinterTime) {
  types::TimeRange boundaries{dt::Stringtime("2021-10-30T21:00:00.1Z", kUtc),
                              dt::Stringtime("2021-10-31T00:00:00.2Z", kUtc)};

  const models::driver_fix::Rates rates_{{kSun, 0, 0, types::Numeric{1}},
                                         {kSun, 1, 30, types::Numeric{3}}};
  auto actual_dst_aware = driver_fix::rates::GetPaidIntervals(
      rates_, {boundaries}, kIsrael, types::HonorDst::kYes);
  PaidIntervals expected_dst_aware{
      {{dt::Stringtime("2021-10-30T21:00:00.1+0000", kUtc),
        dt::Stringtime("2021-10-30T22:30:00+0000", kUtc)},
       {kSun, 0, 0, types::Numeric{1}}},
      {{dt::Stringtime("2021-10-30T22:30:00+0000", kUtc),
        dt::Stringtime("2021-10-30T23:00:00+0000", kUtc)},
       {kSun, 1, 30, types::Numeric{3}}},
      {{dt::Stringtime("2021-10-30T23:00:00+0000", kUtc),
        dt::Stringtime("2021-10-30T23:30:00+0000", kUtc)},
       {kSun, 0, 0, types::Numeric{1}}},
      {{dt::Stringtime("2021-10-30T23:30:00+0000", kUtc),
        dt::Stringtime("2021-10-31T00:00:00.2+0000", kUtc)},
       {kSun, 1, 30, types::Numeric{3}}}};
  ASSERT_EQ(actual_dst_aware, expected_dst_aware);

  auto actual_legacy = driver_fix::rates::GetPaidIntervals(
      rates_, {boundaries}, kIsrael, types::HonorDst::kNo);
  auto actual_test = driver_fix::rates::GetPaidIntervals(
      rates_, {boundaries}, kIsrael, types::HonorDst::kTest);
  PaidIntervals expected_dst_unaware{
      {{dt::Stringtime("2021-10-30T21:00:00.1+0000", kUtc),
        dt::Stringtime("2021-10-30T22:30:00+0000", kUtc)},
       {kSun, 0, 0, types::Numeric{1}}},
      {{dt::Stringtime("2021-10-30T22:30:00+0000", kUtc),
        dt::Stringtime("2021-10-31T00:00:00.2+0000", kUtc)},
       {kSun, 1, 30, types::Numeric{3}}}};
  EXPECT_EQ(actual_legacy, expected_dst_unaware);
  EXPECT_EQ(actual_test, expected_dst_unaware);
}
