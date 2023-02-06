#include <models/priorities/find_matching_ttl.hpp>
#include <taxi_config/definitions/driver_priority_profession_names.hpp>

#include <gtest/gtest.h>

#include "common.hpp"

namespace {

using ValueAttributeRule = handlers::Value;
using AllOfAttributeRule = handlers::AllOf;
using AnyOfAttributeRule = handlers::AnyOf;
using NoneOfAttributeRule = handlers::NoneOf;

using RulesVariant = std::variant<ValueAttributeRule, NoneOfAttributeRule,
                                  AllOfAttributeRule, AnyOfAttributeRule>;

using taxi_config::driver_priority_profession_names::ProfessionName;

template <typename Rule>
void CheckRule(const std::vector<std::string>& tags, bool result) {
  static const models::DriverInfo driver_info{
      kTagsInfo,    ProfessionName::kTaxi, std::nullopt,
      std::nullopt, std::nullopt,          std::nullopt};

  static const models::priorities::FindMatchingTtl property_checker{
      driver_info};

  RulesVariant rule{Rule{tags}};
  ASSERT_EQ(std::visit(property_checker, rule).has_value(), result);
}

}  // namespace

TEST(AchievableRule, VisitAchievableRuleBool) {
  const models::DriverInfo driver_info{kTagsInfo,    ProfessionName::kTaxi,
                                       std::nullopt, std::nullopt,
                                       std::nullopt, std::nullopt};
  const models::priorities::FindMatchingTtl property_checker{driver_info};

  RulesVariant rule;
  rule = ValueAttributeRule{true};
  ASSERT_TRUE(std::visit(property_checker, rule).has_value());
  rule = ValueAttributeRule{false};
  ASSERT_FALSE(std::visit(property_checker, rule).has_value());
}

TEST(AchievableRule, VisitAchievableRuleAlgorithm) {
  CheckRule<AllOfAttributeRule>({"benua", "developer"}, true);
  CheckRule<AllOfAttributeRule>({"benua", "avrora"}, false);
  CheckRule<AnyOfAttributeRule>({"yandex", "google", "yahoo"}, true);
  CheckRule<AnyOfAttributeRule>({"mail.ru", "google", "yahoo"}, false);
  CheckRule<NoneOfAttributeRule>({"vk", "mail.ru"}, true);
  CheckRule<NoneOfAttributeRule>({"developer", "data_miner"}, false);
}
