#include <gmock/gmock.h>

#include "smart_rules/validators/period.hpp"

#include "builders.hpp"

namespace vs = billing_subventions_x::smart_rules::validators;

class ValidatePeriodIsMultipleOfDaysTest
    : public testing::TestWithParam<std::tuple<std::string,  // start
                                               std::string,  // end
                                               int           // days
                                               >> {};

TEST_P(ValidatePeriodIsMultipleOfDaysTest, SilentlyPassesWhenOk) {
  auto [start, end, days] = GetParam();
  ASSERT_NO_THROW(vs::ValidatePeriodIsMultipleOfDays(
      ATimePoint(start), ATimePoint(end), days, ""));
}

INSTANTIATE_TEST_SUITE_P(ValidatePeriodIsMultipleOfDaysTest,
                         ValidatePeriodIsMultipleOfDaysTest,
                         testing::Values(
                             // zone without DST or both switches included
                             std::make_tuple("2021-10-01T00:00:00+03:00",
                                             "2022-09-30T00:00:00+03:00", 7),
                             // zone with DST, switch to winter
                             std::make_tuple("2021-10-24T00:00:00+03:00",
                                             "2021-11-07T00:00:00+02:00", 7),
                             // zone with DST, switch to summer
                             std::make_tuple("2022-03-22T00:00:00+02:00",
                                             "2022-04-05T00:00:00+03:00", 7)));
