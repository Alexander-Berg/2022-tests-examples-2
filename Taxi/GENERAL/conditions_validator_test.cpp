#include "conditions_validator.hpp"

#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include <discounts/models/error.hpp>
#include <discounts/models/names.hpp>

#include <models/names.hpp>

TEST(ConditionsValidator, NoValidators) {
  EXPECT_NO_THROW(
      models::ConditionsValidator{{}}.Validate(rules_match::RuleConditions{}));
}

TEST(ConditionsValidator, NoConditions) {
  models::ConditionsValidator conditions_validator{
      {[](const rules_match::RuleConditions&) { throw std::exception{}; }}};
  EXPECT_THROW(conditions_validator.Validate(rules_match::RuleConditions{}),
               std::exception);
}

TEST(ConditionsValidator, NotEmptyValidator) {
  const auto& validator = models::MakeNotEmptyValidator();

  rules_match::RuleConditions conditions;
  conditions.Set(
      {handlers::libraries::discounts_match::MatchComplexCondition{
           "some_condition",
           {std::vector<handlers::libraries::discounts_match::EmptyValue>{}}},
       {}});
  EXPECT_THROW(validator(conditions), discounts::models::Error);

  conditions.Set({handlers::libraries::discounts_match::MatchComplexCondition{
                      "some_condition", {std::vector<int64_t>{1}}},
                  {}});
  EXPECT_NO_THROW(validator(conditions));
}

TEST(ConditionsValidator, ActivePeriodValidator) {
  const auto& validator = models::MakeActivePeriodValidator();

  rules_match::RuleConditions conditions;
  EXPECT_THROW(validator(conditions), discounts::models::Error);

  conditions.Set({handlers::libraries::discounts_match::MatchComplexCondition{
                      discounts::models::names::conditions::kActivePeriod,
                      {std::vector<int64_t>{1}}},
                  {}});
  EXPECT_THROW(validator(conditions), discounts::models::Error);

  conditions.Set(
      {handlers::libraries::discounts_match::MatchComplexCondition{
           discounts::models::names::conditions::kActivePeriod,
           {std::vector<
               handlers::libraries::discounts_match::TimeRangeValue>{}}},
       {}});
  EXPECT_THROW(validator(conditions), discounts::models::Error);

  conditions.Set(
      {handlers::libraries::discounts_match::MatchComplexCondition{
           discounts::models::names::conditions::kActivePeriod,
           {std::vector<handlers::libraries::discounts_match::TimeRangeValue>{
               {}, {}}}},
       {}});
  EXPECT_THROW(validator(conditions), discounts::models::Error);

  conditions.Set(
      {handlers::libraries::discounts_match::MatchComplexCondition{
           discounts::models::names::conditions::kActivePeriod,
           {std::vector<handlers::libraries::discounts_match::TimeRangeValue>{
               {{}, true, {}, false}}}},
       {}});
  EXPECT_THROW(validator(conditions), discounts::models::Error);

  conditions.Set(
      {handlers::libraries::discounts_match::MatchComplexCondition{
           discounts::models::names::conditions::kActivePeriod,
           {std::vector<handlers::libraries::discounts_match::TimeRangeValue>{
               {{}, false, {}, true}}}},
       {}});
  EXPECT_THROW(validator(conditions), discounts::models::Error);

  conditions.Set(
      {handlers::libraries::discounts_match::MatchComplexCondition{
           discounts::models::names::conditions::kActivePeriod,
           {std::vector<handlers::libraries::discounts_match::TimeRangeValue>{
               {{}, false, {}, false}}}},
       {}});
  EXPECT_THROW(validator(conditions), discounts::models::Error);

  conditions.Set(
      {handlers::libraries::discounts_match::MatchComplexCondition{
           discounts::models::names::conditions::kActivePeriod,
           {std::vector<handlers::libraries::discounts_match::TimeRangeValue>{
               {{}, true, {}, true}}}},
       {}});
  EXPECT_NO_THROW(validator(conditions));
}

TEST(ConditionsValidator, TimeValidator) {
  std::chrono::seconds minimum_time_delta{1};

  const auto& validator = models::MakeTimeValidator(minimum_time_delta);

  rules_match::RuleConditions conditions;

  auto now = utils::datetime::MockNow();
  auto minimum_time = now + minimum_time_delta;

  conditions.Set(
      {handlers::libraries::discounts_match::MatchComplexCondition{
           discounts::models::names::conditions::kActivePeriod,
           {std::vector<handlers::libraries::discounts_match::TimeRangeValue>{
               {minimum_time - std::chrono::seconds{1}, true,
                minimum_time + std::chrono::seconds{1}, true}}}},
       {}});
  EXPECT_THROW(validator(conditions), discounts::models::Error);

  conditions.Set(
      {handlers::libraries::discounts_match::MatchComplexCondition{
           discounts::models::names::conditions::kActivePeriod,
           {std::vector<handlers::libraries::discounts_match::TimeRangeValue>{
               {minimum_time, true, minimum_time + std::chrono::seconds{1},
                true}}}},
       {}});
  EXPECT_THROW(validator(conditions), discounts::models::Error);

  conditions.Set(
      {handlers::libraries::discounts_match::MatchComplexCondition{
           discounts::models::names::conditions::kActivePeriod,
           {std::vector<handlers::libraries::discounts_match::TimeRangeValue>{
               {minimum_time + std::chrono::seconds{1}, true,
                minimum_time + std::chrono::seconds{2}, true}}}},
       {}});
  EXPECT_NO_THROW(validator(conditions));
}

TEST(ConditionsValidator, ShippingTypeValidator) {
  const auto kDelivery = "delivery";
  const auto kPickup = "pickup";
  const auto kWrong = "wrong";

  const auto& validator = models::MakeShippingTypeValidator();
  rules_match::RuleConditions conditions;

  conditions.Set({handlers::libraries::discounts_match::MatchComplexCondition{
                      models::names::conditions::kShippingType,
                      {std::vector<std::string>{kDelivery}}},
                  {}});
  EXPECT_NO_THROW(validator(conditions));

  conditions.Set({handlers::libraries::discounts_match::MatchComplexCondition{
                      models::names::conditions::kShippingType,
                      {std::vector<std::string>{kPickup, kDelivery}}},
                  {}});
  EXPECT_NO_THROW(validator(conditions));

  conditions.Set({handlers::libraries::discounts_match::MatchComplexCondition{
                      models::names::conditions::kShippingType,
                      {std::vector<std::string>{kWrong}}},
                  {}});
  EXPECT_THROW(validator(conditions), discounts::models::Error);

  conditions.Set({handlers::libraries::discounts_match::MatchComplexCondition{
                      models::names::conditions::kShippingType,
                      {std::vector<std::string>{kPickup, kWrong}}},
                  {}});
  EXPECT_THROW(validator(conditions), discounts::models::Error);
}
