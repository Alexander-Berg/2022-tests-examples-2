#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <utils/utils.hpp>

struct ConvertDaytimeTestParam {
  std::string daytime;
  std::string given_timezone_name;
  std::string wished_timezone_name;
  std::string now;
  std::string expected_result;
};

class ConvertDaytimeTestP
    : public testing::Test,
      public testing::WithParamInterface<ConvertDaytimeTestParam> {};

TEST_P(ConvertDaytimeTestP, Test) {
  const auto& p = GetParam();

  const std::string result = utils::ConvertDaytime(
      p.daytime, utils::GetTimezone(p.given_timezone_name),
      utils::GetTimezone(p.wished_timezone_name),
      utils::datetime::Stringtime(p.now));

  ASSERT_EQ(result, p.expected_result);
}

// Reference:
// Europe/Moscow: +03:00 (always)
// Europe/Kiev: +02:00 (winter), +03:00 (summer)
// Asia/Tehran: +03:30 (winter), +04:30 (summer)
// America/Vancouver: -08:00 (winter), -07:00 (summer)

static const std::string kWinterNow = "2020-01-01T12:30:00+0000";
static const std::string kSummerNow = "2020-06-01T12:30:00+0000";

// clang-format off
INSTANTIATE_TEST_SUITE_P(
    ConvertDaytimeTest, ConvertDaytimeTestP,
    testing::Values(
      ConvertDaytimeTestParam{
        "12:00", "Europe/Moscow", "Europe/Moscow",
        kWinterNow, "12:00"
      },
      ConvertDaytimeTestParam{
        "12:00", "Europe/Moscow", "Europe/Kiev",
        kWinterNow, "11:00"
      },
      ConvertDaytimeTestParam{
        "12:00", "Europe/Moscow", "Europe/Kiev",
        kSummerNow, "12:00"
      },
      ConvertDaytimeTestParam{
        "12:45", "Europe/Moscow", "Asia/Tehran",
        kWinterNow, "13:15"
      },
      ConvertDaytimeTestParam{
        "12:45", "Europe/Moscow", "Asia/Tehran",
        kSummerNow, "14:15"
      },
      ConvertDaytimeTestParam{
        "03:00", "Europe/Moscow", "America/Vancouver",
        kWinterNow, "16:00"
      }
    )
);
// clang-format on

struct GetNextWorkdayTestParam {
  std::string start;
  std::string end;
  std::string now;
  std::vector<clients::billing_subventions::AnyRuleWeekdaysA> week_days;
  std::optional<std::string> expected_next_day;
  std::optional<std::string> expected_prev_day;
};

class GetNextPrevWorkdayTestP
    : public testing::Test,
      public testing::WithParamInterface<GetNextWorkdayTestParam> {};

namespace {
cctz::civil_second MakeCivilTime(const std::string& str) {
  const auto time_point = utils::datetime::Stringtime(str);
  return cctz::convert(time_point, utils::GetTimezone("UTC"));
}
}  // namespace

TEST_P(GetNextPrevWorkdayTestP, Test) {
  const auto& p = GetParam();

  const auto expect_result = [](const auto& expected_time, const auto& result) {
    if (expected_time) {
      const auto expected = cctz::civil_day(MakeCivilTime(*expected_time));
      ASSERT_EQ(*result, expected);
    } else {
      ASSERT_EQ(result, std::nullopt);
    }
  };

  const auto next_day =
      utils::GetNextWorkday(MakeCivilTime(p.start), MakeCivilTime(p.end),
                            MakeCivilTime(p.now), p.week_days);

  expect_result(p.expected_next_day, next_day);

  const auto prev_day =
      utils::GetPrevWorkday(MakeCivilTime(p.start), MakeCivilTime(p.end),
                            MakeCivilTime(p.now), p.week_days);

  expect_result(p.expected_prev_day, prev_day);
}

namespace {
using Weekday = clients::billing_subventions::AnyRuleWeekdaysA;
}

// clang-format off
INSTANTIATE_TEST_SUITE_P(
    GetNextPrevWorkdayTest, GetNextPrevWorkdayTestP,
    testing::Values(
      GetNextWorkdayTestParam{
        "2020-06-01T00:00:00+0000", // start: monday
        "2020-06-15T00:00:00+0000",
        "2020-06-01T12:00:00+0000", // now: monday
        {Weekday::kMon, Weekday::kTue, Weekday::kWed},
        "2020-06-01T00:00:00+0000",
        "2020-06-01T00:00:00+0000",
      },
      GetNextWorkdayTestParam{
        "2020-06-01T00:00:00+0000", // start: monday
        "2020-06-15T00:00:00+0000",
        "2020-06-01T12:00:00+0000", // now: monday
        {Weekday::kWed},
        "2020-06-03T00:00:00+0000",
        std::nullopt
      },
      GetNextWorkdayTestParam{
        "2020-06-05T00:00:00+0000", // start: friday
        "2020-06-15T00:00:00+0000",
        "2020-06-01T12:00:00+0000", // now: monday
        {Weekday::kMon, Weekday::kTue, Weekday::kWed, Weekday::kThu,
         Weekday::kFri, Weekday::kSat, Weekday::kSun},
        "2020-06-05T00:00:00+0000",
        std::nullopt
      },
      GetNextWorkdayTestParam{
        "2020-06-05T00:00:00+0000", // start: friday
        "2020-06-15T00:00:00+0000",
        "2020-06-01T12:00:00+0000", // now: monday
        {Weekday::kSat, Weekday::kSun},
        "2020-06-06T00:00:00+0000",
        std::nullopt
      },
      GetNextWorkdayTestParam{
        "2020-06-05T00:00:00+0000", // start: friday
        "2020-06-05T20:00:00+0000",
        "2020-06-01T12:00:00+0000", // now: monday
        {Weekday::kFri},
        "2020-06-05T00:00:00+0000",
        std::nullopt
      },
      GetNextWorkdayTestParam{
        "2020-06-05T00:00:00+0000", // start: friday
        "2020-06-05T20:00:00+0000",
        "2020-06-01T12:00:00+0000", // now: monday
        {Weekday::kMon},
        std::nullopt,
        std::nullopt
      },
      GetNextWorkdayTestParam{
        "2020-06-01T00:00:00+0000", // start: monday
        "2020-06-01T20:00:00+0000", // end: monday
        "2020-06-05T12:00:00+0000", // now: friday
        {Weekday::kMon, Weekday::kTue, Weekday::kWed, Weekday::kThu,
         Weekday::kFri, Weekday::kSat, Weekday::kSun},
        std::nullopt,
        "2020-06-01T00:00:00+0000"
      },
      GetNextWorkdayTestParam{
        "2020-06-01T14:00:00+0000",
        "2020-06-02T04:00:00+0000",
        "2020-06-01T12:00:00+0000",
        {Weekday::kMon, Weekday::kTue, Weekday::kWed, Weekday::kThu,
         Weekday::kFri, Weekday::kSat, Weekday::kSun},
        "2020-06-01T00:00:00+0000",
        "2020-06-01T00:00:00+0000"
      },
      GetNextWorkdayTestParam{
        "2020-06-01T00:00:00+0000",
        "2020-06-02T00:00:00+0000",
        "2020-06-02T00:00:00+0000",
        {Weekday::kMon, Weekday::kTue, Weekday::kWed, Weekday::kThu,
         Weekday::kFri, Weekday::kSat, Weekday::kSun},
        std::nullopt,
        "2020-06-01T00:00:00+0000"
      },
      GetNextWorkdayTestParam{
        "2020-06-01T00:00:00+0000",
        "2020-06-05T00:00:00+0000",
        "2020-06-07T00:00:00+0000",
        {Weekday::kWed},
        std::nullopt,
        "2020-06-03T00:00:00+0000"
      }
    )
);
// clang-format on
