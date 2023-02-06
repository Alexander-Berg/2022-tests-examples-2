#include <models/experiment.hpp>
#include <models/preset.hpp>
#include <models/priority_cache.hpp>
#include <models/version.hpp>

#include <userver/dump/test_helpers.hpp>

#include <gtest/gtest.h>

namespace {

using namespace models;
using namespace db::experiment;
using namespace db::priority;
using namespace db::preset;

const std::string kRuleStr = R"(
{
  "single_rule": {
    "tag_name": "tag_name",
    "priority_value": {
      "backend": 0,
      "display": 0
    }
  }
}
)";

const std::string kPayloadStr = R"(
{
  "main_title": "main_title",
  "constructor": [
    {
      "numbered_list": [
        {"title": "title"}
      ]
    }
  ]
}
)";

const models::Rule kRule{formats::json::FromString(kRuleStr)};

const models::Payloads kPayloads{formats::json::FromString(kPayloadStr), {}};

const models::Conditions kConditions{{}, {}, {}};

CachedPriorityData MakePriorityData(const int32_t id, const std::string& name,
                                    const std::string& tanker_key) {
  return CachedPriorityData{PriorityId{id}, PriorityName{name}, tanker_key};
}

CachedPriorityGeoData MakePriorityGeoData(
    const int32_t id, const PrioritiesAgglomerations& agglomerations) {
  return CachedPriorityGeoData{PriorityId{id}, agglomerations};
}

CachedExperimentData MakeExperimentData(
    const int32_t id, const int32_t priority_id, const std::string& name,
    const std::unordered_set<std::string>& agglomerations) {
  return CachedExperimentData{ExperimentId{id}, PriorityId{priority_id},
                              ExperimentName{name}, agglomerations};
}

CachedPresetData MakePresetData(const int32_t id, const int32_t priority_id,
                                const std::string& name, const bool is_default,
                                const std::vector<std::string>& geo_nodes) {
  return CachedPresetData{PresetId{id}, PriorityId{priority_id},
                          PresetName{name}, is_default, geo_nodes};
}

std::pair<PresetId, PriorityVersionSettings> MakePrioritySettings(
    const int32_t preset_id, const int32_t version_id,
    const int32_t sort_order) {
  return std::pair<PresetId, PriorityVersionSettings>{
      PresetId{preset_id},
      PriorityVersionSettings{VersionId{version_id}, sort_order, kRule,
                              kPayloads, kConditions}};
}

std::pair<PriorityName, MatchedPriority> MakeMatchedPriority(
    const std::string& priority_name, const std::string& preset_name,
    const int32_t version_id, const std::string& tanker_key,
    const int32_t sort_order) {
  const auto priority_settings =
      std::make_shared<MatchedSettings>(MatchedSettings{VersionId{version_id},
                                                        PresetName{preset_name},
                                                        sort_order,
                                                        {},
                                                        {},
                                                        {}});
  return std::pair<PriorityName, MatchedPriority>{
      PriorityName{priority_name},
      MatchedPriority{tanker_key, priority_settings}};
}

bool IsMatchedPrioritiesEqual(const MatchedPriorities& lhs,
                              const MatchedPriorities& rhs) {
  if (lhs.size() != rhs.size()) {
    return false;
  }

  auto lhs_it = lhs.begin();
  auto rhs_it = rhs.begin();
  while (lhs_it != lhs.end() && rhs_it != rhs.end()) {
    const auto& lhs_value = lhs_it->second;
    const auto& rhs_value = rhs_it->second;
    if (lhs_it->first != rhs_it->first ||
        lhs_value.tanker_keys_prefix != rhs_value.tanker_keys_prefix ||
        lhs_value.settings->sort_order != rhs_value.settings->sort_order) {
      return false;
    }
    ++rhs_it;
    ++lhs_it;
  }

  return true;
}

PriorityCache MakePriorityCache() {
  std::vector<CachedPriorityData> priority_data{
      MakePriorityData(0, "branding", "tk0"),
      MakePriorityData(1, "loyalty", "tk1"),
      MakePriorityData(2, "lightbox", "tk2")};

  std::vector<CachedPriorityGeoData> priorities_relations{
      MakePriorityGeoData(0, {{"br_russia", false},
                              {"br_moscow", true},
                              {"moscow", false},
                              {"msk", false}}),
      MakePriorityGeoData(1, {{"br_root", false}, {"br_usa", true}}),
      MakePriorityGeoData(2, {{"br_russia", false},
                              {"ehkspoforum", true},
                              {"spb_fan_zona", true}})};

  std::vector<CachedExperimentData> experiments_data{
      MakeExperimentData(0, 0, "exp_name", {"br_russia", "br_moscow"})};

  std::vector<CachedPresetData> presets_data{
      // branding
      MakePresetData(0, 0, "default", true, {}),
      MakePresetData(1, 0, "custom0", false, {"msk", "spb", "kaliningrad"}),
      MakePresetData(2, 0, "custom1", false, {"boryasvo", "moscow"}),
      // loyalty
      MakePresetData(3, 1, "default", true, {}),
      // lightbox
      MakePresetData(4, 2, "default", true, {}),
      MakePresetData(5, 2, "custom", false, {"spb", "spb_airport"})};

  std::unordered_map<PresetId, PriorityVersionSettings> presets_settings{
      MakePrioritySettings(0, 0, 1), MakePrioritySettings(1, 1, 2),
      MakePrioritySettings(2, 2, 3), MakePrioritySettings(3, 3, 4),
      MakePrioritySettings(4, 4, 5), MakePrioritySettings(5, 5, 6)};

  PriorityCache cache;

  cache.Apply(std::move(priority_data), std::move(priorities_relations),
              std::move(experiments_data), std::move(presets_data),
              std::move(presets_settings));

  return cache;
}

}  // namespace

TEST(PriorityCached, DumpRestore) {
  dump::TestWriteReadCycle(PriorityCache{});
  dump::TestWriteReadCycle(MakePriorityCache());
}

TEST(PriorityCached, FillAndMatch) {
  PriorityCache cache = MakePriorityCache();

  {
    // all
    const MatchedPriorities expected{
        MakeMatchedPriority("branding", "custom0", 1, "tk0", 2),
        MakeMatchedPriority("loyalty", "default", 3, "tk1", 4),
        MakeMatchedPriority("lightbox", "default", 4, "tk2", 5)};
    const MatchedPriorities result =
        cache.MatchPriorities({"msk", "br_moscow", "br_russia", "br_root"});

    ASSERT_TRUE(IsMatchedPrioritiesEqual(expected, result));
  }

  {
    // filter by agglomerations
    const MatchedPriorities expected{
        MakeMatchedPriority("loyalty", "custom", 5, "tk1", 4)};
    const MatchedPriorities result = cache.MatchPriorities({"spb", "br_root"});

    ASSERT_TRUE(IsMatchedPrioritiesEqual(expected, result));
  }

  {
    // non-default settings
    const MatchedPriorities expected{
        MakeMatchedPriority("branding", "custom0", 1, "tk0", 2),
        MakeMatchedPriority("loyalty", "default", 3, "tk1", 4),
        MakeMatchedPriority("lightbox", "custom", 5, "tk2", 6)};
    const MatchedPriorities result =
        cache.MatchPriorities({"spb", "br_russia", "br_root"});

    ASSERT_TRUE(IsMatchedPrioritiesEqual(expected, result));
  }

  {
    // filter by agglomerations and non-default settings
    const MatchedPriorities expected{
        MakeMatchedPriority("branding", "custom0", 1, "tk0", 2),
        MakeMatchedPriority("loyalty", "custom", 5, "tk1", 4)};
    const MatchedPriorities result =
        cache.MatchPriorities({"spb_fan_zona", "spb", "br_russia", "br_root"});

    ASSERT_TRUE(IsMatchedPrioritiesEqual(expected, result));
  }

  {
    // empty geo_nodes
    const MatchedPriorities expected{};
    const MatchedPriorities result = cache.MatchPriorities({});

    ASSERT_TRUE(IsMatchedPrioritiesEqual(expected, result));
  }

  {
    // unknown geo_node
    const MatchedPriorities expected{};
    const MatchedPriorities result = cache.MatchPriorities({"tula"});

    ASSERT_TRUE(IsMatchedPrioritiesEqual(expected, result));
  }
}
