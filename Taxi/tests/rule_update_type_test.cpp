#include <gtest/gtest.h>

#include <userver/utils/datetime.hpp>

#include <logic/rule_update_parser.hpp>

namespace dt = utils::datetime;

struct RuleUpdateTypeData {
  models::TimePoint updated_at;
  models::TimePoint start;
  models::TimePoint end;
  bool apply_update_type_definition_fix;
  logic::RuleUpdateType expected_type;
};

struct RuleUpdateTypeParametrized
    : public ::testing::TestWithParam<RuleUpdateTypeData> {};

logic::RuleUpdateInfoBase CreateRuleUpdateInfoBase(models::TimePoint updated_at,
                                                   models::TimePoint start,
                                                   models::TimePoint end) {
  logic::RuleUpdateInfoBase info;
  info.updated_at = updated_at;
  info.start = start;
  info.end = end;
  return info;
}

TEST_P(RuleUpdateTypeParametrized, Test) {
  const auto [updated_at, start, end, apply_update_type_definition_fix,
              expected_type] = GetParam();

  ASSERT_EQ(
      logic::GetRuleUpdateType(CreateRuleUpdateInfoBase(updated_at, start, end),
                               apply_update_type_definition_fix),
      expected_type);
}

const bool kApply = true;
const bool kNotApply = false;

INSTANTIATE_TEST_SUITE_P(
    RuleUpdateTypeParametrized, RuleUpdateTypeParametrized,
    ::testing::ValuesIn(
        {RuleUpdateTypeData{// updated < begin < end
                            dt::Stringtime("2022-04-01T12:00:00Z"),
                            dt::Stringtime("2022-04-02T12:00:00Z"),
                            dt::Stringtime("2022-04-03T12:00:00Z"), kNotApply,
                            logic::kCreated},
         RuleUpdateTypeData{// updated < end < begin
                            dt::Stringtime("2022-04-01T12:00:00Z"),
                            dt::Stringtime("2022-04-03T12:00:00Z"),
                            dt::Stringtime("2022-04-02T12:00:00Z"), kNotApply,
                            logic::kCreated},
         RuleUpdateTypeData{// updated < end = begin
                            dt::Stringtime("2022-04-01T12:00:00Z"),
                            dt::Stringtime("2022-04-02T12:00:00Z"),
                            dt::Stringtime("2022-04-02T12:00:00Z"), kNotApply,
                            logic::kCreated},
         RuleUpdateTypeData{// begin <= updated < end
                            dt::Stringtime("2022-04-02T12:00:00Z"),
                            dt::Stringtime("2022-04-01T12:00:00Z"),
                            dt::Stringtime("2022-04-03T12:00:00Z"), kNotApply,
                            logic::kClosed},
         RuleUpdateTypeData{// updated < begin < end
                            dt::Stringtime("2022-04-01T12:00:00Z"),
                            dt::Stringtime("2022-04-02T12:00:00Z"),
                            dt::Stringtime("2022-04-03T12:00:00Z"), kApply,
                            logic::kCreated},
         RuleUpdateTypeData{// updated < end < begin
                            dt::Stringtime("2022-04-01T12:00:00Z"),
                            dt::Stringtime("2022-04-03T12:00:00Z"),
                            dt::Stringtime("2022-04-02T12:00:00Z"), kApply,
                            logic::kClosed},
         RuleUpdateTypeData{// updated < end = begin
                            dt::Stringtime("2022-04-01T12:00:00Z"),
                            dt::Stringtime("2022-04-02T12:00:00Z"),
                            dt::Stringtime("2022-04-02T12:00:00Z"), kApply,
                            logic::kClosed},
         RuleUpdateTypeData{// begin <= updated < end
                            dt::Stringtime("2022-04-02T12:00:00Z"),
                            dt::Stringtime("2022-04-01T12:00:00Z"),
                            dt::Stringtime("2022-04-03T12:00:00Z"), kApply,
                            logic::kClosed}}));
