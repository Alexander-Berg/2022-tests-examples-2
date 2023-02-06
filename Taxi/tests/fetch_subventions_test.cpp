
#include <set>

#include <gmock/gmock.h>

#include <userver/utest/utest.hpp>

#include <clients/billing-subventions-x/client.hpp>
#include <clients/billing-subventions-x/responses.hpp>
#include <testing/taxi_config.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/utils/assert.hpp>

#include <clients/billing-subventions-x/client_mock_base.hpp>
#include <taxi_config/subvention-rule-utils/taxi_config.hpp>

#include <subvention-rule-utils/fetch_subventions.hpp>

namespace sru = subvention_rule_utils;
namespace bsx = clients::billing_subventions_x;

namespace {

class MockBSXClient : public bsx::ClientMockBase {
 public:
  using V2RulesSelectResponseBuilder =
      std::function<bsx::v2_rules_select::post::Response(
          const bsx::v2_rules_select::post::Request&)>;

  virtual bsx::v2_rules_select::post::Response V2RulesSelect(
      const bsx::v2_rules_select::post::Request& request,
      const bsx::CommandControl&) const final {
    rule_select_calls_.insert(request.GetBody());

    if (v2_rules_select_response_builder_) {
      return (*v2_rules_select_response_builder_)(request);
    }

    if (v2_rules_select_static_response_) {
      return *v2_rules_select_static_response_;
    }

    return {};
  }

  const std::set<std::string>& GetCalls(const std::string&) const {
    return rule_select_calls_;
  }

  void SetV2RulesSelectResponse(
      const bsx::v2_rules_select::post::Response& response) {
    v2_rules_select_static_response_ = response;
  }

  void SetV2RulesSelectReponseBuilder(V2RulesSelectResponseBuilder builder) {
    v2_rules_select_response_builder_ = builder;
  }

 private:
  mutable std::set<std::string> rule_select_calls_;

  std::optional<V2RulesSelectResponseBuilder> v2_rules_select_response_builder_;
  std::optional<bsx::v2_rules_select::post::Response>
      v2_rules_select_static_response_;
};

std::vector<std::string> ExtractRuleIds(
    const std::vector<bsx::SmartRule>& rules) {
  std::vector<std::string> ids;
  std::transform(rules.begin(), rules.end(), std::back_inserter(ids),
                 [](const auto& rule) {
                   return std::visit([](const auto& rule) { return rule.id; },
                                     rule.AsVariant());
                 });
  return ids;
}

template <class Container, class Value>
bool Contains(const Container& c, const Value& v) {
  return std::find(c.begin(), c.end(), v) != c.end();
}

}  // namespace

struct FetchSubventionsTestData {
  sru::SubventionFetchParameters params;
  std::set<std::string> expected_request_bodies;
};

struct TestSingleRide
    : public testing::TestWithParam<FetchSubventionsTestData> {};

TEST_P(TestSingleRide, TestSingleRide) {
  const MockBSXClient bsx_client;
  subvention_rule_utils::RawClientStrategy strategy(bsx_client);

  dynamic_config::StorageMock storage{
      {taxi_config::SUBVENTION_RULE_UTILS_DROP_ZERO_RULES, false}};

  const auto& test_data = GetParam();
  RunInCoro(
      [&test_data, &strategy, &storage] {
        sru::FetchSingleRideSmartRules(test_data.params, strategy,
                                       storage.GetSnapshot());
      },
      1);

  const auto& calls = bsx_client.GetCalls("V2RulesSelect");
  ASSERT_EQ(calls, test_data.expected_request_bodies);
}

INSTANTIATE_TEST_SUITE_P(
    FetchSingleRideSmartRules, TestSingleRide,
    ::
        testing::
            ValuesIn(

                {FetchSubventionsTestData{
                     {
                         /*subvention_tags =*/
                         sru::tag_constraints::Suitable{{"tag1", "tag2"}},
                         /*time_range = */
                         {
                             utils::datetime::Stringtime(
                                 "2020-01-01T12:00:00Z"),
                             utils::datetime::Stringtime(
                                 "2020-01-01T13:00:00Z"),
                         },
                         /*tariff_classes = */ {{"econom"}},
                         /*tariff_zones = */
                         sru::tariff_zone_constraints::Suitable{{"zone1"}},
                         /*subvention_geoareas = */
                         sru::geoarea_constraints::Exact{
                             {"geoarea1", "geoarea2"}},
                         /*branding = */
                         {bsx::BrandingFilterA::kStickerAndLightbox},
                         /*unique_driver_id = */ {},
                         /*rules_select_limit = */ 128,
                     },
                     {
                         R"({"zones":["zone1"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["single_ride"],"limit":128})",
                         R"({"zones":["zone1"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["single_ride"],"limit":128})",
                     }},

                 FetchSubventionsTestData{
                     {
                         /*subvention_tags =*/
                         sru::tag_constraints::Suitable{{"tag1", "tag2"}},
                         /*time_range = */
                         {
                             utils::datetime::Stringtime(
                                 "2020-01-01T12:00:00Z"),
                             utils::datetime::Stringtime(
                                 "2020-01-01T13:00:00Z"),
                         },
                         /*tariff_classes = */ {{"econom"}},
                         /*tariff_zones = */
                         sru::tariff_zone_constraints::Suitable{{"zone1"}},
                         /*subvention_geoareas = */
                         sru::geoarea_constraints::Suitable{
                             {"geoarea1", "geoarea2"}},
                         /*branding = */
                         {bsx::BrandingFilterA::kStickerAndLightbox},
                         /*unique_driver_id = */ {},
                         /*rules_select_limit = */ 128,
                     },
                     {
                         R"({"zones":["zone1"],"tariff_classes":["econom"],"geoareas_constraint":{"has_geoarea":false},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["single_ride"],"limit":128})",
                         R"({"zones":["zone1"],"tariff_classes":["econom"],"geoareas_constraint":{"has_geoarea":false},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["single_ride"],"limit":128})",
                         R"({"zones":["zone1"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["single_ride"],"limit":128})",
                         R"({"zones":["zone1"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["single_ride"],"limit":128})",
                     }},

                 FetchSubventionsTestData{
                     {
                         /*subvention_tags =*/{},
                         /*time_range = */
                         {
                             utils::datetime::Stringtime(
                                 "2020-01-01T12:00:00Z"),
                             utils::datetime::Stringtime(
                                 "2020-01-01T13:00:00Z"),
                         },
                         /*tariff_classes = */ {{"econom"}},
                         /*tariff_zones = */
                         sru::tariff_zone_constraints::Suitable{{"zone1"}},
                         /*subvention_geoareas = */
                         sru::geoarea_constraints::Exact{
                             {"geoarea1", "geoarea2"}},
                         /*branding = */
                         {bsx::BrandingFilterA::kStickerAndLightbox},
                         /*unique_driver_id = */ {},
                         /*rules_select_limit = */ 128,
                     },
                     {
                         R"({"zones":["zone1"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"rule_types":["single_ride"],"limit":128})",
                     }},

                 FetchSubventionsTestData{
                     {
                         /*subvention_tags =*/
                         sru::tag_constraints::Suitable{{}},
                         /*time_range = */
                         {
                             utils::datetime::Stringtime(
                                 "2020-01-01T12:00:00Z"),
                             utils::datetime::Stringtime(
                                 "2020-01-01T13:00:00Z"),
                         },
                         /*tariff_classes = */ {{"econom"}},
                         /*tariff_zones = */
                         sru::tariff_zone_constraints::Exact{
                             {"zone1", "zone2"}},
                         /*subvention_geoareas = */ {},
                         /*branding = */ {},
                         /*unique_driver_id = */ {},
                         /*rules_select_limit = */ 128,
                     },
                     {
                         R"({"zones":["zone1","zone2"],"tariff_classes":["econom"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["single_ride"],"limit":128})",
                     }},

                 FetchSubventionsTestData{
                     {
                         /*subvention_tags =*/{},
                         /*time_range = */
                         {
                             utils::datetime::Stringtime(
                                 "2020-01-01T12:00:00Z"),
                             utils::datetime::Stringtime(
                                 "2020-01-01T13:00:00Z"),
                         },
                         /*tariff_classes = */ {},
                         /*tariff_zones = */
                         sru::tariff_zone_constraints::Suitable{{"zone1"}},
                         /*subvention_geoareas = */
                         sru::geoarea_constraints::HasGeoarea{},
                         /*branding = */ {},
                         /*unique_driver_id = */ {},
                         /*rules_select_limit = */ 128,
                     },
                     {
                         R"({"zones":["zone1"],"geoareas_constraint":{"has_geoarea":true},"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"rule_types":["single_ride"],"limit":128})",
                     }},
                 // Following tests check tags constraints
                 FetchSubventionsTestData{{
                                              /*subvention_tags =*/
                                              sru::tag_constraints::Exact{
                                                  {"tag1", "tag2"}},
                                              /*time_range = */
                                              {
                                                  utils::datetime::Stringtime(
                                                      "2020-01-01T12:00:00Z"),
                                                  utils::datetime::Stringtime(
                                                      "2020-01-01T13:00:00Z"),
                                              },
                                              /*tariff_classes = */
                                              {{"econom"}},
                                              /*tariff_zones = */
                                              sru::tariff_zone_constraints::
                                                  Suitable{{"zone1"}},
                                              /*subvention_geoareas = */ {},
                                              /*branding = */
                                              {bsx::BrandingFilterA::
                                                   kStickerAndLightbox},
                                              /*unique_driver_id = */ {},
                                              /*rules_select_limit = */ 128,
                                          },
                                          {
                                              R"({"zones":["zone1"],"tariff_classes":["econom"],"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["single_ride"],"limit":128})",
                                          }},

                 FetchSubventionsTestData{
                     {
                         /*subvention_tags =*/
                         sru::tag_constraints::Suitable{{"tag1", "tag2"}},
                         /*time_range = */
                         {
                             utils::datetime::Stringtime(
                                 "2020-01-01T12:00:00Z"),
                             utils::datetime::Stringtime(
                                 "2020-01-01T13:00:00Z"),
                         },
                         /*tariff_classes = */ {{"econom"}},
                         /*tariff_zones = */
                         sru::tariff_zone_constraints::Suitable{{"zone1"}},
                         /*subvention_geoareas = */ {},
                         /*branding = */
                         {bsx::BrandingFilterA::kStickerAndLightbox},
                         /*unique_driver_id = */ {},
                         /*rules_select_limit = */ 128,
                     },
                     {
                         R"({"zones":["zone1"],"tariff_classes":["econom"],"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["single_ride"],"limit":128})",
                         R"({"zones":["zone1"],"tariff_classes":["econom"],"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["single_ride"],"limit":128})",
                     }},

                 FetchSubventionsTestData{
                     {
                         /*subvention_tags =*/
                         sru::tag_constraints::HasTag{},
                         /*time_range = */
                         {
                             utils::datetime::Stringtime(
                                 "2020-01-01T12:00:00Z"),
                             utils::datetime::Stringtime(
                                 "2020-01-01T13:00:00Z"),
                         },
                         /*tariff_classes = */ {{"econom"}},
                         /*tariff_zones = */
                         sru::tariff_zone_constraints::Suitable{{"zone1"}},
                         /*subvention_geoareas = */ {},
                         /*branding = */
                         {bsx::BrandingFilterA::kStickerAndLightbox},
                         /*unique_driver_id = */ {},
                         /*rules_select_limit = */ 128,
                     },
                     {
                         R"({"zones":["zone1"],"tariff_classes":["econom"],"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":true},"rule_types":["single_ride"],"limit":128})",
                     }},

                 FetchSubventionsTestData{
                     {
                         /*subvention_tags =*/
                         sru::tag_constraints::ForSupport{
                             {"tag1", "tag2"},
                         },
                         /*time_range = */
                         {
                             utils::datetime::Stringtime(
                                 "2020-01-01T12:00:00Z"),
                             utils::datetime::Stringtime(
                                 "2020-01-01T13:00:00Z"),
                         },
                         /*tariff_classes = */ {{"econom"}},
                         /*tariff_zones = */
                         sru::tariff_zone_constraints::Suitable{{"zone1"}},
                         /*subvention_geoareas = */ {},
                         /*branding = */
                         {bsx::BrandingFilterA::kStickerAndLightbox},
                         /*unique_driver_id = */ {},
                         /*rules_select_limit = */ 128,
                     },
                     {
                         R"({"zones":["zone1"],"tariff_classes":["econom"],"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["single_ride"],"limit":128})",
                         R"({"zones":["zone1"],"tariff_classes":["econom"],"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["single_ride"],"limit":128})",
                     }}}));

struct TestGoals : public testing::TestWithParam<FetchSubventionsTestData> {};
struct TestGoalsExtendedFetchParameters
    : public testing::TestWithParam<FetchSubventionsTestData> {};

static const auto kBrGeoNodesResponse =
    formats::json::FromString(R"=(
{
    "items": [
        {
            "name": "br_moscow",
            "name_en": "Moscow",
            "name_ru": "Москва",
            "node_type": "agglomeration",
            "parent_name": "br_moskovskaja_obl"
        },
        {
            "name": "br_moscow_adm",
            "name_en": "Moscow (adm)",
            "name_ru": "Москва (адм)",
            "node_type": "node",
            "parent_name": "br_moscow",
            "tariff_zones": [
                "boryasvo",
                "moscow",
                "vko"
            ]
        },
        {
            "name": "br_moscow_middle_region",
            "name_en": "Moscow (Middle Region)",
            "name_ru": "Москва (среднее)",
            "node_type": "node",
            "parent_name": "br_moscow"
        },
        {
            "name": "br_moskovskaja_obl",
            "name_en": "Moscow Region",
            "name_ru": "Московская область",
            "node_type": "node",
            "parent_name": "br_tsentralnyj_fo"
        },
        {
            "name": "br_root",
            "name_en": "Basic Hierarchy",
            "name_ru": "Базовая иерархия",
            "node_type": "root"
        },
        {
            "name": "br_russia",
            "name_en": "Russia",
            "name_ru": "Россия",
            "node_type": "country",
            "parent_name": "br_root"
        },
        {
            "name": "br_tsentralnyj_fo",
            "name_en": "Central Federal District",
            "name_ru": "Центральный ФО",
            "node_type": "node",
            "parent_name": "br_russia"
        }
    ]
}
)=")
        .As<clients::taxi_agglomerations::ListGeoNodes>();

TEST_P(TestGoalsExtendedFetchParameters, TestGoalsExtendedFetchParameters) {
  const caches::agglomerations::Tree agglomerations_tree(kBrGeoNodesResponse);
  const MockBSXClient bsx_client;
  subvention_rule_utils::RawClientStrategy strategy(bsx_client);
  dynamic_config::StorageMock storage{
      {taxi_config::SUBVENTION_RULE_UTILS_ENABLE_EXTENDED_FETCHING_PARAMETERS,
       true},
      {taxi_config::SUBVENTION_RULE_UTILS_DROP_ZERO_RULES, false}};
  const auto& config = storage.GetSnapshot();
  const auto& test_data = GetParam();
  RunInCoro(
      [&test_data, &agglomerations_tree, &strategy, &config] {
        sru::FetchGoalSmartRules(test_data.params, agglomerations_tree,
                                 strategy, config);
      },
      1);

  const auto& calls = bsx_client.GetCalls("V2RulesSelect");
  ASSERT_EQ(calls, test_data.expected_request_bodies);
}

INSTANTIATE_TEST_SUITE_P(
    FetchGoalSmartRules, TestGoalsExtendedFetchParameters,
    ::testing::ValuesIn(

        {
            FetchSubventionsTestData{
                {
                    /*subvention_tags =*/
                    subvention_rule_utils::tag_constraints::Suitable{
                        {"tag1", "tag2"}},
                    /*time_range = */
                    {
                        utils::datetime::Stringtime("2020-01-01T12:00:"
                                                    "00Z"),
                        utils::datetime::Stringtime("2020-01-01T13:00:"
                                                    "00Z"),
                    },
                    /*tariff_classes = */
                    {{"econom"}},
                    /*tariff_zones = */
                    sru::tariff_zone_constraints::Suitable{{"moscow"}},
                    /*subvention_geoareas = */
                    subvention_rule_utils::geoarea_constraints::Exact{
                        {"geoarea1", "geoarea2"}},
                    /*branding = */
                    {bsx::BrandingFilterA::kStickerAndLightbox},
                    /*unique_driver_id = */ {},
                    /*rules_select_limit = */ 128,
                },
                {
                    R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"limit":128})",
                    R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["goal"],"limit":128})",
                }},

            FetchSubventionsTestData{
                {
                    /*subvention_tags
                       =*/
                    subvention_rule_utils::tag_constraints::Suitable{{"tag"
                                                                      "1",
                                                                      "tag"
                                                                      "2"}},
                    /*time_range
                    =
                    */
                    {
                        utils::datetime::Stringtime("2020"
                                                    "-01-"
                                                    "01T1"
                                                    "2:"
                                                    "00:"
                                                    "00"
                                                    "Z"),
                        utils::datetime::Stringtime("2020"
                                                    "-01-"
                                                    "01T1"
                                                    "3:"
                                                    "00:"
                                                    "00"
                                                    "Z"),
                    },
                    /*tariff_classes
                    = */
                    {{"econo"
                      "m"}},
                    /*tariff_zones
                    = */
                    sru::tariff_zone_constraints::Suitable{{"mos"
                                                            "co"
                                                            "w"}},
                    /*subvention_geoareas
                    = */
                    subvention_rule_utils::geoarea_constraints::Exact{{"geo"
                                                                       "are"
                                                                       "a1",
                                                                       "geo"
                                                                       "are"
                                                                       "a"
                                                                       "2"}},
                    /*branding
                    = */
                    {bsx::BrandingFilterA::kStickerAndLightbox},
                    /*unique_driver_id
                    = */
                    {"udid1"},
                    /*rules_select_limit
                    = */
                    128,
                },
                {

                    R"({"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"drivers":["udid1"],"limit":128})",
                    R"({"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["goal"],"drivers":["udid1"],"limit":128})",
                    R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"limit":128})",
                    R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["goal"],"limit":128})",
                }},

            FetchSubventionsTestData{
                {
                    /*subvention_tags =*/
                    subvention_rule_utils::tag_constraints::Suitable{{}},
                    /*time_range = */
                    {
                        utils::datetime::Stringtime("2020-01-01T12:00:"
                                                    "00Z"),
                        utils::datetime::Stringtime("2020-01-01T13:00:"
                                                    "00Z"),
                    },
                    /*tariff_classes = */
                    {{"econom"}},
                    /*tariff_zones = */
                    sru::tariff_zone_constraints::Exact{{"moscow"}},
                    /*subvention_geoareas = */
                    subvention_rule_utils::geoarea_constraints::Exact{
                        {"geoarea1", "geoarea2"}},
                    /*branding = */
                    {bsx::BrandingFilterA::kStickerAndLightbox},
                    /*unique_driver_id = */
                    {"udid1"},
                    /*rules_select_limit = */
                    128,
                },
                {
                    R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"drivers":["udid1"],"limit":128})",
                    R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"limit":128})",
                }},

            FetchSubventionsTestData{
                {
                    /*subvention_tags
                       =*/
                    subvention_rule_utils::tag_constraints::Suitable{{}},
                    /*time_range
                       = */
                    {
                        utils::datetime::Stringtime("2020-01-01T12:00:00Z"),
                        utils::datetime::Stringtime("2020-01-01T13:00:00Z"),
                    },
                    /*tariff_classes
                       = */
                    {{"econo"
                      "m"}},
                    /*tariff_zones
                       = */
                    sru::tariff_zone_constraints::Suitable{{"moscow"}},
                    /*subvention_geoareas
                       = */
                    subvention_rule_utils::geoarea_constraints::Exact{
                        {"geoarea1", "geoarea2"}},
                    /*branding
                       = */
                    {bsx::BrandingFilterA::kStickerAndLightbox},
                    /*unique_driver_id
                       = */
                    {},
                    /*rules_select_limit
                       = */
                    128,
                },
                {
                    R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"limit":128})",
                }},

            FetchSubventionsTestData{
                {
                    /*subvention_tags
                        =*/
                    subvention_rule_utils::tag_constraints::Suitable{{"tag"
                                                                      "1",
                                                                      "tag"
                                                                      "2"}},
                    /*time_range
                    =
                    */
                    {
                        utils::datetime::Stringtime("2020"
                                                    "-01-"
                                                    "01T1"
                                                    "2:"
                                                    "00:"
                                                    "00"
                                                    "Z"),
                        utils::datetime::Stringtime("2020"
                                                    "-01-"
                                                    "01T1"
                                                    "3:"
                                                    "00:"
                                                    "00"
                                                    "Z"),
                    },
                    /*tariff_classes
                    = */
                    {{"econom"}},
                    /*tariff_zones
                    = */
                    sru::tariff_zone_constraints::Suitable{{"mos"
                                                            "co"
                                                            "w"}},
                    /*subvention_geoareas
                    = */
                    subvention_rule_utils::geoarea_constraints::Suitable{{"geo"
                                                                          "are"
                                                                          "a1",
                                                                          "geo"
                                                                          "are"
                                                                          "a"
                                                                          "2"}},
                    /*branding
                    = */
                    {bsx::BrandingFilterA::kStickerAndLightbox},
                    /*unique_driver_id
                    = */
                    {"udid1"},
                    /*rules_select_limit
                    = */
                    128,
                },
                {
                    R"({"tariff_classes":["econom"],"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"drivers":["udid1"],"limit":128})",
                    R"({"tariff_classes":["econom"],"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["goal"],"drivers":["udid1"],"limit":128})",
                    R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"has_geoarea":false},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"limit":128})",
                    R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"has_geoarea":false},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["goal"],"limit":128})",
                    R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"limit":128})",
                    R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["goal"],"limit":128})",
                }},

        }));

TEST_P(TestGoals, TestGoals) {
  const caches::agglomerations::Tree agglomerations_tree(kBrGeoNodesResponse);
  const MockBSXClient bsx_client;
  subvention_rule_utils::RawClientStrategy strategy(bsx_client);
  dynamic_config::StorageMock storage{
      {taxi_config::SUBVENTION_RULE_UTILS_ENABLE_EXTENDED_FETCHING_PARAMETERS,
       false},
      {taxi_config::SUBVENTION_RULE_UTILS_DROP_ZERO_RULES, false}};
  const auto& config = storage.GetSnapshot();
  const auto& test_data = GetParam();
  RunInCoro(
      [&test_data, &agglomerations_tree, &strategy, &config] {
        sru::FetchGoalSmartRules(test_data.params, agglomerations_tree,
                                 strategy, config);
      },
      1);

  const auto& calls = bsx_client.GetCalls("V2RulesSelect");
  ASSERT_EQ(calls, test_data.expected_request_bodies);
}

INSTANTIATE_TEST_SUITE_P(FetchGoalSmartRules, TestGoals,
                         ::testing::
                             ValuesIn(

                                 {
                                     FetchSubventionsTestData{
                                         {
                                             /*subvention_tags =*/
                                             subvention_rule_utils::
                                                 tag_constraints::Suitable{
                                                     {"tag1", "tag2"}},
                                             /*time_range = */
                                             {
                                                 utils::datetime::Stringtime(
                                                     "2020-01-01T12:00:"
                                                     "00Z"),
                                                 utils::datetime::Stringtime(
                                                     "2020-01-01T13:00:"
                                                     "00Z"),
                                             },
                                             /*tariff_classes = */
                                             {{"econom"}},
                                             /*tariff_zones = */
                                             sru::tariff_zone_constraints::
                                                 Suitable{{"moscow"}},
                                             /*subvention_geoareas = */
                                             subvention_rule_utils::
                                                 geoarea_constraints::Exact{
                                                     {"geoarea1", "geoarea2"}},
                                             /*branding = */
                                             {bsx::BrandingFilterA::
                                                  kStickerAndLightbox},
                                             /*unique_driver_id = */ {},
                                             /*rules_select_limit = */ 128,
                                         },
                                         {
                                             R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"limit":128})",
                                             R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["goal"],"limit":128})",
                                         }},

                                     FetchSubventionsTestData{
                                         {
                                             /*subvention_tags =*/
                                             subvention_rule_utils::
                                                 tag_constraints::Suitable{
                                                     {"tag1", "tag2"}},
                                             /*time_range
                                             =
                                             */
                                             {
                                                 utils::datetime::Stringtime(
                                                     "2020-01-01T12:00:00Z"),
                                                 utils::datetime::Stringtime(
                                                     "2020-01-01T13:00:00Z"),
                                             },
                                             /*tariff_classes
                                             = */
                                             {{"econom"}},
                                             /*tariff_zones
                                             = */
                                             sru::tariff_zone_constraints::
                                                 Suitable{{"moscow"}},
                                             /*subvention_geoareas
                                             = */
                                             subvention_rule_utils::
                                                 geoarea_constraints::Exact{
                                                     {"geoarea1", "geoarea2"}},
                                             /*branding
                                             = */
                                             {bsx::BrandingFilterA::
                                                  kStickerAndLightbox},
                                             /*unique_driver_id
                                             = */
                                             {"udid1"},
                                             /*rules_select_limit
                                             = */
                                             128,
                                         },
                                         {

                                             R"({"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"drivers":["udid1"],"limit":128})",
                                             R"({"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["goal"],"drivers":["udid1"],"limit":128})",
                                             R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"limit":128})",
                                             R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["goal"],"limit":128})",
                                         }},

                                     FetchSubventionsTestData{
                                         {
                                             /*subvention_tags =*/
                                             subvention_rule_utils::
                                                 tag_constraints::Suitable{{}},
                                             /*time_range = */
                                             {
                                                 utils::datetime::Stringtime(
                                                     "2020-01-01T12:00:00Z"),
                                                 utils::datetime::Stringtime(
                                                     "2020-01-01T13:00:00Z"),
                                             },
                                             /*tariff_classes = */
                                             {{"econom"}},
                                             /*tariff_zones = */
                                             sru::tariff_zone_constraints::
                                                 Exact{{"moscow"}},
                                             /*subvention_geoareas = */
                                             subvention_rule_utils::
                                                 geoarea_constraints::Exact{
                                                     {"geoarea1", "geoarea2"}},
                                             /*branding = */
                                             {bsx::BrandingFilterA::
                                                  kStickerAndLightbox},
                                             /*unique_driver_id = */
                                             {"udid1"},
                                             /*rules_select_limit = */
                                             128,
                                         },
                                         {
                                             R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"drivers":["udid1"],"limit":128})",
                                             R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"limit":128})",
                                         }},

                                     FetchSubventionsTestData{
                                         {
                                             /*subvention_tags =*/
                                             subvention_rule_utils::
                                                 tag_constraints::Suitable{{}},
                                             /*time_range = */
                                             {
                                                 utils::datetime::Stringtime(
                                                     "2020-01-01T12:00:00Z"),
                                                 utils::datetime::Stringtime(
                                                     "2020-01-01T13:00:00Z"),
                                             },
                                             /*tariff_classes = */
                                             {{"econom"}},
                                             /*tariff_zones = */
                                             sru::tariff_zone_constraints::
                                                 Suitable{{"moscow"}},
                                             /*subvention_geoareas = */
                                             subvention_rule_utils::
                                                 geoarea_constraints::Exact{
                                                     {"geoarea1", "geoarea2"}},
                                             /*branding = */
                                             {bsx::BrandingFilterA::
                                                  kStickerAndLightbox},
                                             /*unique_driver_id = */ {},
                                             /*rules_select_limit = */
                                             128,
                                         },
                                         {
                                             R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"limit":128})",
                                         }},

                                     FetchSubventionsTestData{
                                         {
                                             /*subvention_tags
                                                =*/
                                             subvention_rule_utils::
                                                 tag_constraints::Suitable{
                                                     {"tag"
                                                      "1",
                                                      "tag"
                                                      "2"}},
                                             /*time_range
                                             =
                                             */
                                             {
                                                 utils::datetime::Stringtime(
                                                     "2020"
                                                     "-01-"
                                                     "01T1"
                                                     "2:"
                                                     "00:"
                                                     "00"
                                                     "Z"),
                                                 utils::datetime::Stringtime(
                                                     "2020"
                                                     "-01-"
                                                     "01T1"
                                                     "3:"
                                                     "00:"
                                                     "00"
                                                     "Z"),
                                             },
                                             /*tariff_classes
                                             = */
                                             {{"econom"}},
                                             /*tariff_zones
                                             = */
                                             sru::tariff_zone_constraints::
                                                 Suitable{{"mos"
                                                           "co"
                                                           "w"}},
                                             /*subvention_geoareas
                                             = */
                                             subvention_rule_utils::
                                                 geoarea_constraints::Suitable{
                                                     {"geo"
                                                      "are"
                                                      "a1",
                                                      "geo"
                                                      "are"
                                                      "a"
                                                      "2"}},
                                             /*branding
                                             = */
                                             {bsx::BrandingFilterA::
                                                  kStickerAndLightbox},
                                             /*unique_driver_id
                                             = */
                                             {"udid1"},
                                             /*rules_select_limit
                                             = */
                                             128,
                                         },
                                         {
                                             R"({"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"drivers":["udid1"],"limit":128})",
                                             R"({"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["goal"],"drivers":["udid1"],"limit":128})",
                                             R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"has_geoarea":false},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"limit":128})",
                                             R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"has_geoarea":false},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["goal"],"limit":128})",
                                             R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"has_tag":false},"rule_types":["goal"],"limit":128})",
                                             R"({"zones":["br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm","br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm/moscow"],"tariff_classes":["econom"],"geoareas_constraint":{"geoareas":["geoarea1","geoarea2"]},"branding":["sticker_and_lightbox"],"time_range":{"start":"2020-01-01T12:00:00+00:00","end":"2020-01-01T13:00:00+00:00"},"tags_constraint":{"tags":["tag1","tag2"]},"rule_types":["goal"],"limit":128})",
                                         }},

                                 }));

struct FetchSubventionsResponseTestData {
  sru::SubventionFetchParameters params;
  bsx::v2_rules_select::post::Response bsx_response;
  sru::FetchedRules expected_response;
};

struct TestSingleRideResponse
    : public testing::TestWithParam<FetchSubventionsResponseTestData> {};

UTEST_P(TestSingleRideResponse, TestSingleRideResponseTestSingleRideResponse) {
  MockBSXClient bsx_client;
  subvention_rule_utils::RawClientStrategy strategy(bsx_client);

  const auto& test_data = GetParam();
  dynamic_config::StorageMock storage{
      {taxi_config::SUBVENTION_RULE_UTILS_DROP_ZERO_RULES, false}};

  bsx_client.SetV2RulesSelectResponse(test_data.bsx_response);
  auto response = sru::FetchSingleRideSmartRules(test_data.params, strategy,
                                                 storage.GetSnapshot());

  auto& response_rule = response.enabled.front();
  auto& expected_rule = test_data.expected_response.enabled.front();

  ASSERT_EQ(response_rule, expected_rule);
}

INSTANTIATE_UTEST_SUITE_P(
    CheckResponseOfFetchSubventionsResponse, TestSingleRideResponse,
    ::testing::ValuesIn({FetchSubventionsResponseTestData{
        {
            /*subvention_tags =*/{},
            /*time_range = */
            {
                utils::datetime::Stringtime("2020-01-01T12:00:00Z"),
                utils::datetime::Stringtime("2020-01-01T13:00:00Z"),
            },
            /*tariff_classes = */ {{"econom"}},
            /*tariff_zones = */
            sru::tariff_zone_constraints::Suitable{{"moscow"}},
            /*subvention_geoareas = */
            subvention_rule_utils::geoarea_constraints::Exact{
                {"geoarea1", "geoarea2"}},
            /*branding = */
            {bsx::BrandingFilterA::kStickerAndLightbox},
            /*unique_driver_id = */ {},
            /*rules_select_limit = */ 128,
        },
        bsx::v2_rules_select::post::Response200{bsx::SelectRulesResponse{
            ::std::vector<bsx::SmartRule>{bsx::SmartRule{bsx::SingleRideRule{
                /*id = */ "1",
                /*rule_type = */ bsx::SmartRuleType::kSingleRide,
                /*start = */
                utils::datetime::Stringtime("2020-01-01T12:00:00Z"),
                /*end = */
                utils::datetime::Stringtime("2020-01-01T13:00:00Z"),
                /*updated_at = */
                utils::datetime::Stringtime("2020-01-01T12:00:00Z"),
                /*tag = */ {},
                /*stop_tag = */ {},
                /*branding_type = */ {},
                /*activity_points = */ {},
                /*rates = */
                ::std::vector<clients::billing_subventions_x::RateSingleRide>{
                    bsx::RateSingleRide{bsx::WeekDay::kTue, "00:01",
                                        "100500.0"},
                    bsx::RateSingleRide{bsx::WeekDay::kMon, "00:01",
                                        "100500.0"}},
                /*budget_id = */ "123",
                /*draft_id = */ "12",
                /*zone = */ "moscow",
                /*tariff_class = */ "comfort",
                /*geoarea = */ {},
            }}},
            {}}},
        sru::FetchedRules{
            std::vector<bsx::SmartRule>{bsx::SmartRule{
                bsx::SingleRideRule{
                    /*id = */ "1",
                    /*rule_type = */ bsx::SmartRuleType::kSingleRide,
                    /*start = */
                    utils::datetime::Stringtime("2020-01-01T12:00:00Z"),
                    /*end = */
                    utils::datetime::Stringtime("2020-01-01T13:00:00Z"),
                    /*updated_at = */
                    utils::datetime::Stringtime("2020-01-01T12:00:00Z"),
                    /*tag = */ {},
                    /*stop_tag = */ {},
                    /*branding_type = */ {},
                    /*activity_points = */ {},
                    /*rates = */
                    ::std::vector<
                        clients::billing_subventions_x::RateSingleRide>{
                        bsx::RateSingleRide{bsx::WeekDay::kMon, "00:01",
                                            "100500.0"},
                        bsx::RateSingleRide{bsx::WeekDay::kTue, "00:01",
                                            "100500.0"}},
                    /*budget_id = */ "123",
                    /*draft_id = */ "12",
                    /*zone = */ "moscow",
                    /*tariff_class = */ "comfort",
                    /*geoarea = */ {},
                },
            }},
            {}}}}));

struct TestGoalStopTagData {
  sru::TagsConstraint tags_constraint;
  bool expect_enabled;
};

struct TestGoalStopTag : public testing::TestWithParam<TestGoalStopTagData> {};

UTEST_P(TestGoalStopTag, TestGoalStopTag) {
  sru::SubventionFetchParameters params;
  params.tags_constraint = GetParam().tags_constraint;

  const caches::agglomerations::Tree agglomerations_tree(kBrGeoNodesResponse);

  MockBSXClient bsx_client;
  bsx_client.SetV2RulesSelectReponseBuilder(
      [](const bsx::v2_rules_select::post::Request& request)
          -> bsx::v2_rules_select::post::Response200 {
        if (request.body.tags_constraint != std::nullopt &&
            std::holds_alternative<bsx::TagsConstraintT0>(
                *request.body.tags_constraint)) {
          bsx::GoalRule goal_rule;
          goal_rule.id = "1";
          goal_rule.rule_type = bsx::SmartRuleType::kGoal;
          goal_rule.stop_tag = "stop_tag";
          return bsx::v2_rules_select::post::Response200{
              bsx::SelectRulesResponse{
                  ::std::vector<bsx::SmartRule>{bsx::SmartRule{goal_rule}}}};
        }

        return {};
      });
  subvention_rule_utils::RawClientStrategy strategy(bsx_client);

  dynamic_config::StorageMock storage{
      {taxi_config::SUBVENTION_RULE_UTILS_ENABLE_GOAL_STOP_TAGS, true},
      {taxi_config::SUBVENTION_RULE_UTILS_DROP_ZERO_RULES, false}};

  const auto fetched = sru::FetchGoalSmartRules(
      params, agglomerations_tree, strategy, storage.GetSnapshot());

  if (GetParam().expect_enabled) {
    ASSERT_EQ(fetched.enabled.size(), 1);
    ASSERT_EQ(fetched.disabled.size(), 0);
  } else {
    ASSERT_EQ(fetched.enabled.size(), 0);
    ASSERT_EQ(fetched.disabled.size(), 1);
  }
}

const std::vector<TestGoalStopTagData> kTestGoalStopTagData = {

    {
        // tags_constraint
        sru::tag_constraints::Suitable{{"tag1", "tag2"}},
        // expect_enabled
        true,
    },
    {
        // tags_constraint
        sru::tag_constraints::Suitable{{"tag1", "tag2", "stop_tag"}},
        // expect_enabled
        false,
    },
    {
        // tags_constraint
        sru::tag_constraints::Suitable{{"stop_tag"}},
        // expect_enabled
        false,
    },

};

INSTANTIATE_UTEST_SUITE_P(CheckResponseOfGoalStopTag, TestGoalStopTag,
                          ::testing::ValuesIn(kTestGoalStopTagData));

UTEST(TestDisablingByTag, Test) {
  sru::SubventionFetchParameters params;
  params.tags_constraint =
      sru::tag_constraints::Suitable{{"subv_disable_personal_goal"}};
  params.unique_driver_ids = {"udid"};

  const caches::agglomerations::Tree agglomerations_tree(kBrGeoNodesResponse);

  MockBSXClient bsx_client;
  bsx_client.SetV2RulesSelectReponseBuilder(
      [](const bsx::v2_rules_select::post::Request& request)
          -> bsx::v2_rules_select::post::Response200 {
        std::vector<bsx::SmartRule> result;

        if (request.body.tags_constraint != std::nullopt &&
            std::holds_alternative<bsx::TagsConstraintT0>(
                *request.body.tags_constraint)) {
          bsx::GoalRule goal_rule;
          goal_rule.rule_type = bsx::SmartRuleType::kGoal;
          goal_rule.id =
              (request.body.drivers && !request.body.drivers->empty())
                  ? "personal"
                  : "non-personal";
          result.push_back(bsx::SmartRule{goal_rule});
        }

        return bsx::v2_rules_select::post::Response200{
            bsx::SelectRulesResponse{result}};
      });
  subvention_rule_utils::RawClientStrategy strategy(bsx_client);

  dynamic_config::StorageMock storage{
      {taxi_config::SUBVENTION_RULE_UTILS_ENABLE_GOAL_STOP_TAGS, false},
      {taxi_config::SUBVENTION_RULE_UTILS_ENABLE_EXTENDED_FETCHING_PARAMETERS,
       false},
      {taxi_config::SUBVENTION_RULE_UTILS_DROP_ZERO_RULES, false}};

  const auto fetched = sru::FetchGoalSmartRules(
      params, agglomerations_tree, strategy, storage.GetSnapshot());

  EXPECT_THAT(ExtractRuleIds(fetched.enabled),
              testing::ElementsAre("non-personal"));
  EXPECT_THAT(ExtractRuleIds(fetched.disabled),
              testing::ElementsAre("personal"));
}

UTEST(FetchSubventions, DegenerateRuleDropping) {
  sru::SubventionFetchParameters params;

  const caches::agglomerations::Tree agglomerations_tree(kBrGeoNodesResponse);

  MockBSXClient bsx_client;
  bsx_client.SetV2RulesSelectReponseBuilder(
      [](const bsx::v2_rules_select::post::Request& request)
          -> bsx::v2_rules_select::post::Response200 {
        using clients::billing_subventions_x::SmartRuleType;

        std::vector<bsx::SmartRule> result;
        const auto rule_types =
            request.body.rule_types.value_or(std::vector<SmartRuleType>{
                {SmartRuleType::kGoal, SmartRuleType::kSingleOntop,
                 SmartRuleType::kSingleRide}});

        if (Contains(rule_types, SmartRuleType::kGoal)) {
          bsx::GoalRule goal_rule;
          goal_rule.rule_type = bsx::SmartRuleType::kGoal;
          goal_rule.start =
              utils::datetime::Stringtime("2020-01-01T12:00:00+0300");
          goal_rule.end = goal_rule.start;
          goal_rule.id = "mock_goal_id";
          result.push_back(bsx::SmartRule{goal_rule});
        }
        if (Contains(rule_types, SmartRuleType::kSingleRide)) {
          bsx::SingleRideRule single_ride_rule;
          single_ride_rule.rule_type = bsx::SmartRuleType::kSingleRide;
          single_ride_rule.start =
              utils::datetime::Stringtime("2020-01-01T12:00:00+0300");
          single_ride_rule.end = single_ride_rule.start;
          single_ride_rule.id = "mock_single_ride_id";
          result.push_back(bsx::SmartRule{single_ride_rule});
        }
        if (Contains(rule_types, SmartRuleType::kSingleOntop)) {
          bsx::SingleOnTopRule single_ontop_rule;
          single_ontop_rule.rule_type = bsx::SmartRuleType::kSingleOntop;
          single_ontop_rule.start =
              utils::datetime::Stringtime("2020-01-01T12:00:00+0300");
          single_ontop_rule.end = single_ontop_rule.start;
          single_ontop_rule.id = "mock_single_ontop_id";
          result.push_back(bsx::SmartRule{single_ontop_rule});
        }

        return bsx::v2_rules_select::post::Response200{
            bsx::SelectRulesResponse{result}};
      });
  subvention_rule_utils::RawClientStrategy strategy(bsx_client);

  dynamic_config::StorageMock storage{
      {taxi_config::SUBVENTION_RULE_UTILS_ENABLE_GOAL_STOP_TAGS, false},
      {taxi_config::SUBVENTION_RULE_UTILS_ENABLE_EXTENDED_FETCHING_PARAMETERS,
       false},
      {taxi_config::SUBVENTION_RULE_UTILS_DROP_ZERO_RULES, true}};

  auto fetched = sru::FetchGoalSmartRules(params, agglomerations_tree, strategy,
                                          storage.GetSnapshot());

  EXPECT_THAT(ExtractRuleIds(fetched.enabled), testing::IsEmpty());
  EXPECT_THAT(ExtractRuleIds(fetched.disabled), testing::IsEmpty());

  fetched =
      sru::FetchSingleRideSmartRules(params, strategy, storage.GetSnapshot());

  EXPECT_THAT(ExtractRuleIds(fetched.enabled), testing::IsEmpty());
  EXPECT_THAT(ExtractRuleIds(fetched.disabled), testing::IsEmpty());

  fetched =
      sru::FetchSingleOntopSmartRules(params, strategy, storage.GetSnapshot());

  EXPECT_THAT(ExtractRuleIds(fetched.enabled), testing::IsEmpty());
  EXPECT_THAT(ExtractRuleIds(fetched.disabled), testing::IsEmpty());
}
