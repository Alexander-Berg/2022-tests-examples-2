#include <gmock/gmock.h>
#include <converters/config_converter.hpp>
#include <userver/utest/utest.hpp>

#include <taxi_config/variables/MARKET_HIDE_RULES.hpp>

using Config = taxi_config::market_hide_rules::MarketHideRules;

using Case = taxi_config::market_hide_rules::HideRuleCase;
using Feature = taxi_config::market_hide_rules::Feature;

namespace NUnifiedHideRule {

bool operator==(const NUnifiedHideRule::TCase& a,
                const NUnifiedHideRule::TCase& b) {
  return std::tie(a.RuleId, a.restriction.CategoriesInclude,
                  a.restriction.CategoriesExclude, a.restriction.VendorInclude,
                  a.restriction.VendorExclude, a.restriction.ModelsInclude,
                  a.restriction.ModelsExclude, a.restriction.MskusInclude,
                  a.restriction.MskusExclude, a.restriction.BusinessInclude,
                  a.restriction.BusinessExclude, a.restriction.ShopInclude,
                  a.restriction.ShopExclude, a.restriction.FeedInclude,
                  a.restriction.FeedExclude, a.restriction.WarehouseInclude,
                  a.restriction.WarehouseExclude,
                  a.restriction.OfferIdInclude) ==
         std::tie(b.RuleId, b.restriction.CategoriesInclude,
                  b.restriction.CategoriesExclude, b.restriction.VendorInclude,
                  b.restriction.VendorExclude, b.restriction.ModelsInclude,
                  b.restriction.ModelsExclude, b.restriction.MskusInclude,
                  b.restriction.MskusExclude, b.restriction.BusinessInclude,
                  b.restriction.BusinessExclude, b.restriction.ShopInclude,
                  b.restriction.ShopExclude, b.restriction.FeedInclude,
                  b.restriction.FeedExclude, b.restriction.WarehouseInclude,
                  b.restriction.WarehouseExclude, b.restriction.OfferIdInclude);
}

}  // namespace NUnifiedHideRule

namespace market_hide_offers_dyn2yt::tests {

class TestDumper : public NUnifiedHideRule::IDumper {
 public:
  MOCK_METHOD(void, AddCase, (const NUnifiedHideRule::TCase& ruleCase),
              (override));
  MOCK_METHOD(void, AddFeature,
              (const TString& name,
               const TVector<NUnifiedHideRule::TRuleId>& ruleBlacklist,
               const TVector<NUnifiedHideRule::TRuleId>& ruleWhitelist),
              (override));
};

UTEST(ConfigConterver, CheckAllFields) {
  std::vector<std::pair<Case, NUnifiedHideRule::TCase>> test_cases{
      {{.rule_id = 15, .include_regions = std::vector<uint64_t>{25, 30}},
       {.RuleId = 15, .restriction = {.RegionsInclude = {25, 30}}}},
      {{.rule_id = 17, .exclude_regions = std::vector<uint64_t>{35, 40}},
       {.RuleId = 17, .restriction = {.RegionsExclude = {35, 40}}}},
      {{.rule_id = 19, .include_categories = std::vector<uint64_t>{45, 50}},
       {.RuleId = 19, .restriction = {.CategoriesInclude = {45, 50}}}},
      {{.rule_id = 21, .exclude_categories = std::vector<uint64_t>{55, 60}},
       {.RuleId = 21, .restriction = {.CategoriesExclude = {55, 60}}}},
      {{.rule_id = 23, .include_vendors = std::vector<uint64_t>{65, 70}},
       {.RuleId = 23, .restriction = {.VendorInclude = {65, 70}}}},
      {{.rule_id = 17, .exclude_vendors = std::vector<uint64_t>{25, 30}},
       {.RuleId = 17, .restriction = {.VendorExclude = {25, 30}}}},
      {{.rule_id = 15, .include_models = std::vector<uint64_t>{25, 30}},
       {.RuleId = 15, .restriction = {.ModelsInclude = {25, 30}}}},
      {{.rule_id = 17, .exclude_models = std::vector<uint64_t>{25, 30}},
       {.RuleId = 17, .restriction = {.ModelsExclude = {25, 30}}}},
      {{.rule_id = 15, .include_mskus = std::vector<uint64_t>{25, 30}},
       {.RuleId = 15, .restriction = {.MskusInclude = {25, 30}}}},
      {{.rule_id = 17, .exclude_mskus = std::vector<uint64_t>{25, 30}},
       {.RuleId = 17, .restriction = {.MskusExclude = {25, 30}}}},
      {{.rule_id = 15, .include_business = std::vector<uint64_t>{25, 30}},
       {.RuleId = 15, .restriction = {.BusinessInclude = {25, 30}}}},
      {{.rule_id = 17, .exclude_business = std::vector<uint64_t>{25, 30}},
       {.RuleId = 17, .restriction = {.BusinessExclude = {25, 30}}}},
      {{.rule_id = 15, .include_shops = std::vector<uint64_t>{25, 30}},
       {.RuleId = 15, .restriction = {.ShopInclude = {25, 30}}}},
      {{.rule_id = 17, .exclude_shops = std::vector<uint64_t>{25, 30}},
       {.RuleId = 17, .restriction = {.ShopExclude = {25, 30}}}},
      {{.rule_id = 15, .include_feeds = std::vector<uint64_t>{25, 30}},
       {.RuleId = 15, .restriction = {.FeedInclude = {25, 30}}}},
      {{.rule_id = 17, .exclude_feeds = std::vector<uint64_t>{25, 30}},
       {.RuleId = 17, .restriction = {.FeedExclude = {25, 30}}}},
      {{.rule_id = 15, .include_warehouses = std::vector<uint64_t>{25, 30}},
       {.RuleId = 15, .restriction = {.WarehouseInclude = {25, 30}}}},
      {{.rule_id = 17, .exclude_warehouses = std::vector<uint64_t>{25, 30}},
       {.RuleId = 17, .restriction = {.WarehouseExclude = {25, 30}}}},
  };

  for (const auto& [config_case, unified_rules_case] : test_cases) {
    Config config{.cases = std::vector<Case>{config_case}};

    std::shared_ptr<TestDumper> dumper = std::make_shared<TestDumper>();
    market_hide_offers_dyn2yt::TConfigConverter converter(config, dumper);

    EXPECT_CALL(*dumper, AddCase(unified_rules_case)).Times(1);

    NLog::TNullLog nullLog;
    ASSERT_NO_THROW(converter.Convert(nullLog));
  }
}

UTEST(ConfigConterver, CheckFeatures) {
  Config config{
      .cases =
          std::vector<Case>{
              {.rule_id = 15, .include_regions = std::vector<uint64_t>{25, 30}},
              {.rule_id = 19,
               .include_categories = std::vector<uint64_t>{45, 50}},
              {.rule_id = 21, .include_mskus = std::vector<uint64_t>{55, 60}},
          },
      .features = std::vector<Feature>{
          {.feature_name = "test-feature",
           .enabled_rules = std::vector<uint32_t>{15, 19},
           .disabled_rules = std::vector<uint32_t>{21}},
      }};

  std::shared_ptr<TestDumper> dumper = std::make_shared<TestDumper>();
  market_hide_offers_dyn2yt::TConfigConverter converter(config, dumper);

  using TRules = TVector<NUnifiedHideRule::TRuleId>;
  EXPECT_CALL(*dumper, AddCase(testing::_)).Times(3);
  EXPECT_CALL(*dumper, AddFeature(TString("test-feature"), TRules({21}),
                                  TRules({15, 19})))
      .Times(1);

  NLog::TNullLog nullLog;
  ASSERT_NO_THROW(converter.Convert(nullLog));
}

}  // namespace market_hide_offers_dyn2yt::tests
