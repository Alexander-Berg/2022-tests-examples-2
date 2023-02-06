#include <models/priorities/find_achievable.hpp>
#include <models/priorities/find_matching.hpp>
#include <taxi_config/definitions/driver_priority_profession_names.hpp>

#include <gtest/gtest.h>

#include "common.hpp"

TEST(TagsRankedRule, MatchAndAchieve) {
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

  PriorityRule rule{
      RankedRule{{TagRule{"benua", {10}}, TagRule{"developer", {9}},
                  TagRule{"director", {20}}}}};

  auto matched = std::visit(find_matching, rule);
  ASSERT_TRUE(matched);

  const views::Priority dev_priority{"developer", 9, kValidLimited};
  ASSERT_EQ(dev_priority, *matched);

  auto achievable = std::visit(find_achievable, rule);
  ASSERT_TRUE(achievable);
  // already a developer, not yet a director: 20 - 9 == 11
  const views::Priority director_priority{"director", 11, 20};
  ASSERT_EQ(director_priority, achievable);

  rule = RankedRule{{TagRule{"aurora", {9}}, TagRule{"alaska", {10}},
                     TagRule{"siettle", {-10}}}};
  ASSERT_FALSE(std::visit(find_matching, rule));
  achievable = std::visit(find_achievable, rule);
  ASSERT_TRUE(achievable);

  views::Priority achievable_priority{"aurora", 9};
  ASSERT_EQ(achievable_priority, *achievable);

  rule = RankedRule{{TagRule{"washington", {11}}, TagRule{"benua", {10}},
                     TagRule{"morozov", {8}}}};
  matched = std::visit(find_matching, rule);
  ASSERT_TRUE(matched);

  const views::Priority benua_priority{"benua", 10};
  ASSERT_EQ(benua_priority, matched);

  achievable = std::visit(find_achievable, rule);
  // next achievable priority has lesser value so shouldn't be shown to driver
  ASSERT_FALSE(achievable);
}
