#include <gtest/gtest.h>

#include "utils/suggested_tariffs.hpp"

namespace {

namespace st = utils::suggested_tariffs;
namespace sti = utils::suggested_tariffs::internal;

models::geo::GeoAddress CreateGeoAddress(
    const std::string& title, const std::optional<std::string>& type,
    const std::optional<std::vector<std::string>>& rubrics,
    const std::optional<std::vector<std::string>>& tags,
    const std::optional<handlers::SuggestAction> action =
        handlers::SuggestAction::kSearch) {
  models::geo::GeoAddress address;

  address.suggest_action = action;
  address.title.text = title;
  address.type = type;

  if (rubrics.has_value()) {
    address.geo_object = clients::yamaps::GeoObject{};

    for (const auto& rubric : rubrics.value()) {
      address.geo_object->rubrics.push_back({rubric, rubric, std::nullopt});
    }
  }

  address.tags = tags;

  return address;
}

}  // namespace

TEST(TestSuggestedTariffs, TestRuleMatching) {
  sti::MatchingRule rule{"id",           st::HandlerType::kSuggest,
                         "organization", {{"rubric_med"}},
                         {{"medicine"}}, {{{"ru", {"детск"}}}}};

  ASSERT_TRUE(sti::IsItemMatched(
      CreateGeoAddress("Детская поликлиника", "organization", {{"rubric_med"}},
                       {{"some_tag", "medicine"}}),
      rule, "ru", st::HandlerType::kSuggest));

  ASSERT_FALSE(sti::IsItemMatched(
      CreateGeoAddress("Поликлиника", "organization", {{"rubric_med"}},
                       {{"some_tag", "medicine"}}),
      rule, "ru", st::HandlerType::kSuggest));

  ASSERT_FALSE(sti::IsItemMatched(
      CreateGeoAddress("Детская поликлиника", std::nullopt, {{"rubric_med"}},
                       {{"some_tag", "medicine"}}),
      rule, "ru", st::HandlerType::kSuggest));

  ASSERT_FALSE(sti::IsItemMatched(
      CreateGeoAddress("Детская поликлиника", "unknown", {{"rubric_med"}},
                       {{"some_tag", "medicine"}}),
      rule, "ru", st::HandlerType::kSuggest));

  ASSERT_FALSE(
      sti::IsItemMatched(CreateGeoAddress("Детская поликлиника", "organization",
                                          {{"some_rubric"}}, {{"medicine"}}),
                         rule, "ru", st::HandlerType::kSuggest));

  ASSERT_FALSE(
      sti::IsItemMatched(CreateGeoAddress("Детская поликлиника", "organization",
                                          {{"rubric_med"}}, {{"some_tag"}}),
                         rule, "ru", st::HandlerType::kSuggest));

  ASSERT_FALSE(
      sti::IsItemMatched(CreateGeoAddress("Детская поликлиника", "organization",
                                          {{"rubric_med"}}, {{"medicine"}}),
                         rule, "ru", st::HandlerType::kZerosuggest));
}

TEST(TestSuggestedTariffs, TestRulesMatching) {
  std::vector<sti::MatchingRule> rules{{"id1",
                                        st::HandlerType::kZerosuggest,
                                        "organization",
                                        {{"rubric_med"}},
                                        {{"medicine"}},
                                        {{{"ru", {"детск"}}}}},
                                       {"id2",
                                        std::nullopt,
                                        "organization",
                                        std::nullopt,
                                        {{"baby shop"}},
                                        {{{"en", {"shop"}}}}}};

  ASSERT_TRUE(sti::IsItemMatched(
      CreateGeoAddress("Детская поликлиника", "organization", {{"rubric_med"}},
                       {{"medicine"}}, handlers::SuggestAction::kSearch),
      rules, "ru", "uberkids", st::HandlerType::kZerosuggest));
  ASSERT_TRUE(sti::IsItemMatched(
      CreateGeoAddress("BabySHOP", "organization", {{"some_rubric"}},
                       {{"baby shop"}}, handlers::SuggestAction::kSearch),
      rules, "en", "uberkids", st::HandlerType::kSuggest));
  ASSERT_TRUE(sti::IsItemMatched(
      CreateGeoAddress("BabySHOP", "organization", {{"some_rubric"}},
                       {{"baby shop"}}, handlers::SuggestAction::kSearch),
      rules, "en", "uberkids", st::HandlerType::kZerosuggest));
  ASSERT_TRUE(sti::IsItemMatched(
      CreateGeoAddress("BabySHOP", "organization", {{"rubric_med"}},
                       {{"baby shop"}}, std::nullopt),
      rules, "en", "uberkids", st::HandlerType::kSuggest));

  ASSERT_FALSE(sti::IsItemMatched(
      CreateGeoAddress("Детская поликлиника", "organization", {{"rubric_med"}},
                       {{"medicine"}}, handlers::SuggestAction::kSubstitute),
      rules, "ru", "uberkids", st::HandlerType::kZerosuggest));
  ASSERT_FALSE(sti::IsItemMatched(
      CreateGeoAddress("BabySHOP", "organization", {{"rubric_med"}},
                       {{"baby shop"}}, handlers::SuggestAction::kMapSearch),
      rules, "en", "uberkids", st::HandlerType::kSuggest));
  ASSERT_FALSE(sti::IsItemMatched(
      CreateGeoAddress("BabySHOP", "organization", {{"rubric_med"}}, {{"shop"}},
                       handlers::SuggestAction::kSearch),
      rules, "en", "uberkids", st::HandlerType::kZerosuggest));
}
