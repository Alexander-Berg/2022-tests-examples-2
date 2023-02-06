#include <gtest/gtest.h>

#include <chrono>
#include <ctime>
#include <locale>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

#include <userver/utils/datetime.hpp>

#include <cctz/civil_time.h>

#include <common_handlers/personal_summary/common.hpp>
#include <common_handlers/personal_summary/constructor.hpp>

namespace handlers {

bool operator==(DayAndMonth lhs, DayAndMonth rhs) {
  return lhs.month == rhs.month && lhs.day == rhs.day;
}

}  // namespace handlers

using TimePoint = std::chrono::system_clock::time_point;

static constexpr const char* kTimeZone = "Europe/Moscow";

TimePoint MakeTimePoint(std::string_view str) {
  std::tm tm = {};
  std::stringstream ss;
  ss << str;
  ss >> std::get_time(&tm, "%Y %m %d T %H %M %S");
  if (ss.fail()) {
    throw std::runtime_error("MakeTimePoint failed");
  }
  return std::chrono::system_clock::from_time_t(std::mktime(&tm));
}

using RuleHours = std::vector<int>;
using DayAndMonth = handlers::DayAndMonth;

struct TestExpirationDate {
  std::string rule_ends_at;
  std::optional<std::string> tag_ttl;
  RuleHours rule_hours;
  DayAndMonth expected;
};

struct ExpirationDateParametrized
    : public ::testing::TestWithParam<TestExpirationDate> {
  cctz::civil_day MakeTimePointWithTimeZone(std::string_view str) {
    return cctz::civil_day(
        utils::datetime::Localize(MakeTimePoint(str), kTimeZone));
  }
};

TEST_P(ExpirationDateParametrized, Variants) {
  const auto param = GetParam();
  const auto res = handlers::GetRuleExpirationDate(
      MakeTimePoint(param.rule_ends_at), param.rule_hours,
      param.tag_ttl ? std::make_optional(MakeTimePoint(*param.tag_ttl))
                    : std::nullopt,
      kTimeZone);

  ASSERT_EQ(res, param.expected);
}

RuleHours EmptyHours() { return {}; }
static const RuleHours kRuleHours = {3, 5, 7};

static constexpr const char* kRuleEnd = "2014 11 05 T 00 00 00";
static constexpr const char* kTtlAfterRuleEnd = "2014 11 06 T 12 34 56";
static constexpr const char* kTtlBeforeRuleEnd = "2014 11 04 T 12 34 56";
static constexpr const char* kTtlBeforeRuleEndAfterRuleHours =
    "2014 11 04 T 12 34 56";
static constexpr const char* kTtlBeforeRuleEndBetweenRuleHours =
    "2014 11 04 T 06 01 00";
static constexpr const char* kTtlBeforeRuleEndBeforeRuleHours =
    "2014 11 04 T 02 00 00";
static constexpr const char* kTtlBeforeRuleEndBeforeRuleHoursNeedChangeDate1 =
    "2014 11 01 T 02 00 00";

const std::vector<TestExpirationDate> kExpirationDateVariants = {
    // no ttl, no hours
    {kRuleEnd, std::nullopt, EmptyHours(), DayAndMonth(4, 11)},
    // // no ttl, hours set
    {kRuleEnd, std::nullopt, kRuleHours, DayAndMonth(4, 11)},
    // ttt after rule end
    {kRuleEnd, kTtlAfterRuleEnd, kRuleHours, DayAndMonth(4, 11)},
    // ttl before rule, no hours
    {kRuleEnd, kTtlBeforeRuleEnd, EmptyHours(), DayAndMonth(4, 11)},
    // ttl before rule end and after rule hours
    {kRuleEnd, kTtlBeforeRuleEndAfterRuleHours, kRuleHours, DayAndMonth(4, 11)},
    // ttl before rule end and between rule hours
    {kRuleEnd, kTtlBeforeRuleEndBetweenRuleHours, kRuleHours,
     DayAndMonth(4, 11)},
    // ttl before rule and before rule hours
    {kRuleEnd, kTtlBeforeRuleEndBeforeRuleHours, kRuleHours,
     DayAndMonth(3, 11)},
    // ttl before rule and before rule hours: needs change month
    {kRuleEnd, kTtlBeforeRuleEndBeforeRuleHoursNeedChangeDate1, kRuleHours,
     DayAndMonth(31, 10)},
};

INSTANTIATE_TEST_SUITE_P(ExpirationDate, ExpirationDateParametrized,
                         ::testing::ValuesIn(kExpirationDateVariants));
