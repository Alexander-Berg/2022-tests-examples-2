#include <models/priorities/find_achievable.hpp>
#include <models/priorities/find_matching.hpp>
#include <taxi_config/definitions/driver_priority_profession_names.hpp>

#include <gtest/gtest.h>

#include "common.hpp"

TEST(TagRule, VisitTagRule) {
  using namespace models;
  using namespace handlers;
  using taxi_config::driver_priority_profession_names::ProfessionName;

  const DriverInfo driver_info{kTagsInfo,    ProfessionName::kTaxi,
                               std::nullopt, std::nullopt,
                               std::nullopt, std::nullopt};
  const priorities::FindMatching find_matching{
      driver_info, priorities::ValueDestination::kBackend};
  const priorities::FindAchievable find_achievable{
      driver_info, priorities::ValueDestination::kBackend};

  PriorityRule rule = SingleRule{TagRule{"benua", {10}}};

  const auto matched = std::visit(find_matching, rule);
  ASSERT_TRUE(!!matched);

  const views::Priority kBenuaPriority{"benua", 10};
  ASSERT_EQ(kBenuaPriority, *matched);

  ASSERT_FALSE(std::visit(find_achievable, rule));

  rule = SingleRule{TagRule{"aurora", {9}}};
  ASSERT_FALSE(std::visit(find_matching, rule));
  const auto achievable = std::visit(find_achievable, rule);
  ASSERT_TRUE(achievable);

  const views::Priority kAuroraPriority{"aurora", 9};
  ASSERT_EQ(kAuroraPriority, *achievable);
}
