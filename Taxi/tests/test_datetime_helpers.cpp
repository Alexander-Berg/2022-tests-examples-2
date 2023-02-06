#include <userver/utest/utest.hpp>

#include <userver/utils/datetime.hpp>
#include <utils/datetime_helpers.hpp>

void AssertEquals(const utils::datetime_helpers::DatetimeProperties& expected,
                  const utils::datetime_helpers::DatetimeProperties& actual) {
  ASSERT_EQ(expected.week_day, actual.week_day);
  ASSERT_EQ(expected.hour, actual.hour);
  ASSERT_EQ(expected.minute, actual.minute);
}

UTEST(TestDatetimeHelpers, GetLocalDatetimePropertiesForTimezoneTest) {
  // Moscow UTC+3
  AssertEquals(utils::datetime_helpers::DatetimeProperties{2, 23, 59},
               utils::datetime_helpers::GetLocalDatetimePropertiesForTimezone(
                   ::utils::datetime::Stringtime("2020-05-26T20:59:59Z"),
                   "Europe/Moscow")
                   .value());

  // Yekaterinburg UTC+5
  AssertEquals(utils::datetime_helpers::DatetimeProperties{3, 1, 0},
               utils::datetime_helpers::GetLocalDatetimePropertiesForTimezone(
                   ::utils::datetime::Stringtime("2020-05-26T20:00:59Z"),
                   "Asia/Yekaterinburg")
                   .value());
}
