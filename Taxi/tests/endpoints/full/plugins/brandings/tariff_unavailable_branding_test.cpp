#include <endpoints/full/core/input.hpp>
#include <endpoints/full/plugins/brandings/subplugins/tariff_unavailable_branding.hpp>

#include <userver/utest/utest.hpp>

#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

namespace routestats::full::brandings {

namespace {

const std::string kLocale = "ru";

core::Experiments MockExperiments(
    const std::vector<std::string>& branding_ids) {
  core::ExpMappedData experiments;
  using Exp = experiments3::RoutestatsTariffUnavailableBrandings;

  formats::json::ValueBuilder exp_value = formats::json::Type::kObject;
  exp_value["enabled"] = true;
  exp_value["mappings"] = formats::json::Type::kArray;

  for (const auto& branding_id : branding_ids) {
    auto field = [&branding_id](const std::string& name) {
      return branding_id + "_" + name;
    };

    formats::json::ValueBuilder branding = formats::json::Type::kObject;
    branding["type"] = field("type");
    branding["icon"] = field("icon");
    branding["title_key"] = field("title_key");
    branding["subtitle_key"] = field("subtitle_key");

    formats::json::ValueBuilder mapping = formats::json::Type::kObject;
    mapping["id"] = branding_id;
    mapping["branding"] = branding;

    exp_value["mappings"].PushBack(std::move(mapping));
  }

  experiments[Exp::kName] = {
      Exp::kName, formats::json::ValueBuilder{exp_value}.ExtractValue(), {}};

  return {std::move(experiments)};
}

std::shared_ptr<const ::routestats::plugins::top_level::Context> CreateContext(
    const std::string& locale,
    const std::optional<std::vector<std::string>>& branding_ids_opt) {
  auto context = test::full::GetDefaultContext();
  context.user.auth_context.locale = locale;

  if (branding_ids_opt.has_value()) {
    context.experiments.uservices_routestats_exps =
        MockExperiments(branding_ids_opt.value());
  }

  return test::full::MakeTopLevelContext(context);
}

core::ServiceLevel CreateServiceLevel(
    const std::string& class_,
    const std::optional<core::TariffUnavailable>& tariff_unavailable =
        std::nullopt) {
  auto service_level = test::MockDefaultServiceLevel(class_);

  service_level.tariff_unavailable = tariff_unavailable;

  return service_level;
}

service_level::TariffBranding CreateBranding(const std::string& id,
                                             const std::string& locale) {
  auto field = [&id](const std::string& name) { return id + "_" + name; };
  auto localize = [&locale](const std::string& text) {
    return text + "##" + locale;
  };
  auto text_field = [&localize, &field](const std::string& name) {
    return localize(field(name));
  };

  service_level::TariffBranding branding;

  branding.type = field("type");
  branding.icon = field("icon");
  branding.title = text_field("title_key");
  branding.subtitle = text_field("subtitle_key");

  return branding;
}

void AssertEq(const service_level::TariffBranding& expected,
              const service_level::TariffBranding& actual) {
  ASSERT_EQ(expected.type, actual.type);
  ASSERT_EQ(expected.icon, actual.icon);
  ASSERT_EQ(expected.title, actual.title);
  ASSERT_EQ(expected.subtitle, actual.subtitle);
}

}  // namespace

TEST(TariffUnavailableBrandingPlugin, HappyPath) {
  TariffUnavailableBrandingPlugin plugin;
  auto locale = "ru";
  auto branding_id = "branding_id";
  auto context = CreateContext(locale, {{branding_id}});
  auto service_levels = std::vector<core::ServiceLevel>{
      CreateServiceLevel("econom"),
      CreateServiceLevel("business", {{"code", "message"}}),
      CreateServiceLevel("vip", {{"code", "message", branding_id}})};

  plugin.OnServiceLevelsReady(context, service_levels);

  ASSERT_EQ(plugin.GetBrandings("unknown_tariff").size(), 0);
  ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
  ASSERT_EQ(plugin.GetBrandings("business").size(), 0);

  const auto& vip_brandings = plugin.GetBrandings("vip");
  ASSERT_EQ(vip_brandings.size(), 1);

  const auto& branding = vip_brandings.front();

  AssertEq(CreateBranding(branding_id, locale), branding);
}

TEST(TariffUnavailableBrandingPlugin, UnknownBrandingId) {
  TariffUnavailableBrandingPlugin plugin;
  auto locale = "ru";
  auto unknown_branding_id = "unknown_branding_id";
  auto branding_id = "branding_id";
  auto context = CreateContext(locale, {{branding_id}});
  auto service_levels = std::vector<core::ServiceLevel>{
      CreateServiceLevel("vip", {{"code", "message", unknown_branding_id}})};

  plugin.OnServiceLevelsReady(context, service_levels);

  ASSERT_EQ(plugin.GetBrandings("vip").size(), 0);
}

TEST(TariffUnavailableBrandingPlugin, BrandingsExpNotMatched) {
  TariffUnavailableBrandingPlugin plugin;
  auto locale = "ru";
  auto branding_id = "branding_id";
  auto context = CreateContext(locale, std::nullopt);
  auto service_levels = std::vector<core::ServiceLevel>{
      CreateServiceLevel("vip", {{"code", "message", branding_id}})};

  plugin.OnServiceLevelsReady(context, service_levels);

  ASSERT_EQ(plugin.GetBrandings("vip").size(), 0);
}

}  // namespace routestats::full::brandings
