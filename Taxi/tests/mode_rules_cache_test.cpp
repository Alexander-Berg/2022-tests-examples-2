#include <caches/mode_rules_cache.hpp>

#include <variant>

#include <gtest/gtest.h>
#include <boost/range/adaptor/transformed.hpp>
#include <boost/uuid/string_generator.hpp>

#include <utils/utils.hpp>

using namespace utils::datetime;

namespace {

const models::mode_rules::Id rule_id1{
    boost::uuids::string_generator{}("4fcdbbcb-3026-41d7-941f-aceb1fd314c3")};
const models::mode_rules::Id rule_id2{
    boost::uuids::string_generator{}("085c9271-3fcc-49ff-9ea5-4e338938cfe0")};
const models::mode_rules::Id rule_id3{
    boost::uuids::string_generator{}("bc13c1b2-c50e-4d85-8ce5-587ad68b9cc7")};
const models::mode_rules::Id rule_id4{
    boost::uuids::string_generator{}("a72fa8d6-92f5-4d57-8270-4275ae6546e9")};
const models::mode_rules::Id rule_id5{
    boost::uuids::string_generator{}("cba519b9-3461-47d9-8261-6811c4f35988")};

const driver_mode::WorkMode work_mode1{"mode1"};
const driver_mode::WorkMode work_mode2{"mode2"};
const driver_mode::WorkMode work_mode3{"mode3"};

db::mapping::ModeRuleRow CreateDbRow(const models::mode_rules::Id& id,
                                     const driver_mode::WorkMode& work_mode,
                                     models::TimePoint starts_at) {
  return {id,
          work_mode,
          std::nullopt,
          starts_at,
          std::nullopt,
          std::nullopt,
          std::nullopt,
          driver_mode::DisplayMode{"some_mode"},
          models::DisplayProfile{"some_profile"},
          driver_mode::BillingMode{"some_billing_mode"},
          driver_mode::BillingModeRule{"some_billing_mode_rule"},
          std::nullopt};
}

void CheckModeRulesIdEqual(
    const std::vector<models::mode_rules::ModeRuleCPtr>& actual_mode_rules,
    const std::unordered_set<models::mode_rules::Id>& expected_ruled_ids) {
  const auto actual_rule_ids =
      utils::Eval(actual_mode_rules |
                  boost::adaptors::transformed([](const auto& mode_rule) {
                    return mode_rule->rule_id;
                  }));

  EXPECT_EQ(actual_rule_ids.size(), expected_ruled_ids.size());

  for (const auto& rule_id : actual_rule_ids) {
    EXPECT_EQ(expected_ruled_ids.count(rule_id), 1)
        << "Rule not found " << ToString(rule_id);
  }
}

}  // namespace

caches::mode_rules::Cache CreateCache() {
  caches::mode_rules::Cache result;
  // work_mode1
  result.insert_or_assign(
      models::mode_rules::Id{rule_id1},
      CreateDbRow(rule_id1, work_mode1,
                  Stringtime("2020-10-10T12:30:00.0+0000")));

  result.insert_or_assign(
      models::mode_rules::Id{rule_id2},
      CreateDbRow(rule_id2, work_mode1,
                  Stringtime("2020-11-10T12:30:00.0+0000")));

  result.insert_or_assign(
      models::mode_rules::Id{rule_id3},
      CreateDbRow(rule_id3, work_mode1,
                  Stringtime("2020-12-10T12:30:00.0+0000")));
  // work_mode2
  result.insert_or_assign(
      models::mode_rules::Id{rule_id4},
      CreateDbRow(rule_id4, work_mode2,
                  Stringtime("2020-11-10T13:30:00.0+0000")));

  result.insert_or_assign(
      models::mode_rules::Id{rule_id5},
      CreateDbRow(rule_id5, work_mode2,
                  Stringtime("2020-12-10T13:30:00.0+0000")));

  return result;
}

TEST(FindModeRules, SingleRuleTest) {
  const auto cache = CreateCache();

  {
    const auto time_point = Stringtime("2020-09-10T12:30:00.0+0000");
    const auto mode_rule_opt =
        cache.FindRuleWithStartAtNotGreater(work_mode1, time_point);
    ASSERT_EQ(mode_rule_opt, std::nullopt);
  }

  {
    const auto time_point = Stringtime("2020-10-10T12:30:00.0+0000");
    auto mode_rule_opt =
        cache.FindRuleWithStartAtNotGreater(work_mode1, time_point);
    ASSERT_NE(mode_rule_opt, std::nullopt);
    ASSERT_EQ((*mode_rule_opt)->rule_id.GetUnderlying(),
              rule_id1.GetUnderlying());
  }

  {
    const auto time_point = Stringtime("2020-10-10T13:30:00.0+0000");
    const auto mode_rule_opt =
        cache.FindRuleWithStartAtNotGreater(work_mode1, time_point);
    ASSERT_NE(mode_rule_opt, std::nullopt);
    ASSERT_EQ((*mode_rule_opt)->rule_id.GetUnderlying(),
              rule_id1.GetUnderlying());
  }

  {
    const auto time_point = Stringtime("2020-11-10T12:30:00.0+0000");
    const auto mode_rule_opt =
        cache.FindRuleWithStartAtNotGreater(work_mode1, time_point);
    ASSERT_NE(mode_rule_opt, std::nullopt);
    ASSERT_EQ((*mode_rule_opt)->rule_id.GetUnderlying(),
              rule_id2.GetUnderlying());
  }

  {
    const auto time_point = Stringtime("2021-01-10T12:30:00.0+0000");
    const auto mode_rule_opt =
        cache.FindRuleWithStartAtNotGreater(work_mode1, time_point);
    ASSERT_NE(mode_rule_opt, std::nullopt);
    ASSERT_EQ((*mode_rule_opt)->rule_id.GetUnderlying(),
              rule_id3.GetUnderlying());
  }

  {
    const auto time_point = Stringtime("2020-10-10T12:30:00.0+0000");
    const auto mode_rule_opt =
        cache.FindRuleWithStartAtNotGreater(work_mode3, time_point);
    ASSERT_EQ(mode_rule_opt, std::nullopt);
  }
}

TEST(FindModeRules, AllRulesTest) {
  const auto cache = CreateCache();

  {
    const auto time_point = Stringtime("2020-09-10T12:30:00.0+0000");
    const auto mode_rules = cache.GetAllRulesWithStartAtNotGreater(time_point);
    ASSERT_EQ(mode_rules.empty(), true);
  }

  {
    const auto time_point = Stringtime("2020-10-10T12:30:00.0+0000");
    const auto mode_rules = cache.GetAllRulesWithStartAtNotGreater(time_point);
    ASSERT_EQ(mode_rules.empty(), false);
    CheckModeRulesIdEqual(mode_rules, {rule_id1});
  }

  {
    const auto time_point = Stringtime("2020-11-10T14:30:00.0+0000");
    const auto mode_rules = cache.GetAllRulesWithStartAtNotGreater(time_point);
    ASSERT_EQ(mode_rules.empty(), false);
    CheckModeRulesIdEqual(mode_rules, {rule_id4, rule_id2});
  }

  {
    const auto time_point = Stringtime("2021-11-10T14:30:00.0+0000");
    const auto mode_rules = cache.GetAllRulesWithStartAtNotGreater(time_point);
    ASSERT_EQ(mode_rules.empty(), false);
    CheckModeRulesIdEqual(mode_rules, {rule_id3, rule_id5});
  }
}
