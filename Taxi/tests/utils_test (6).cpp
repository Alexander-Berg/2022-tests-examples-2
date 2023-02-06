#include <utils/utils.hpp>

#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>
#include <userver/utils/datetime/from_string_saturating.hpp>

namespace std::chrono {
::std::ostream& operator<<(::std::ostream& os,
                           const std::chrono::system_clock::time_point& value) {
  return os << ::utils::datetime::Timestring(value);
}
}  // namespace std::chrono

namespace {
using TimePoint = std::chrono::system_clock::time_point;

struct Parameters {
  TimePoint time_point;
  size_t factor_minutes;
  TimePoint expected;

  Parameters(const std::string& time_point_str, size_t factor_minutes,
             const std::string& expected_str)
      : time_point(
            utils::datetime::FromRfc3339StringSaturating(time_point_str)),
        factor_minutes(factor_minutes),
        expected(utils::datetime::FromRfc3339StringSaturating(expected_str)) {}
};
}  // namespace

class CeilTimeP : public ::testing::TestWithParam<Parameters> {};

TEST_P(CeilTimeP, CeilTimeTest) {
  const auto& [time_point, factor_minutes, expected] = GetParam();
  auto tested =
      utils::CeilTime(time_point, std::chrono::minutes(factor_minutes));
  ASSERT_EQ(expected, tested);
}

// clang-format off
INSTANTIATE_TEST_SUITE_P(
    CeilTimeTest, CeilTimeP,
    ::testing::Values(
        Parameters("2020-01-20T12:00:00+03:00", 5, "2020-01-20T12:00:00+03:00"),
        Parameters("2020-01-20T12:00:01+03:00", 5, "2020-01-20T12:05:00+03:00"),
        Parameters("2020-01-20T12:04:00+03:00", 5, "2020-01-20T12:05:00+03:00"),
        Parameters("2020-01-20T12:04:32+03:00", 5, "2020-01-20T12:05:00+03:00"),
        Parameters("2020-01-20T12:02:00+03:00", 5, "2020-01-20T12:05:00+03:00"),
        Parameters("2020-01-20T12:04:00+03:00", 1, "2020-01-20T12:04:00+03:00"),
        Parameters("2020-01-20T12:04:32+03:00", 10, "2020-01-20T12:10:00+03:00"),
        Parameters("2020-01-20T12:04:32+03:00", 0, "2020-01-20T12:04:32+03:00")));
// clang-format on
