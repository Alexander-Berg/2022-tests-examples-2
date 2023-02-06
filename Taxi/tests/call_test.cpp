#include <gtest/gtest.h>

#include <chrono>
#include <memory>

#include <testing/taxi_config.hpp>
#include <userver/engine/run_in_coro.hpp>
#include <userver/formats/json/string_builder.hpp>
#include <userver/utils/assert.hpp>

#include <taxi_config/variables/SUBVENTION_RULE_UTILS_DROP_ZERO_RULES.hpp>

#include "common.hpp"
#include "mocked_bsx.hpp"

#include <models/limiter.hpp>
#include <subvention_matcher/impl/impl.hpp>

using namespace subvention_matcher;
using namespace subvention_matcher::impl;

using PS = PropertySource;

TEST(ValidateSuitableRules, Test) {
  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{BrandingProperty{{false, false}}, PS::kDriver},  //
       {ActivityProperty{{50}}, PS::kDriver},            //
       {TagsProperty{{{"tag"}}}, PS::kDriver},           //
       {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
       {ZoneProperty{{"zone"}}, PS::kDriver},            //
       {ClassProperty{{"class"}}, PS::kDriver}}));

  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{BrandingProperty{{false, false}}, PS::kDriver},  //
       {ActivityProperty{{50}}, PS::kDriver},            //
       {TagsProperty{{{"tag"}}}, PS::kDriver},           //
       {GeoareaProperty{{std::nullopt}}, PS::kDriver},   //
       {ZoneProperty{{"zone"}}, PS::kDriver},            //
       {ClassProperty{{"class"}}, PS::kDriver}}));

  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{BrandingProperty{{false, false}}, PS::kDriver},  //
       {ActivityProperty{{50}}, PS::kDriver},            //
       {TagsProperty{{{"tag"}}}, PS::kDriver},           //
       {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
       {ZoneProperty{{"zone"}}, PS::kDriver},            //
       {ZoneProperty{{"zone2"}}, PS::kDriver},           //
       {ClassProperty{{"class"}}, PS::kDriver}}));

  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{BrandingProperty{{false, false}}, PS::kDriver},  //
       {ActivityProperty{{50}}, PS::kDriver},            //
       {TagsProperty{{{"tag"}}}, PS::kDriver},           //
       {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
       {ZoneProperty{{"zone"}}, PS::kDriver},            //
       {ClassProperty{{"class"}}, PS::kDriver},          //
       {ClassProperty{{"class2"}}, PS::kDriver}}));

  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{BrandingProperty{{false, false}}, PS::kDriver},  //
       {ActivityProperty{{50}}, PS::kDriver},            //
       {TagsProperty{{{"tag"}}}, PS::kDriver},           //
       {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
       {GeoareaProperty{{"geoarea2"}}, PS::kDriver},     //
       {ZoneProperty{{"zone"}}, PS::kDriver},            //
       {ClassProperty{{"class"}}, PS::kDriver}}));

  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{ActivityProperty{{50}}, PS::kDriver},        //
       {TagsProperty{{{"tag"}}}, PS::kDriver},       //
       {GeoareaProperty{{"geoarea"}}, PS::kDriver},  //
       {ZoneProperty{{"zone"}}, PS::kDriver},        //
       {ClassProperty{{"class"}}, PS::kDriver}}));

  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{TagsProperty{{{"tag"}}}, PS::kDriver},       //
       {GeoareaProperty{{"geoarea"}}, PS::kDriver},  //
       {ZoneProperty{{"zone"}}, PS::kDriver},        //
       {ClassProperty{{"class"}}, PS::kDriver}}));

  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{GeoareaProperty{{"geoarea"}}, PS::kDriver},  //
       {ZoneProperty{{"zone"}}, PS::kDriver},        //
       {ClassProperty{{"class"}}, PS::kDriver}}));

  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{ZoneProperty{{"zone"}}, PS::kDriver},  //
       {ClassProperty{{"class"}}, PS::kDriver}}));

  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{ZoneProperty{{"zone"}}, PS::kDriver}}));

  ASSERT_THROW(ValidateDriverPropertiesForSuitableRules({}),
               MissingRequiredPropertyError);

  ASSERT_THROW(ValidateDriverPropertiesForSuitableRules(
                   {{BrandingProperty{{false, false}}, PS::kDriver},  //
                    {BrandingProperty{{false, true}}, PS::kDriver},   //
                    {ActivityProperty{{50}}, PS::kDriver},            //
                    {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                    {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
                    {ZoneProperty{{"zone"}}, PS::kDriver},            //
                    {ClassProperty{{"class"}}, PS::kDriver}}),
               NotUniquePropertyError);

  ASSERT_THROW(ValidateDriverPropertiesForSuitableRules(
                   {{BrandingProperty{{false, false}}, PS::kDriver},  //
                    {ActivityProperty{{50}}, PS::kDriver},            //
                    {ActivityProperty{{40}}, PS::kDriver},            //
                    {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                    {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
                    {ZoneProperty{{"zone"}}, PS::kDriver},            //
                    {ClassProperty{{"class"}}, PS::kDriver}}),
               NotUniquePropertyError);

  ASSERT_THROW(ValidateDriverPropertiesForSuitableRules(
                   {{BrandingProperty{{false, false}}, PS::kDriver},  //
                    {ActivityProperty{{50}}, PS::kDriver},            //
                    {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                    {TagsProperty{{{"tag2"}}}, PS::kDriver},          //
                    {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
                    {ZoneProperty{{"zone"}}, PS::kDriver},            //
                    {ClassProperty{{"class"}}, PS::kDriver}}),
               NotUniquePropertyError);

  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{GeoareaProperty{{"geoarea"}}, PS::kDriver},  //
       {ZoneProperty{{"zone"}}, PS::kDriver}}));

  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{GeoareaProperty{{"geoarea"}}, PS::kDriver},   //
       {GeoareaProperty{{"geoarea2"}}, PS::kDriver},  //
       {ZoneProperty{{"zone"}}, PS::kDriver}}));

  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{ZoneProperty{{"zone"}}, PS::kDriver}}));
  ASSERT_NO_THROW(ValidateDriverPropertiesForSuitableRules(
      {{GeoareaProperty{{std::nullopt}}, PS::kDriver},  //
       {ZoneProperty{{"zone"}}, PS::kDriver}}));

  ASSERT_THROW(ValidateDriverPropertiesForSuitableRules(
                   {{GeoareaProperty{{std::nullopt}}, PS::kDriver},  //
                    {GeoareaProperty{{"geoarea"}}, PS::kDriver},     //
                    {ZoneProperty{{"zone"}}, PS::kDriver}}),
               IncompatiblePropertyValuesError);

  ASSERT_THROW(ValidateDriverPropertiesForSuitableRules(
                   {{GeoareaProperty{{"geoarea"}}, PS::kDriver},     //
                    {GeoareaProperty{{std::nullopt}}, PS::kDriver},  //
                    {ZoneProperty{{"zone"}}, PS::kDriver}}),
               IncompatiblePropertyValuesError);
}

struct SuitableRulesData {
  TimePoint at;
  DriverProperties driver_properties;
  Rules expected;
  std::multiset<std::string> expected_body;
};

struct SuitableRulesParametrized : public BaseTestWithParam<SuitableRulesData> {
};

TEST_P(SuitableRulesParametrized, Test) {
  mocks::BSXClient bsx_client;

  const auto& params = GetParam();

  RunInCoro(
      [&params, &bsx_client] {
        models::RulesSelectLimiter rps_limiter{"test_limiter"};

        models::limiter_config::RulesSelectSettings settings{
            100,   // exec_rate
            1000,  // max_queue_size
        };
        rps_limiter.SetLimiterSettings(settings);

        dynamic_config::StorageMock config_storage{
            {taxi_config::SUBVENTION_RULE_UTILS_DROP_ZERO_RULES, false}};

        ASSERT_EQ(
            GetSuitableRules({params.at, params.at + std::chrono::seconds(1)},
                             params.driver_properties, {}, bsx_client,
                             rps_limiter, config_storage.GetSnapshot()),
            params.expected);
      },
      1);

  const auto& calls = bsx_client.GetCalls("V2RulesSelect");
  ASSERT_EQ(calls.size(), params.expected_body.size());
  ASSERT_EQ(calls, params.expected_body);
}

INSTANTIATE_TEST_SUITE_P(
    SuitableRulesParametrized, SuitableRulesParametrized,
    ::testing::ValuesIn({
        SuitableRulesData{
            {
                //
            },
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver}},           //
            {
                //
            },
            {},
        },

        SuitableRulesData{
            {
                //
            },
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ClassProperty{{"class"}}, PS::kDriver}},         //
            {
                //
            },
            {
                R"({"zones":["zone"],"tariff_classes":["class"],"time_range":{"start":"1970-01-01T00:00:00+00:00","end":"1970-01-01T00:00:01+00:00"},"tags_constraint":{"tags":["tag"]},"rule_types":["single_ride"],"limit":100})",
                R"({"zones":["zone"],"tariff_classes":["class"],"time_range":{"start":"1970-01-01T00:00:00+00:00","end":"1970-01-01T00:00:01+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["single_ride"],"limit":100})",
            },
        },

        SuitableRulesData{
            {
                //
            },
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {GeoareaProperty{{std::nullopt}}, PS::kDriver},   //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ClassProperty{{"class"}}, PS::kDriver}},         //
            {
                //
            },
            {
                R"({"zones":["zone"],"tariff_classes":["class"],"time_range":{"start":"1970-01-01T00:00:00+00:00","end":"1970-01-01T00:00:01+00:00"},"tags_constraint":{"tags":["tag"]},"rule_types":["single_ride"],"limit":100})",
                R"({"zones":["zone"],"tariff_classes":["class"],"time_range":{"start":"1970-01-01T00:00:00+00:00","end":"1970-01-01T00:00:01+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["single_ride"],"limit":100})",
            },
        },

        SuitableRulesData{
            {
                //
            },
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ClassProperty{{"class"}}, PS::kDriver}},         //
            {
                //
            },
            {
                R"({"zones":["zone"],"tariff_classes":["class"],"geoareas_constraint":{"geoareas":["geoarea"]},"time_range":{"start":"1970-01-01T00:00:00+00:00","end":"1970-01-01T00:00:01+00:00"},"tags_constraint":{"tags":["tag"]},"rule_types":["single_ride"],"limit":100})",
                R"({"zones":["zone"],"tariff_classes":["class"],"geoareas_constraint":{"geoareas":["geoarea"]},"time_range":{"start":"1970-01-01T00:00:00+00:00","end":"1970-01-01T00:00:01+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["single_ride"],"limit":100})",
            },
        },

        SuitableRulesData{
            {
                //
            },
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{"tag"}}}, PS::kDriver},           //
                {GeoareaProperty{{"geoarea"}}, PS::kDriver},      //
                {GeoareaProperty{{"geoarea2"}}, PS::kDriver},     //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ZoneProperty{{"zone2"}}, PS::kDriver},           //
                {ClassProperty{{"class"}}, PS::kDriver},          //
                {ClassProperty{{"class2"}}, PS::kDriver}},        //
            {
                //
            },
            {
                R"({"zones":["zone","zone2"],"tariff_classes":["class","class2"],"geoareas_constraint":{"geoareas":["geoarea","geoarea2"]},"time_range":{"start":"1970-01-01T00:00:00+00:00","end":"1970-01-01T00:00:01+00:00"},"tags_constraint":{"tags":["tag"]},"rule_types":["single_ride"],"limit":100})",
                R"({"zones":["zone","zone2"],"tariff_classes":["class","class2"],"geoareas_constraint":{"geoareas":["geoarea","geoarea2"]},"time_range":{"start":"1970-01-01T00:00:00+00:00","end":"1970-01-01T00:00:01+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["single_ride"],"limit":100})",
            },
        },

        SuitableRulesData{
            {
                //
            },
            DriverProperties{
                {BrandingProperty{{false, false}}, PS::kDriver},  //
                {ActivityProperty{{50}}, PS::kDriver},            //
                {TagsProperty{{{}}}, PS::kDriver},                //
                {ZoneProperty{{"zone"}}, PS::kDriver},            //
                {ClassProperty{{"class"}}, PS::kDriver}},         //
            {
                //
            },
            {
                R"({"zones":["zone"],"tariff_classes":["class"],"time_range":{"start":"1970-01-01T00:00:00+00:00","end":"1970-01-01T00:00:01+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["single_ride"],"limit":100})",
            },
        },
    }));

using PT = PropertyType;
TEST(ValidateMatchRules, Test) {
  ASSERT_NO_THROW(ValidateDriverPropertiesForMatchRules({
      {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},                //
      {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},             //
      {PT::kGeoarea, {GeoareaProperty{{"geoarea"}}, PS::kDriver}},       //
      {PT::kBranding, {BrandingProperty{{false, false}}, PS::kDriver}},  //
      {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},            //
      {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},               //
  }));

  ASSERT_NO_THROW(ValidateDriverPropertiesForMatchRules({
      {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},                //
      {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},             //
      {PT::kBranding, {BrandingProperty{{false, false}}, PS::kDriver}},  //
      {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},            //
      {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},               //
  }));

  ASSERT_THROW(
      ValidateDriverPropertiesForMatchRules({
          {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},             //
          {PT::kBranding, {BrandingProperty{{false, false}}, PS::kDriver}},  //
          {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},            //
          {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},               //
      }),
      MissingRequiredPropertyError);

  ASSERT_THROW(
      ValidateDriverPropertiesForMatchRules({
          {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},                //
          {PT::kBranding, {BrandingProperty{{false, false}}, PS::kDriver}},  //
          {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},            //
          {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},               //
      }),
      MissingRequiredPropertyError);

  ASSERT_THROW(ValidateDriverPropertiesForMatchRules({
                   {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},      //
                   {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},   //
                   {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},  //
                   {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},     //
               }),
               MissingRequiredPropertyError);

  ASSERT_THROW(
      ValidateDriverPropertiesForMatchRules({
          {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},                //
          {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},             //
          {PT::kBranding, {BrandingProperty{{false, false}}, PS::kDriver}},  //
          {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},               //
      }),
      MissingRequiredPropertyError);

  ASSERT_THROW(
      ValidateDriverPropertiesForMatchRules({
          {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},                //
          {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},             //
          {PT::kBranding, {BrandingProperty{{false, false}}, PS::kDriver}},  //
          {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},            //
      }),
      MissingRequiredPropertyError);
}

// TODO: return this test after moving to subvention matcher to library

// struct GetRuleMatchesData {
//   TimePoint at;
//   DriverPropertiesByType driver_properties;
//   RuleMatches expected;
//   std::string expected_body;
// };

// struct GetRuleMatchesParametrized
//     : public BaseTestWithParam<GetRuleMatchesData> {};

// TEST_P(GetRuleMatchesParametrized, Test) {
//   mocks::BSXClient bsx_client;

//   const auto& param = GetParam();
//   RunInCoro(
//       [&param, &bsx_client]() {
//         ASSERT_EQ(GetRuleMatches(param.at, param.driver_properties,
//         bsx_client,
//                                  engine::current_task::GetTaskProcessor()),
//                   param.expected);
//       },
//       1);

//   const auto& calls = bsx_client.GetCalls("V2RulesMatch");
//   ASSERT_EQ(calls.size(), 1);
//   ASSERT_EQ(calls[0], param.expected_body);
// }

// INSTANTIATE_TEST_SUITE_P(
//     GetRuleMatchesParametrized, GetRuleMatchesParametrized,
//     ::testing::ValuesIn({
//         GetRuleMatchesData{
//             {
//                 //
//             },
//             DriverPropertiesByType{
//                 {PT::kBranding,
//                  {{BrandingProperty{{false, false}}, PS::kDriver}}},       //
//                 {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},  //
//                 {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},   //
//                 {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},      //
//                 {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}},   //
//             },
//             {
//                 //
//             },
//             R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"1970-01-01T00:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})"
//             //
//         },

//         GetRuleMatchesData{
//             {
//                 //
//             },
//             DriverPropertiesByType{
//                 {PT::kBranding,
//                  {{BrandingProperty{{false, true}}, PS::kDriver}}},        //
//                 {PT::kActivity, {{ActivityProperty{{60}}, PS::kDriver}}},  //
//                 {PT::kTags,
//                  {{TagsProperty{{{"tag", "tag2"}}}, PS::kDriver}}}, //
//                 {PT::kGeoarea, {{GeoareaProperty{{"geoarea"}},
//                 PS::kDriver}}},
//                 // {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}}, //
//                 {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}}, //
//             },
//             {
//                 //
//             },
//             R"({"activity_points":60,"geoareas":["geoarea"],"has_lightbox":true,"has_sticker":false,"reference_time":"1970-01-01T00:00:00+00:00","tags":["tag","tag2"],"tariff_class":"class","zone":"zone"})"
//             //
//         },

//     }));

struct KeypointMatchData {
  TimeRange time_range;
  Rules rules;
  cctz::time_zone client_timezone;
  handlers::TariffSettingsCacheData tariff_settings;
  DriverPropertiesByType properties_by_type;

  KeyPoints expected_keypoints;
  KeyPointRuleMatches expected;

  std::vector<std::string> expected_match_calls;
  std::vector<mocks::bsx::v2_rules_match::post::Response200> match_responses;
};

struct KeypointMatchParametrized : public BaseTestWithParam<KeypointMatchData> {
};

TEST_P(KeypointMatchParametrized, Test) {
  mocks::BSXClient bsx_client;

  const auto& param = GetParam();

  for (auto& resp : param.match_responses) {
    formats::json::StringBuilder sb;
    mocks::bsx::v2_rules_match::post::WriteToStream(resp, sb);

    bsx_client.responses["V2RulesMatch"].push_back(sb.GetString());
  }

  const auto key_points = subvention_matcher::impl::GetKeyPoints(
      param.time_range, param.rules, param.tariff_settings);

  ASSERT_EQ(key_points, param.expected_keypoints);

  // TODO: return this test after moving to subvention matcher to library

  //   RunInCoro(
  //       [&param, &key_points, &bsx_client]() {
  //         auto matched = impl::GetRuleMatches(
  //             key_points, param.properties_by_type, bsx_client,
  //             engine::current_task::GetTaskProcessor());

  //         const auto& calls = bsx_client.GetCalls("V2RulesMatch");
  //         ASSERT_EQ(calls, param.expected_match_calls);

  //         ASSERT_EQ(matched, param.expected);
  //       },
  //       1);
}

Rule CreateRule(const std::string& rates) {
  static uint32_t kId{0};

  Rule result;
  result.id = std::to_string(kId++);
  result.zone = "moscow";
  result.tariff_class = "econom";
  result.start = dt::Stringtime("2020-08-31T21:00:00Z");
  result.end = dt::Stringtime("2020-09-07T21:00:00Z");

  auto array = formats::json::FromString(rates);
  array.CheckArrayOrNull();
  result.rates.reserve(array.GetSize());
  for (const auto& item : array) {
    result.rates.push_back(
        item.As<clients::billing_subventions_x::RateSingleRide>());
  }

  return result;
}

static const Rule kRuleA = CreateRule(R"JSON(
        [
            {
                "week_day": "mon",
                "start": "21:00",
                "bonus_amount": "0"
            },
            {
                "week_day": "tue",
                "start": "09:00",
                "bonus_amount": "200"
            },
            {
                "week_day": "wed",
                "start": "18:00",
                "bonus_amount": "0"
            },
            {
                "week_day": "thu",
                "start": "05:00",
                "bonus_amount": "400"
            }
        ]
    )JSON");

static const Rule kRuleB = CreateRule(R"JSON(
        [
            {
                "week_day": "mon",
                "start": "21:00",
                "bonus_amount": "300"
            },
            {
                "week_day": "tue",
                "start": "09:00",
                "bonus_amount": "0"
            },
            {
                "week_day": "wed",
                "start": "18:00",
                "bonus_amount": "500"
            },
            {
                "week_day": "thu",
                "start": "05:00",
                "bonus_amount": "0"
            }
        ]
    )JSON");

using MatchResponse = mocks::bsx::v2_rules_match::post::Response200;

MatchResponse MakeMatchResponse(std::string_view amount, const Rule& rule) {
  namespace bsx_client = clients::billing_subventions_x;
  return MatchResponse{
      mocks::bsx::V2MatchRulesResponse{
          {bsx_client::MatchingRule{bsx_client::MatchingSingleRideRule{
              rule, mocks::bsx::SmartRuleType::kSingleRide,
              std::string(amount)}}},
      },
  };
}

static const MatchResponse kRuleAMatchResponse =
    MakeMatchResponse("100", kRuleA);

static const MatchResponse kRuleBMatchResponse =
    MakeMatchResponse("100", kRuleB);

static const DriverPropertiesByType kDefaultProperties{
    {PT::kBranding, {{BrandingProperty{{false, false}}, PS::kDriver}}},  //
    {PT::kActivity, {{ActivityProperty{{50}}, PS::kDriver}}},            //
    {PT::kTags, {{TagsProperty{{{"tag"}}}, PS::kDriver}}},               //
    {PT::kZone, {{ZoneProperty{{"zone"}}, PS::kDriver}}},                //
    {PT::kClass, {{ClassProperty{{"class"}}, PS::kDriver}}},             //
};

static const DriverPropertyMap kDefaultPropertyMap{
    {PT::kBranding, {BrandingProperty{{false, false}}, PS::kDriver}},  //
    {PT::kActivity, {ActivityProperty{{50}}, PS::kDriver}},            //
    {PT::kTags, {TagsProperty{{{"tag"}}}, PS::kDriver}},               //
    {PT::kZone, {ZoneProperty{{"zone"}}, PS::kDriver}},                //
    {PT::kClass, {ClassProperty{{"class"}}, PS::kDriver}},             //
};

static const handlers::TariffSettingsCacheData kDefaultTariffSettings =
    std::make_shared<
        std::unordered_map<models::HomeZone, models::TariffSettings>>(
        std::unordered_map<models::HomeZone, models::TariffSettings>{
            {models::HomeZone{"moscow"},
             models::TariffSettings{models::HomeZone{"moscow"}, "rus",
                                    "Europe/Moscow"}}});

INSTANTIATE_TEST_SUITE_P(
    KeypointMatchParametrized, KeypointMatchParametrized,
    ::testing::ValuesIn({
        KeypointMatchData{
            TimeRange{
                dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
            },
            Rules{kRuleA},
            GetMskTz(),
            kDefaultTariffSettings,
            kDefaultProperties,
            KeyPoints{
                dt::Stringtime("2020-09-01T06:00:00Z"),
                dt::Stringtime("2020-09-02T15:00:00Z"),
                dt::Stringtime("2020-09-03T02:00:00Z"),
                dt::Stringtime("2020-09-07T18:00:00Z"),
            },
            KeyPointRuleMatches{
                {
                    dt::Stringtime("2020-09-01T06:00:00Z"),
                    RuleScheduleMatches{
                        {kRuleA, ScheduleItem{kDefaultPropertyMap, 200}},
                    },
                },
                {
                    dt::Stringtime("2020-09-02T15:00:00Z"),
                    RuleScheduleMatches{},
                },
                {
                    dt::Stringtime("2020-09-03T02:00:00Z"),
                    RuleScheduleMatches{
                        {kRuleA, ScheduleItem{kDefaultPropertyMap, 400}},
                    },
                },
                {
                    dt::Stringtime("2020-09-07T18:00:00Z"),
                    RuleScheduleMatches{},
                },
            },
            {
                R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"2020-09-01T06:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})",
                R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"2020-09-02T15:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})",
                R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"2020-09-03T02:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})",
            },
            {
                MakeMatchResponse("200", kRuleA),

                MatchResponse{mocks::bsx::V2MatchRulesResponse{
                    {},
                }},
                MakeMatchResponse("400", kRuleA),
            },
        },

        KeypointMatchData{
            TimeRange{
                dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
            },
            Rules{kRuleB},
            GetMskTz(),
            kDefaultTariffSettings,
            kDefaultProperties,
            KeyPoints{
                dt::Stringtime("2020-09-01T00:00:00Z"),
                dt::Stringtime("2020-09-01T06:00:00Z"),
                dt::Stringtime("2020-09-02T15:00:00Z"),
                dt::Stringtime("2020-09-03T02:00:00Z"),
                dt::Stringtime("2020-09-07T18:00:00Z"),
                dt::Stringtime("2020-09-07T21:00:00Z"),
            },
            KeyPointRuleMatches{
                {
                    {
                        dt::Stringtime("2020-09-01T00:00:00Z"),
                        RuleScheduleMatches{
                            {kRuleB, ScheduleItem{kDefaultPropertyMap, 300}},
                        },
                    },
                    {
                        dt::Stringtime("2020-09-01T06:00:00Z"),
                        RuleScheduleMatches{},
                    },
                    {
                        dt::Stringtime("2020-09-02T15:00:00Z"),
                        RuleScheduleMatches{
                            {kRuleB, ScheduleItem{kDefaultPropertyMap, 500}},
                        },
                    },
                    {
                        dt::Stringtime("2020-09-03T02:00:00Z"),
                        RuleScheduleMatches{},
                    },
                    {
                        dt::Stringtime("2020-09-07T18:00:00Z"),
                        RuleScheduleMatches{
                            {kRuleB, ScheduleItem{kDefaultPropertyMap, 300}},
                        },
                    },
                    {
                        dt::Stringtime("2020-09-07T21:00:00Z"),
                        RuleScheduleMatches{},
                    },
                },
            },
            {R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"2020-09-01T00:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})",
             R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"2020-09-01T06:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})",
             R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"2020-09-02T15:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})",
             R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"2020-09-03T02:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})",
             R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"2020-09-07T18:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})"},
            {
                MakeMatchResponse("300", kRuleB),
                MatchResponse{mocks::bsx::V2MatchRulesResponse{
                    {},
                }},
                MakeMatchResponse("500", kRuleB),
                MatchResponse{mocks::bsx::V2MatchRulesResponse{
                    {},
                }},
                MakeMatchResponse("300", kRuleB),
            },
        },

        KeypointMatchData{
            TimeRange{
                dt::Stringtime("2020-09-01T00:00:00Z"),  // Tue
                dt::Stringtime("2020-09-08T00:00:00Z"),  // Tue
            },
            Rules{kRuleA, kRuleB},
            GetMskTz(),
            kDefaultTariffSettings,
            kDefaultProperties,
            KeyPoints{
                dt::Stringtime("2020-09-01T00:00:00Z"),
                dt::Stringtime("2020-09-01T06:00:00Z"),
                dt::Stringtime("2020-09-02T15:00:00Z"),
                dt::Stringtime("2020-09-03T02:00:00Z"),
                dt::Stringtime("2020-09-07T18:00:00Z"),
                dt::Stringtime("2020-09-07T21:00:00Z"),
            },
            KeyPointRuleMatches{
                {
                    {
                        dt::Stringtime("2020-09-01T00:00:00Z"),
                        RuleScheduleMatches{
                            {kRuleB, ScheduleItem{kDefaultPropertyMap, 300}},
                        },
                    },
                    {
                        dt::Stringtime("2020-09-01T06:00:00Z"),
                        RuleScheduleMatches{
                            {kRuleA, ScheduleItem{kDefaultPropertyMap, 200}},
                        },
                    },
                    {
                        dt::Stringtime("2020-09-02T15:00:00Z"),
                        RuleScheduleMatches{
                            {kRuleB, ScheduleItem{kDefaultPropertyMap, 500}},
                        },
                    },
                    {
                        dt::Stringtime("2020-09-03T02:00:00Z"),
                        RuleScheduleMatches{
                            {kRuleA, ScheduleItem{kDefaultPropertyMap, 400}},
                        },
                    },
                    {
                        dt::Stringtime("2020-09-07T18:00:00Z"),
                        RuleScheduleMatches{
                            {kRuleB, ScheduleItem{kDefaultPropertyMap, 300}},
                        },
                    },
                    {
                        dt::Stringtime("2020-09-07T21:00:00Z"),
                        RuleScheduleMatches{},
                    },
                },
            },
            {R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"2020-09-01T00:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})",
             R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"2020-09-01T06:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})",
             R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"2020-09-02T15:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})",
             R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"2020-09-03T02:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})",
             R"({"activity_points":50,"geoareas":[],"has_lightbox":false,"has_sticker":false,"reference_time":"2020-09-07T18:00:00+00:00","tags":["tag"],"tariff_class":"class","zone":"zone"})"},
            {
                MakeMatchResponse("300", kRuleB),
                MakeMatchResponse("200", kRuleA),
                MakeMatchResponse("500", kRuleB),
                MakeMatchResponse("400", kRuleA),
                MakeMatchResponse("300", kRuleB),
            },
        },
    }));
