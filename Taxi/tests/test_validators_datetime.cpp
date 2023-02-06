#include <string>

#include <gmock/gmock.h>
#include <chrono>

#include <userver/utils/datetime.hpp>

#include "smart_rules/validators/datetime.hpp"
#include "smart_rules/validators/exceptions.hpp"

namespace {

namespace vs = billing_subventions_x::smart_rules::validators;

constexpr std::chrono::hours kThreshold(2);

TEST(DatetimeValidator, SilentlyPassesWhenOk) {
  auto now = utils::datetime::Stringtime("2020-09-01T12:00:00Z");
  auto check = utils::datetime::Stringtime("2020-09-01T12:11:00Z");
  ASSERT_NO_THROW(vs::ValidateDatetimeGreaterThan(check, now, ""));
}

TEST(DatetimeValidator, ThrowsInvalidArgumentWhenValidationFails) {
  auto now = utils::datetime::Stringtime("2020-09-01T12:00:00Z");
  auto check = utils::datetime::Stringtime("2020-09-01T11:11:00Z");
  ASSERT_THROW(vs::ValidateDatetimeGreaterThan(check, now, ""),
               vs::ValidationError);
}

TEST(DatetimeValidator, DescribesFailureWithHint) {
  auto now = utils::datetime::Stringtime("2020-09-01T12:00:00Z");
  auto check = utils::datetime::Stringtime("2020-09-01T11:11:00Z");
  try {
    vs::ValidateDatetimeGreaterThan(check, now, "Start datetime");
    FAIL();
  } catch (const vs::ValidationError& exc) {
    const std::string expected =
        "Start datetime '2020-09-01T11:11:00+0000' must be greater than "
        "'2020-09-01T12:00:00+0000'";
    ASSERT_THAT(std::string(exc.what()), ::testing::Eq(expected));
  }
}

TEST(DatetimeValidator, SilentlyPassesWhenOkWithThreshold) {
  auto now = utils::datetime::Stringtime("2020-09-01T12:00:00Z");
  auto check = utils::datetime::Stringtime("2020-09-01T14:00:01Z");
  ASSERT_NO_THROW(vs::ValidateDatetimeGreaterThan(check, now, kThreshold, ""));
}

TEST(DatetimeValidator, ThrowsInvalidArgumentWhenValidationWithThresholdFails) {
  auto now = utils::datetime::Stringtime("2020-09-01T12:00:00Z");
  auto check = utils::datetime::Stringtime("2020-09-01T09:30:00Z");
  ASSERT_THROW(vs::ValidateDatetimeGreaterThan(check, now, kThreshold, ""),
               vs::ValidationError);
}

TEST(DatetimeValidator, DescribesFailureWithHintAndThreshold) {
  auto now = utils::datetime::Stringtime("2020-09-01T12:00:00Z");
  auto check = utils::datetime::Stringtime("2020-09-01T14:00:00Z");
  try {
    vs::ValidateDatetimeGreaterThan(check, now, kThreshold, "Start datetime");
    FAIL();
  } catch (const vs::ValidationError& exc) {
    const std::string expected =
        "Start datetime '2020-09-01T14:00:00+0000' must be greater than "
        "'2020-09-01T12:00:00+0000' + 2 hours";
    ASSERT_THAT(std::string(exc.what()), ::testing::Eq(expected));
  }
}
}  // namespace
