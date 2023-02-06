#include <gtest/gtest.h>

#include <userver/utils/algo.hpp>

#include "common.hpp"

#include <db/types.hpp>
#include <logic/update_schedules.hpp>
#include <models/types.hpp>

using namespace logic;
using namespace logic::impl;

namespace {

struct TestParams {
  GroupedTags new_tags;
  GroupedAffectedSchedules current_affected_schedules;
  std::vector<db::NewAffectedSchedulesData> new_affected_schedules;
};

GroupedAffectedSchedules CreateAffected(
    const std::map<models::ScheduleParameters, std::vector<models::TagsSet>>&
        grouped_tags) {
  GroupedAffectedSchedules grouped_affected;
  int64_t idx = 0;
  for (const auto& [group, tag_sets] : grouped_tags) {
    auto& affected = grouped_affected[group];
    for (const auto& tags : tag_sets) {
      db::AffectedScheduleTagged sch;
      sch.idx = idx++;
      sch.zone = group.zone;
      sch.tariff_class = group.tariff_class;
      sch.rule_type = group.rule_type;
      sch.tags = utils::AsContainer<std::vector<std::string>>(tags);
      affected.push_back(std::move(sch));
    }
  }
  return grouped_affected;
}

}  // namespace

struct AppendNewTagsTestParametrized : public BaseTestWithParam<TestParams> {};

TEST_P(AppendNewTagsTestParametrized, Test) {
  const auto new_affected = MakeNewSchedulesWithNewTags(
      GetParam().new_tags, GetParam().current_affected_schedules);
  ASSERT_EQ(new_affected, GetParam().new_affected_schedules);
}

static const auto kMoscowEco =
    models::ScheduleParameters{"moscow", "eco", models::RuleType::kSingleRide};
static const auto kSpbEco =
    models::ScheduleParameters{"spb", "eco", models::RuleType::kSingleRide};
static const auto kSpbComfortPlus = models::ScheduleParameters{
    "spb", "comfortplus", models::RuleType::kSingleRide};

static const GroupedTags kEmptyNewTags = {};
static const GroupedAffectedSchedules kEmptyAffected = {};
static const std::vector<db::NewAffectedSchedulesData> kEmptyResult = {};

INSTANTIATE_TEST_SUITE_P(AppendNewTagsTestParametrized,
                         AppendNewTagsTestParametrized,
                         ::testing::ValuesIn({
                             TestParams{
                                 kEmptyNewTags,
                                 kEmptyAffected,
                                 kEmptyResult,
                             },
                             TestParams{
                                 kEmptyNewTags,
                                 CreateAffected({
                                     {
                                         kMoscowEco,
                                         {},
                                     },
                                 }),
                                 kEmptyResult,
                             },
                             TestParams{
                                 kEmptyNewTags,
                                 CreateAffected({
                                     {
                                         kMoscowEco,
                                         {
                                             {
                                                 "eco_t1",
                                                 "eco_t2",
                                             },
                                         },
                                     },
                                 }),
                                 kEmptyResult,
                             },
                             TestParams{
                                 {
                                     {
                                         kMoscowEco,
                                         {
                                             "eco_n1",
                                             "eco_n2",
                                         },
                                     },
                                 },
                                 CreateAffected({
                                     {
                                         kMoscowEco,
                                         {
                                             {
                                                 "eco_t1",
                                             },
                                             {
                                                 "eco_t1",
                                             },
                                         },
                                     },
                                 }),
                                 {
                                     {
                                         0,
                                         {
                                             "eco_t1",
                                             "eco_n1",
                                         },
                                     },
                                     {
                                         1,
                                         {
                                             "eco_t1",
                                             "eco_n1",
                                         },
                                     },
                                     {
                                         0,
                                         {
                                             "eco_t1",
                                             "eco_n2",
                                         },
                                     },
                                     {
                                         1,
                                         {
                                             "eco_t1",
                                             "eco_n2",
                                         },
                                     },
                                 },
                             },
                             TestParams{
                                 {
                                     {
                                         kMoscowEco,
                                         {
                                             "eco_n1",
                                         },
                                     },
                                     {
                                         kSpbEco,
                                         {
                                             "eco_n10",
                                         },
                                     },
                                     {
                                         kSpbComfortPlus,
                                         {
                                             "c+_n1",
                                             "c+_n2",
                                         },
                                     },
                                 },
                                 CreateAffected({
                                     {
                                         kMoscowEco,
                                         {
                                             {
                                                 "eco_t1",
                                             },
                                             {},
                                         },
                                     },
                                     {
                                         kSpbEco,
                                         {
                                             {
                                                 "eco_t10",
                                             },
                                             {
                                                 "eco_t20",
                                             },
                                         },
                                     },
                                     {
                                         kSpbComfortPlus,
                                         {
                                             {
                                                 "c+_t1",
                                             },
                                             {},
                                         },
                                     },
                                 }),
                                 {
                                     {
                                         0,
                                         {
                                             "c+_t1",
                                             "c+_n1",
                                         },
                                     },
                                     {
                                         1,
                                         {
                                             "c+_n1",
                                         },
                                     },
                                     {
                                         0,
                                         {
                                             "c+_t1",
                                             "c+_n2",
                                         },
                                     },
                                     {
                                         1,
                                         {
                                             "c+_n2",
                                         },
                                     },
                                     {
                                         2,
                                         {
                                             "eco_t1",
                                             "eco_n1",
                                         },
                                     },
                                     {
                                         3,
                                         {
                                             "eco_n1",
                                         },
                                     },
                                     {
                                         4,
                                         {
                                             "eco_t10",
                                             "eco_n10",
                                         },
                                     },
                                     {
                                         5,
                                         {
                                             "eco_t20",
                                             "eco_n10",
                                         },
                                     },
                                 },
                             },
                         }));
