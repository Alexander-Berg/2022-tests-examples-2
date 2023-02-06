#include <models/priorities/find_achievable.hpp>
#include <models/priorities/find_matching.hpp>
#include <taxi_config/definitions/driver_priority_profession_names.hpp>

#include <gtest/gtest.h>

#include "common.hpp"

TEST(TagsExcludingRule, MatchAndAchieve) {
  using namespace models;
  using namespace handlers;
  using Priority = views::Priority;
  using taxi_config::driver_priority_profession_names::ProfessionName;

  const DriverInfo driver_info{kTagsInfo,    ProfessionName::kTaxi,
                               std::nullopt, std::nullopt,
                               std::nullopt, std::nullopt};
  const priorities::FindMatching find_matching{
      driver_info, priorities::ValueDestination::kBackend};
  const priorities::FindAchievable find_achievable{
      driver_info, priorities::ValueDestination::kBackend};

  PriorityRule rule =
      ExcludingRule{{TagRule{"benua", {10}}, TagRule{"aurora", {9}}}};

  auto matched = std::visit(find_matching, rule);
  ASSERT_TRUE(matched);

  const Priority kBenuaPriority{"benua", 10};
  ASSERT_EQ(kBenuaPriority, *matched);

  // already matched benua
  ASSERT_FALSE(std::visit(find_achievable, rule));

  rule = ExcludingRule{{TagRule{"aurora", {9}}, TagRule{"siettle", {-10}}}};
  ASSERT_FALSE(std::visit(find_matching, rule));
  auto achievable = std::visit(find_achievable, rule);
  ASSERT_TRUE(achievable);

  // negative priority shouldn't be achievable, siettle was ignored
  Priority achievable_priority{"", 9};
  ASSERT_EQ(achievable_priority, *achievable);

  rule = ExcludingRule{{TagRule{"aurora", {9}}, TagRule{"morozov", {8}}}};
  ASSERT_FALSE(std::visit(find_matching, rule));
  achievable = std::visit(find_achievable, rule);
  ASSERT_TRUE(achievable);

  // minimal rule is achievable
  achievable_priority = Priority{"", 8};
  ASSERT_EQ(achievable_priority, *achievable);

  rule = ExcludingRule{{TagRule{"developer", {0}}, TagRule{"morozov", {8}},
                        TagRule{"benua", {10}}}};
  matched = std::visit(find_matching, rule);
  ASSERT_TRUE(matched);

  const Priority kDeveloperPriority{"developer", 0, kValidLimited};
  ASSERT_EQ(kDeveloperPriority, matched);
  ASSERT_FALSE(std::visit(find_achievable, rule));
}
