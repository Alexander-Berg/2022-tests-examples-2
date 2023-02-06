#include <endpoints/full/plugins/brandings/subplugins/brandings_surge_redirect.hpp>

#include <boost/algorithm/string.hpp>

#include <set>

#include <userver/utest/utest.hpp>

#include <experiments3/new_summary.hpp>
#include <experiments3/surge_promotions.hpp>
#include <geometry/position.hpp>

#include <tests/context_mock_test.hpp>
#include <userver/formats/json/serialize.hpp>

namespace routestats::full::brandings {

namespace {

formats::json::Value MakeNewSummaryExp(bool enabled) {
  formats::json::ValueBuilder builder{};
  builder["enabled"] = enabled;
  return builder.ExtractValue();
}

formats::json::Value MakeSurgePromotionsExp(
    bool enabled, const std::string& surge_threshold) {
  formats::json::ValueBuilder builder{};
  builder["enabled"] = enabled;

  builder["icon"] = formats::json::ValueBuilder();
  builder["icon"]["image_tag"] = "my_image_tag";

  builder["surge_threshold"] = surge_threshold;

  builder["tanker_keys"] = formats::json::ValueBuilder();
  builder["tanker_keys"]["text"] = "promo.surge_redirect_transport.text";
  builder["tanker_keys"]["title"] = "promo.surge_redirect_transport.title";

  builder["widget_settings"] = formats::json::ValueBuilder();
  builder["widget_settings"]["deeplink"] = "yandextaxi://masstransit";
  builder["widget_settings"]["promo_priority"] = 11;

  return builder.ExtractValue();
}

core::Experiments MockExperiments(
    bool new_summary_exp_enabled, bool surge_promotions_exp_enabled,
    const std::string& surge_promotions_exp_surge_threshold) {
  core::ExpMappedData experiments;
  using NewSummary = experiments3::NewSummary;
  using SurgePromotions = experiments3::SurgePromotions;

  experiments[NewSummary::kName] = {
      NewSummary::kName, MakeNewSummaryExp(new_summary_exp_enabled), {}};
  experiments[SurgePromotions::kName] = {
      SurgePromotions::kName,
      MakeSurgePromotionsExp(surge_promotions_exp_enabled,
                             surge_promotions_exp_surge_threshold),
      {}};

  return {std::move(experiments)};
}

core::ServiceLevel BuildServiceLevel(
    const std::string& class_,
    const std::optional<std::string>& surge_threshold) {
  core::ServiceLevel sl;
  sl.class_ = class_;

  if (surge_threshold) {
    sl.surge = {decimal64::Decimal<4>{*surge_threshold}};
  }

  return sl;
}

geometry::Position BuildPoint(const double lat, const double lon) {
  return {geometry::Latitude::FromValue(lat),
          geometry::Longitude::FromValue(lon)};
}

std::vector<core::ServiceLevel> PrepareServiceLevels() {
  return {BuildServiceLevel("econom", "1.8"),
          BuildServiceLevel("business", "1.2"),
          BuildServiceLevel("comfortplus", "1"),
          BuildServiceLevel("vip", std::nullopt)};
}

}  // namespace

struct TestCase {
  std::string case_alias;
  bool new_summary_exp_enabled;
  bool surge_promotions_exp_enabled;
  std::string surge_threshold;
  std::unordered_set<std::string> branding_classes;
};

const std::vector<TestCase> kTestCases{
    {"SurgePromotionsExpDisabled", false, false, "1", {}},
    {"SurgeThreshold1",
     false,
     true,
     "1",
     {"econom", "business", "comfortplus"}},
    {"SurgeThreshold2", false, true, "1.5", {"econom"}},
    {"SurgeThreshold3", false, true, "2", {}},
    {"NewSummaryExpEnabled", true, true, "1.0", {}},
};

class TestSurgeRedirectPlugin : public testing::TestWithParam<TestCase> {};

void CompareDeeplink(const std::string& original_deeplink,
                     const std::string& expected_deeplink) {
  std::vector<std::string> original_parts;
  std::vector<std::string> expected_parts;

  boost::split(original_parts, original_deeplink, boost::is_any_of("?"));
  boost::split(expected_parts, expected_deeplink, boost::is_any_of("?"));
  ASSERT_EQ(original_parts.size(), 2);
  ASSERT_EQ(expected_parts.size(), 2);

  ASSERT_EQ(original_parts[0], expected_parts[0]);

  std::vector<std::string> original_args;
  std::vector<std::string> expected_args;

  boost::split(original_args, original_parts[1], boost::is_any_of("&"));
  boost::split(expected_args, expected_parts[1], boost::is_any_of("&"));
  ASSERT_EQ(original_args.size(), expected_args.size());

  ASSERT_EQ(std::set<std::string>(original_args.begin(), original_args.end()),
            std::set<std::string>(expected_args.begin(), expected_args.end()));
}

TEST_P(TestSurgeRedirectPlugin, DisabledSurgePromotionExp) {
  const auto& [_, new_summary_exp_enabled, surge_promotions_exp_enabled,
               surge_threshold, branding_classes] = GetParam();

  BrandingsSurgeRedirectPlugin plugin;
  const auto service_levels = PrepareServiceLevels();
  auto plugin_ctx = test::full::GetDefaultContext();
  plugin_ctx.experiments.uservices_routestats_exps = MockExperiments(
      new_summary_exp_enabled, surge_promotions_exp_enabled, surge_threshold);
  plugin_ctx.input.original_request.route = {{
      BuildPoint(37.53472388755793, 55.750507058344134),
      BuildPoint(37.53360806644724, 55.8001525488165),
      BuildPoint(37.55008646364724, 55.775830344410507),
      BuildPoint(37.6425635, 55.7347652),
  }};

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  std::unordered_set<std::string> classes(
      {"econom", "business", "comfortplus", "vip"});

  for (const auto& class_ : classes) {
    const auto plugin_brandings = plugin.GetBrandings(class_);
    if (branding_classes.count(class_)) {
      ASSERT_EQ(plugin_brandings.size(), 1);
      ASSERT_EQ(plugin_brandings[0].title,
                "promo.surge_redirect_transport.title##");
      ASSERT_EQ(plugin_brandings[0].subtitle.value(),
                "promo.surge_redirect_transport.text##");
      ASSERT_EQ(plugin_brandings[0].icon.value(), "my_image_tag");
      ASSERT_EQ(plugin_brandings[0].type, "deeplink");

      ASSERT_TRUE(plugin_brandings[0].deeplink.has_value());
      CompareDeeplink(*plugin_brandings[0].deeplink,
                      "yandextaxi://"
                      "masstransit?mid2-lon=55.775830&mid1-lon=55.800153&mid1-"
                      "lat=37.533608&start-lat=37.534724&start-lon=55.750507&"
                      "end-lon=55.734765&mid2-lat=37.550086&end-lat=37.642564");
    } else {
      ASSERT_EQ(plugin_brandings.size(), 0);
    }
  }
}

INSTANTIATE_TEST_SUITE_P(/* no prefix */, TestSurgeRedirectPlugin,
                         testing::ValuesIn(kTestCases),
                         [](const testing::TestParamInfo<TestCase>& info) {
                           return info.param.case_alias;
                         });

}  // namespace routestats::full::brandings
