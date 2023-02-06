#include <gtest/gtest.h>

#include <ranges/to_container.hpp>
#include <subvention-rule-utils/helpers/tariff_classes.hpp>
#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/utils/algo.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <common_handlers/goals_summary/fetch_goals.hpp>
#include <common_handlers/goals_summary/types.hpp>
#include <views/driver/v1/subvention-view/v1/view/summary/get/types.hpp>

namespace dt = utils::datetime;

namespace handlers::driver_v1_subvention_view_v1_view_summary::get {

auto NextStepOrdersInfoAsTuple(const NextStepOrdersInfo& info) {
  return std::tie(info.is_completed, info.orders_between_steps,
                  info.orders_left_to_next_step, info.diff_income,
                  info.abs_income);
}

bool operator==(const NextStepOrdersInfo& lhs, const NextStepOrdersInfo& rhs) {
  return NextStepOrdersInfoAsTuple(lhs) == NextStepOrdersInfoAsTuple(rhs);
}

}  // namespace handlers::driver_v1_subvention_view_v1_view_summary::get

namespace summary = handlers::driver_v1_subvention_view_v1_view_summary::get;
namespace sru = subvention_rule_utils;

namespace tests {

namespace {

bs::TripBounds MakeTripBounds(int lower,
                              std::optional<int> upper = std::nullopt,
                              std::optional<int> bonus = std::nullopt) {
  bs::TripBounds res;
  res.lower_bound = lower;
  res.upper_bound = upper;
  res.bonus_amount = std::to_string(bonus.value_or(100));
  return res;
}

using Branding = bs::AnyRuleBrandingtype;

bs::DailyGuaranteeRule MakeNmfgRule(
    Branding branding, std::string_view rule_id,
    const std::vector<std::string>& tags,
    const std::optional<std::vector<std::string>>& tariff_classes) {
  bs::DailyGuaranteeRule res;
  res.subvention_rule_id = rule_id;
  res.branding_type = branding;
  res.tags = tags;
  res.tariff_classes = tariff_classes;
  return res;
}

std::vector<bs::TripBounds> MakeTripBounds() {
  std::vector<bs::TripBounds> res;
  res.push_back(MakeTripBounds(2, 4, 10));
  res.push_back(MakeTripBounds(5, 7, 11));
  res.push_back(MakeTripBounds(8, std::nullopt, 12));
  res.push_back(MakeTripBounds(9, 14, 13));
  return res;
}

handlers::ExtendedRuleWithProgressPtr CreateExtendedRule(
    int bonus_amount, std::string_view rule_id) {
  using ResType = handlers::ExtendedRuleWithProgressPtr::element_type;
  bs::GuaranteeRule bs_rule;
  bs_rule.subvention_rule_id = rule_id;
  bs_rule.bonus_amount = std::to_string(bonus_amount);
  auto rule = std::shared_ptr<handlers::ExtendedRuleBase>(
      new handlers::ExtendedRule(bs::Rule(bs_rule), false, {}));
  return std::make_shared<ResType>(rule, -1);
}

using namespace handlers;

GoalSteps ToGoalSteps(const std::vector<bs::TripBounds>& trip_bounds) {
  GoalSteps res;
  for (const auto& [lower, _, bonus] : trip_bounds) {
    res.push_back({size_t(lower), bonus});
  }
  return res;
}

GoalWithProgress MakeGoalWithProgress(
    const std::vector<bs::TripBounds>& trip_bounds, int progress) {
  GoalWithProgress res;
  res.goal_steps = ToGoalSteps(trip_bounds);
  res.progress = progress;
  return res;
}

}  // namespace

const TimePoint kMockNow = dt::Stringtime("2021-06-22T16:30:00Z");
const std::string kDefaultTimeZone = "Europe/Moscow";

struct TestNextStepInfoData {
  GoalWithProgress rule;
  summary::NextStepOrdersInfo expected;
};

struct NextStepInfoDataParametrized
    : public ::testing::TestWithParam<TestNextStepInfoData> {};

TEST_P(NextStepInfoDataParametrized, Variants) {
  const auto param = GetParam();
  const auto res = summary::GetNextStepOrdersInfo(param.rule);
  ASSERT_EQ(res, param.expected);
}

const std::vector<bs::TripBounds> kManyTripsBounds = MakeTripBounds();
const std::vector<bs::TripBounds> kSingleTripsBounds = {
    MakeTripBounds(30, std::nullopt, 1000)};

const std::vector<TestNextStepInfoData> kNextStepInfoDataVariants = {
    {MakeGoalWithProgress(kManyTripsBounds, 1), {1, 2, 10, 10, false}},
    {MakeGoalWithProgress(kManyTripsBounds, 2), {3, 3, 1, 11, false}},
    {MakeGoalWithProgress(kManyTripsBounds, 7), {1, 3, 1, 12, false}},
    {MakeGoalWithProgress(kManyTripsBounds, 8), {1, 1, 1, 13, false}},
    {MakeGoalWithProgress(kManyTripsBounds, 10), {9, 0, 13, 13, true}},
    {MakeGoalWithProgress(kManyTripsBounds, 100500), {9, 0, 13, 13, true}},
    {MakeGoalWithProgress(kSingleTripsBounds, 1), {29, 30, 1000, 1000, false}},
    {MakeGoalWithProgress(kSingleTripsBounds, 30), {30, 0, 1000, 1000, true}},
    {MakeGoalWithProgress(kSingleTripsBounds, 100500),
     {30, 0, 1000, 1000, true}},
};

INSTANTIATE_TEST_SUITE_P(SummaryTypes, NextStepInfoDataParametrized,
                         ::testing::ValuesIn(kNextStepInfoDataVariants));

GoalWithProgress MakeGoalWithProgress(
    std::string_view group_id, const bs::AnyRule& rule, size_t progress,
    const std::vector<bs::TripBounds>& trip_bounds) {
  GoalWithProgress res;
  const auto rule_tariffs =
      rule.tariff_classes.value_or(std::vector<std::string>{});
  res.tariff_classes = TariffClasses(cbegin(rule_tariffs), cend(rule_tariffs));
  res.currency = rule.currency;
  res.end = rule.end;
  res.rule_id = group_id;
  res.goal_steps = ToGoalSteps(trip_bounds);
  res.progress = progress;
  return res;
}

TEST(SummaryTypes, BestSingleRideRule) {
  const std::vector<handlers::ExtendedRuleWithProgressPtr> rules = {
      CreateExtendedRule(100, "id1"),
      CreateExtendedRule(200, "id2"),
      CreateExtendedRule(50, "id3"),
  };
  const auto rule = summary::GetBestSingleRideRule(
      rules, {}, "RUB", kDefaultTimeZone, {}, summary::ScreensLinksSettings{},
      {}, handlers::GetScheduleCheckPolicy::kDefault);
  ASSERT_EQ(rule->GetRuleId(), "id2");
}

struct NmfgData {
  std::vector<bs::DailyGuaranteeRule> rules;
  models::TagsSet tags;
  std::optional<std::string> expected_rule_id;
  std::set<std::string> active_tariffs;
  bool use_bsx_matching_logic;
};

struct NmfgDataParametrized : public ::testing::TestWithParam<NmfgData> {};

TEST_P(NmfgDataParametrized, Variants) {
  const auto param = GetParam();
  const auto res = handlers::FindMatchingBestSubvention(
      param.rules, param.tags, param.active_tariffs,
      param.use_bsx_matching_logic);
  const auto rule_id =
      res ? make_optional(res->subvention_rule_id) : std::nullopt;
  ASSERT_EQ(rule_id, param.expected_rule_id);
}

const models::TagsSet kDriverTags = {"tag1", "tag2"};
const models::TagsSet kDriverTagsNoIntersect = {"tag404"};

const std::vector<std::string> kTariffClasses = {"economy"};
const std::vector<std::string> kTariffClassesNoIntersect = {"courier",
                                                            "delivery"};
const std::set<std::string> kActiveTariffs =
    std::set<std::string>(kTariffClasses.cbegin(), kTariffClasses.cend());

const std::vector<bs::DailyGuaranteeRule> kNmfgRules = {
    MakeNmfgRule(Branding::kNoFullBranding, "id1", {"tag1"}, std::nullopt),
    MakeNmfgRule(Branding::kSticker, "id2", {"tag2"}, std::nullopt),
    MakeNmfgRule(Branding::kFullBranding, "id3", {"tag3"}, std::nullopt),
};

const std::vector<bs::DailyGuaranteeRule> kNmfgRulesWithTariffs = {
    MakeNmfgRule(Branding::kNoFullBranding, "id1", {}, kTariffClasses),
    MakeNmfgRule(Branding::kNoFullBranding, "id2", {"tag1"},
                 kTariffClassesNoIntersect),
};

const std::vector<NmfgData> NmfgDataVariants = {
    {kNmfgRules, kDriverTags, "id2", kActiveTariffs, false},
    {kNmfgRules, kDriverTagsNoIntersect, std::nullopt, kActiveTariffs, false},
    {kNmfgRulesWithTariffs, kDriverTags, "id2", kActiveTariffs, false},
    {kNmfgRulesWithTariffs, kDriverTags, std::nullopt, kActiveTariffs, true},
};

INSTANTIATE_TEST_SUITE_P(GetBestDailyGuaranteeRule, NmfgDataParametrized,
                         ::testing::ValuesIn(NmfgDataVariants));

struct BestGoalData {
  GoalsWithProgress goals;
  std::optional<std::string> expected_rule_id;
};

DriverInfo CreateDefaultDriverInfo() {
  DriverInfo res;
  res.activity = 80;
  res.active_tariffs = {"econom"};
  return res;
}

const DriverInfo kDriverInfo = CreateDefaultDriverInfo();

class RequirementStrategyMock final : public handlers::RequirementStrategyBase {
 private:
  handlers::RequirementStatus CheckActivity(
      const handlers::GoalWithProgress& goal) const override {
    if (driver_info_.activity >= *goal.activity) {
      return handlers::RequirementStatus::kSatisfied;
    } else {
      return handlers::RequirementStatus::kViolated;
    }
  }
  handlers::RequirementStatus CheckBranding(
      const handlers::GoalWithProgress& /*goal*/) const override {
    return handlers::RequirementStatus::kSatisfied;
  }
  handlers::RequirementStatus CheckLocation(
      const handlers::GoalWithProgress& /*goal*/) const override {
    return handlers::RequirementStatus::kSatisfied;
  }
  handlers::RequirementStatus CheckTariff(
      const handlers::GoalWithProgress& goal) const override {
    auto mapped_goal_classes =
        sru::helpers::MapTariffClasses(goal.tariff_classes, config_);
    auto mapped_driver_classes =
        sru::helpers::MapTariffClasses(driver_info_.active_tariffs, config_) |
        ranges::ToSet;
    if (utils::ContainsIf(mapped_goal_classes,
                          [&mapped_driver_classes](const auto& tariff) {
                            return mapped_driver_classes.count(tariff);
                          })) {
      return handlers::RequirementStatus::kSatisfied;
    } else {
      return handlers::RequirementStatus::kViolated;
    }
  }

 public:
  explicit RequirementStrategyMock(const handlers::DriverInfo driver_info,
                                   const dynamic_config::Snapshot& config)
      : driver_info_(driver_info), config_(config) {}

  bool HasObstaclesToCompleteGoal(
      const handlers::GoalWithProgress& goal) const override {
    return !goal.IsCompleted() && !CheckAllRequirements(goal);
  }

 private:
  const handlers::DriverInfo driver_info_;
  const dynamic_config::Snapshot& config_;
};

struct BestGoalDataParametrizedOld
    : public ::testing::TestWithParam<BestGoalData> {};

TEST_P(BestGoalDataParametrizedOld, Variants) {
  const auto param = GetParam();
  const auto& config = dynamic_config::GetDefaultSnapshot();
  utils::datetime::MockNowSet(kMockNow);
  const bool use_new_goals_getbest_algorithm = false;
  const auto res = summary::GetBestGoalRule(
      param.goals, kDefaultTimeZone, summary::ScreensLinksSettings{},
      RequirementStrategyMock(kDriverInfo, config),
      use_new_goals_getbest_algorithm, {});
  const auto rule_id = res ? make_optional(res->GetRuleId()) : std::nullopt;
  ASSERT_EQ(rule_id, param.expected_rule_id);
}

struct GoalParams {
  std::string rule_id;
  bool is_future = false;
  bool matches_driver_info = true;
  bool is_active = false;
  size_t orders_to_next_step = 2;
  size_t progress = 0;
  int window = 2;
};

GoalWithProgress MakeGoalWithProgress(const GoalParams& params) {
  GoalWithProgress res;
  res.window = params.window;
  const auto driver_info = kDriverInfo;
  res.tariff_classes = driver_info.active_tariffs | ranges::ToUnorderedSet;
  res.activity = driver_info.activity;
  if (!params.matches_driver_info) {
    res.activity.value() += 1;
  }
  const auto time_zone = utils::MakeTimeZone(kDefaultTimeZone);
  cctz::civil_minute now_day(cctz::convert(kMockNow, time_zone));
  if (params.is_future) {
    now_day += 24 * 60;
  }
  res.schedule[cctz::civil_day(now_day)] = {
      {now_day - 5, now_day + params.is_active}};
  res.start = dt::Stringtime(params.is_future ? "2021-06-22T21:00:00Z"
                                              : "2021-06-21T21:00:00Z");
  res.rule_id = params.rule_id;
  res.progress = params.progress;
  res.goal_steps = {{params.progress + params.orders_to_next_step, "100"}};

  return res;
}

GoalWithProgress CreateActiveRule(std::string_view rule_id, size_t progress,
                                  size_t orders_to_next_step, int window = 2) {
  GoalParams params;
  params.rule_id = rule_id;
  params.orders_to_next_step = orders_to_next_step;
  params.progress = progress;
  params.window = window;
  params.is_active = true;
  params.is_future = false;
  params.matches_driver_info = true;
  return MakeGoalWithProgress(params);
}

GoalWithProgress CreateNotActiveRule(std::string_view rule_id,
                                     size_t progress) {
  GoalParams params;
  params.rule_id = rule_id;
  params.orders_to_next_step = 2;
  params.progress = progress;
  params.window = 2;
  params.is_active = false;
  params.is_future = false;
  params.matches_driver_info = true;
  return MakeGoalWithProgress(params);
}

GoalWithProgress CreateFutureRule(std::string_view rule_id,
                                  bool matches_driver_params) {
  GoalParams params;
  params.rule_id = rule_id;
  params.orders_to_next_step = 2;
  params.progress = 0;
  params.window = 2;
  params.is_active = false;
  params.is_future = true;
  params.matches_driver_info = matches_driver_params;
  return MakeGoalWithProgress(params);
}

const GoalWithProgress kTodayActiveRuleWithProgress =
    CreateActiveRule("id1", 1, 1, 2);
const GoalWithProgress kTodayActiveRuleWithProgress2 =
    CreateActiveRule("id2", 1, 2, 2);
const GoalWithProgress kTodayActiveRuleWithProgress3 =
    CreateActiveRule("id3", 1, 2, 3);
const GoalWithProgress kTodayActiveRuleWithoutProgress =
    CreateActiveRule("id4", 0, 2, 3);
const GoalWithProgress kTodayNotActiveRuleWithProgress =
    CreateNotActiveRule("id5", 1);
const GoalWithProgress kTodayNotActiveRuleWithoutProgress =
    CreateNotActiveRule("id6", 0);
const GoalWithProgress kFutureRuleMatchesDriverInfo =
    CreateFutureRule("id7", true);
const GoalWithProgress kFutureRuleNotMatchesDriverInfo =
    CreateFutureRule("id8", false);

const GoalsWithProgress kAllRules = {
    kTodayActiveRuleWithProgress,       kTodayActiveRuleWithoutProgress,
    kTodayActiveRuleWithProgress2,      kTodayNotActiveRuleWithProgress,
    kTodayNotActiveRuleWithoutProgress, kFutureRuleMatchesDriverInfo,
    kFutureRuleNotMatchesDriverInfo};

const GoalsWithProgress kActiveRules = {
    kTodayActiveRuleWithProgress, kTodayActiveRuleWithoutProgress,
    kTodayActiveRuleWithProgress2, kTodayNotActiveRuleWithProgress,
    kTodayNotActiveRuleWithoutProgress};

const GoalsWithProgress kNotActiveRules = {
    kTodayNotActiveRuleWithProgress, kTodayNotActiveRuleWithoutProgress,
    kFutureRuleMatchesDriverInfo, kFutureRuleNotMatchesDriverInfo};

const GoalsWithProgress kFutureRules = {kFutureRuleMatchesDriverInfo,
                                        kFutureRuleNotMatchesDriverInfo};

const GoalsWithProgress kActiveRulesWithSameProgressAndOrdersToNextStep = {
    kTodayActiveRuleWithProgress2, kTodayActiveRuleWithProgress3};

const GoalsWithProgress kGoalsWithProgress = {
    kTodayActiveRuleWithProgress, kTodayActiveRuleWithProgress2,
    kTodayActiveRuleWithProgress3, kTodayNotActiveRuleWithProgress};

const GoalsWithProgress kGoalsWithoutProgress = {
    kTodayActiveRuleWithoutProgress, kTodayNotActiveRuleWithoutProgress};

const std::vector<BestGoalData> BestGoalVariantsOld = {
    {kAllRules, "id1"},
    {kActiveRules, "id1"},
    {kNotActiveRules, "id5"},
    {kFutureRules, "id7"},
    {kActiveRulesWithSameProgressAndOrdersToNextStep, "id2"},
    {kGoalsWithProgress, "id1"},
    {kGoalsWithoutProgress, "id4"},
    {{}, std::nullopt}};

INSTANTIATE_TEST_SUITE_P(GetBestGoalRule, BestGoalDataParametrizedOld,
                         ::testing::ValuesIn(BestGoalVariantsOld));

const auto kNow = dt::Stringtime("2022-01-11T15:00:00Z");
const auto kTimeZoneName = "UTC";

struct BestGoalDataParametrizedNew
    : public ::testing::TestWithParam<BestGoalData> {};

TEST_P(BestGoalDataParametrizedNew, Variants) {
  const auto param = GetParam();
  const auto& config = dynamic_config::GetDefaultSnapshot();
  utils::datetime::MockNowSet(kNow);
  const bool use_new_goals_getbest_algorithm = true;
  const auto res = summary::GetBestGoalRule(
      param.goals, kTimeZoneName, summary::ScreensLinksSettings{},
      RequirementStrategyMock(kDriverInfo, config),
      use_new_goals_getbest_algorithm, {});
  const auto rule_id = res ? make_optional(res->GetRuleId()) : std::nullopt;
  ASSERT_EQ(rule_id, param.expected_rule_id);
}

const auto time_zone = utils::MakeTimeZone(kTimeZoneName);
const cctz::civil_minute now_minute(cctz::convert(kNow, time_zone));
const cctz::civil_day today(now_minute);

GoalWithProgress MakeCompleteGoal() {
  GoalWithProgress goal;
  goal.rule_id = "complete";
  goal.progress = 1;
  goal.goal_steps = {{1, "88"}};
  goal.schedule = {{today, {{today, today + 1}}}};
  return goal;
}

GoalWithProgress MakeIncompleteAndEndedGoal() {
  GoalWithProgress goal;
  goal.rule_id = "incomplete_and_ended";
  goal.progress = 0;
  goal.goal_steps = {{1, "88"}};
  const cctz::civil_minute begin_of_day(today);
  goal.schedule = {{today, {{begin_of_day, begin_of_day + 1}}}};
  return goal;
}

GoalWithProgress MakeIncompleAndActiveGoal() {
  GoalWithProgress goal;
  goal.rule_id = "incomplete_and_active";
  goal.progress = 0;
  goal.goal_steps = {{1, "88"}};
  goal.schedule = {{today, {{today, today + 1}}}};
  goal.activity = 0;
  goal.tariff_classes = {"econom"};
  return goal;
}

const auto kCompleteGoal = MakeCompleteGoal();
const auto kIncompleteEndedGoal = MakeIncompleteAndEndedGoal();
const auto kIncompleteAndActiveGoal = MakeIncompleAndActiveGoal();

const std::vector<BestGoalData> BestGoalVariantsNew = {
    {{kIncompleteAndActiveGoal, kCompleteGoal, kIncompleteEndedGoal},
     kIncompleteAndActiveGoal.rule_id},
    {{kIncompleteAndActiveGoal, kCompleteGoal},
     kIncompleteAndActiveGoal.rule_id},
    {{kIncompleteAndActiveGoal, kIncompleteEndedGoal},
     kIncompleteAndActiveGoal.rule_id},
    {{kIncompleteAndActiveGoal}, kIncompleteAndActiveGoal.rule_id},
    {{kCompleteGoal, kIncompleteEndedGoal}, kCompleteGoal.rule_id},
    {{kCompleteGoal}, kCompleteGoal.rule_id},
    {{kIncompleteEndedGoal}, kIncompleteEndedGoal.rule_id}};

INSTANTIATE_TEST_SUITE_P(GetBestGoalRule, BestGoalDataParametrizedNew,
                         ::testing::ValuesIn(BestGoalVariantsNew));

}  // namespace tests
