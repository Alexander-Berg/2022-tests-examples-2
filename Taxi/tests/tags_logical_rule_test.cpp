#include <variant>

#include <models/priorities/find_achievable.hpp>
#include <models/priorities/find_matching.hpp>
#include <taxi_config/definitions/driver_priority_profession_names.hpp>

#include <gtest/gtest.h>

#include "common.hpp"

TEST(TagsLogicalRule, Match) {
  using namespace models;
  using namespace handlers;
  using taxi_config::driver_priority_profession_names::ProfessionName;

  auto tags_info = kTagsInfo;
  tags_info["luxoft"] = models::TagInfo{kValidLimited, {}};
  const DriverInfo driver_info{tags_info,    ProfessionName::kTaxi,
                               std::nullopt, std::nullopt,
                               std::nullopt, std::nullopt};
  const priorities::FindMatching find_matching{
      driver_info, priorities::ValueDestination::kBackend};

  {
    const AndRule yandex_spb_taxi{
        {{AllOf{{"yandex", "developer"}}, NoneOf{{"benua"}}}}};
    TagRule tag_rule;
    tag_rule.tag_name = "taxi";
    tag_rule.priority_value = {10};
    tag_rule.override = {{yandex_spb_taxi}};

    ASSERT_FALSE(find_matching(SingleRule{tag_rule}));
  }

  {
    const auto yandex_spb_big =
        AndRule{{{AllOf{{"yandex", "developer"}}, AllOf{{"benua"}}}}};
    const PriorityRule rule =
        SingleRule{TagRule{"big", {10}, {{yandex_spb_big}}}};

    const auto result = std::visit(find_matching, rule);
    const views::Priority big_yandex_priority{"big", 10, kValidLimited};
    ASSERT_EQ(result, big_yandex_priority);
  }

  {
    const auto galera = OrRule{{{AllOf{{"webim"}}, AllOf{{"luxoft"}}}}};
    const PriorityRule rule = SingleRule{TagRule{"galera", {10}, {{galera}}}};
    const auto result = std::visit(find_matching, rule);
    const views::Priority galera_priority{"galera", 10, kValidLimited};
    ASSERT_EQ(result, galera_priority);
  }

  {
    const auto moscow_office =
        OrRule{{{AllOf{{"yandex", "moscow"}}, AllOf{{"kaspersky"}}}}};
    const PriorityRule rule =
        SingleRule{TagRule{"moscow", {10}, {{moscow_office}}}};
    ASSERT_FALSE(std::visit(find_matching, rule));
  }
}

TEST(TagsLogicalRule, FindAchievablePriority) {
  using namespace models;
  using namespace handlers;
  using taxi_config::driver_priority_profession_names::ProfessionName;

  DriverInfo driver_info{kTagsInfo,    ProfessionName::kTaxi, std::nullopt,
                         std::nullopt, std::nullopt,          std::nullopt};
  driver_info.tags_info["spb"] = models::TagInfo{kValidInfinity, {}};
  driver_info.tags_info["cto"] = models::TagInfo{kValidInfinity, {}};
  const priorities::FindAchievable find_achievable(
      driver_info, priorities::ValueDestination::kBackend);

  {
    const auto cool_developer = AllOf{{"developer"}};
    const auto developer_in_benua =
        AndRule{{{AllOf{{"developer"}}}, {AllOf{{"yandex", "spb"}}}}};
    const auto cto_in_benua = AndRule{{{AllOf{{"developer"}}},
                                       {AllOf{{"yandex", "spb"}}},
                                       {AllOf{{"director", "cto"}}}}};
    // although values from TagRules are not present in driver_info, these
    // tags should be considered as matched, because of logical rule
    const PriorityRule rule{RankedRule{
        {TagRule{"benua_in_developer", {10}, {{developer_in_benua}}},
         TagRule{"cool_developer", {9}, {{cool_developer}}},
         // driver does have tag cto, but he doesn't meet requirements from
         // logical rule, so this priority should be achievable, not matched
         TagRule{"cto", {20}, {{cto_in_benua}}}}}};

    const auto achievable = std::visit(find_achievable, rule);
    ASSERT_TRUE(achievable);
    // already a developer, not yet a cto: 20 - 9 == 11
    const views::Priority director_priority{"cto", 11, 20};
    ASSERT_EQ(director_priority, achievable);
  }
}
