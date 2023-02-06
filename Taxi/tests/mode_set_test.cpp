#include <userver/utest/utest.hpp>

#include <chrono>
#include <tuple>

#include <userver/utils/datetime.hpp>

#include <common/validators/time_settings.hpp>

using namespace utils::datetime;
using namespace taxi_config::driver_mode_subscription_time_validation_settings;

class QuestionablePeriod
    : public testing::Test,
      public testing::WithParamInterface<std::tuple<
          std::chrono::system_clock::time_point, Restrictions, std::string,
          std::tuple<std::chrono::system_clock::time_point,
                     std::chrono::system_clock::time_point>>> {};

TEST_P(QuestionablePeriod, Hourly) {
  const auto& [now, rest, timezone, res] = GetParam();

  cctz::time_zone tz;
  if (!load_time_zone(timezone, &tz)) {
    throw std::runtime_error("Can't load time zone: " + timezone);
  }

  auto to_string =
      [](const std::tuple<std::chrono::system_clock::time_point,
                          std::chrono::system_clock::time_point>& pair)
      -> std::string {
    return Timestring(std::get<0>(pair)) + " | " +
           Timestring(std::get<1>(pair));
  };

  utils::Lazy<cctz::time_zone> lazy_timezone{std::move(tz)};

  ASSERT_EQ(to_string(res),
            to_string(common::validators::impl::GetQuestionablePeriod(
                now, rest, lazy_timezone)));
}

static const Restrictions kHourRestriction{RestrictionsIntervaltype::kHourly, 1,
                                           1};
static const Restrictions kDayRestriction{RestrictionsIntervaltype::kDayly, 1,
                                          1};

INSTANTIATE_TEST_SUITE_P(
    QuestionablePeriodBase, QuestionablePeriod,
    testing::Values(
        std::make_tuple(
            Stringtime("2019-11-10T12:30:00.0+0000"), kHourRestriction,
            kDefaultTimezone,
            std::make_tuple(Stringtime("2019-11-10T11:30:00+0000"),
                            Stringtime("2019-11-10T12:30:00+0000"))),
        std::make_tuple(
            Stringtime("2019-11-10T00:30:00+0000"), kHourRestriction,
            kDefaultTimezone,
            std::make_tuple(Stringtime("2019-11-09T23:30:00+0000"),
                            Stringtime("2019-11-10T00:30:00+0000"))),
        std::make_tuple(
            Stringtime("2019-11-10T00:00:00+0000"), kHourRestriction,
            kDefaultTimezone,
            std::make_tuple(Stringtime("2019-11-09T23:00:00+0000"),
                            Stringtime("2019-11-10T00:00:00+0000"))),
        std::make_tuple(
            Stringtime("2019-11-10T12:30:00.0+0000"), kHourRestriction,
            kDefaultDriverTimezone,
            std::make_tuple(Stringtime("2019-11-10T11:30:00+0000"),
                            Stringtime("2019-11-10T12:30:00+0000"))),

        std::make_tuple(
            Stringtime("2019-11-10T12:30:00.0+0000"), kDayRestriction,
            kDefaultTimezone,
            std::make_tuple(Stringtime("2019-11-10T00:00:00+0000"),
                            Stringtime("2019-11-11T00:00:00+0000"))),
        std::make_tuple(
            Stringtime("2019-11-10T00:00:00.0+0000"), kDayRestriction,
            kDefaultTimezone,
            std::make_tuple(Stringtime("2019-11-10T00:00:00+0000"),
                            Stringtime("2019-11-11T00:00:00+0000"))),
        std::make_tuple(
            Stringtime("2019-11-10T00:30:00.0+0000"), kDayRestriction,
            kDefaultTimezone,
            std::make_tuple(Stringtime("2019-11-10T00:00:00+0000"),
                            Stringtime("2019-11-11T00:00:00+0000")))));
