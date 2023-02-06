#include <endpoints/full/core/input.hpp>
#include <endpoints/full/plugins/brandings/subplugins/long_search_branding.hpp>

#include <userver/utest/utest.hpp>

#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

namespace routestats::full::brandings {

namespace {
const std::string kDefaultLocale = "ru";

core::Experiments MockExperiments(bool enabled) {
  core::ExpMappedData experiments;
  using Exp = experiments3::RoutestatsLongSearchBranding;

  formats::json::ValueBuilder exp_value = formats::json::Type::kObject;
  exp_value["enabled"] = enabled;

  formats::json::ValueBuilder branding_settings_map =
      formats::json::Type::kObject;
  formats::json::ValueBuilder uberx_settings = formats::json::Type::kObject;

  uberx_settings["title"] = "test_title";
  formats::json::ValueBuilder popup = formats::json::Type::kObject;
  popup["title"] = "test_popup_title";
  popup["text"] = "test_popup_text";
  popup["button_title"] = "test_popup_button_title";
  uberx_settings["popup"] = popup;

  formats::json::ValueBuilder search_screen = formats::json::Type::kObject;
  search_screen["title"] = "test_ss_title";
  search_screen["subtitle"] = "test_ss_subtitle";
  uberx_settings["search_screen"] = search_screen;

  branding_settings_map["uberx"] = uberx_settings;
  exp_value["class_map_branding_settings"] = branding_settings_map;

  experiments[Exp::kName] = {
      Exp::kName, formats::json::ValueBuilder{exp_value}.ExtractValue(), {}};

  return {std::move(experiments)};
}

std::shared_ptr<const ::routestats::plugins::top_level::Context> CreateContext(
    const std::optional<bool> is_exp_enabled) {
  auto context = test::full::GetDefaultContext();
  context.user.auth_context.locale = kDefaultLocale;

  if (is_exp_enabled.has_value()) {
    context.experiments.uservices_routestats_exps =
        MockExperiments(is_exp_enabled.value());
  }

  return test::full::MakeTopLevelContext(context);
}

core::ServiceLevel CreateServiceLevel(const std::string& class_) {
  auto service_level = test::MockDefaultServiceLevel(class_);
  return service_level;
}

std::string GetTextField(const std::string& text) {
  auto localize = [](const std::string& text) {
    return text + "##" + kDefaultLocale;
  };
  return localize(text);
}

service_level::TariffBranding CreateBranding() {
  service_level::TariffBranding branding;

  branding.type = "long_search";
  branding.title = GetTextField("test_title");
  branding.popup = service_level::Popup{
      GetTextField("test_popup_title"), GetTextField("test_popup_text"),
      GetTextField("test_popup_button_title")};
  return branding;
}

core::ServiceLevelSearchScreen CreateSearchScreen() {
  core::ServiceLevelSearchScreen search_screen{
      GetTextField("test_ss_title"),
      GetTextField("test_ss_subtitle"),
  };
  return search_screen;
}

void ApplyExtensions(std::vector<core::ServiceLevel>& service_levels,
                     const ServiceLevelExtensions& extensions) {
  for (auto& sl : service_levels) {
    const auto class_name = sl.Class();
    if (extensions.count(class_name) == 0) {
      continue;
    }
    extensions.at(class_name)->Apply("", sl);
  }
}

void AssertEq(const service_level::Popup& expected,
              const service_level::Popup& actual) {
  ASSERT_EQ(expected.title, actual.title);
  ASSERT_EQ(expected.text, actual.text);
  ASSERT_EQ(expected.button_title, actual.button_title);
}

void AssertEq(const service_level::TariffBranding& expected,
              const service_level::TariffBranding& actual) {
  ASSERT_EQ(expected.type, actual.type);
  ASSERT_EQ(expected.title, actual.title);
  if (expected.popup.has_value()) {
    AssertEq(expected.popup.value(), actual.popup.value());
  } else {
    ASSERT_FALSE(actual.popup.has_value());
  }
}

void AssertEq(const core::ServiceLevelSearchScreen& expected,
              const core::ServiceLevelSearchScreen& actual) {
  ASSERT_EQ(expected.title, actual.title);
  ASSERT_EQ(expected.subtitle, actual.subtitle);
}

}  // namespace

TEST(LongSearchBrandingPlugin, BrandingsOk) {
  LongSearchBrandingPlugin plugin;
  auto context = CreateContext(true);
  auto service_levels = std::vector<core::ServiceLevel>{
      CreateServiceLevel("uberx"), CreateServiceLevel("some_other_class")};

  plugin.OnServiceLevelsReady(context, service_levels);

  ASSERT_EQ(plugin.GetBrandings("some_other_class").size(), 0);

  const auto& uberx_brandings = plugin.GetBrandings("uberx");
  ASSERT_EQ(uberx_brandings.size(), 1);

  const auto& branding = uberx_brandings.front();
  AssertEq(CreateBranding(), branding);
}

class BrandingsDisabledExpParametrize
    : public ::testing::TestWithParam<std::optional<bool>> {
 protected:
  LongSearchBrandingPlugin plugin;
};

TEST_P(BrandingsDisabledExpParametrize, BrandingsDisabledExp) {
  std::optional<bool> is_exp_enabled = GetParam();

  auto context = CreateContext(is_exp_enabled);
  auto service_levels = std::vector<core::ServiceLevel>{
      CreateServiceLevel("uberx"), CreateServiceLevel("some_other_class")};

  plugin.OnServiceLevelsReady(context, service_levels);

  ASSERT_EQ(plugin.GetBrandings("some_other_class").size(), 0);
  ASSERT_EQ(plugin.GetBrandings("uberx").size(), 0);
}

INSTANTIATE_TEST_CASE_P(LongSearchBrandingPlugin,
                        BrandingsDisabledExpParametrize,
                        ::testing::Values(std::nullopt, false));

TEST(LongSearchBrandingPlugin, SearchScreenOk) {
  LongSearchBrandingPlugin plugin;
  auto context = CreateContext(true);

  auto service_levels = std::vector<core::ServiceLevel>{
      CreateServiceLevel("uberx"), CreateServiceLevel("some_other_class")};
  const auto& uberx_serivce_level = service_levels[0];
  const auto& some_other_service_level = service_levels[1];

  const auto extensions = plugin.ExtendServiceLevels(context, service_levels);
  ASSERT_EQ(extensions.size(), 1);

  ApplyExtensions(service_levels, extensions);

  ASSERT_TRUE(uberx_serivce_level.search_screen.has_value());
  ASSERT_FALSE(some_other_service_level.search_screen.has_value());
  AssertEq(CreateSearchScreen(), uberx_serivce_level.search_screen.value());
}

class SearchScreenDisabledExpParametrize
    : public ::testing::TestWithParam<std::optional<bool>> {
 protected:
  LongSearchBrandingPlugin plugin;
};

TEST_P(SearchScreenDisabledExpParametrize, SearchScreenDisabledExp) {
  std::optional<bool> is_exp_enabled = GetParam();
  auto context = CreateContext(is_exp_enabled);

  auto service_levels = std::vector<core::ServiceLevel>{
      CreateServiceLevel("uberx"), CreateServiceLevel("some_other_class")};

  const auto extensions = plugin.ExtendServiceLevels(context, service_levels);
  ASSERT_EQ(extensions.size(), 0);
}

INSTANTIATE_TEST_CASE_P(LongSearchBrandingPlugin,
                        SearchScreenDisabledExpParametrize,
                        ::testing::Values(std::nullopt, false));

}  // namespace routestats::full::brandings
